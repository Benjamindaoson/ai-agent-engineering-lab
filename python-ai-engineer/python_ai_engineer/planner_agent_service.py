from .plan import Plan


class PlannerAgentService:
    def __init__(self, planner_agent, agent_map: dict):
        self.planner_agent = planner_agent
        self.agent_map = agent_map

    def plan(self, prompt: str) -> Plan:
        return Plan.from_json(self.planner_agent.call(prompt))

    def execute(self, plan: Plan) -> str:
        for step in plan.steps:
            agent = self.agent_map.get(step.agent_name)
            if agent is None:
                return f"Step {step.step_num} failed: agent not found: {step.agent_name}"
            try:
                agent.call(step.prompt)
            except Exception as exc:
                # ponytail: agent dispatch boundary; fail the current step, not the full classroom run.
                return f"Step {step.step_num} failed: {exc}"
        return "Execution complete"
