import Link from "next/link";
import {
  ArrowRight,
  BookOpenCheck,
  BrainCircuit,
  CalendarDays,
  ClipboardCheck,
  Route,
  ShieldCheck,
  Target,
  TerminalSquare,
} from "lucide-react";
import { apiGet, type Course, type Dashboard, type Project } from "@/lib/api";

export default async function LearningPlanPage() {
  const dashboard = await apiGet<Dashboard>("/api/dashboard");
  const plan = dashboard.learning_plan;
  const activeProject = dashboard.workspace_state.active_project ?? dashboard.next_project ?? dashboard.projects[0] ?? null;
  const firstCourse = dashboard.adaptive_courses[0] ?? null;
  const topGap = dashboard.skill_gaps[0] ?? null;
  const progress = Math.min(100, Math.round((dashboard.evidence_count / Math.max(1, dashboard.projects.length * 2)) * 100));

  return (
    <main className="route-map" aria-label="可执行学习路线地图">
      <section className="lab-header">
        <div>
          <span className="badge">Learning Route Map</span>
          <h1>可执行路线地图</h1>
          <p>{plan.summary}</p>
        </div>
        <div className="hero-actions">
          <Link className="button secondary" href="/intake">
            <BrainCircuit size={16} /> 重新规划
          </Link>
          <Link className="button" href="/coach">
            下一步行动 <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <section className="route-command-strip">
        <RouteMetric label="目标角色" value={plan.target_role} />
        <RouteMetric label="当前水平" value={plan.current_level} />
        <RouteMetric label="每周投入" value={`${plan.weekly_hours} 小时`} />
        <RouteMetric label="预计周期" value={`${plan.estimated_weeks} 周`} />
      </section>

      <section className="route-overview">
        <article className="route-progress-card">
          <span className="badge badge-amber">下一步行动</span>
          <h2>{dashboard.next_best_action.title}</h2>
          <p>{dashboard.next_best_action.reason}</p>
          <div className="route-progress">
            <div style={{ width: `${progress}%` }} />
          </div>
          <small>证据进度：{dashboard.evidence_count} 条 Evidence / 目标 {dashboard.projects.length * 2} 条</small>
          <div className="coach-actions">
            <Link className="button" href={dashboard.next_best_action.primary_cta.href}>
              {dashboard.next_best_action.primary_cta.label} <ArrowRight size={16} />
            </Link>
            <Link className="button secondary" href={dashboard.next_best_action.secondary_cta.href}>
              {dashboard.next_best_action.secondary_cta.label}
            </Link>
          </div>
        </article>

        <aside className="route-signal-card">
          <h2>
            <ShieldCheck size={18} /> 证据缺口
          </h2>
          {topGap ? (
            <div className="gap-signal">
              <strong>{topGap.name}</strong>
              <p>当前 {topGap.current_score} / 目标 {topGap.required_level}，还差 {topGap.gap} 分。</p>
            </div>
          ) : (
            <p className="muted">当前没有明显证据缺口，继续推进项目交付。</p>
          )}
          <div className="gap-list">
            {dashboard.skill_gaps.slice(0, 4).map((gap) => (
              <div key={gap.slug}>
                <span>{gap.name}</span>
                <strong>{gap.current_score}/{gap.required_level}</strong>
              </div>
            ))}
          </div>
        </aside>
      </section>

      <section className="route-board">
        <aside className="route-rail">
          <h2>路线导航</h2>
          <Link href="/coach">
            <BrainCircuit size={16} /> Coach
          </Link>
          {activeProject ? (
            <Link href={`/lab/${activeProject.learner_project_id}`}>
              <TerminalSquare size={16} /> 当前项目
            </Link>
          ) : null}
          {firstCourse ? (
            <Link href={`/learn/${firstCourse.id}`}>
              <BookOpenCheck size={16} /> 当前课程
            </Link>
          ) : null}
          <Link href="/passport">
            <ClipboardCheck size={16} /> Skill Passport
          </Link>
        </aside>

        <section className="route-weeks-map">
          <div className="section-heading">
            <div>
              <span className="badge">每周目标</span>
              <h2>从学习计划到交付动作</h2>
            </div>
            <CalendarDays size={22} />
          </div>

          {plan.weeks.map((week) => {
            const relatedCourses = coursesForWeek(week.courses, dashboard.adaptive_courses);
            const relatedProject = projectForWeek(week.week, dashboard.projects);
            const relatedGap = dashboard.skill_gaps[(week.week - 1) % Math.max(1, dashboard.skill_gaps.length)] ?? null;
            return (
              <article className="route-week-card" key={week.week}>
                <div className="week-index">
                  <span>Week</span>
                  <strong>{week.week}</strong>
                </div>
                <div className="week-body">
                  <span className="badge">每周目标</span>
                  <h3>{week.focus}</h3>
                  <p>{week.outcome}</p>

                  <div className="week-link-grid">
                    <div>
                      <span><BookOpenCheck size={15} /> 关联课程</span>
                      {relatedCourses.length ? (
                        relatedCourses.slice(0, 2).map((course) => (
                          <Link key={course.id} href={`/learn/${course.id}`}>
                            {course.title}
                          </Link>
                        ))
                      ) : (
                        <small>{week.courses.join(" / ")}</small>
                      )}
                    </div>

                    <div>
                      <span><TerminalSquare size={15} /> 关联项目</span>
                      {relatedProject ? (
                        <Link href={`/lab/${relatedProject.learner_project_id}`}>
                          {relatedProject.title}
                        </Link>
                      ) : (
                        <small>等待项目路径生成</small>
                      )}
                    </div>

                    <div>
                      <span><Target size={15} /> 证据缺口</span>
                      {relatedGap ? (
                        <small>{relatedGap.name} 还差 {relatedGap.gap} 分</small>
                      ) : (
                        <small>暂无明显缺口</small>
                      )}
                    </div>
                  </div>
                </div>
              </article>
            );
          })}
        </section>
      </section>
    </main>
  );
}

function RouteMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="memory-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function coursesForWeek(courseSlugs: string[], courses: Course[]) {
  const normalized = new Set(courseSlugs);
  const exact = courses.filter((course) => normalized.has(course.slug));
  if (exact.length) return exact;
  return courses.filter((course) => courseSlugs.some((slug) => course.slug.includes(slug) || slug.includes(course.slug))).slice(0, 2);
}

function projectForWeek(week: number, projects: Project[]) {
  if (!projects.length) return null;
  if (week <= 2) return projects[0];
  if (week <= 5) return projects[1] ?? projects[0];
  return projects[2] ?? projects[projects.length - 1];
}
