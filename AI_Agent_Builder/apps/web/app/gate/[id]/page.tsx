import Link from "next/link";
import { AlertTriangle, Bot, CheckCircle2, ClipboardCheck, FileSearch, TerminalSquare } from "lucide-react";
import { apiGet, apiPost, type ReviewGateWorkbench } from "@/lib/api";
import { humanizeText, statusText } from "@/lib/humanize";

export default async function ReviewGatePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let workbench = await apiGet<ReviewGateWorkbench>(`/api/reviews/jobs/${id}/workbench`);

  if (workbench.job.status === "queued") {
    try {
      await apiPost(`/api/reviews/jobs/${id}/run`, {});
    } catch {
      // Development can render twice; a second render may find the job already running.
    }
    workbench = await apiGet<ReviewGateWorkbench>(`/api/reviews/jobs/${id}/workbench?after_run=${Date.now()}`);
  }

  const latestRun = workbench.sandbox.latest;
  const review = workbench.review;

  return (
    <main className="check-report" aria-label="项目检查报告">
      <header className="cockpit-hero compact-hero">
        <div className="live-orb" aria-hidden="true">
          <FileSearch size={32} />
          <span />
        </div>
        <div>
          <span className="eyebrow">作品检查员</span>
          <h1>项目检查报告</h1>
          <p>
            {workbench.project_context.project.title} / {workbench.project_context.task.title}
          </p>
          <div className="cockpit-actions">
            <Link className="button secondary" href={workbench.handoffs.project_lab.href}>回到项目继续改</Link>
            <Link className="button" href={workbench.handoffs.report.href}>查看完整检查报告</Link>
          </div>
        </div>
      </header>

      <section className="canvas-grid two-column">
        <section className="mission-canvas">
          <article className="today-card">
            <span className="eyebrow">这次结论</span>
            <h2>{review ? readinessLabel(review.hiring_readiness) : "正在检查你的作品"}</h2>
            <p>{humanizeText(review?.summary ?? "AI 会先看项目能不能运行，再看实现、文档、评估和求职可信度。")}</p>
            {review ? (
              <div className="score-ring">
                <strong>{review.overall_score}</strong>
                <span>/ 100</span>
              </div>
            ) : null}
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <TerminalSquare size={20} />
              <div>
                <span>第一步</span>
                <h2>能不能运行</h2>
              </div>
            </div>
            {latestRun ? (
              <>
                <p>{latestRun.command}</p>
                <div className="evidence-strip">
                  <span>{statusText(latestRun.status)}</span>
                  <span>exit {latestRun.exit_code ?? "-"}</span>
                  <span>{latestRun.duration_ms ?? 0} ms</span>
                </div>
                <pre>{latestRun.stdout_ref || latestRun.stderr_ref || "没有运行输出。"}</pre>
              </>
            ) : (
              <p className="muted">还没有运行记录。刷新后会从等待状态开始检查。</p>
            )}
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <CheckCircle2 size={20} />
              <div>
                <span>第二步</span>
                <h2>哪里做得好</h2>
              </div>
            </div>
            {review ? (
              <div className="rubric-grid">
                {review.rubric_scores.map((score) => (
                  <div className="metric-card" key={score.rubric_item_key}>
                    <strong>{rubricLabel(score.rubric_item_key)}</strong>
                    <span>{score.score} / {score.max_score}</span>
                    <p>{humanizeText(score.reason)}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">检查完成后会显示具体得分和原因。</p>
            )}
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <ClipboardCheck size={20} />
              <div>
                <span>第三步</span>
                <h2>下一轮只改这几件事</h2>
              </div>
            </div>
            {workbench.coach_tasks.length ? (
              <div className="reason-list">
                {workbench.coach_tasks.map((task) => (
                  <div className="reason-item" key={task.id}>
                    <strong>{humanizeText(task.title)}</strong>
                    <p>{humanizeText(task.reason)}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">检查完成后，AI 教练会把低分项变成下一轮修改任务。</p>
            )}
          </article>
        </section>

        <aside className="coach-presence">
          <div className="agent-card sticky-agent">
            <div className="agent-face">
              <Bot size={22} />
              <div>
                <span>作品检查员正在看</span>
                <strong>{statusText(workbench.job.status)}</strong>
              </div>
            </div>
            <div className="memory-item">
              <span>检查方式</span>
              <strong>{modeLabel(workbench.agent.mode)}</strong>
            </div>
            <div className="memory-item">
              <span>能力证据</span>
              <strong>{workbench.evidence.count} 条</strong>
            </div>
            {review?.risk_flags.length ? (
              <div className="risk-list">
                {review.risk_flags.map((flag) => (
                  <div className="risk-item" key={`${flag.type}-${flag.description}`}>
                    <AlertTriangle size={16} />
                    <div>
                      <strong>{humanizeText(flag.type)}</strong>
                      <p>{humanizeText(flag.description)}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">暂时没有高风险提示。</p>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

function readinessLabel(value: string) {
  const labels: Record<string, string> = {
    hire_ready: "接近可以投递",
    needs_revision: "还需要修改",
    not_ready: "暂时不建议投递",
  };
  return labels[value] ?? humanizeText(value);
}

function modeLabel(mode: string) {
  if (mode === "claude_agent_sdk") return "Claude AI";
  if (mode === "mock") return "演示模式";
  if (mode === "rule") return "规则检查";
  return humanizeText(mode);
}

function rubricLabel(key: string) {
  const labels: Record<string, string> = {
    runnable: "能不能运行",
    architecture: "架构是否清楚",
    evaluation: "有没有评估",
    documentation: "文档是否完整",
    delivery: "是否像可交付项目",
    rag_retrieval_quality: "检索质量",
    engineering_quality: "工程质量",
  };
  return labels[key] ?? humanizeText(key);
}
