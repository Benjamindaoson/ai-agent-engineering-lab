import Link from "next/link";
import { ArrowRight, FlaskConical, ShieldCheck } from "lucide-react";
import { apiGet, type Project } from "@/lib/api";

const projectFlow = [
  ["01", "课程补给", "当前任务缺什么，系统推荐最小课程。"],
  ["02", "项目实现", "在 Project Lab 中完成真实提交物。"],
  ["03", "Sandbox", "运行代码、测试和日志采集。"],
  ["04", "Agent Review", "自动评审 Prompt、代码、文档和评测。"],
  ["05", "能力证据", "评审结果进入能力图谱和 Skill Passport。"],
];

export default async function ProjectsPage() {
  const data = await apiGet<{ projects: Project[] }>("/api/projects");

  return (
    <>
      <header className="page-header">
        <div>
          <span className="badge">项目实战</span>
          <h1 className="page-title">3 个递进式 AI Agent 项目</h1>
          <p className="subtitle">
            训练营不卖“看完课程”的幻觉。每个项目都要产生可运行代码、文档、Demo、评测报告和可进入 Skill Passport 的能力证据。
          </p>
        </div>
      </header>

      <section className="workflow" aria-label="项目实战流程">
        {projectFlow.map(([index, title, description]) => (
          <div className="workflow-step" key={index}>
            <span>{index}</span>
            <strong>{title}</strong>
            <p>{description}</p>
          </div>
        ))}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2><ShieldCheck size={18} /> 项目路径</h2>
            <p className="muted">项目顺序按能力递进设计：Prompt/Workflow → RAG → Tool Use 自动化。</p>
          </div>
        </div>
        {data.projects.length === 0 ? <p className="muted">暂未分配项目。</p> : null}
        <div className="list">
          {data.projects.map((project) => (
            <div className="row" key={project.learner_project_id}>
              <div>
                <span className="badge badge-amber">项目 {project.level}</span>
                <p className="row-title">{project.title}</p>
                <p className="row-meta">{project.description}</p>
              </div>
              <div className="toolbar">
                <span className="badge">{statusLabel(project.status)}</span>
                <Link className="button" href={`/lab/${project.learner_project_id}`}>
                  <FlaskConical size={16} /> 进入项目 <ArrowRight size={16} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

function statusLabel(status: string) {
  if (status === "passed") return "已通过";
  if (status === "needs_revision") return "需修改";
  if (status === "review_queued") return "待评审";
  if (status === "ai_reviewing") return "评审中";
  return "进行中";
}
