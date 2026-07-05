from pathlib import Path

from .agent_skill_demo1 import run_agent_skill_demo1
from .demos import (
    run_fanout_pipeline_demo,
    run_hello_world_demo,
    run_human_in_the_loop_demo,
    run_rag_demo,
    run_sequential_pipeline_demo,
    run_tool_context_demo,
    run_tool_demo,
    run_tool_group_demo,
)
from .plan_demo import run_plan_demo


def main() -> None:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print("== HelloWorldDemo ==")
    print(run_hello_world_demo())
    print("\n== ToolDemo ==")
    print(run_tool_demo())
    print("\n== ToolContextDemo ==")
    print(run_tool_context_demo())
    print("\n== ToolGroupDemo ==")
    for line in run_tool_group_demo():
        print(line)
    print("\n== HumanInTheLoopDemo ==")
    print(run_human_in_the_loop_demo(confirm=False))
    print("\n== SequentialPipelineDemo ==")
    print(run_sequential_pipeline_demo())
    print("\n== FanoutPipelineDemo ==")
    for line in run_fanout_pipeline_demo():
        print(line)
    print("\n== AgentSkillDemo1 ==")
    print(run_agent_skill_demo1())
    print("\n== RAGDemo ==")
    print(run_rag_demo("什么是apikey"))
    print("\n== PlanDemo ==")
    print(run_plan_demo())


if __name__ == "__main__":
    main()
