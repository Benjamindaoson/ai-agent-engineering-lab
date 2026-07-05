import type { AgentCommandCenter, LearningPlan } from "@/lib/api";
import { humanizeText, submissionText } from "@/lib/humanize";

export type LearnerTrack = "foundation" | "builder" | "workflow";

export type SkillMapData = {
  target_job: { title: string } | null;
  skills: Array<{
    slug: string;
    name: string;
    required_level: number;
    current_score: number;
    confidence: number;
    evidence_count: number;
  }>;
};

export type MissionThread = {
  id: string;
  label: string;
  title: string;
  status: string;
  detail: string;
  href: string;
};

export function resolveLearnerTrack(center: AgentCommandCenter, plan: LearningPlan): LearnerTrack {
  const text = `${plan.current_level} ${plan.target_role} ${center.learner.target_role}`.toLowerCase();
  if (text.includes("workflow") || text.includes("product") || text.includes("business")) return "workflow";
  if (text.includes("engineer") || text.includes("intermediate") || text.includes("advanced")) return "builder";
  return "foundation";
}

export function trackLabel(track: LearnerTrack) {
  if (track === "builder") return "Builder Track";
  if (track === "workflow") return "Workflow Track";
  return "Foundation Track";
}

export function trackPositioning(track: LearnerTrack) {
  if (track === "builder") return "你已有工程基础，系统会直接把你推向 RAG、Agent Workflow、评估和部署挑战。";
  if (track === "workflow") return "你更适合从业务流程拆解、低代码/工具编排和企业场景 Demo 开始。";
  return "你可以零基础进入，但训练标准按准工程师交付要求设计。";
}

export function buildMissionThreads(center: AgentCommandCenter, plan: LearningPlan, skillMap: SkillMapData): MissionThread[] {
  const project = center.active_project;
  const task = project?.tasks[0] ?? null;
  const course = task?.courses[0] ?? center.course_queue.items[0] ?? null;
  const weakest = [...skillMap.skills].sort(
    (a, b) => b.required_level - b.current_score - (a.required_level - a.current_score),
  )[0];
  const command = center.agent_queue.commands[0] ?? null;

  return [
    {
      id: "main",
      label: "主线",
      title: project?.title ?? "确认第一条项目主线",
      status: project?.status ?? "planning",
      detail: humanizeText(task?.description ?? plan.summary),
      href: project?.workspace_href ?? "/intake",
    },
    {
      id: "foundation",
      label: "补弱",
      title: weakest ? `${humanizeText(weakest.name)} 差距 ${Math.max(0, weakest.required_level - weakest.current_score)} 分` : "等待诊断短板",
      status: weakest?.current_score ? "active" : "not_started",
      detail: "系统会把短板拆成小课和练习，不会让你盲目刷完整课程库。",
      href: "/skill-map",
    },
    {
      id: "course",
      label: "课程",
      title: course?.title ?? "等待课程推荐",
      status: "status" in (course ?? {}) ? String((course as { status?: string }).status ?? "not_started") : "not_started",
      detail: humanizeText(course?.reason ?? "课程只在当前任务需要时出现。"),
      href: course?.href ?? "/courses",
    },
    {
      id: "practice",
      label: "练习",
      title: "当前小课必须产出一个微练习",
      status: "required",
      detail: "练习要证明你能把知识用到项目里，而不是只看懂概念。",
      href: course?.href ?? "/courses",
    },
    {
      id: "review",
      label: "检查",
      title: command?.title ? humanizeText(command.title) : "作品检查与重训",
      status: center.quality_gate.status,
      detail: humanizeText(command?.reason ?? "提交作品后，系统会检查运行结果、文档、评估和独立性。"),
      href: command?.quality_gate.href ?? center.quality_gate.href ?? "/projects",
    },
    {
      id: "career",
      label: "求职",
      title: "把训练证据转成求职材料",
      status: center.evidence.count > 0 ? "ready" : "waiting",
      detail: `当前已有 ${center.evidence.count} 条能力证据。最终要变成项目说明、简历 bullet 和面试讲解。`,
      href: center.evidence.passport_href,
    },
  ];
}

export function requiredOutputs(center: AgentCommandCenter) {
  const task = center.active_project?.tasks[0];
  return (task?.required_submission_types ?? []).map(submissionText);
}

export function agentTeam(center: AgentCommandCenter) {
  return [
    ["诊断 Agent", "判断你是零基础、工程师还是业务型学习者。"],
    ["路线 Agent", "生成主线项目和补弱支线。"],
    ["课程 Agent", "只推荐当前任务需要的小课。"],
    ["练习 Agent", "检查你是否能马上应用知识。"],
    ["项目教练 Agent", humanizeText(center.tutor.policy)],
    ["作品检查 Agent", "运行项目、读提交物、生成下一轮修改任务。"],
    ["独立性 Agent", humanizeText(center.tutor.ai_dependency_guardrail)],
    ["求职证据 Agent", "把项目证据整理成招聘方能读懂的报告。"],
  ];
}
