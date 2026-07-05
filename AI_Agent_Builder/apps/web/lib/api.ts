import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: await authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST ${path} failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

async function authHeaders(): Promise<Record<string, string>> {
  if (process.env.NEXT_PUBLIC_AUTH_MODE === "supabase") {
    const accessToken = await getSupabaseAccessToken();
    return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
  }
  return {
    "X-AgentLab-Learner-Id": process.env.NEXT_PUBLIC_DEMO_LEARNER_ID ?? "learner-demo",
    "X-AgentLab-User-Email": process.env.NEXT_PUBLIC_DEMO_LEARNER_EMAIL ?? "learner@example.com",
    "X-AgentLab-User-Name": process.env.NEXT_PUBLIC_DEMO_LEARNER_NAME ?? "Demo Learner",
  };
}

async function getSupabaseAccessToken(): Promise<string | null> {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    return null;
  }
  const cookieStore = await cookies();
  const supabase = createServerClient(url, anonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options));
        } catch {
          // Server components cannot always mutate cookies; server actions can.
        }
      },
    },
  });
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}

export type Job = {
  id: string;
  slug: string;
  title: string;
  description: string;
};

export type Project = {
  learner_project_id: string;
  project_template_slug: string;
  title: string;
  description: string;
  level: string;
  status: string;
};

export type Course = {
  id: string;
  slug: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  estimated_minutes: number;
  status: string;
  recommendation_reason?: string;
  reason?: string;
  priority_score?: number;
  lesson_count?: number;
};

export type CourseLesson = {
  id: string;
  title: string;
  content_type: string;
  content_ref: string | null;
  body: string;
  sort_order: number;
};

export type CourseDetail = Course & {
  skill_name: string | null;
  lessons: CourseLesson[];
  exercise: {
    id: string;
    course_module_id: string;
    prompt: string;
    expected_keywords: string[];
    rubric: Record<string, number>;
    created_at: string;
  };
  exercise_attempts: Array<{
    id: string;
    answer: string;
    score: number;
    feedback: string;
    next_action: string;
    status: string;
    created_at: string;
  }>;
  project_bindings: Array<{
    project_title: string;
    task_title: string;
    reason: string;
  }>;
  storage: {
    module_ref: string;
    lesson_refs: Array<string | null>;
  };
};

export type ProjectDetail = {
  id: string;
  project_template_slug: string;
  title: string;
  description: string;
  status: string;
  tasks: Array<{
    id: string;
    slug: string;
    title: string;
    description: string;
    required_submission_types: string[];
    recommended_courses: Course[];
  }>;
  coach_tasks: CoachTask[];
  latest_submission: {
    id: string;
    status: string;
    github_repo_url: string | null;
    demo_url: string | null;
    readme_url: string | null;
    evaluation_report_url: string | null;
    reflection_text: string | null;
    latest_review_id: string | null;
    latest_review: Review | null;
    created_at: string;
    updated_at: string;
  } | null;
  agent_queue: AgentCommandQueue;
};

export type CoachTask = {
  id: string;
  learner_id: string;
  learner_project_id: string | null;
  review_id: string | null;
  source_type: string;
  title: string;
  reason: string;
  actions: Array<{
    type: string;
    label: string;
    instruction: string;
    deliverable: string;
  }>;
  status: string;
  priority: number;
  created_at: string;
  completed_at: string | null;
};

export type AgentCommand = {
  id: string;
  source_type: string;
  source_id: string;
  agent: string;
  status: string;
  priority: number;
  title: string;
  reason: string;
  actions: CoachTask["actions"];
  primary_handoff: {
    label: string;
    href: string;
  };
  course_handoff: {
    label: string;
    href: string;
  };
  quality_gate: {
    href: string;
    status: string;
    submission_id: string | null;
    review_id: string | null;
    required_checks: string[];
    acceptance: string[];
  };
  evidence_outcome: string;
  project_id: string | null;
  created_at: string | null;
};

export type AgentCommandQueue = {
  contract_version: "agent_command_queue.v1";
  source: string;
  policy: string;
  commands: AgentCommand[];
};

export type TutorMessage = {
  id: string;
  role: "learner" | "tutor";
  content: string;
  hint_level: number | null;
  learning_signal: string | null;
  created_at: string;
};

export type TutorState = {
  session: {
    id: string;
    learner_project_id: string;
    task_id: string | null;
    status: string;
    ai_dependency_score: number;
    ai_dependency_rating: "low" | "medium" | "high";
    created_at: string;
    updated_at: string;
  };
  messages: TutorMessage[];
  agent_runs: Array<{
    id: string;
    agent_name: string;
    status: string;
    created_at: string;
  }>;
};

export type AgentTrace = {
  id: string;
  agent_name: string;
  runtime: "rule" | "claude_agent_sdk" | "mock";
  provider: string;
  model: string | null;
  tool_names: string[];
  status: string;
  latency_ms: number | null;
  parent_type: string | null;
  parent_id: string | null;
  created_at: string;
};

export type NextBestAction = {
  type: string;
  title: string;
  reason: string;
  estimated_minutes: number;
  primary_cta: {
    label: string;
    href: string;
  };
  secondary_cta: {
    label: string;
    href: string;
  };
  evidence_outcome: string;
};

export type AgentDecision = {
  agent_name: string;
  status: string;
  primary_action: {
    type: string;
    label: string;
    href: string;
  };
  reasoning: Array<{
    title: string;
    detail: string;
  }>;
  missing_inputs: string[];
  evidence_outcome: string | null;
  target_role?: string;
};

export type WorkspaceState = {
  learner_stage: string;
  next_best_action: NextBestAction;
  active_project: Project | null;
  recommended_course: Course | null;
  open_coach_tasks: CoachTask[];
  latest_evidence: Array<{
    id: string;
    skill: string;
    skill_slug: string;
    evidence_text: string;
    score: number;
    confidence: number;
    created_at: string;
  }>;
  agent_decision: AgentDecision;
};

export type AgentRuntimeStatus = {
  active_runtime: "rule" | "claude_agent_sdk" | "mock";
  available_runtimes: Array<"rule" | "claude_agent_sdk" | "mock">;
  tool_runtime: string;
};

export type LearningPlan = {
  target_role: string;
  current_level: string;
  estimated_weeks: number;
  summary: string;
  blockers: string[];
  weekly_hours: number;
  weeks: Array<{
    week: number;
    focus: string;
    outcome: string;
    courses: string[];
  }>;
};

export type PlanningMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  payload: {
    quick_options?: string[];
    missing_slot?: string | null;
  } | null;
  created_at: string;
};

export type PlanningSession = {
  id: string;
  status: "started" | "clarifying" | "ready_to_confirm" | "confirmed";
  intent: {
    primary_goal?: string;
    confidence?: number;
    signals?: string[];
  };
  context: Record<string, string | number | null>;
  plan_preview: LearningPlan | null;
  missing_slot: string | null;
  created_at: string;
  updated_at: string;
  confirmed_at: string | null;
};

export type PlanningState = {
  session: PlanningSession | null;
  messages: PlanningMessage[];
  agent_runs: Array<{
    id: string;
    agent_name: string;
    status: string;
    created_at: string;
  }>;
  learning_plan: LearningPlan;
  intake: {
    target_role: string;
    weekly_hours: number;
    career_goal: string;
    constraints: string | null;
  };
};

export type Dashboard = {
  learner: {
    display_name: string;
    email: string;
  };
  learning_plan: LearningPlan;
  next_best_action: NextBestAction;
  workspace_state: WorkspaceState;
  agent_runtimes: {
    planner: AgentRuntimeStatus;
    tutor: AgentRuntimeStatus;
    reviewer: AgentRuntimeStatus;
  };
  next_project: Project | null;
  projects: Project[];
  skill_gaps: Array<{
    slug: string;
    name: string;
    gap: number;
    current_score: number;
    required_level: number;
  }>;
  adaptive_courses: Course[];
  evidence_count: number;
};

export type DemoMode = {
  headline: string;
  positioning: string;
  next_best_action: NextBestAction;
  steps: Array<{
    name: string;
    promise: string;
    screen: string;
    proof: string;
    status: string;
    href: string;
  }>;
  metrics: {
    projects: number;
    evidence_count: number;
    adaptive_courses: number;
    agent_runtimes: Dashboard["agent_runtimes"];
  };
};

export type AgentCommandCenter = {
  contract_version: "agent_command_center.v1";
  learner: {
    id: string;
    display_name: string;
    email: string;
    target_role: string;
    weekly_hours: number;
  };
  agent: {
    name: string;
    mode: "rule" | "claude_agent_sdk" | "mock";
    status: string;
    stage: string;
    tools: string[];
    reasoning: Array<{
      title: string;
      detail: string;
    }>;
    missing_inputs: string[];
    runtime_status: Dashboard["agent_runtimes"];
  };
  mission: {
    title: string;
    reason: string;
    estimated_minutes: number;
    success_evidence: string;
    next_best_action: {
      type: string;
      label: string;
      href: string;
    };
    secondary_action: {
      label: string;
      href: string;
    };
  };
  workflow: {
    current_step_id: "plan" | "learn" | "build" | "review" | "passport";
    steps: Array<{
      id: "plan" | "learn" | "build" | "review" | "passport";
      label: string;
      status: string;
      agent: string;
      output: string;
    }>;
  };
  active_project: {
    id: string;
    slug: string;
    title: string;
    description: string;
    status: string;
    workspace_href: string;
    tasks: Array<{
      id: string;
      slug: string;
      title: string;
      description: string;
      required_submission_types: string[];
      courses: Array<{
        id: string;
        title: string;
        category: string;
        estimated_minutes: number;
        href: string;
        reason: string | null;
      }>;
    }>;
    coach_tasks: CoachTask[];
    latest_submission: ProjectDetail["latest_submission"];
  } | null;
  agent_queue: AgentCommandQueue;
  course_queue: {
    strategy: string;
    storage: {
      module_table: string;
      lesson_table: string;
      binding_table: string;
      progress_table: string;
    };
    items: Array<{
      id: string;
      slug: string;
      title: string;
      description: string;
      category: string;
      difficulty: string;
      estimated_minutes: number;
      status: string;
      priority_score: number;
      reason: string;
      href: string;
    }>;
  };
  quality_gate: {
    status: "not_started" | "queued" | "running" | "passed" | "needs_revision";
    href: string;
    submission_id: string | null;
    review_id: string | null;
    required_checks: string[];
    acceptance: string[];
  };
  tutor: {
    name: string;
    policy: string;
    entry_href: string;
    ai_dependency_guardrail: string;
  };
  evidence: {
    store: string;
    count: number;
    latest_items: WorkspaceState["latest_evidence"];
    top_skill_gaps: Dashboard["skill_gaps"];
    passport_href: string;
  };
  data_sources: Record<string, string>;
  handoffs: Record<string, { label: string; href: string }>;
};

export type CourseWorkbench = {
  contract_version: "course_workbench.v1";
  agent: {
    name: "MicroExerciseCoach";
    mode: "rule" | "claude_agent_sdk";
    status: string;
    policy: string;
    tools: string[];
  };
  course: Course & {
    skill_name: string | null;
  };
  mission: {
    title: string;
    reason: string;
    success_evidence: string;
    next_best_action: {
      label: string;
      href: string;
    };
  };
  project_context: {
    project: {
      id: string;
      slug: string;
      title: string;
      description: string;
      status: string;
      workspace_href: string;
    } | null;
    task: {
      id: string;
      slug: string;
      title: string;
      description: string;
      required_submission_types: string[];
    } | null;
    why_now: string;
  };
  lessons: CourseLesson[];
  exercise: CourseDetail["exercise"] & {
    pass_standard: {
      minimum_score: number;
      required_keywords: string[];
      outcome: string;
    };
  };
  latest_attempt: CourseDetail["exercise_attempts"][number] | null;
  agent_queue: AgentCommandQueue;
  storage: CourseDetail["storage"];
  handoffs: Record<string, { label: string; href: string }>;
  data_sources: Record<string, string>;
};

export type Review = {
  id: string;
  reviewer_type: string;
  overall_score: number;
  hiring_readiness: string;
  confidence: number;
  summary: string;
  next_action: string;
  rubric_scores: Array<{
    rubric_item_key: string;
    score: number;
    max_score: number;
    reason: string;
  }>;
  risk_flags: Array<{
    type: string;
    severity: string;
    description: string;
  }>;
  coach_tasks?: CoachTask[];
};

export type ReviewGateSandboxRun = {
  id: string;
  review_job_id: string;
  submission_id: string;
  status: string;
  command: string;
  exit_code: number | null;
  duration_ms: number | null;
  stdout_ref: string | null;
  stderr_ref: string | null;
  created_at: string;
  finished_at: string | null;
};

export type ReviewGateWorkbench = {
  contract_version: "review_gate_workbench.v1";
  agent: {
    name: "ReviewAgent";
    mode: "mock" | "claude_agent_sdk" | "rule";
    status: string;
    policy: string;
    tools: string[];
  };
  job: {
    id: string;
    status: string;
    mode: string;
    submission_id: string;
    review_id: string | null;
    attempt_count: number;
    last_error: string | null;
    created_at: string;
    started_at: string | null;
    finished_at: string | null;
  };
  submission: {
    id: string;
    status: string;
    learner_project_id: string;
    task_id: string;
    github_repo_url: string | null;
    demo_url: string | null;
    readme_url: string | null;
    architecture_doc_url: string | null;
    evaluation_report_url: string | null;
    source_repo_path: string | null;
    sandbox_command: string | null;
    reflection_text: string | null;
    created_at: string;
    updated_at: string;
  };
  project_context: {
    project: {
      id: string;
      slug: string;
      title: string;
      description: string;
      status: string;
      workspace_href: string;
    };
    task: {
      id: string;
      slug: string;
      title: string;
      description: string;
      required_submission_types: string[];
    };
  };
  workflow: {
    current_step_id: "sandbox" | "agent_review" | "evidence" | "next_task";
    steps: Array<{
      id: "sandbox" | "agent_review" | "evidence" | "next_task";
      label: string;
      status: string;
      agent: string;
      output: string;
    }>;
  };
  sandbox: {
    status: string;
    latest: ReviewGateSandboxRun | null;
    runs: ReviewGateSandboxRun[];
  };
  review: Review | null;
  agent_runs: Array<{
    id: string;
    provider: string;
    model: string | null;
    mode: string;
    status: string;
    latency_ms: number | null;
    cost_usd: number | null;
    created_at: string;
    finished_at: string | null;
  }>;
  evidence: {
    store: string;
    items: Array<{
      id: string;
      skill: string;
      skill_slug: string;
      evidence_text: string;
      score: number;
      confidence: number;
      is_passport_eligible: number;
      created_at: string;
    }>;
    count: number;
    passport_eligible_count: number;
  };
  coach_tasks: CoachTask[];
  handoffs: Record<string, { label: string; href: string }>;
  data_sources: Record<string, string>;
};
