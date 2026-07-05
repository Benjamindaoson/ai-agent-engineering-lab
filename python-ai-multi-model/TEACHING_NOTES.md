# 教学注释：python-ai-multi-model

这一关讲多模型能力：Agent 不只能处理文本，还能处理图片、视频、音频。

## 这一关学什么

- 图片生成请求
- 图片理解请求
- 视频理解请求
- 音频转写和摘要
- 多模型 provider 配置

## 先看哪些文件

1. `python_ai_multi_model/dashscope_service.py`：多模型请求 payload。
2. `python_ai_multi_model/multi_model_controller.py`：四类入口。
3. `python_ai_multi_model/offline_demo.py`：课堂离线演示入口。

## 课堂讲法

离线课堂重点讲请求结构，不追求真实生成图片或视频理解。真实模型调用放到进阶验收。
