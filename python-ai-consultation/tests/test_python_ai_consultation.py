import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_ai_consultation.consultation_controller import ConsultationController
from python_ai_consultation.consultation_query_expander import ConsultationQueryExpander
from python_ai_consultation.consultation_tools import ConsultationTools
from python_ai_consultation.department_summary_job import DepartmentSummaryJob
from python_ai_consultation.department_summary_vector_store_job import DepartmentSummaryVectorStoreJob
from python_ai_consultation.vector_store import SimpleVectorStore


class FakeChatClient:
    def __init__(self, text="建议优先挂消化内科。"):
        self.text = text
        self.calls = []

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self.text


class PythonAiConsultationTests(unittest.TestCase):
    def test_vector_store_job_loads_department_summary_documents(self):
        with tempfile.TemporaryDirectory() as tempdir:
            pathlib.Path(tempdir, "消化内科.txt").write_text("腹痛、腹泻、胃炎", encoding="utf-8")

            documents = DepartmentSummaryVectorStoreJob(tempdir).get_department_info_documents()

        self.assertEqual("消化内科", documents[0].metadata["departmentName"])
        self.assertIn("腹痛", documents[0].text)

    def test_query_expander_returns_only_user_history_questions(self):
        history = [
            {"role": "user", "content": "我肚子疼"},
            {"role": "assistant", "content": "疼多久了？"},
            {"role": "user", "content": "还腹泻"},
        ]

        expanded = ConsultationQueryExpander().expand("最新问题", history)

        self.assertEqual(["我肚子疼", "还腹泻"], expanded)

    def test_simple_vector_store_retrieves_top_matching_departments(self):
        store = SimpleVectorStore(
            DepartmentSummaryVectorStoreJob.from_mapping(
                {
                    "消化内科": "胃痛 腹痛 腹泻 胃炎",
                    "骨科": "骨折 关节疼痛 腰椎",
                    "呼吸与危重症医学科": "咳嗽 发热 肺炎",
                }
            ).get_department_info_documents()
        )

        documents = store.search(["胃痛腹泻"], top_k=2)

        self.assertEqual("消化内科", documents[0].metadata["departmentName"])

    def test_controller_streams_rag_context_and_keeps_chat_memory(self):
        store = SimpleVectorStore(
            DepartmentSummaryVectorStoreJob.from_mapping({"消化内科": "胃痛 腹痛 腹泻"}).get_department_info_documents()
        )
        chat_client = FakeChatClient("请补充疼痛持续时间，可能需要消化内科。")
        controller = ConsultationController(store, chat_client, ConsultationTools())

        stream_text = "".join(chunk["content"] for chunk in controller.sse("c1", "我胃痛腹泻"))

        self.assertIn("消化内科", chat_client.calls[0][1])
        self.assertIn("请补充", stream_text)
        self.assertEqual("我胃痛腹泻", controller.chat_memory["c1"][0]["content"])

    def test_register_tool_records_department(self):
        tools = ConsultationTools()

        result = tools.register("消化内科")

        self.assertEqual("挂号成功，请等待医生处理", result)
        self.assertEqual(["消化内科"], tools.registrations)

    def test_summary_job_skips_existing_and_writes_missing_summary(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as target:
            pathlib.Path(source, "消化内科.txt").write_text("消化内科介绍", encoding="utf-8")
            job = DepartmentSummaryJob(FakeChatClient("消化内科主要诊治胃痛。"), source, target)

            written = job.init()

            self.assertEqual(["消化内科.txt"], written)
            self.assertIn("胃痛", pathlib.Path(target, "消化内科.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
