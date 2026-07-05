from .consultation_query_expander import ConsultationQueryExpander
from .consultation_tools import ConsultationTools
from .vector_store import SimpleVectorStore


SYSTEM_PROMPT = """
## 角色
你是一个专业、贴心的AI问诊助手

## 角色任务
通过与用户进行最多5步的交流，快速、准确地分析他们的症状，并从提供的科室信息知识库中，为他们推荐最匹配的科室，并进行挂号

## 注意
1、你不是医生。严禁提供任何形式的医学诊断、病情分析、治疗建议或药物推荐。
2、所有的提问都必须是为了判断科室而服务的。
3、整个对话必须在5个交互回合内完成。
4、如果不能准确确定应该挂哪个科，继续询问病人的其他症状。
5、一定要先让用户确认科室之后，才进行挂号。
"""


class ConsultationController:
    def __init__(
        self,
        vector_store: SimpleVectorStore,
        chat_client,
        consultation_tools: ConsultationTools,
        query_expander: ConsultationQueryExpander | None = None,
    ):
        self.vector_store = vector_store
        self.chat_client = chat_client
        self.consultation_tools = consultation_tools
        self.query_expander = query_expander or ConsultationQueryExpander()
        self.chat_memory: dict[str, list[dict]] = {}

    def sse(self, chat_id: str, question: str):
        history = self.chat_memory.setdefault(chat_id, [])
        queries = [question, *self.query_expander.expand(question, history)]
        documents = self.vector_store.search(queries, top_k=3, similarity_threshold=0)
        context = "\n\n".join(
            f"科室：{document.metadata.get('departmentName')}\n{document.text}" for document in documents
        )
        user_prompt = f"用户问题：{question}\n\n科室知识库：\n{context or '未检索到匹配科室'}"
        answer = self.chat_client.complete(SYSTEM_PROMPT, user_prompt)
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        yield from self._stream(answer)

    def _stream(self, text: str, chunk_size: int = 24):
        for index in range(0, len(text), chunk_size):
            yield {"content": text[index : index + chunk_size]}
