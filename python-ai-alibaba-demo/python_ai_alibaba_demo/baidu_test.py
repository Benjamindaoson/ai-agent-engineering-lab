from __future__ import annotations

from urllib.parse import quote_plus


def build_baidu_search_request(query: str, top_k: int = 10) -> dict[str, object]:
    return {
        "query": query,
        "top_k": top_k,
        "url": f"https://www.baidu.com/s?wd={quote_plus(query)}",
    }


def baidu_search(query: str, top_k: int = 10) -> dict[str, object]:
    request = build_baidu_search_request(query, top_k=top_k)
    return {
        "request": request,
        "items": [
            {
                "title": f"Baidu search for {query}",
                "url": request["url"],
                "snippet": "Offline demo request only. Live Baidu access is not required.",
            }
        ],
    }


def main() -> None:
    print(baidu_search("Spring AI Alibaba"))


if __name__ == "__main__":
    main()
