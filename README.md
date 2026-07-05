# Handwritten AI Agent — Python

一套面向 AI Agent 工程实践的 Python 课程工程，包含 19 个教学项目、课程闯关工具和 AgentLab 学习平台。

Python 课程总览：[docs/python-course-map.md](docs/python-course-map.md)

Java/Python 目录对比：[docs/java-python-comparison.md](docs/java-python-comparison.md)

Python 19 关课堂路线：[docs/python-level-map.md](docs/python-level-map.md)

Python 项目质量评估：[docs/python-project-quality-review.md](docs/python-project-quality-review.md)

课堂闯关入口：

```powershell
python course.py status
python course.py run all
```

`course.py` 默认只能运行当前关，当前关通过后才会解锁下一关。

全量质量门禁：

```powershell
python scripts/python_quality_gate.py
```

生产级平台能力单独放在：[production-platform](production-platform)

## AgentLab 一键启动

首次运行会自动创建 Python 虚拟环境、安装锁定依赖并初始化本地 SQLite：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-local.ps1
```

启动完成后访问 `http://127.0.0.1:3000`。只安装依赖和初始化数据库、不启动服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-local.ps1 -SetupOnly
```

## License

本项目采用 [Eclipse Public License 1.0](LICENSE)。你可以在遵守许可证条款的前提下使用、修改和分发本项目。
