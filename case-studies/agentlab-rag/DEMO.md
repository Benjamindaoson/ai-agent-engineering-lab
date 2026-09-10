# AgentLab 现场演示脚本（约 7 分钟）

1. 运行 `./scripts/start.ps1`，打开首页，介绍这是让真实 Browser Agent 上线前完成工程救火的工作台。
2. 点击“开始项目”，完成三道入职试炼。说明题目只排序固定任务，不让 LLM 自造验收标准。
3. 进入“可靠性：修复假成功”工作台。展示 Monaco、允许修改文件与验收条件。
4. 先保持 `FIXED_MODE = False`，运行一次。结果页会说明页面和 Agent 认为成功，但 SQLite 没有采购记录。
5. 将 `FIXED_MODE` 改为 `True`，再次运行。展示后台状态、Browser Use/Chromium、SQLite 成功和 Evidence。
6. 打开 Project Delivery Report，比较修改前后 False Success、恢复、调用、耗时与成本。
7. 切到历史 Replay，明确说明这里是“历史真实运行记录”，不是现场伪造的执行。
8. 简介安全任务：恶意网页提示不会触发文件读取；系统程序检查工具、地址与 fake secret。最后介绍成本任务：业务成功与工程验收分离。

如果现场没有可用 API Key 或网络，完整展示 Replay、工作区、Evidence 和 Delivery；不要把 Replay 说成现场运行。
