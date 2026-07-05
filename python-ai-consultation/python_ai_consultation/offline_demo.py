from .consultation_controller import ConsultationController
from .consultation_tools import ConsultationTools
from .department_summary_vector_store_job import DepartmentSummaryVectorStoreJob
from .vector_store import SimpleVectorStore


class DemoChatClient:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return """我不是医生，不能做诊断或给治疗建议。

根据你描述的胃痛、腹泻，当前知识库里更匹配的是 **消化内科**。

为了更准确分诊，请再补充：
- 症状持续了多久？
- 是否伴随发热、呕吐或便血？

如果你确认挂消化内科，我可以帮你进行挂号。"""


def main() -> None:
    documents = DepartmentSummaryVectorStoreJob.from_mapping(
        {
            "消化内科": "胃痛 腹痛 腹泻 胃炎 消化性溃疡",
            "呼吸与危重症医学科": "咳嗽 发热 肺炎 哮喘",
            "骨科": "骨折 关节疼痛 腰椎",
        }
    ).get_department_info_documents()
    tools = ConsultationTools()
    controller = ConsultationController(SimpleVectorStore(documents), DemoChatClient(), tools)
    print("问诊回复：")
    for chunk in controller.sse("demo", "我胃痛腹泻，应该挂什么科？"):
        print(chunk["content"], end="", flush=True)
    print("\n\n确认挂号：")
    print(tools.register("消化内科"))


if __name__ == "__main__":
    main()
