import Link from "next/link";
import { Award, Network, ShieldCheck } from "lucide-react";
import { apiGet } from "@/lib/api";
import { humanizeText } from "@/lib/humanize";

type SkillMap = {
  target_job: { slug: string; title: string } | null;
  skills: Array<{
    slug: string;
    name: string;
    required_level: number;
    current_score: number;
    confidence: number;
    evidence_count: number;
  }>;
};

export default async function SkillMapPage() {
  const skillMap = await apiGet<SkillMap>("/api/skill-map/me");
  const evidence = await apiGet<{ evidence_items: Array<{ id: string; skill: string; evidence_text: string; score: number }> }>("/api/evidence/me");

  return (
    <main className="training-cockpit" aria-label="能力画像">
      <header className="cockpit-hero compact-hero">
        <div className="live-orb" aria-hidden="true">
          <Network size={32} />
          <span />
        </div>
        <div>
          <span className="eyebrow">岗位能力差距</span>
          <h1>能力画像</h1>
          <p>
            这里不让学员自评。系统根据项目作品、小课练习、检查结果和修改记录，
            判断你离目标岗位还差哪些能力。
          </p>
          <Link className="button" href="/passport">
            <Award size={16} /> 生成求职能力报告
          </Link>
        </div>
      </header>

      <section className="canvas-grid two-column">
        <section className="mission-canvas">
          <article className="canvas-panel">
            <div className="panel-title">
              <Network size={20} />
              <div>
                <span>目标岗位：{skillMap.target_job?.title ?? "未选择"}</span>
                <h2>能力差距</h2>
              </div>
            </div>
            {skillMap.skills.map((skill) => {
              const percent = Math.min(100, Math.round((skill.current_score / skill.required_level) * 100));
              return (
                <div key={skill.slug}>
                  <div className="metric">
                    <span>{humanizeText(skill.name)}</span>
                    <strong>{skill.current_score}/{skill.required_level}</strong>
                  </div>
                  <div className="progress"><span style={{ width: `${percent}%` }} /></div>
                  <p className="row-meta">已有 {skill.evidence_count} 条证据，可信度 {Math.round(skill.confidence * 100)}%。</p>
                </div>
              );
            })}
          </article>
        </section>

        <aside className="coach-presence">
          <div className="agent-card sticky-agent">
            <div className="agent-face">
              <ShieldCheck size={22} />
              <div>
                <span>可核验证据</span>
                <strong>{evidence.evidence_items.length} 条</strong>
              </div>
            </div>
            <div className="reason-list">
              {evidence.evidence_items.slice(0, 6).map((item) => (
                <div className="reason-item" key={item.id}>
                  <strong>{humanizeText(item.skill)}: {item.score}</strong>
                  <p>{humanizeText(item.evidence_text)}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
