import Link from "next/link";
import {
  ArrowRight,
  BookOpenCheck,
  Bot,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  Code2,
  FileText,
  GraduationCap,
  Route,
  ShieldCheck,
  Target,
} from "lucide-react";
import { apiGet, type AgentCommandCenter, type LearningPlan } from "@/lib/api";
import {
  agentTeam,
  buildMissionThreads,
  requiredOutputs,
  resolveLearnerTrack,
  trackLabel,
  trackPositioning,
  type SkillMapData,
} from "@/lib/learner-mission";
import { humanizeText, statusText } from "@/lib/humanize";

export default async function CoachPage() {
  const [center, plan, skillMap] = await Promise.all([
    apiGet<AgentCommandCenter>("/api/agents/command-center"),
    apiGet<LearningPlan>("/api/learning-plan/me"),
    apiGet<SkillMapData>("/api/skill-map/me"),
  ]);
  const track = resolveLearnerTrack(center, plan);
  const threads = buildMissionThreads(center, plan, skillMap);
  const project = center.active_project;
  const task = project?.tasks[0] ?? null;
  const course = task?.courses[0] ?? center.course_queue.items[0] ?? null;
  const outputs = requiredOutputs(center);
  const weakest = [...skillMap.skills].sort(
    (a, b) => b.required_level - b.current_score - (a.required_level - a.current_score),
  )[0];

  return (
    <main className="mission-control-v2" aria-label="个人训练中枢">
      <section className="mission-topbar">
        <div>
          <span className="system-kicker">诊断分流完成</span>
          <h1>你的专属 AI Agent 训练中枢</h1>
          <p>{trackPositioning(track)}</p>
        </div>
        <div className="topbar-actions">
          <Link className="button secondary" href="/intake">重新诊断</Link>
          <Link className="button" href={project?.workspace_href ?? "/intake"}>
            进入当前训练 <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <section className="track-brief">
        <article>
          <Target size={22} />
          <span>当前训练轨道</span>
          <strong>{trackLabel(track)}</strong>
        </article>
        <article>
          <GraduationCap size={22} />
          <span>目标角色</span>
          <strong>{center.learner.target_role}</strong>
        </article>
        <article>
          <Route size={22} />
          <span>每周投入</span>
          <strong>{center.learner.weekly_hours} 小时</strong>
        </article>
        <article>
          <ShieldCheck size={22} />
          <span>最弱短板</span>
          <strong>{weakest ? humanizeText(weakest.name) : "等待更多证据"}</strong>
        </article>
      </section>

      <section className="mission-layout">
        <aside className="mission-sidebar">
          <h2>多线程训练</h2>
          <p>真实学习不会只走一条线。系统会同时推进主线项目、补弱、小课、练习、检查和求职证据。</p>
          <div className="thread-list">
            {threads.map((thread) => (
              <Link className="thread-link" href={thread.href} key={thread.id}>
                <span>{thread.label}</span>
                <strong>{thread.title}</strong>
                <small>{statusText(thread.status)}</small>
              </Link>
            ))}
          </div>
        </aside>

        <section className="mission-main">
          <article className="primary-mission">
            <div className="mission-heading">
              <div>
                <span className="system-kicker">当前主线任务</span>
                <h2>{project?.title ?? "先完成诊断，生成第一条训练主线"}</h2>
              </div>
              <Code2 size={28} />
            </div>
            <p>{humanizeText(task?.description ?? plan.summary)}</p>
            <div className="output-row">
              {outputs.length ? outputs.map((output) => <span key={output}>{output}</span>) : <span>目标、基础、时间、项目方向</span>}
            </div>
            <div className="mission-actions">
              <Link className="button" href={project?.workspace_href ?? "/intake"}>打开项目工作室</Link>
              <Link className="button secondary" href="/learning-plan">查看专属学习路线</Link>
            </div>
          </article>

          <div className="learning-split">
            <article className="course-window">
              <div className="mission-heading compact">
                <div>
                  <span className="system-kicker">课程窗口</span>
                  <h2>{course?.title ?? "等待课程推荐"}</h2>
                </div>
                <BookOpenCheck size={24} />
              </div>
              <p>{humanizeText(course?.reason ?? "课程会在当前项目任务需要时出现。")}</p>
              <dl>
                <div><dt>为什么现在学</dt><dd>{course ? "它会直接影响当前项目提交物质量。" : "先完成诊断后再推荐。"}</dd></div>
                <div><dt>学习时间</dt><dd>{course ? `${course.estimated_minutes} 分钟` : "-"}</dd></div>
                <div><dt>学完产出</dt><dd>一个可提交的小练习 + 项目中的一次修改。</dd></div>
              </dl>
              <Link className="button secondary" href={course?.href ?? "/courses"}>进入课程训练室</Link>
            </article>

            <article className="practice-window">
              <div className="mission-heading compact">
                <div>
                  <span className="system-kicker">练习窗口</span>
                  <h2>先证明你能用，再进入项目提交</h2>
                </div>
                <ClipboardCheck size={24} />
              </div>
              <p>每节小课都必须配一个微练习：实现动作、验证方法、失败后的调整策略。</p>
              <div className="practice-checks">
                <span><CheckCircle2 size={16} /> 说清楚实现动作</span>
                <span><CheckCircle2 size={16} /> 给出验证方法</span>
                <span><CheckCircle2 size={16} /> 记录失败后如何调整</span>
              </div>
              <Link className="button secondary" href={course?.href ?? "/courses"}>打开当前练习</Link>
            </article>
          </div>

          <article className="studio-window">
            <div className="mission-heading compact">
              <div>
                <span className="system-kicker">项目工作室</span>
                <h2>课程和练习最终都要回到作品</h2>
              </div>
              <FileText size={24} />
            </div>
            <p>项目不是表单。它是招聘方能追问的证据：代码、Demo、README、架构说明、评估记录、复盘。</p>
            <div className="studio-grid">
              <div><strong>主线项目</strong><span>{project?.title ?? "待生成"}</span></div>
              <div><strong>当前任务</strong><span>{task?.title ?? "待生成"}</span></div>
              <div><strong>检查入口</strong><span>{statusText(center.quality_gate.status)}</span></div>
            </div>
          </article>
        </section>

        <aside className="agent-team">
          <div className="agent-team-header">
            <Bot size={22} />
            <div>
              <span className="system-kicker">Agent Team</span>
              <h2>系统背后的教练组</h2>
            </div>
          </div>
          {agentTeam(center).map(([name, detail]) => (
            <div className="agent-role" key={name}>
              <BrainCircuit size={16} />
              <div>
                <strong>{name}</strong>
                <p>{detail}</p>
              </div>
            </div>
          ))}
        </aside>
      </section>
    </main>
  );
}
