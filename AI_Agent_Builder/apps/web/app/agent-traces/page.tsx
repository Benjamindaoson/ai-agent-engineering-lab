import { Activity, Bot, Cpu, Workflow } from "lucide-react";
import { apiGet, type AgentTrace } from "@/lib/api";

export default async function AgentTracesPage() {
  const data = await apiGet<{ agent_traces: AgentTrace[] }>("/api/agent-traces/me");
  const traces = data.agent_traces;
  const claudeCount = traces.filter((trace) => trace.runtime === "claude_agent_sdk").length;
  const ruleCount = traces.filter((trace) => trace.runtime === "rule").length;
  const mockCount = traces.filter((trace) => trace.runtime === "mock").length;

  return (
    <>
      <header className="page-header">
        <div>
          <span className="badge">Agent Kernel</span>
          <h1 className="page-title">Agent 运行轨迹</h1>
          <p className="subtitle">
            这里展示 Planner、Tutor、Reviewer 的统一运行记录。现在本地默认使用规则/Mock runtime；
            切换 Claude 配置后，Reviewer 会以 Claude Agent SDK runtime 写入同一张 trace 表。
          </p>
        </div>
      </header>

      <section className="stat-grid compact">
        <div className="stat">
          <span>Total Agent Runs</span>
          <strong>{traces.length}</strong>
        </div>
        <div className="stat">
          <span>Rule Runtime</span>
          <strong>{ruleCount}</strong>
        </div>
        <div className="stat">
          <span>Claude SDK</span>
          <strong>{claudeCount}</strong>
        </div>
        <div className="stat">
          <span>Mock Review</span>
          <strong>{mockCount}</strong>
        </div>
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Runtime Trace</p>
            <h2><Activity size={18} /> 统一 Agent Trace</h2>
          </div>
        </div>

        {traces.length === 0 ? (
          <p className="muted">还没有 Agent 运行记录。先完成一次规划、Tutor 求助或项目评审。</p>
        ) : (
          <div className="list">
            {traces.map((trace) => (
              <article className="row" key={trace.id}>
                <div>
                  <span className="badge">{runtimeLabel(trace.runtime)}</span>
                  <p className="row-title">{trace.agent_name}</p>
                  <p className="row-meta">
                    Provider: {trace.provider}
                    {trace.model ? ` / Model: ${trace.model}` : ""} / Status: {trace.status}
                  </p>
                  <div className="toolbar" style={{ marginTop: 8 }}>
                    {trace.tool_names.map((tool) => (
                      <span className="badge badge-amber" key={tool}>{tool}</span>
                    ))}
                  </div>
                </div>
                <div className="metric-card">
                  {trace.runtime === "claude_agent_sdk" ? <Bot size={18} /> : trace.runtime === "mock" ? <Cpu size={18} /> : <Workflow size={18} />}
                  <span>{trace.parent_type ?? "agent_run"}</span>
                  <strong>{trace.latency_ms ?? 0}ms</strong>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}

function runtimeLabel(runtime: string) {
  if (runtime === "claude_agent_sdk") return "Claude Agent SDK";
  if (runtime === "mock") return "Mock Runtime";
  return "Rule Runtime";
}
