import Link from "next/link";
import { redirect } from "next/navigation";
import path from "node:path";
import {
  ArrowRight,
  BookOpenCheck,
  Bot,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  FileCode2,
  MessageSquareText,
  SendHorizontal,
  TerminalSquare,
} from "lucide-react";
import { apiGet, apiPost, type AgentCommandCenter, type TutorState } from "@/lib/api";
import { humanizeText, statusText, submissionText } from "@/lib/humanize";

async function submitProject(formData: FormData) {
  "use server";
  const learnerProjectId = String(formData.get("learner_project_id"));
  const response = await apiPost<{ review_job_id: string }>("/api/submissions", {
    learner_project_id: learnerProjectId,
    task_id: String(formData.get("task_id")),
    github_repo_url: String(formData.get("github_repo_url")),
    demo_url: optionalUrl(formData.get("demo_url")),
    readme_url: optionalUrl(formData.get("readme_url")),
    architecture_doc_url: optionalUrl(formData.get("architecture_doc_url")),
    evaluation_report_url: optionalUrl(formData.get("evaluation_report_url")),
    source_repo_path: String(formData.get("source_repo_path") || ""),
    sandbox_command: String(formData.get("sandbox_command") || ""),
    reflection_text: String(formData.get("reflection_text") || ""),
    queue_review: true,
    mode: process.env.NEXT_PUBLIC_AGENT_REVIEW_MODE ?? "mock",
  });
  redirect(`/gate/${response.review_job_id}`);
}

async function sendTutorMessage(formData: FormData) {
  "use server";
  const learnerProjectId = String(formData.get("learner_project_id"));
  await apiPost<TutorState>(`/api/projects/${learnerProjectId}/tutor/messages`, {
    message: String(formData.get("message") || ""),
  });
  redirect(`/lab/${learnerProjectId}#project-coach`);
}

export default async function ProjectLabPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [center, tutor] = await Promise.all([
    apiGet<AgentCommandCenter>(`/api/agents/command-center?learner_project_id=${encodeURIComponent(id)}`),
    apiGet<TutorState>(`/api/projects/${id}/tutor`),
  ]);
  const project = center.active_project;
  const task = project?.tasks[0] ?? null;
  const course = task?.courses[0] ?? center.course_queue.items[0] ?? null;
  const command = center.agent_queue.commands[0] ?? null;
  const sampleRepoPath = process.env.NEXT_PUBLIC_SAMPLE_REPO_PATH ?? path.resolve(process.cwd(), "../..", "samples", "rag-agent");

  if (!project || !task) {
    return (
      <main className="training-cockpit">
        <section className="today-card">
          <h1>项目还没准备好</h1>
          <p>先回到 AI 教练，让它确认你的目标和第一条项目路线。</p>
          <Link className="button" href="/coach">回到 AI 教练</Link>
        </section>
      </main>
    );
  }

  return (
    <main className="project-canvas" aria-label="项目画布">
      <header className="cockpit-hero compact-hero">
        <div className="live-orb" aria-hidden="true">
          <TerminalSquare size={32} />
          <span />
        </div>
        <div>
          <span className="eyebrow">项目画布</span>
          <h1>{project.title}</h1>
          <p>{humanizeText(project.description)}</p>
          <div className="cockpit-actions">
            <Link className="button secondary" href="/coach">回到 AI 教练</Link>
            {course ? <Link className="button secondary" href={course.href}>打开当前小课</Link> : null}
          </div>
        </div>
      </header>

      <section className="canvas-grid">
        <aside className="cockpit-rail">
          <h2>项目步骤</h2>
          <RailStep index={1} title="理解任务" active />
          <RailStep index={2} title="补当前小课" active={center.workflow.current_step_id === "learn"} />
          <RailStep index={3} title="做出作品" active={center.workflow.current_step_id === "build"} />
          <RailStep index={4} title="提交作品" active={center.quality_gate.status === "not_started"} />
          <RailStep index={5} title="查看检查报告" active={center.quality_gate.status !== "not_started"} />
          <RailStep index={6} title="修改再提交" active={center.quality_gate.status === "needs_revision"} />
        </aside>

        <section className="mission-canvas">
          <article className="challenge-card">
            <div>
              <span className="eyebrow">当前挑战</span>
              <h2>{task.title}</h2>
              <p>你不是在填表。你正在完成一个训练挑战：在限制条件内做出作品，然后让 AI 检查员判断是否达到可交付标准。</p>
            </div>
            <div className="challenge-grid">
              <div><strong>限制条件</strong><span>先完成最小可运行版本，不追求大而全</span></div>
              <div><strong>通关条件</strong><span>代码、演示、说明、评估、复盘都能被检查</span></div>
              <div><strong>解锁能力</strong><span>{task.required_submission_types.map(submissionText).slice(0, 2).join(" + ")}</span></div>
            </div>
          </article>

          <article className="today-card">
            <span className="eyebrow">AI 教练给你的下一步</span>
            <h2>{humanizeText(command?.title ?? center.mission.title)}</h2>
            <p>{humanizeText(command?.reason ?? center.mission.reason)}</p>
            <div className="coach-action-list">
              {(command?.actions ?? []).slice(0, 3).map((action) => (
                <div className="coach-action" key={action.label}>
                  <strong>{humanizeText(action.label)}</strong>
                  <p>{humanizeText(action.instruction)}</p>
                  <span>要留下：{humanizeText(action.deliverable)}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <ClipboardCheck size={20} />
              <div>
                <span>当前任务</span>
                <h2>{task.title}</h2>
              </div>
            </div>
            <p>{humanizeText(task.description)}</p>
            <div className="evidence-strip">
              {task.required_submission_types.map((item) => (
                <span key={item}>{submissionText(item)}</span>
              ))}
            </div>
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <BookOpenCheck size={20} />
              <div>
                <span>这个任务需要的小课</span>
                <h2>{course?.title ?? "不需要先学新课"}</h2>
              </div>
            </div>
            <p>{humanizeText(course?.reason ?? "AI 教练判断你现在应该直接推进作品。")}</p>
            {course ? (
              <Link className="button secondary" href={course.href}>
                学完马上回来改项目 <ArrowRight size={16} />
              </Link>
            ) : null}
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <FileCode2 size={20} />
              <div>
                <span>提交作品</span>
                <h2>让作品检查员看一轮</h2>
              </div>
            </div>
            <form className="submission-grid" action={submitProject}>
              <input type="hidden" name="learner_project_id" value={project.id} />
              <input type="hidden" name="task_id" value={task.id} />
              <label>代码仓库 URL<input name="github_repo_url" type="url" defaultValue="https://github.com/example/rag-agent" required /></label>
              <label>在线演示 URL<input name="demo_url" type="url" defaultValue="https://example.com" /></label>
              <label>项目说明 URL<input name="readme_url" type="url" defaultValue="https://github.com/example/rag-agent#readme" /></label>
              <label>架构说明 URL<input name="architecture_doc_url" type="url" defaultValue="https://example.com/architecture" /></label>
              <label>测试和评估记录 URL<input name="evaluation_report_url" type="url" defaultValue="https://example.com/eval" /></label>
              <label>本地源码路径<input name="source_repo_path" defaultValue={sampleRepoPath} required /></label>
              <label>运行检查命令<input name="sandbox_command" defaultValue="python -m unittest discover -s tests -q" required /></label>
              <label className="wide-field">
                项目复盘
                <textarea name="reflection_text" rows={4} defaultValue="我说明了核心取舍、失败样例、评估方法和下一轮改进计划。" />
              </label>
              <button type="submit">
                提交作品，让 AI 帮我检查 <SendHorizontal size={16} />
              </button>
            </form>
          </article>
        </section>

        <aside className="coach-presence" id="project-coach">
          <div className="agent-card sticky-agent">
            <div className="agent-face">
              <Bot size={22} />
              <div>
                <span>常驻项目教练</span>
                <strong>AI 项目教练</strong>
              </div>
            </div>
            <p className="muted">{humanizeText(center.tutor.policy)}</p>
            <div className="signal-card">
              <strong>AI 代做风险：{dependencyLabel(tutor.session.ai_dependency_rating)}</strong>
              <p>{humanizeText(center.tutor.ai_dependency_guardrail)}</p>
            </div>
            <div className="chat-log">
              {tutor.messages.slice(-4).map((message) => (
                <article className={`chat-message ${message.role === "learner" ? "learner" : "tutor"}`} key={message.id}>
                  <strong>{message.role === "learner" ? "你" : "AI 项目教练"}</strong>
                  <p>{humanizeText(message.content)}</p>
                </article>
              ))}
            </div>
            <form action={sendTutorMessage} className="chat-composer">
              <input type="hidden" name="learner_project_id" value={project.id} />
              <textarea
                name="message"
                rows={4}
                defaultValue="请先指出我这个项目最容易被招聘方面试追问的风险，不要直接给完整答案。"
                required
              />
              <button type="submit">
                让 AI 项目教练看一下 <MessageSquareText size={16} />
              </button>
            </form>
          </div>
        </aside>
      </section>
    </main>
  );
}

function optionalUrl(value: FormDataEntryValue | null) {
  const text = String(value || "").trim();
  return text.length ? text : null;
}

function RailStep({ index, title, active }: { index: number; title: string; active: boolean }) {
  return (
    <div className="rail-step" data-active={active ? "true" : "false"}>
      <span>{String(index).padStart(2, "0")}</span>
      <strong>{title}</strong>
      <small>{active ? "正在处理" : "后面会做"}</small>
    </div>
  );
}

function dependencyLabel(rating: string) {
  if (rating === "high") return "高";
  if (rating === "medium") return "中";
  return "低";
}
