import Link from "next/link";
import { ArrowRight, BriefcaseBusiness, ClipboardCheck } from "lucide-react";
import { apiPost } from "@/lib/api";

export default async function PassportGeneratePage() {
  const passport = await apiPost<{ slug: string; version: number }>("/api/passports/generate", {});

  return (
    <main className="training-cockpit" aria-label="求职能力报告生成">
      <section className="cockpit-hero compact-hero">
        <div className="live-orb" aria-hidden="true">
          <BriefcaseBusiness size={32} />
          <span />
        </div>
        <div>
          <span className="eyebrow">第 {passport.version} 版</span>
          <h1>求职能力报告已生成</h1>
          <p>
            系统已经整理你的项目、代码链接、Demo、作品检查结果、能力证据和 AI 代做风险。
            这不是结业证书，而是一份给招聘方看的能力证据档案。
          </p>
          <Link className="button" href={`/passport/${passport.slug}`}>
            打开求职能力报告 <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <section className="canvas-grid two-column">
        <article className="canvas-panel">
          <div className="panel-title">
            <BriefcaseBusiness size={20} />
            <div>
              <span>招聘方最关心</span>
              <h2>你到底能不能交付 AI 项目</h2>
            </div>
          </div>
          <div className="reason-list">
            <div className="reason-item"><strong>做过哪些项目</strong><p>展示项目名称、完成状态、代码和作品说明。</p></div>
            <div className="reason-item"><strong>能力分数从哪里来</strong><p>来自项目提交、作品检查、小课练习和修改记录。</p></div>
            <div className="reason-item"><strong>是不是 AI 代做</strong><p>显示 AI 辅助风险，保留独立思考和调试过程。</p></div>
          </div>
        </article>

        <aside className="agent-card">
          <div className="agent-face">
            <ClipboardCheck size={22} />
            <div>
              <span>下一步</span>
              <strong>预览并检查报告</strong>
            </div>
          </div>
          <p className="muted">打开报告后，检查项目名称、证据文本和能力分数是否能被招聘方看懂。</p>
          <Link className="button secondary" href={`/passport/${passport.slug}`}>预览报告</Link>
        </aside>
      </section>
    </main>
  );
}
