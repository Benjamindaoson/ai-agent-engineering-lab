from pathlib import Path

from .document import Document


class DepartmentSummaryVectorStoreJob:
    def __init__(self, department_summary_info_dir: str | Path):
        self.department_summary_info_dir = Path(department_summary_info_dir)
        self._mapping: dict[str, str] | None = None

    @classmethod
    def from_mapping(cls, mapping: dict[str, str]) -> "DepartmentSummaryVectorStoreJob":
        job = cls(".")
        job._mapping = mapping
        return job

    def get_department_info_documents(self) -> list[Document]:
        if self._mapping is not None:
            return [Document(content, {"departmentName": name}) for name, content in self._mapping.items()]
        documents: list[Document] = []
        for path in sorted(self.department_summary_info_dir.glob("*.txt")):
            documents.append(Document(path.read_text(encoding="utf-8"), {"departmentName": path.stem}))
        return documents

    def init(self, vector_store) -> int:
        documents = self.get_department_info_documents()
        for index in range(0, len(documents), 5):
            vector_store.add(documents[index : index + 5])
        return len(documents)
