# Production Platform Stage

这个目录用于放“生产级 Agent 平台”能力，与项目根目录的 19 个课程关卡分开维护。

课程项目解决的是：学习 Agent 能力、离线演示、Java/Python 对照、顺序闯关。

这个目录解决的是：如果以后要做成真正可上线的平台，需要补哪些工程能力。

## 范围

生产平台阶段包含：

- 账号
- 权限
- 审计
- 部署
- 观测
- 限流
- 真实 Docker 验收
- 真实 Playwright 验收
- 真实线上模型验收

## 不做什么

当前不把这 19 个 Python 课程项目强行合并成生产平台。

原因很简单：课程工程和生产平台的目标不同。课程项目要短、清楚、可讲；生产平台要安全、稳定、可运维。

## 建议顺序

1. 先做统一配置和环境检查。
2. 再做账号、权限、审计。
3. 再做限流、观测、部署。
4. 最后接真实 Docker、Playwright、线上模型验收。

## 当前文件

- `platform-capability-checklist.md`：生产平台能力清单。
- `environment_check.py`：只读环境检查脚本。

运行：

```powershell
python production-platform/environment_check.py
```
