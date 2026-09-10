"""
西班牙旅游规划 Agent：LangChain 教学示范版

教学目标
========
1. 使用 LangChain `create_agent` 构建可调用工具的 Agent。
2. 接入真实外部数据，而不是编写返回固定文本的“假工具”。
3. 明确区分：
   - 工具返回的事实；
   - Agent 基于事实给出的规划建议；
   - 当前无法验证、必须由用户确认的信息。
4. 展示输入校验、HTTP 重试、错误处理、缓存和工具调用审计。
5. 避免典型冲突：没有真实价格时，绝不为了完成预算表而虚构费用。

真实数据源
==========
- Open-Meteo：近期天气预报
- Geoapify Geocoding：西班牙城市定位
- Geoapify Places：景点、博物馆、餐厅、酒店、海滩、公园候选项
- Geoapify Routing：城市间道路路线
- Frankfurter：最新可用的每日参考汇率
- 本地确定性工具：可用预算分析、已知费用核算

环境要求
========
Python 3.11+

安装：
    pip install -U langchain langchain-deepseek python-dotenv requests

创建 .env：
    DEEPSEEK_API_KEY=你的_DeepSeek_API_Key
    GEOAPIFY_API_KEY=你的_Geoapify_API_Key

说明
====
- `deepseek-chat` 支持工具调用；不要替换成不支持工具调用的模型。
- Open-Meteo 的普通预报最多覆盖未来约 16 天，本示例会主动校验日期。
- Frankfurter 返回每日参考汇率，不是外汇交易平台的实时成交价。
- Geoapify Places 返回“候选地点”，不代表评分最高、最热门或官方推荐。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache
from typing import Any, Literal, Sequence

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_deepseek import ChatDeepSeek


# =============================================================================
# 1. 配置与基础设施
# =============================================================================

load_dotenv()

REQUEST_TIMEOUT_SECONDS = 20
MAX_WEATHER_FORECAST_DAYS = 16
SPAIN_COUNTRY_CODE = "es"


@dataclass(frozen=True)
class Settings:
    """集中保存运行所需配置，避免在业务代码中散落读取环境变量。"""

    deepseek_api_key: str
    geoapify_api_key: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """读取并验证环境变量；缓存后只执行一次。"""

    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    geoapify_api_key = os.getenv("GEOAPIFY_API_KEY", "").strip()

    missing: list[str] = []
    if not deepseek_api_key:
        missing.append("DEEPSEEK_API_KEY")
    if not geoapify_api_key:
        missing.append("GEOAPIFY_API_KEY")

    if missing:
        raise RuntimeError(
            "缺少环境变量：" + ", ".join(missing) + "。请先在 .env 中配置。"
        )

    return Settings(
        deepseek_api_key=deepseek_api_key,
        geoapify_api_key=geoapify_api_key,
    )


class ExternalAPIError(RuntimeError):
    """外部 API 请求或响应异常。"""


def build_http_session() -> requests.Session:
    """
    创建带自动重试的 HTTP Session。

    会对连接错误、429 限流和常见 5xx 服务错误进行有限次数重试。
    """

    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": "SpainTravelAgentTeachingDemo/2.0",
            "Accept": "application/json",
        }
    )
    return session


HTTP = build_http_session()


def request_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
) -> Any:
    """发送 GET 请求并返回解析后的 JSON；统一处理网络和响应错误。"""

    try:
        response = HTTP.get(url, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        # 不打印带查询参数的完整 URL，避免 API Key 出现在日志中。
        raise ExternalAPIError(f"请求外部服务失败（{url}）：{exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise ExternalAPIError(f"外部服务返回了无效 JSON（{url}）") from exc


def safe_list_item(values: Any, index: int) -> Any:
    """安全读取 API 返回数组中的元素，避免数组缺失或长度不一致时崩溃。"""

    if isinstance(values, list) and 0 <= index < len(values):
        return values[index]
    return None


def normalize_currency_code(code: str) -> str:
    """校验并标准化 ISO 风格的三位货币代码。"""

    normalized = code.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError(f"无效货币代码：{code!r}，应使用 EUR、CNY、USD 等三位代码")
    return normalized


# =============================================================================
# 2. 内部辅助函数：在西班牙境内解析城市
# =============================================================================

@lru_cache(maxsize=128)
def geocode_spain_city(city: str) -> dict[str, Any]:
    """
    使用 Geoapify Geocoding API 在西班牙境内查找城市。

    关键可靠性措施：
    - `type=city`：只搜索城市、城镇、村庄等城市级地点；
    - `filter=countrycode:es`：避免同名城市被解析到其他国家；
    - 返回 `place_id`：供 Places API 使用城市行政边界过滤。
    """

    city = city.strip()
    if not city:
        raise ValueError("城市名称不能为空")

    settings = get_settings()
    data = request_json(
        "https://api.geoapify.com/v1/geocode/search",
        params={
            "text": city,
            "type": "city",
            "filter": f"countrycode:{SPAIN_COUNTRY_CODE}",
            "format": "json",
            "lang": "en",
            "limit": 5,
            "apiKey": settings.geoapify_api_key,
        },
    )

    results = data.get("results", []) if isinstance(data, dict) else []
    if not results:
        raise ValueError(f"未在西班牙境内找到城市：{city}")

    # 优先选择名称精确匹配项；中文输入等无法直接匹配时，使用 API 排名第一项。
    normalized_query = city.casefold()
    chosen = results[0]
    for candidate in results:
        candidate_names = {
            str(candidate.get("city", "")).casefold(),
            str(candidate.get("name", "")).casefold(),
            str(candidate.get("municipality", "")).casefold(),
        }
        if normalized_query in candidate_names:
            chosen = candidate
            break

    country_code = str(chosen.get("country_code", "")).casefold()
    if country_code != SPAIN_COUNTRY_CODE:
        raise ValueError(f"城市解析结果不在西班牙境内：{city}")

    latitude = chosen.get("lat")
    longitude = chosen.get("lon")
    if not isinstance(latitude, (int, float)) or not isinstance(
        longitude, (int, float)
    ):
        raise ValueError(f"城市解析结果缺少有效经纬度：{city}")

    return {
        "query": city,
        "name": chosen.get("city") or chosen.get("name") or city,
        "formatted": chosen.get("formatted"),
        "country": chosen.get("country"),
        "country_code": chosen.get("country_code"),
        "latitude": latitude,
        "longitude": longitude,
        "timezone": chosen.get("timezone", {}).get("name")
        if isinstance(chosen.get("timezone"), dict)
        else chosen.get("timezone"),
        "place_id": chosen.get("place_id"),
        "result_type": chosen.get("result_type"),
    }


# =============================================================================
# 3. 工具一：真实天气预报
# =============================================================================

WEATHER_CODES: dict[int, str] = {
    0: "晴朗",
    1: "大致晴朗",
    2: "局部多云",
    3: "阴天",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "中等毛毛雨",
    55: "强毛毛雨",
    56: "轻微冻毛毛雨",
    57: "强冻毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "轻微冻雨",
    67: "强冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "霰",
    80: "小阵雨",
    81: "中等阵雨",
    82: "强阵雨",
    85: "小阵雪",
    86: "大阵雪",
    95: "雷暴",
    96: "雷暴并伴有小冰雹",
    99: "雷暴并伴有强冰雹",
}


@tool
def get_weather_forecast(
    city: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """
    查询西班牙城市在指定日期范围内的真实近期天气预报。

    参数：
    - city：西班牙城市名，例如 Madrid、Barcelona、马德里；
    - start_date、end_date：YYYY-MM-DD，包含首尾两天。

    限制：
    - 仅支持从今天开始、未来最多约 16 天的近期预报；
    - 不得用本工具查询数月后的精确天气或历史天气。
    """

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        today = date.today()
        latest_supported = today + timedelta(days=MAX_WEATHER_FORECAST_DAYS - 1)

        if end < start:
            return {"ok": False, "error": "end_date 不能早于 start_date"}
        if start < today:
            return {
                "ok": False,
                "error": "该工具只查询从今天开始的未来天气预报，不查询历史天气",
            }
        if end > latest_supported:
            return {
                "ok": False,
                "error": (
                    f"日期超出近期预报范围；当前最多查询至 "
                    f"{latest_supported.isoformat()}"
                ),
            }

        location = geocode_spain_city(city)
        data = request_json(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "daily": (
                    "weather_code,temperature_2m_max,temperature_2m_min,"
                    "precipitation_probability_max,wind_speed_10m_max"
                ),
                "timezone": "auto",
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "precipitation_unit": "mm",
            },
        )

        daily = data.get("daily", {}) if isinstance(data, dict) else {}
        dates = daily.get("time", [])
        if not isinstance(dates, list) or not dates:
            return {"ok": False, "error": "天气 API 未返回每日预报数据"}

        forecasts: list[dict[str, Any]] = []
        for index, current_date in enumerate(dates):
            raw_code = safe_list_item(daily.get("weather_code"), index)
            weather_text = (
                WEATHER_CODES.get(raw_code, f"未知天气代码：{raw_code}")
                if isinstance(raw_code, int)
                else "数据源未提供"
            )

            forecasts.append(
                {
                    "date": current_date,
                    "weather_code": raw_code,
                    "weather": weather_text,
                    "temperature_max_c": safe_list_item(
                        daily.get("temperature_2m_max"), index
                    ),
                    "temperature_min_c": safe_list_item(
                        daily.get("temperature_2m_min"), index
                    ),
                    "precipitation_probability_percent": safe_list_item(
                        daily.get("precipitation_probability_max"), index
                    ),
                    "wind_speed_max_kmh": safe_list_item(
                        daily.get("wind_speed_10m_max"), index
                    ),
                }
            )

        return {
            "ok": True,
            "source": "Open-Meteo Weather Forecast API",
            "retrieved_for": location,
            "forecast_timezone": data.get("timezone")
            if isinstance(data, dict)
            else None,
            "forecast": forecasts,
            "notice": (
                "天气预报会随模型更新而变化；临近出发时应再次查询。"
            ),
        }

    except ExternalAPIError as exc:
        return {"ok": False, "error": f"天气服务请求失败：{exc}"}
    except (ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "error": f"天气参数或数据处理失败：{exc}"}


# =============================================================================
# 4. 工具二：真实地点候选搜索
# =============================================================================

PlaceType = Literal[
    "attractions",
    "museums",
    "historic_sites",
    "restaurants",
    "spanish_restaurants",
    "hotels",
    "beaches",
    "parks",
]

PLACE_CATEGORY_MAP: dict[str, str] = {
    "attractions": "tourism.attraction,tourism.sights",
    "museums": "entertainment.museum",
    "historic_sites": "tourism.sights,building.historic",
    "restaurants": "catering.restaurant",
    "spanish_restaurants": (
        "catering.restaurant.spanish,catering.restaurant.tapas"
    ),
    "hotels": "accommodation.hotel",
    "beaches": "beach",
    "parks": "leisure.park",
}


def extract_place_website(properties: dict[str, Any]) -> str | None:
    """从 Geoapify 不同层级字段中提取网站；不存在就返回 None。"""

    direct = properties.get("website")
    if isinstance(direct, str) and direct.strip():
        return direct

    contact = properties.get("contact")
    if isinstance(contact, dict):
        website = contact.get("website")
        if isinstance(website, str) and website.strip():
            return website

    datasource = properties.get("datasource")
    if isinstance(datasource, dict):
        raw = datasource.get("raw")
        if isinstance(raw, dict):
            website = raw.get("website") or raw.get("contact:website")
            if isinstance(website, str) and website.strip():
                return website

    return None


def extract_opening_hours(properties: dict[str, Any]) -> str | None:
    """提取营业时间；没有数据时返回 None，绝不补写。"""

    direct = properties.get("opening_hours")
    if isinstance(direct, str) and direct.strip():
        return direct

    datasource = properties.get("datasource")
    if isinstance(datasource, dict):
        raw = datasource.get("raw")
        if isinstance(raw, dict):
            opening_hours = raw.get("opening_hours")
            if isinstance(opening_hours, str) and opening_hours.strip():
                return opening_hours

    return None


@tool
def search_places(
    city: str,
    place_type: PlaceType,
    limit: int = 8,
) -> dict[str, Any]:
    """
    在西班牙指定城市的行政边界内搜索真实地点候选项。

    place_type 可选：
    attractions、museums、historic_sites、restaurants、
    spanish_restaurants、hotels、beaches、parks。

    返回名称、地址、距城市中心的近似距离、经纬度、网站和营业时间。
    结果只是基于 OpenStreetMap 数据的候选地点，不代表“最佳”“最高评分”或官方推荐。
    工具未返回的网站、营业时间、价格、评分等信息不得自行编造。
    """

    try:
        if place_type not in PLACE_CATEGORY_MAP:
            return {"ok": False, "error": f"不支持的地点类型：{place_type}"}

        limit = max(1, min(int(limit), 20))
        location = geocode_spain_city(city)
        settings = get_settings()

        longitude = location["longitude"]
        latitude = location["latitude"]
        place_id = location.get("place_id")

        # 优先按城市行政边界过滤；若 API 未提供 place_id，则退化为 20km 圆形范围。
        spatial_filter = (
            f"place:{place_id}"
            if place_id
            else f"circle:{longitude},{latitude},20000"
        )

        data = request_json(
            "https://api.geoapify.com/v2/places",
            params={
                "categories": PLACE_CATEGORY_MAP[place_type],
                "filter": spatial_filter,
                "bias": f"proximity:{longitude},{latitude}",
                "limit": limit,
                "lang": "en",
                "apiKey": settings.geoapify_api_key,
            },
        )

        features = data.get("features", []) if isinstance(data, dict) else []
        places: list[dict[str, Any]] = []

        for feature in features:
            properties = feature.get("properties", {})
            if not isinstance(properties, dict):
                continue

            raw_distance = properties.get("distance")
            distance_km = (
                round(raw_distance / 1000, 2)
                if isinstance(raw_distance, (int, float))
                else None
            )

            name = (
                properties.get("name")
                or properties.get("address_line1")
                or "数据源未提供名称"
            )

            places.append(
                {
                    "name": name,
                    "address": properties.get("formatted"),
                    "city": properties.get("city"),
                    "distance_from_city_center_km": distance_km,
                    "latitude": properties.get("lat"),
                    "longitude": properties.get("lon"),
                    "website": extract_place_website(properties),
                    "opening_hours": extract_opening_hours(properties),
                    "categories": properties.get("categories", []),
                    "place_id": properties.get("place_id"),
                }
            )

        return {
            "ok": True,
            "source": "Geoapify Places API / OpenStreetMap",
            "search_city": location,
            "place_type": place_type,
            "result_count": len(places),
            "places": places,
            "notice": (
                "这些是数据源返回的候选项，不是评分榜单；"
                "营业时间、网站、价格等字段可能缺失或过期，出行前需向场所官方确认。"
            ),
        }

    except ExternalAPIError as exc:
        return {"ok": False, "error": f"地点服务请求失败：{exc}"}
    except (ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "error": f"地点参数或数据处理失败：{exc}"}


# =============================================================================
# 5. 工具三：城市间真实道路路线
# =============================================================================

RouteMode = Literal["drive", "walk", "bicycle"]


@tool
def get_city_to_city_road_route(
    origin_city: str,
    destination_city: str,
    mode: RouteMode = "drive",
) -> dict[str, Any]:
    """
    查询两个西班牙城市中心之间的真实道路路线距离和估算时间。

    mode 可选：drive、walk、bicycle。

    重要限制：
    - 这是道路路线，不是火车、飞机或公共交通时刻表；
    - 不得把道路行驶时间描述成高铁、火车或飞机时间；
    - 结果是路线服务估算，不包含实时交通拥堵和票价。
    """

    try:
        if mode not in {"drive", "walk", "bicycle"}:
            return {"ok": False, "error": f"不支持的路线方式：{mode}"}

        origin = geocode_spain_city(origin_city)
        destination = geocode_spain_city(destination_city)
        settings = get_settings()

        waypoints = (
            f"{origin['latitude']},{origin['longitude']}|"
            f"{destination['latitude']},{destination['longitude']}"
        )

        data = request_json(
            "https://api.geoapify.com/v1/routing",
            params={
                "waypoints": waypoints,
                "mode": mode,
                "format": "json",
                "apiKey": settings.geoapify_api_key,
            },
        )

        results = data.get("results", []) if isinstance(data, dict) else []
        if not results:
            return {"ok": False, "error": "路线 API 未返回可用路线"}

        route = results[0]
        distance_m = route.get("distance")
        duration_s = route.get("time")

        if not isinstance(distance_m, (int, float)) or not isinstance(
            duration_s, (int, float)
        ):
            return {"ok": False, "error": "路线 API 未返回有效距离或时间"}

        return {
            "ok": True,
            "source": "Geoapify Routing API",
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "distance_km": round(distance_m / 1000, 1),
            "duration_hours": round(duration_s / 3600, 2),
            "duration_minutes": round(duration_s / 60),
            "notice": (
                "该结果是城市中心之间的道路路线估算，不是铁路、航空或实时交通数据。"
            ),
        }

    except ExternalAPIError as exc:
        return {"ok": False, "error": f"路线服务请求失败：{exc}"}
    except (ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "error": f"路线参数或数据处理失败：{exc}"}


# =============================================================================
# 6. 工具四：最新每日参考汇率
# =============================================================================

@tool
def convert_currency(
    amount: float,
    base_currency: str,
    target_currency: str,
) -> dict[str, Any]:
    """
    使用 Frankfurter 最新可用的每日参考汇率进行货币换算。

    货币必须使用三位代码，例如 EUR、CNY、USD、GBP。
    该汇率不是银行最终结算价，也不是外汇市场实时成交价。
    """

    try:
        if amount < 0:
            return {"ok": False, "error": "金额不能小于 0"}

        base = normalize_currency_code(base_currency)
        target = normalize_currency_code(target_currency)

        if base == target:
            return {
                "ok": True,
                "source": "本地恒等换算",
                "rate_date": date.today().isoformat(),
                "amount": round(amount, 2),
                "base_currency": base,
                "target_currency": target,
                "rate": 1.0,
                "converted_amount": round(amount, 2),
                "notice": "源货币与目标货币相同，无需调用外部汇率服务。",
            }

        data = request_json(
            f"https://api.frankfurter.dev/v2/rate/{base}/{target}"
        )
        if not isinstance(data, dict):
            return {"ok": False, "error": "汇率 API 返回格式异常"}

        rate = data.get("rate")
        if not isinstance(rate, (int, float)):
            return {
                "ok": False,
                "error": f"没有获得 {base} 到 {target} 的有效汇率",
            }

        return {
            "ok": True,
            "source": "Frankfurter v2",
            "rate_date": data.get("date"),
            "amount": round(amount, 2),
            "base_currency": base,
            "target_currency": target,
            "rate": rate,
            "converted_amount": round(amount * rate, 2),
            "notice": (
                "这是最新可用的每日参考汇率，不是实时交易价；"
                "银行卡、支付平台和银行可能收取点差或手续费。"
            ),
        }

    except ExternalAPIError as exc:
        return {"ok": False, "error": f"汇率服务请求失败：{exc}"}
    except (ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "error": f"汇率参数或数据处理失败：{exc}"}


# =============================================================================
# 7. 工具五：可用预算分析（不需要虚构价格）
# =============================================================================

@tool
def analyze_budget_capacity(
    total_budget: float,
    number_of_people: int,
    number_of_days: int,
    currency: str = "EUR",
) -> dict[str, Any]:
    """
    分析旅行总预算对应的每人预算、每日预算和每人每日预算。

    该工具只分析“可使用多少钱”，不查询、假设或编造机票、酒店、门票等价格。
    """

    try:
        if total_budget < 0:
            return {"ok": False, "error": "总预算不能小于 0"}
        if number_of_people <= 0:
            return {"ok": False, "error": "人数必须大于 0"}
        if number_of_days <= 0:
            return {"ok": False, "error": "旅行天数必须大于 0"}

        normalized_currency = normalize_currency_code(currency)

        return {
            "ok": True,
            "source": "本地确定性计算",
            "currency": normalized_currency,
            "total_budget": round(total_budget, 2),
            "number_of_people": number_of_people,
            "number_of_days": number_of_days,
            "budget_per_person": round(total_budget / number_of_people, 2),
            "budget_per_day_for_group": round(total_budget / number_of_days, 2),
            "budget_per_person_per_day": round(
                total_budget / number_of_people / number_of_days,
                2,
            ),
            "notice": (
                "该结果只是预算容量，不代表旅行实际成本，也不证明预算一定充足。"
            ),
        }

    except (ValueError, TypeError) as exc:
        return {"ok": False, "error": f"预算参数处理失败：{exc}"}


# =============================================================================
# 8. 工具六：已知费用核算（仅在用户提供费用时调用）
# =============================================================================

@tool
def calculate_known_trip_costs(
    international_transport: float,
    accommodation: float,
    local_transport: float,
    food: float,
    attraction_tickets: float,
    other_expenses: float,
    total_budget: float,
    currency: str = "EUR",
) -> dict[str, Any]:
    """
    汇总用户已经提供或外部可靠来源已经返回的旅行费用，并计算预算余额。

    所有金额必须使用相同货币。
    没有获得真实费用时，不得为了调用本工具而自行填写估算值。
    """

    try:
        normalized_currency = normalize_currency_code(currency)
        values = {
            "international_transport": international_transport,
            "accommodation": accommodation,
            "local_transport": local_transport,
            "food": food,
            "attraction_tickets": attraction_tickets,
            "other_expenses": other_expenses,
            "total_budget": total_budget,
        }

        if any(value < 0 for value in values.values()):
            return {"ok": False, "error": "费用和预算金额不能小于 0"}

        cost_items = {
            key: value for key, value in values.items() if key != "total_budget"
        }
        total_cost = sum(cost_items.values())
        remaining = total_budget - total_cost

        return {
            "ok": True,
            "source": "本地确定性计算",
            "currency": normalized_currency,
            "breakdown": {
                key: round(value, 2) for key, value in cost_items.items()
            },
            "total_cost": round(total_cost, 2),
            "total_budget": round(total_budget, 2),
            "remaining_budget": round(remaining, 2),
            "within_budget": remaining >= 0,
            "notice": "结果完全取决于输入费用是否真实、完整且使用同一货币。",
        }

    except (ValueError, TypeError) as exc:
        return {"ok": False, "error": f"费用参数处理失败：{exc}"}


# =============================================================================
# 9. Agent 系统提示词
# =============================================================================

SYSTEM_PROMPT = """
你是一名严谨、可审计的西班牙旅游规划 Agent。

你的目标不是写一篇看起来合理的旅游文章，而是：
基于工具返回的真实数据，给出明确区分“事实、建议和未知项”的旅行方案。

【一、先检查需求】
完整规划至少需要：出发城市、旅行起止日期、人数、总预算、预算币种、兴趣偏好。
如果用户明确要求直接规划，但仍缺少关键字段，只询问真正缺失的字段；不要重复询问已经提供的信息。

【二、工具使用规则】
1. 涉及近期天气，必须调用 get_weather_forecast；行程包含多个城市时，应分别查询。
2. 涉及景点、博物馆、餐厅、酒店、海滩或公园，必须调用 search_places。
3. 涉及西班牙城市间道路距离或道路时间，必须调用 get_city_to_city_road_route。
4. 涉及币种换算，必须调用 convert_currency。
5. 涉及总预算的每人/每日容量，必须调用 analyze_budget_capacity。
6. 只有用户已经提供各项费用，或其他可靠工具已经返回费用时，才能调用 calculate_known_trip_costs。
7. 工具调用失败时，明确说明失败；不得用模型常识伪造一个“像真的”结果。

【三、事实边界】
1. 不得编造天气、路线距离、汇率、营业时间、网站、评分、门票、机票、酒店或交通票价。
2. 工具没有返回的信息，明确写“数据源未提供”或“需要官方确认”。
3. Frankfurter 是每日参考汇率，不得描述为实时外汇成交价。
4. Geoapify Places 返回地点候选项，不是评分榜单；不得称其为“最佳”“最热门”或“排名第一”。
5. Geoapify Routing 返回道路路线，不得描述成高铁、火车、航班或公共交通时刻。
6. 没有价格数据时，只能分析预算容量，不能断言总预算一定够或不够。
7. 对营业时间、门票和预订要求，应提醒用户在出发前查看场所官方渠道。

【四、规划原则】
1. 优先减少不必要的跨城往返。
2. 根据天气，把降雨风险较高的日期优先安排室内活动。
3. 每日活动量应合理，不要为了覆盖更多地点而堆砌行程。
4. 可根据地址、城市中心距离和常识做“近似集中”的规划建议，但不得声称已经求得数学最优路线。
5. 明确标出：工具事实、规划建议、待确认项。

【五、最终输出结构】
请使用中文，并按以下结构输出：
1. 需求摘要
2. 城市与天数分配
3. 每日行程（注明“建议”而非已预订安排）
4. 天气摘要（工具事实）
5. 城市间道路路线（工具事实，并注明不是铁路时间）
6. 地点候选项及数据来源
7. 预算与汇率
   - 已换算的总预算
   - 每人、每日、每人每日预算容量
   - 未获得真实价格时，不制作虚假的完整费用明细
8. 数据限制与出发前确认清单

最终答案必须让读者一眼看出：哪些是工具验证的数据，哪些只是你的规划建议。
""".strip()


# =============================================================================
# 10. 创建模型和 Agent
# =============================================================================

def build_agent() -> Any:
    """构建 LangChain Agent；在此处统一配置模型和工具。"""

    # 提前校验环境变量，避免执行到一半才发现缺少 Key。
    get_settings()

    model = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        max_tokens=4096,
        timeout=60,
        max_retries=2,
    )

    return create_agent(
        model=model,
        tools=[
            get_weather_forecast,
            search_places,
            get_city_to_city_road_route,
            convert_currency,
            analyze_budget_capacity,
            calculate_known_trip_costs,
        ],
        system_prompt=SYSTEM_PROMPT,
    )


# =============================================================================
# 11. 教学辅助：执行轨迹与工具调用审计
# =============================================================================

def content_to_text(content: Any) -> str:
    """兼容字符串和内容块形式的模型输出。"""

    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
                else:
                    parts.append(json.dumps(block, ensure_ascii=False))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)


def print_execution_trace(messages: Sequence[BaseMessage]) -> None:
    """打印模型消息、工具调用和工具返回，便于课堂观察 Agent 循环。"""

    print("\n" + "=" * 88)
    print("Agent 完整执行轨迹")
    print("=" * 88)

    for index, message in enumerate(messages, start=1):
        print(f"\n--- Message {index}: {message.__class__.__name__} ---")

        if isinstance(message, AIMessage) and message.tool_calls:
            if message.content:
                print(content_to_text(message.content))
            print("工具调用：")
            for call in message.tool_calls:
                print(
                    json.dumps(
                        {
                            "name": call.get("name"),
                            "args": call.get("args"),
                            "id": call.get("id"),
                        },
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )
                )
        elif isinstance(message, ToolMessage):
            print(f"工具名称：{message.name}")
            print(content_to_text(message.content))
        else:
            print(content_to_text(message.content))


def audit_tool_usage(messages: Sequence[BaseMessage]) -> dict[str, Any]:
    """
    审计工具调用次数和明显失败结果。

    这不是替代 Agent 的业务逻辑，而是向学生展示：
    系统提示词属于软约束，关键要求还应在程序层检查。
    """

    call_counts: dict[str, int] = {}
    call_arguments: list[dict[str, Any]] = []
    failed_tool_messages: list[dict[str, str]] = []

    for message in messages:
        if isinstance(message, AIMessage):
            for call in message.tool_calls or []:
                name = str(call.get("name", "unknown"))
                call_counts[name] = call_counts.get(name, 0) + 1
                call_arguments.append(
                    {
                        "name": name,
                        "args": call.get("args", {}),
                    }
                )

        if isinstance(message, ToolMessage):
            text = content_to_text(message.content)
            compact = text.replace(" ", "").lower()
            if '"ok":false' in compact or "'ok':false" in compact:
                failed_tool_messages.append(
                    {
                        "name": message.name or "unknown",
                        "result": text,
                    }
                )

    # 针对本文件 main() 的示例请求设定最低预期。
    minimum_expected_calls = {
        "get_weather_forecast": 2,
        "search_places": 4,
        "get_city_to_city_road_route": 1,
        "convert_currency": 1,
        "analyze_budget_capacity": 1,
    }

    missing_or_insufficient = {
        name: {
            "expected_at_least": minimum,
            "actual": call_counts.get(name, 0),
        }
        for name, minimum in minimum_expected_calls.items()
        if call_counts.get(name, 0) < minimum
    }

    return {
        "call_counts": call_counts,
        "call_arguments": call_arguments,
        "missing_or_insufficient": missing_or_insufficient,
        "failed_tool_messages": failed_tool_messages,
        "passed_minimum_demo_policy": (
            not missing_or_insufficient and not failed_tool_messages
        ),
    }


def extract_final_answer(messages: Sequence[BaseMessage]) -> str:
    """提取最后一条 AI 文本消息作为最终答案。"""

    for message in reversed(messages):
        if isinstance(message, AIMessage) and not message.tool_calls:
            text = content_to_text(message.content).strip()
            if text:
                return text
    raise RuntimeError("Agent 没有生成最终文本答案")


# =============================================================================
# 12. 可直接运行的完整示例
# =============================================================================

def main() -> None:
    """运行一次完整的西班牙双城旅行规划示例。"""

    # Open-Meteo 只提供近期预报，因此使用动态日期确保示例长期可运行。
    trip_start = date.today() + timedelta(days=3)
    trip_end = trip_start + timedelta(days=6)  # 含首尾共 7 天

    user_request = f"""
我计划两个人从中国深圳前往西班牙旅行 7 天。

旅行日期：
{trip_start.isoformat()} 至 {trip_end.isoformat()}（包含首尾两天）

总预算：
两个人合计 30000 元人民币。

计划城市：
马德里和巴塞罗那。

兴趣：
历史建筑、博物馆、西班牙美食、海边风景。

请完成以下任务：
1. 合理分配两个城市的天数，尽量减少跨城往返；
2. 分别查询两个城市在旅行日期内的真实天气；
3. 查询真实的历史景点、博物馆、西班牙餐厅候选项；
4. 在巴塞罗那查询海滩候选项；
5. 查询马德里到巴塞罗那的驾车道路距离和道路时间；
6. 把 30000 元人民币换算成欧元；
7. 分析每人、每日和每人每日的可用预算。

当前没有提供真实机票、酒店、铁路票、门票和餐饮报价。
因此不要编造这些价格，也不要制作虚假的完整费用明细。
""".strip()

    agent = build_agent()
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_request,
                }
            ]
        }
    )

    messages = result.get("messages", [])
    if not isinstance(messages, list) or not messages:
        raise RuntimeError("Agent 返回结果中没有 messages")

    print_execution_trace(messages)

    audit = audit_tool_usage(messages)
    print("\n" + "=" * 88)
    print("工具调用审计")
    print("=" * 88)
    print(json.dumps(audit, ensure_ascii=False, indent=2, default=str))

    print("\n" + "=" * 88)
    print("最终旅行方案")
    print("=" * 88)
    print(extract_final_answer(messages))


if __name__ == "__main__":
    main()
