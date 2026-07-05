import Link from "next/link";
import { redirect } from "next/navigation";
import { ArrowRight, BookOpenCheck, Bot, BrainCircuit, CheckCircle2, ClipboardCheck, SendHorizontal, TerminalSquare } from "lucide-react";
import { apiGet, apiPost, type CourseWorkbench } from "@/lib/api";
import { humanizeText, statusText } from "@/lib/humanize";

async function submitExercise(formData: FormData) {
  "use server";
  const courseId = String(formData.get("course_module_id"));
  await apiPost("/api/courses/exercises/attempts", {
    course_module_id: courseId,
    answer: String(formData.get("answer") || ""),
  });
  redirect(`/learn/${courseId}?exercise=submitted#micro-exercise`);
}

export default async function CourseWorkbenchPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const workbench = await apiGet<CourseWorkbench>(`/api/courses/${id}/workbench`);
  const project = workbench.project_context.project;
  const task = workbench.project_context.task;
  const latestAttempt = workbench.latest_attempt;

  return (
    <main className="micro-lesson" aria-label="小课练习">
      <header className="cockpit-hero compact-hero">
        <div className="live-orb" aria-hidden="true">
          <BookOpenCheck size={32} />
          <span />
        </div>
        <div>
          <span className="eyebrow">当前任务需要的小课</span>
          <h1>这一步需要的小课</h1>
          <p>{workbench.course.title}</p>
          <div className="cockpit-actions">
            <Link className="button secondary" href={workbench.handoffs.command_center.href}>回到 AI 教练</Link>
            <Link className="button secondary" href={workbench.handoffs.project_lab.href}>回到项目画布</Link>
          </div>
        </div>
      </header>

      <section className="canvas-grid two-column">
        <section className="mission-canvas">
          <article className="challenge-card">
            <div>
              <span className="eyebrow">任务弹药包</span>
              <h2>只补当前挑战马上要用的知识</h2>
              <p>小课不是课程库。它是你完成当前项目挑战前的一次短补给，学完必须马上用到作品里。</p>
            </div>
            <div className="challenge-grid">
              <div><strong>时间盒</strong><span>{workbench.course.estimated_minutes} 分钟</span></div>
              <div><strong>通关练习</strong><span>{workbench.exercise.pass_standard.minimum_score} 分以上</span></div>
              <div><strong>回到项目</strong><span>把方法写进代码、README 或评估记录</span></div>
            </div>
          </article>

          <article className="today-card">
            <span className="eyebrow">为什么现在学这个</span>
            <h2>{humanizeText(workbench.mission.title)}</h2>
            <p>{humanizeText(workbench.mission.reason)}</p>
            <div className="mission-proof">
              <CheckCircle2 size={18} />
              <span>{humanizeText(workbench.mission.success_evidence)}</span>
            </div>
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <TerminalSquare size={20} />
              <div>
                <span>学完马上用在哪里</span>
                <h2>{task?.title ?? "你的当前项目任务"}</h2>
              </div>
            </div>
            <p>{humanizeText(workbench.project_context.why_now)}</p>
            {project ? (
              <Link className="button secondary" href={project.workspace_href}>
                回项目里应用 <ArrowRight size={16} />
              </Link>
            ) : null}
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <BookOpenCheck size={20} />
              <div>
                <span>小课内容</span>
                <h2>只学这一小段</h2>
              </div>
            </div>
            <div className="reason-list">
              {workbench.lessons.map((lesson) => (
                <div className="reason-item" key={lesson.id}>
                  <strong>{lesson.title}</strong>
                  <p>{humanizeText(lesson.body)}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="canvas-panel" id="micro-exercise">
            <div className="panel-title">
              <BrainCircuit size={20} />
              <div>
                <span>小练习</span>
                <h2>证明你能用到项目里</h2>
              </div>
            </div>
            <p>{humanizeText(workbench.exercise.prompt)}</p>
            <form action={submitExercise} className="chat-composer">
              <input type="hidden" name="course_module_id" value={workbench.course.id} />
              <textarea
                name="answer"
                rows={7}
                defaultValue="我会把这节小课的方法应用到当前项目：先写一个具体实现动作，再设计 3 个验证样例。如果验证失败，我会记录失败输入、调整参数或提示词，并把结果写入 README 或 evaluation report。"
                required
              />
              <button type="submit">
                交给小课教练检查 <SendHorizontal size={16} />
              </button>
            </form>
          </article>
        </section>

        <aside className="coach-presence">
          <div className="agent-card sticky-agent">
            <div className="agent-face">
              <Bot size={22} />
              <div>
                <span>小课教练</span>
                <strong>边学边做</strong>
              </div>
            </div>
            <div className="memory-item">
              <span>状态</span>
              <strong>{statusText(workbench.course.status)}</strong>
            </div>
            <div className="memory-item">
              <span>预计时间</span>
              <strong>{workbench.course.estimated_minutes} 分钟</strong>
            </div>
            <div className="memory-item">
              <span>通过标准</span>
              <strong>{workbench.exercise.pass_standard.minimum_score} / 100</strong>
            </div>
            <div className="evidence-strip">
              {workbench.exercise.pass_standard.required_keywords.map((keyword) => (
                <span key={keyword}>{keyword}</span>
              ))}
            </div>
            <div className="agent-card inner-card">
              <div className="agent-face">
                <ClipboardCheck size={20} />
                <div>
                  <span>最近反馈</span>
                  <strong>{latestAttempt ? `${latestAttempt.score} / 100` : "还没提交"}</strong>
                </div>
              </div>
              <p className="muted">
                {latestAttempt ? humanizeText(latestAttempt.feedback) : "提交小练习后，小课教练会判断你是否真的能把知识用到项目里。"}
              </p>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
