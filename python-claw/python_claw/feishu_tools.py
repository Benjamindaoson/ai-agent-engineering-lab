from __future__ import annotations

import operator
from datetime import datetime
from typing import Callable


class FeishuTools:
    def __init__(self, random_func: Callable[[int, int], int] | None = None) -> None:
        self.random_func = random_func

    def get_current_time(self) -> str:
        return "当前时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_weather(self, city: str) -> str:
        weathers = ["晴天", "多云", "小雨", "大雨", "阴天"]
        temps = ["22°C", "25°C", "28°C", "18°C", "20°C"]
        index = abs(self._stable_hash(city)) % len(weathers)
        return f"{city} 的天气：{weathers[index]}，温度：{temps[index]}"

    def calculate(self, expression: str) -> str:
        expr = expression.replace(" ", "")
        for symbol, func in {"+": operator.add, "*": operator.mul, "/": operator.truediv}.items():
            if symbol in expr:
                return self._calculate_binary(expr, symbol, func)
        if "-" in expr[1:]:
            return self._calculate_binary(expr, "-", operator.sub)
        return f"计算结果: {expr}"

    def generate_random_number(self, min_value: int, max_value: int) -> str:
        if min_value > max_value:
            return "错误：最小值不能大于最大值"
        if self.random_func:
            value = self.random_func(min_value, max_value)
        else:
            import random

            value = random.randint(min_value, max_value)
        return f"随机数: {value}"

    def translate(self, text: str, target_lang: str) -> str:
        return f"【模拟翻译】将 \"{text}\" 翻译为{target_lang}"

    def _calculate_binary(self, expr: str, symbol: str, func) -> str:
        try:
            left, right = expr.split(symbol, 1)
            return f"计算结果: {func(float(left), float(right))}"
        except (ValueError, ZeroDivisionError):
            return "计算失败，请检查表达式格式"

    def _stable_hash(self, value: str) -> int:
        total = 0
        for char in value:
            total = (31 * total + ord(char)) & 0xFFFFFFFF
        return total
