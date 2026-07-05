from dataclasses import dataclass


DEFAULT_CUSTOMER_TEXT = """# AI-Order 客服知识库

### 如何下单？
告诉我您想要的商品，确认商品后提供收货信息，再创建订单并支付。

### 退款到账时间
退款一般 3-5 个工作日到账。

### 配送费用
订单满299元免运费，不满299元收取15元运费。
"""


@dataclass
class Document:
    text: str
    metadata: dict


class OrderDocumentParser:
    def __init__(self, content: str = DEFAULT_CUSTOMER_TEXT):
        self.content = content

    def parse(self) -> list[Document]:
        documents: list[Document] = []
        for title, body in self.parse_third_level_headings(self.content).items():
            documents.append(Document(f"{title}\n{body}", {"title": title, "level": "h3"}))
        return documents

    def parse_third_level_headings(self, content: str) -> dict[str, str]:
        headings: dict[str, str] = {}
        current_title: str | None = None
        current_lines: list[str] = []
        for line in content.splitlines():
            if line.startswith("### "):
                if current_title is not None:
                    headings[current_title] = "\n".join(current_lines).strip()
                current_title = line[4:].strip()
                current_lines = []
            elif line.startswith("#") and current_title is not None:
                headings[current_title] = "\n".join(current_lines).strip()
                current_title = None
                current_lines = []
            elif current_title is not None:
                current_lines.append(line)
        if current_title is not None:
            headings[current_title] = "\n".join(current_lines).strip()
        return headings
