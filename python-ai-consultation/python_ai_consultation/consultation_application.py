from pathlib import Path

from .chat_client import ChatClient
from .consultation_controller import ConsultationController
from .consultation_tools import ConsultationTools
from .department_summary_vector_store_job import DepartmentSummaryVectorStoreJob
from .document import Document
from .model_config import ModelConfig
from .vector_store import SimpleVectorStore


def default_summary_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "ai-consultation" / "department_summary_info"


def create_controller(chat_client=None) -> ConsultationController:
    summary_dir = default_summary_dir()
    if summary_dir.exists():
        documents = DepartmentSummaryVectorStoreJob(summary_dir).get_department_info_documents()
    else:
        documents = [
            Document("胃痛 腹痛 腹泻 胃炎", {"departmentName": "消化内科"}),
            Document("咳嗽 发热 肺炎 哮喘", {"departmentName": "呼吸与危重症医学科"}),
            Document("骨折 关节疼痛 腰椎", {"departmentName": "骨科"}),
        ]
    client = chat_client or ChatClient(ModelConfig.from_env())
    return ConsultationController(SimpleVectorStore(documents), client, ConsultationTools())


def main() -> None:
    controller = create_controller()
    chat_id = "cli"
    question = input("请输入问诊问题: ").strip()
    for chunk in controller.sse(chat_id, question):
        print(chunk["content"], end="", flush=True)
    print()


if __name__ == "__main__":
    main()
