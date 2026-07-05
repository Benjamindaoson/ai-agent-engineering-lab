import Link from "next/link";
import { ArrowRight, CheckCircle2, MonitorPlay } from "lucide-react";
import { apiGet, type DemoMode } from "@/lib/api";

export default async function DemoPage() {
  const demo = await apiGet<DemoMode>("/api/demo-mode");

  return (
    <>
      <header className="page-header">
        <div>
          <span className="badge">Investor Demo Mode</span>
          <h1 className="page-title">{demo.headline}</h1>
          <p className="subtitle">{demo.positioning}</p>
        </div>
        <Link className="button" href={demo.next_best_action.primary_cta.href}>
          {demo.next_best_action.primary_cta.label} <ArrowRight size={16} />
        </Link>
      </header>

      <section className="stat-grid">
        <div className="stat">
          <span>项目实战</span>
          <strong>{demo.metrics.projects}</strong>
        </div>
        <div className="stat">
          <span>能力证据</span>
          <strong>{demo.metrics.evidence_count}</strong>
        </div>
        <div className="stat">
          <span>课程补给</span>
          <strong>{demo.metrics.adaptive_courses}</strong>
        </div>
        <div className="stat">
          <span>核心内核</span>
          <strong>Evidence</strong>
        </div>
      </section>

      <section className="panel">
        <h2><MonitorPlay size={18} /> 演示脚本</h2>
        <p className="muted">
          这条路径用于向投资人、企业客户和第一批学员展示：系统如何把学习行为变成可验证的交付能力。
        </p>
        <div className="step-list">
          {demo.steps.map((step) => (
            <div className="step" key={step.name}>
              <div>
                <div className="section-heading">
                  <div>
                    <h3>{step.name}</h3>
                    <p className="muted">{step.promise}</p>
                  </div>
                  <span className="badge"><CheckCircle2 size={13} /> {step.status}</span>
                </div>
                <div className="grid">
                  <div className="metric-card">
                    <span>演示页面</span>
                    <strong>{step.screen}</strong>
                    <Link className="button secondary compact-button" href={step.href}>
                      打开页面
                    </Link>
                  </div>
                  <div className="metric-card">
                    <span>可信证据</span>
                    <p className="row-meta">{step.proof}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
