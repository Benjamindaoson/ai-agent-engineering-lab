# Python 项目清理与一键运行设计

## 目标

删除本地工具配置、缓存、依赖副本、构建结果和演示输出，使项目成为可发布的源码仓库；保留课程、测试、产品代码和必要文档，并提供一次命令完成本地依赖恢复与 AgentLab 启动。

## 删除范围

- 根目录代理/编辑器配置：`.agents/`、`.claude/`、`.codex/`、`.github/`、`.vscode/`
- 根目录遗留与运行产物：`snake.html`、`snake.css`、`snake.js`、空 `workspace/`
- 全项目缓存和输出：`__pycache__/`、`.pytest_cache/`、`output/`、测试结果
- AgentLab 本地状态：内部 `.agents/`、`.codex/`、嵌套 `.git/`、`.venv/`、`node_modules/`、`.next/`、`test-results/`、`tsconfig.tsbuildinfo`、`agentlab.db`

所有删除目标必须先解析为绝对路径并验证位于 `handwritten-ai-agent-python` 内；不使用通配符删除项目源码。

## 保留范围

- 19 个 Python 课程模块、测试、README 和依赖清单
- 根课程入口、质量门禁和课程文档
- AgentLab 源码、测试、数据库 schema/seed、`package.json`、`package-lock.json`、`.env.example`
- `openspec/`、`production-platform/` 和产品设计文档

## 一键运行

在 Python 项目根目录新增 `run-local.ps1`：

1. 检查 `python` 与 `npm`。
2. 缺少 `AI_Agent_Builder/.venv` 时创建虚拟环境。
3. 使用 `requirements.txt` 安装后端依赖。
4. 缺少 `node_modules` 时使用 `npm ci` 安装锁定依赖。
5. 运行数据库 seed。
6. 启动 FastAPI `127.0.0.1:8000` 和 Next.js `127.0.0.1:3000`。
7. 输出进程号、访问地址和停止命令。

脚本提供 `-SetupOnly`，用于只恢复依赖、初始化数据库和执行验证，不启动长期服务。

## 验收

- 删除清单中的路径全部不存在。
- 课程源码、19 个模块和 AgentLab 源码仍存在。
- 从无 `.venv`、`node_modules`、`.next`、数据库的状态执行 `run-local.ps1 -SetupOnly` 成功。
- Python课程根测试、19项目质量门禁、AgentLab API测试、Web类型检查与生产构建通过。
- 实际启动后 `/health` 返回成功，Web首页可访问。
