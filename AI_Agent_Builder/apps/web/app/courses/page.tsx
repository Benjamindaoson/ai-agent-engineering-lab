import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowRight, BookOpenCheck, CheckCircle2, ClipboardCheck, Target, TerminalSquare } from "lucide-react";
import { apiGet, type AgentCommandCenter, type Course, type CourseDetail } from "@/lib/api";
import { humanizeText } from "@/lib/humanize";

type CourseLibrary = {
  storage: {
    module_table: string;
    lesson_table: string;
    binding_table: string;
    progress_table: string;
  };
  courses: Course[];
};

export default async function CoursesPage() {
  const [data, center] = await Promise.all([
    apiGet<CourseLibrary>("/api/courses"),
    apiGet<AgentCommandCenter>("/api/agents/command-center"),
  ]);
  const details = await Promise.all(data.courses.map((course) => apiGet<CourseDetail>(`/api/courses/${course.id}`)));
  const detailById = new Map(details.map((detail) => [detail.id, detail]));
  const completed = data.courses.filter((course) => course.status === "completed").length;
  const totalMinutes = data.courses.reduce((sum, course) => sum + course.estimated_minutes, 0);
  const nextCourse = data.courses.find((course) => course.status !== "completed") ?? data.courses[0] ?? null;
  const project = center.active_project;
  const task = project?.tasks[0] ?? null;

  return (
    <main className="course-queue" aria-label="自适应课程队列">
      <section className="lab-header">
        <div>
          <span className="badge">自适应课程队列</span>
          <h1>当前任务需要的小课</h1>
          <p>
            这里不是课程库。AI 教练会根据你的项目任务和能力短板，只推荐现在做项目必须补的最小课程。
            学完以后要回到项目，把内容写进代码、文档、测试或复盘。
          </p>
        </div>
        <div className="hero-actions">
          {nextCourse ? (
            <Link className="button" href={`/learn/${nextCourse.id}`}>
              打开下一节小课 <ArrowRight size={16} />
            </Link>
          ) : null}
          <Link className="button secondary" href="/learning-plan">查看学习路线</Link>
        </div>
      </section>

      <section className="course-command-strip">
        <CourseMetric label="小课数量" value={`${data.courses.length} 节`} />
        <CourseMetric label="已完成" value={`${completed} 节`} />
        <CourseMetric label="预计投入" value={`${totalMinutes} 分钟`} />
        <CourseMetric label="当前项目" value={project?.title ?? "先确认学习路线"} />
      </section>

      <section className="grid-wide">
        <article className="panel active-coach-task">
          <div className="section-heading">
            <div>
              <span className="badge badge-amber">为什么不让你刷课</span>
              <h2>{task ? task.title : "先让 AI 教练确认你的项目任务"}</h2>
            </div>
            <Target size={22} />
          </div>
          <p>
            {task
              ? humanizeText(task.description)
              : "课程只在项目需要时出现。没有项目任务时，先回到 AI 教练确认目标和第一条项目路线。"}
          </p>
          <div className="course-principles">
            <div><Target size={18} /><span>先看当前任务</span></div>
            <div><BookOpenCheck size={18} /><span>只补必要小课</span></div>
            <div><ClipboardCheck size={18} /><span>学完形成作品证据</span></div>
          </div>
        </article>

        <aside className="panel">
          <h2><BookOpenCheck size={18} /> 课程怎么保存</h2>
          <p className="muted">
            课程内容存在系统数据里，每节小课都有内容、练习、项目绑定和学习进度。
            用户不用看到表名，只需要知道为什么现在学、学完用在哪里。
          </p>
          <div className="metric"><span>内容形态</span><strong>文字小课 + 练习</strong></div>
          <div className="metric"><span>后续可扩展</span><strong>视频 / 文档 / 代码仓库</strong></div>
        </aside>
      </section>

      <section className="course-card-list">
        {data.courses.map((course, index) => {
          const detail = detailById.get(course.id);
          return (
            <article className="adaptive-course-card" key={course.id}>
              <div className="course-rank">
                <span>顺序</span>
                <strong>{String(index + 1).padStart(2, "0")}</strong>
              </div>

              <div className="course-main">
                <div className="course-card-header">
                  <div>
                    <span className={course.status === "completed" ? "badge" : "badge badge-amber"}>
                      {statusLabel(course.status)}
                    </span>
                    <h2>{humanizeText(course.title)}</h2>
                    <p>{humanizeText(course.description)}</p>
                  </div>
                  <div className="course-meta-pill">
                    <span>{categoryLabel(course.category)}</span>
                    <strong>{course.estimated_minutes} 分钟</strong>
                  </div>
                </div>

                <div className="course-evidence-grid">
                  <InfoBlock
                    icon={<Target size={16} />}
                    title="为什么推荐"
                    text={humanizeText(course.recommendation_reason ?? course.reason ?? "适合当前项目任务。")}
                  />
                  <InfoBlock
                    icon={<TerminalSquare size={16} />}
                    title="绑定哪个项目任务"
                    text={bindingText(detail)}
                  />
                  <InfoBlock
                    icon={<CheckCircle2 size={16} />}
                    title="学完产出什么"
                    text={evidenceText(course, detail)}
                  />
                </div>

                <div className="course-bottom-row">
                  <div className="keyword-strip">
                    {(detail?.exercise.expected_keywords ?? []).slice(0, 5).map((keyword) => (
                      <span className="badge" key={keyword}>{keyword}</span>
                    ))}
                  </div>

                  <div className="course-actions">
                    <Link className="button secondary" href={`/learn/${course.id}`}>
                      <BookOpenCheck size={16} /> 进入小课练习
                    </Link>
                    <Link className="button ghost" href={project?.workspace_href ?? "/coach"}>
                      回到项目里使用
                    </Link>
                  </div>
                </div>
              </div>
            </article>
          );
        })}
      </section>
    </main>
  );
}

function CourseMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="memory-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function InfoBlock({ icon, title, text }: { icon: ReactNode; title: string; text: string }) {
  return (
    <div className="course-info-block">
      <span>{icon} {title}</span>
      <p>{text}</p>
    </div>
  );
}

function bindingText(detail?: CourseDetail) {
  if (!detail?.project_bindings.length) return "来自当前能力短板，完成后回到项目里应用。";
  return detail.project_bindings
    .slice(0, 2)
    .map((binding) => `${binding.project_title} / ${binding.task_title}`)
    .join("；");
}

function evidenceText(course: Course, detail?: CourseDetail) {
  const skill = humanizeText(detail?.skill_name ?? course.category);
  const keywords = detail?.exercise.expected_keywords?.slice(0, 3).join("、");
  if (keywords) return `提交小练习，并把 ${keywords} 写进项目说明或测试记录，形成 ${skill} 的能力证据。`;
  return `完成小练习，并应用到项目作品，形成 ${skill} 的能力证据。`;
}

function statusLabel(status: string) {
  if (status === "completed") return "已完成";
  if (status === "in_progress") return "学习中";
  return "未开始";
}

function categoryLabel(category: string) {
  if (category === "Agent") return "智能体";
  if (category === "Prompt") return "提示词";
  if (category === "RAG") return "知识库问答";
  if (category === "Workflow") return "工作流";
  return humanizeText(category);
}
