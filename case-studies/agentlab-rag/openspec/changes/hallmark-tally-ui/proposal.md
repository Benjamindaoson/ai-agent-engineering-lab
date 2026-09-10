## Why

AgentLab 已具备真实运行与 Evidence 验收，但当前界面仍是通用深色控制台，无法以足够清晰、有辨识度的视觉层级表达“真实 Agent 工程救火”的价值。用户选择以 Hallmark 开源 Tally 示例为直接视觉基础，使用其适合指标与审计工作台的设计语言。

## What Changes

- 以 Tally 的浅色靛蓝 token、圆角工作台、指标卡和响应式网格重做 SPA 的六个视图。
- 以 Cobalt 的承诺与可验证证据结构重做首页；所有业务文案、指标和 AgentLab 品牌保持真实。
- 引入项目级 `design.md`，锁定跨视图共享的颜色、字体、间距、动效和交互规则。
- 移除手工绘制的假浏览器圆点；只展示真实 Browser Agent 截图或真实运行状态。

## Capabilities

### New Capabilities

- `hallmark-agentlab-design-system`: AgentLab 共享、可访问且响应式的 Hallmark/Tally 设计系统。
- `evidence-workbench-presentation`: 用真实任务、运行与 Evidence 数据呈现的产品工作台和结果界面。

### Modified Capabilities

- `agentlab-product-mvp`: 六个既有产品视图的视觉和交互呈现改为统一设计系统，且不改变后台任务、会话和运行契约。

## Impact

- 修改 `agentlab_web/src/App.tsx`、`agentlab_web/src/styles.css` 和 `agentlab_web/src/product.css`。
- 新增根目录 `design.md` 与 UI 行为测试；不修改 FastAPI API、真实运行器、受控世界、历史 Proof 或依赖版本。
