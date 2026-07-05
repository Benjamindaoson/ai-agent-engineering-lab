import { redirect } from "next/navigation";
import { ArrowRight, Bot, BrainCircuit, CheckCircle2, SendHorizontal } from "lucide-react";
import { apiGet, apiPost, type PlanningState } from "@/lib/api";
import { humanizeText } from "@/lib/humanize";

async function startPlanning(formData: FormData) {
  "use server";
  await apiPost("/api/planning/sessions", {
    message: String(formData.get("message") || ""),
  });
  redirect("/intake");
}

async function sendPlanningMessage(formData: FormData) {
  "use server";
  const sessionId = String(formData.get("session_id"));
  await apiPost(`/api/planning/sessions/${sessionId}/messages`, {
    message: String(formData.get("message") || ""),
  });
  redirect("/intake");
}

async function confirmPlan(formData: FormData) {
  "use server";
  const sessionId = String(formData.get("session_id"));
  await apiPost(`/api/planning/sessions/${sessionId}/confirm`, {});
  redirect("/learning-plan");
}

export default async function IntakePage() {
  const state = await apiGet<PlanningState>("/api/planning/sessions/current");
  const session = state.session;
  const planPreview = session?.plan_preview ?? null;
  const latestAssistant = [...state.messages].reverse().find((message) => message.role === "assistant");
  const quickOptions = latestAssistant?.payload?.quick_options ?? [];
  const ready = session?.status === "ready_to_confirm" || session?.status === "confirmed";

  return (
    <main className="planner-cockpit" aria-label="Planning Agent">
      <section className="cockpit-hero">
        <div className="live-orb" aria-hidden="true">
          <BrainCircuit size={34} />
          <span />
        </div>
        <div>
          <span className="eyebrow">Planning Agent</span>
          <h1>先问清楚，再给你安排路线</h1>
          <p>
            这里不是测评问卷。AI 教练会像面试一样追问目标、背景、时间和作品方向，
            然后生成一条能落到项目和求职证据上的学习路线。
          </p>
        </div>
      </section>

      <section className="planner-grid">
        <aside className="cockpit-rail">
          <h2>我已经理解到</h2>
          <Memory label="目标" value={String(session?.intent?.primary_goal ?? state.intake.career_goal ?? "还没确认")} />
          <Memory label="目标岗位" value={state.intake.target_role} />
          <Memory label="每周时间" value={`${state.intake.weekly_hours} 小时`} />
          <Memory label="当前状态" value={session ? sessionStatus(session.status) : "等待开始"} />
        </aside>

        <section className="planning-room">
          <article className="agent-dialogue-card">
            <div className="agent-face">
              <Bot size={22} />
              <div>
                <span>AI 教练正在问</span>
                <strong>{ready ? "信息足够，可以生成路线" : "只问当前最关键的一件事"}</strong>
              </div>
            </div>

            {!session ? (
              <>
                <h2>你想通过 AI 能力换来什么结果？</h2>
                <p className="muted">可以直接说人话，比如：我想转行、想接单、想做企业自动化、想做一个能写进简历的 RAG 项目。</p>
                <form action={startPlanning} className="chat-composer">
                  <textarea
                    name="message"
                    rows={5}
                    defaultValue="我想转行做 AI Agent 工程师，每周能学 8 小时，希望做出能写进简历的 RAG 和自动化 Agent 项目。"
                    required
                  />
                  <button type="submit">
                    让 AI 教练开始判断 <SendHorizontal size={16} />
                  </button>
                </form>
              </>
            ) : (
              <>
                <div className="conversation">
                  {state.messages.slice(-5).map((message) => (
                    <article className={`chat-message ${message.role === "user" ? "learner" : "tutor"}`} key={message.id}>
                      <strong>{message.role === "user" ? "你" : "Planning Agent"}</strong>
                      <p>{humanizeText(message.content)}</p>
                    </article>
                  ))}
                </div>

                {ready ? (
                  <form action={confirmPlan} className="chat-composer">
                    <input type="hidden" name="session_id" value={session.id} />
                    <button type="submit">
                      确认这条路线 <ArrowRight size={16} />
                    </button>
                  </form>
                ) : (
                  <form action={sendPlanningMessage} className="chat-composer">
                    <input type="hidden" name="session_id" value={session.id} />
                    <textarea name="message" rows={4} placeholder="直接回答 AI 教练这一轮的问题" required />
                    <button type="submit">
                      继续回答 <SendHorizontal size={16} />
                    </button>
                  </form>
                )}

                {quickOptions.length ? (
                  <div className="quick-replies">
                    {quickOptions.map((option) => (
                      <form action={sendPlanningMessage} key={option}>
                        <input type="hidden" name="session_id" value={session.id} />
                        <input type="hidden" name="message" value={option} />
                        <button className="button secondary" type="submit">{option}</button>
                      </form>
                    ))}
                  </div>
                ) : null}
              </>
            )}
          </article>
        </section>

        <aside className="coach-presence">
          <div className="agent-card">
            <div className="agent-face">
              <CheckCircle2 size={22} />
              <div>
                <span>路线会包含</span>
                <strong>课程、项目、证据</strong>
              </div>
            </div>
            {planPreview && ready ? (
              <div className="reason-list">
                <div className="reason-item">
                  <strong>{planPreview.target_role}</strong>
                  <p>{humanizeText(planPreview.summary)}</p>
                </div>
                {planPreview.weeks.slice(0, 3).map((week) => (
                  <div className="reason-item" key={week.week}>
                    <strong>第 {week.week} 周：{week.focus}</strong>
                    <p>{week.outcome}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">AI 教练会先问清楚再生成路线。信息不足时，不会假装给你完整答案。</p>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

function Memory({ label, value }: { label: string; value: string }) {
  return (
    <div className="memory-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function sessionStatus(status: string) {
  const labels: Record<string, string> = {
    started: "刚开始",
    clarifying: "正在澄清",
    ready_to_confirm: "可以确认",
    confirmed: "已确认",
  };
  return labels[status] ?? status;
}
