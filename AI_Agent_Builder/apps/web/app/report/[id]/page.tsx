import Link from "next/link";
import { AlertTriangle, BarChart3, BriefcaseBusiness, CheckCircle2, ShieldCheck } from "lucide-react";
import { apiGet, type Review } from "@/lib/api";
import { humanizeText } from "@/lib/humanize";

export default async function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const review = await apiGet<Review>(`/api/reviews/${id}`);

  return (
    <main className="check-report" aria-label="完整检查报告">
      <header className="cockpit-hero compact-hero">
        <div className="live-orb" aria-hidden="true">
          <ShieldCheck size={32} />
          <span />
        </div>
        <div>
          <span className="eyebrow">{readinessLabel(review.hiring_readiness)}</span>
          <h1>完整检查报告</h1>
          <p>这不是作业批改，而是一份面向招聘方的项目可信度报告：项目是否能运行、哪里可信、哪里还要补。</p>
          <div className="cockpit-actions">
            <Link className="button secondary" href="/skill-map">查看能力画像</Link>
            <Link className="button" href="/passport">生成求职能力报告</Link>
          </div>
        </div>
      </header>

      <section className="canvas-grid two-column">
        <section className="mission-canvas">
          <article className="today-card">
            <span className="eyebrow">总评</span>
            <h2>{review.overall_score} / 100</h2>
            <p>{humanizeText(review.summary)}</p>
            <div className="mission-proof">
              <CheckCircle2 size={18} />
              <span>{nextActionLabel(review.next_action)}</span>
            </div>
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <BarChart3 size={20} />
              <div>
                <span>具体评分</span>
                <h2>哪些能力已经能证明</h2>
              </div>
            </div>
            <div className="rubric-grid">
              {review.rubric_scores.map((score) => (
                <div className="metric-card" key={score.rubric_item_key}>
                  <strong>{rubricLabel(score.rubric_item_key)}</strong>
                  <span>{score.score} / {score.max_score}</span>
                  <p>{humanizeText(score.reason)}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <CheckCircle2 size={20} />
              <div>
                <span>下一步</span>
                <h2>下一轮只改这几件事</h2>
              </div>
            </div>
            {review.coach_tasks?.length ? (
              <div className="coach-action-list">
                {review.coach_tasks.flatMap((task) =>
                  task.actions.map((action) => (
                    <div className="coach-action" key={`${task.id}-${action.type}-${action.label}`}>
                      <strong>{humanizeText(action.label)}</strong>
                      <p>{humanizeText(action.instruction)}</p>
                      <span>交付物：{humanizeText(action.deliverable)}</span>
                    </div>
                  )),
                )}
              </div>
            ) : (
              <p className="muted">当前检查没有生成额外修改任务。</p>
            )}
          </article>
        </section>

        <aside className="coach-presence">
          <div className="agent-card sticky-agent">
            <div className="agent-face">
              <BriefcaseBusiness size={22} />
              <div>
                <span>招聘方会关心</span>
                <strong>可信度 {Math.round(review.confidence * 100)}%</strong>
              </div>
            </div>
            {review.risk_flags.length ? (
              <div className="risk-list">
                {review.risk_flags.map((flag) => (
                  <div className="risk-item" key={`${flag.type}-${flag.description}`}>
                    <AlertTriangle size={16} />
                    <div>
                      <strong>{riskLabel(flag.type)} / {severityLabel(flag.severity)}</strong>
                      <p>{humanizeText(flag.description)}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">当前检查没有高风险标记。</p>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

function nextActionLabel(value: string) {
  if (value === "revise") return "继续修改后再提交检查";
  if (value === "pass") return "可以进入下一个项目或生成求职能力报告";
  return humanizeText(value);
}

function readinessLabel(value: string) {
  if (value === "hire_ready") return "接近可以投递";
  if (value === "needs_revision") return "还需要修改";
  if (value === "not_ready") return "暂时不建议投递";
  return humanizeText(value);
}

function riskLabel(type: string) {
  const labels: Record<string, string> = {
    ai_dependency: "AI 代做风险",
    missing_eval: "缺少评估",
    weak_docs: "文档不足",
    runtime_failure: "运行问题",
  };
  return labels[type] ?? humanizeText(type);
}

function severityLabel(severity: string) {
  if (severity === "high") return "高";
  if (severity === "medium") return "中";
  return "低";
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
