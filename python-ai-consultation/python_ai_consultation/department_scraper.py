import re
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


class DepartmentScraper:
    BASE_URL = "https://www.xy3yy.com"
    START_URL = BASE_URL + "/ksjj/15380.html"

    def __init__(self, output_dir: str | Path = "ai-consultation/department_info"):
        self.output_dir = Path(output_dir)

    def scrape_from_mapping(self, pages: dict[str, str]) -> list[Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        written = []
        for department_name, content in pages.items():
            path = self.output_dir / (self._safe_filename(department_name) + ".txt")
            path.write_text(content, encoding="utf-8")
            written.append(path)
        return written

    def fetch_text(self, url: str) -> str:
        with urllib.request.urlopen(url, timeout=20) as response:
            return response.read().decode("utf-8", errors="replace")

    def extract_links(self, html: str, base_url: str | None = None) -> dict[str, str]:
        base = base_url or self.BASE_URL
        links: dict[str, str] = {}
        for href, text in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, flags=re.I | re.S):
            name = re.sub(r"<[^>]+>", "", text).strip()
            if href and name and name != "科室介绍":
                links[name] = urljoin(base, href)
        return links

    def _safe_filename(self, department_name: str) -> str:
        return re.sub(r'[/\\?%*:|"<>\\s]+', "_", department_name).strip("_")
