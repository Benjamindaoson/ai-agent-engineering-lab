import streamlit as st
import os
import tempfile
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI

# ==========================================
# 页面基础设置 (UI 标题和布局)
# ==========================================
st.set_page_config(page_title="成都市控规审查 AI 助手", page_icon="🏛️", layout="wide")
st.title("🏛️ 成都市控规调整审查 AI 智能体")
st.markdown("基于真实历史案卷雷区构建的智能审查系统")

# ==========================================
# 核心大模型配置与知识库加载 (使用缓存加速)
# ==========================================
# 替换为你的真实 API Key
LLM_API_KEY = "${DEEPSEEK_API_KEY}"
LLM_BASE_URL = "https://api.deepseek.com/v1"
client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

@st.cache_resource # 加上这个装饰器，数据库只加载一次，网页就不会卡
def load_knowledge_base():
    embeddings = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")
    vector_db = Chroma(persist_directory="./chengdu_planning_db", embedding_function=embeddings)
    return vector_db

vector_db = load_knowledge_base()

# ==========================================
# 左侧边栏：文件上传区
# ==========================================
with st.sidebar:
    st.header("📂 案卷上传区")
    uploaded_file = st.file_uploader("请上传待审查的控规方案 (PDF格式)", type=["pdf"])

    st.markdown("---")
    st.markdown("### 💡 系统提示")
    st.markdown("1. 上传 PDF 后，AI 将自动审阅并输出审查意见。")
    st.markdown("2. 您也可以直接在右侧对话框中向我提问，例如：*“成都市关于变电站退让有什么规矩？”*")

# ==========================================
# 聊天对话状态管理
# ==========================================
if "messages" not in st.session_state:
    # 默认的第一句问候语
    st.session_state.messages = [{"role": "assistant", "content": "您好！我是成都市控规审查 AI 助手。请在左侧上传案卷 PDF，或者直接向我提问。"}]

# 在页面上渲染之前的聊天记录
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 核心交互逻辑：处理上传的 PDF
# ==========================================
if uploaded_file is not None and "pdf_processed" not in st.session_state:
    with st.chat_message("user"):
        st.markdown(f"**[系统提示]** 用户上传了文件：`{uploaded_file.name}`，请求出具审查意见。")

    with st.chat_message("assistant"):
        with st.spinner('🤖 AI 正在逐页精读案卷并比对历史雷区，请稍候...'):
            # 将上传的内存文件临时保存到本地，供 PyPDFLoader 读取
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            try:
                # 1. 粗略提取前几页内容作为诉求（采用V1简版逻辑以便快速演示）
                loader = PyPDFLoader(tmp_file_path)
                pages = loader.load()
                text_content = "\n".join([p.page_content for p in pages[:10]])

                # 2. 让 AI 提炼诉求
                prompt1 = f"请作为规划师，提炼以下文本中的【核心调整诉求】(200字内)：\n{text_content[:3000]}"
                req_res = client.chat.completions.create(
                    model="deepseek-chat", messages=[{"role": "user", "content": prompt1}], temperature=0.1
                )
                core_request = req_res.choices[0].message.content

                st.info(f"**AI 提炼的核心诉求：**\n{core_request}")

                # 3. 检索本地知识库
                similar_docs = vector_db.similarity_search(core_request, k=3)
                context = "\n".join([f"【参考案卷】{doc.page_content}" for doc in similar_docs])

                # 4. 生成最终审查意见
                system_prompt = "你是成都市规划局资深审查专家。请根据新诉求和提供的历史雷区，写出客观严谨的技术审查意见，分为：一、成果完整性；二、核心技术审查意见；三、后续会签建议。"
                user_prompt = f"【历史雷区库】\n{context}\n\n【新案卷诉求】\n{core_request}"

                final_res = client.chat.completions.create(
                    model="deepseek-chat", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], temperature=0.3
                )
                final_report = final_res.choices[0].message.content

                # 打印出最终报告
                st.markdown(final_report)

                # 将结果存入聊天记录
                st.session_state.messages.append({"role": "user", "content": f"请审查文件：{uploaded_file.name}"})
                st.session_state.messages.append({"role": "assistant", "content": f"**核心诉求：**\n{core_request}\n\n**审查意见：**\n{final_report}"})

                # 标记该文件已处理，避免重复跑
                st.session_state.pdf_processed = True

            finally:
                os.remove(tmp_file_path) # 清理临时文件

# ==========================================
# 核心交互逻辑：处理用户直接输入的文本聊天
# ==========================================
if prompt := st.chat_input("您可以直接向我提问关于规划审查的规矩..."):
    # 1. 显示用户的提问
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. AI 回答（带检索功能）
    with st.chat_message("assistant"):
        with st.spinner('检索知识库中...'):
            # 去数据库找答案
            similar_docs = vector_db.similarity_search(prompt, k=2)
            context = "\n".join([doc.page_content for doc in similar_docs])

            ans_prompt = f"你是成都规划局专家。请基于以下历史案卷知识，回答用户问题。如果历史知识没提及，请依据城市规划常识回答。\n【历史知识】\n{context}\n\n【用户问题】\n{prompt}"

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": ans_prompt}],
                temperature=0.3
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
# streamlit run app.py