# 西班牙旅游规划 Agent

这是一个 LangChain 教学示范项目，用 DeepSeek 和 Geoapify API 生成西班牙旅行规划。

## 项目用途

用户输入旅行偏好后，Agent 会尝试生成：

- 行程建议；
- 城市和景点推荐；
- 地理位置相关信息；
- 简单旅行说明。

## 文件说明

```text
spain_travel_agent_teaching_demo.py       主示例脚本
requirements_spain_travel_agent.txt       依赖列表
env_example_spain_travel_agent.txt        环境变量模板
spain_travel_agent_teaching_bundle.zip    教学打包文件
README_spain_travel_agent.md              当前说明文件
```

## 安装

```powershell
pip install -r requirements_spain_travel_agent.txt
```

## 配置

复制环境变量模板为 `.env`：

```powershell
Copy-Item env_example_spain_travel_agent.txt .env
```

填写：

```env
DEEPSEEK_API_KEY=你的_DeepSeek_API_Key
GEOAPIFY_API_KEY=你的_Geoapify_API_Key
```

真实 `.env` 不应提交到 GitHub。

## 运行

```powershell
python spain_travel_agent_teaching_demo.py
```

## 当前状态

这是轻量教学 Demo，不是完整旅游产品。它的价值在于展示 LangChain Agent、外部 API 和旅行规划任务的基本组合方式。
