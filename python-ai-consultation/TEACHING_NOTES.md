# 教学注释：python-ai-consultation

这一关讲垂直领域咨询 Agent。它可以做分诊建议，但不能替代医生诊断。

## 这一关学什么

- 咨询问答边界
- 科室分诊
- RAG 检索
- 挂号确认
- 安全提示

## 先看哪些文件

1. `python_ai_consultation/consultation_controller.py`：咨询主流程。
2. `python_ai_consultation/consultation_tools.py`：挂号工具。
3. `python_ai_consultation/department_summary_vector_store_job.py`：科室摘要如何加载。
4. `python_ai_consultation/consultation_query_expander.py`：历史问题如何辅助检索。
5. `python_ai_consultation/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

这一关必须讲安全边界：可以建议去哪个科室，但不能说“你得了什么病”。
