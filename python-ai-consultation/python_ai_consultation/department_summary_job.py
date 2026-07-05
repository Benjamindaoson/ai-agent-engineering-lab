from pathlib import Path


SUMMARY_SYSTEM_PROMPT = """
## 角色
你是一个AI问诊助手

## 任务
请根据提供的科室介绍内容，总结出该科室主要诊治的疾病有哪些，只需要返回最精炼的总结即可
"""


class DepartmentSummaryJob:
    def __init__(self, chat_client, department_info_dir: str | Path, department_summary_info_dir: str | Path):
        self.chat_client = chat_client
        self.department_info_dir = Path(department_info_dir)
        self.department_summary_info_dir = Path(department_summary_info_dir)

    def init(self) -> list[str]:
        self.department_summary_info_dir.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        for source_path in sorted(self.department_info_dir.glob("*.txt")):
            target_path = self.department_summary_info_dir / source_path.name
            if target_path.exists():
                continue
            content = source_path.read_text(encoding="utf-8")
            summary = self.chat_client.complete(SUMMARY_SYSTEM_PROMPT, "科室介绍：" + content)
            target_path.write_text(summary, encoding="utf-8")
            written.append(source_path.name)
        return written
