import { BriefcaseBusiness, ClipboardCheck, Network, ShieldCheck } from "lucide-react";
import { apiGet } from "@/lib/api";
import { humanizeText, statusText } from "@/lib/humanize";

type Passport = {
  slug: string;
  visibility: string;
  latest_snapshot: {
    version: number;
    learner: { display_name: string; email: string };
    target_job: { title: string } | null;
    skill_summary: Array<{ slug: string; name: string; current_score: number; required_level: number }>;
    projects: Array<{ title: string; status: string }>;
    evidence: Array<{ id: string; skill: string; score: number; evidence_text: string }>;
    ai_dependency?: {
      average_score: number;
      max_score: number;
      session_count: number;
      rating: "low" | "medium" | "high";
    };
  };
};

export default async function PassportPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const passport = await apiGet<Passport>(`/api/passports/${slug}`);
  const snapshot = passport.latest_snapshot;
  const dependency = snapshot.ai_dependency ?? { average_score: 0, max_score: 0, session_count: 0, rating: "low" };

  return (
    <main className="training-cockpit" aria-label="求职能力报告">
      <header className="cockpit-hero compact-hero">
        <div className="live-orb" aria-hidden="true">
          <BriefcaseBusiness size={32} />
          <span />
        </div>
        <div>
          <span className="eyebrow">{visibilityLabel(passport.visibility)} / v{snapshot.version}</span>
          <h1>{snapshot.learner.display_name} 的求职能力报告</h1>
          <p>
            目标岗位：{snapshot.target_job?.title ?? "未选择"}。这不是结业证书，
            而是把项目、作品检查和学习过程整理成招聘方能看懂的能力证据档案。
          </p>
        </div>
      </header>

      <section className="canvas-grid two-column">
        <section className="mission-canvas">
          <article className="canvas-panel">
            <div className="panel-title">
              <Network size={20} />
              <div>
                <span>能力画像</span>
                <h2>岗位能力差距</h2>
              </div>
            </div>
            {snapshot.skill_summary.map((skill) => (
              <div className="metric" key={skill.slug}>
                <span>{humanizeText(skill.name)}</span>
                <strong>{skill.current_score}/{skill.required_level}</strong>
              </div>
            ))}
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <BriefcaseBusiness size={20} />
              <div>
                <span>项目证据</span>
                <h2>完成项目</h2>
              </div>
            </div>
            {snapshot.projects.map((project) => (
              <div className="metric" key={project.title}>
                <span>{project.title}</span>
                <strong>{statusText(project.status)}</strong>
              </div>
            ))}
          </article>

          <article className="canvas-panel">
            <div className="panel-title">
              <ClipboardCheck size={20} />
              <div>
                <span>可核验材料</span>
                <h2>能力证据</h2>
              </div>
            </div>
            <div className="reason-list">
              {snapshot.evidence.map((item) => (
                <div className="reason-item" key={item.id}>
                  <strong>{humanizeText(item.skill)}: {item.score}</strong>
                  <p>{humanizeText(item.evidence_text)}</p>
                </div>
              ))}
            </div>
          </article>
        </section>

        <aside className="coach-presence">
          <div className="agent-card sticky-agent">
            <div className="agent-face">
              <ShieldCheck size={22} />
              <div>
                <span>AI 代做风险</span>
                <strong>{dependencyLabel(dependency.rating)}</strong>
              </div>
            </div>
            <div className="memory-item"><span>平均风险分</span><strong>{dependency.average_score}</strong></div>
            <div className="memory-item"><span>最高风险分</span><strong>{dependency.max_score}</strong></div>
            <div className="memory-item"><span>教练对话次数</span><strong>{dependency.session_count}</strong></div>
            <p className="muted">分数越低，说明学员在训练中保留了更多独立拆解、调试和解释过程。</p>
          </div>
        </aside>
      </section>
    </main>
  );
}

function visibilityLabel(value: string) {
  if (value === "public") return "公开";
  if (value === "private") return "私密";
  if (value === "unlisted") return "未公开";
  return humanizeText(value);
}

function dependencyLabel(rating: string) {
  if (rating === "high") return "高";
  if (rating === "medium") return "中";
  return "低";
}
