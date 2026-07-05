from .consultation_controller import ConsultationController
from .consultation_tools import ConsultationTools
from .department_summary_vector_store_job import DepartmentSummaryVectorStoreJob
from .vector_store import SimpleVectorStore


class FakeChatClient:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        assert "严禁提供任何形式的医学诊断" in system_prompt
        assert "消化内科" in user_prompt
        return "请补充症状持续时间，可优先咨询消化内科。"


def main() -> None:
    documents = DepartmentSummaryVectorStoreJob.from_mapping({"消化内科": "胃痛 腹痛 腹泻"}).get_department_info_documents()
    tools = ConsultationTools()
    controller = ConsultationController(SimpleVectorStore(documents), FakeChatClient(), tools)
    text = "".join(chunk["content"] for chunk in controller.sse("check", "胃痛腹泻"))
    assert "消化内科" in text
    assert tools.register("消化内科") == "挂号成功，请等待医生处理"
    print("python-ai-consultation self check passed")


if __name__ == "__main__":
    main()
