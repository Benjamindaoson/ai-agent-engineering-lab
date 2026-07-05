# Java/Python 项目拆分设计

## 目标

将仓库中混合的 Java、Python、课程资料和 AgentLab 平台整理为两个名称明确的顶级项目。除 Git 元数据外，仓库根目录不保留其他项目文件或目录。

```text
shouxieagent/
├─ .git/
├─ handwritten-ai-agent-java/
└─ handwritten-ai-agent-python/
```

## 归属规则

### handwritten-ai-agent-java

- 根 Maven 聚合工程 `pom.xml`
- 当前 `java-projects/` 下的 20 个 Java/Spring 模块，直接成为该项目的子目录
- Java 项目专用 README 和忽略规则

### handwritten-ai-agent-python

- 当前 `python-projects/` 下的 19 个 Python 教学模块，直接成为该项目的子目录
- `course.py`、`scripts/`、`tests/` 和 Python 课程文档
- `AI_Agent_Builder/`：其核心 API、Worker、Agent Runner 和数据层是 Python；Next.js 是该平台的 Web 子应用，不构成独立顶级项目
- `production-platform/`：入口和环境检查是 Python
- `openspec/`：现有变更主要记录 Java 到 Python 的课程迁移及 Python 课程改进
- `.agents/`、`.claude/`、`.codex/`、`.github/`、`.vscode/` 等当前工程辅助配置
- 根目录其余 Python 脚本、静态演示文件、文档与许可证

## 路径调整

- Java 聚合 `pom.xml` 的模块路径删除 `java-projects/` 前缀。
- `course.py` 改为从自身目录直接查找 19 个课程模块。
- Python 质量门禁、测试和文档链接改为新根目录下的相对路径。
- 两个项目分别提供 README；公共许可证在两个项目各保留一份。
- 不改动各教学模块内部业务实现，不进行重构。

## 安全与 Git

- 保留仓库根 `.git/`，它是“根目录只保留两个项目”的唯一隐藏例外。
- 迁移前记录现有 Git 状态；不清理、不恢复、不覆盖用户已有改动。
- 所有移动都限制在当前仓库绝对路径内。
- 若目标路径已存在同名文件，停止移动并报告冲突，不覆盖。

## 验收

1. 根目录除 `.git/` 外只包含两个指定目录。
2. Java Maven 聚合模块路径均存在。
3. Python 课程的 19 个模块均可被 `course.py` 和质量门禁发现。
4. README、测试和脚本中不再引用旧的 `java-projects/` 或 `python-projects/` 根路径。
5. 执行只读结构检查、Python 测试及可行的 Maven模型校验；外部模型、Docker、浏览器和网络服务不作为此次目录迁移验收条件。

## 非目标

- 不重构 Java 或 Python Agent 实现。
- 不合并 19/20 个教学模块。
- 不把 AgentLab 拆成第三个顶级项目。
- 不删除当前未提交内容。
