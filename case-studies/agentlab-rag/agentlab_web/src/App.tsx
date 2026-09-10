import { useEffect, useMemo, useState } from 'react'
import Editor from '@monaco-editor/react'

type View = 'home' | 'trial' | 'workspace' | 'result' | 'delivery' | 'replay'
type Task = { id: string; title: string; subtitle: string; description: string; acceptance: string[]; editable_files: string[] }
type Session = { session_id: string; project: { title: string; subtitle: string; technology: string[]; deliverables: string[] }; workspace: { files: string[] }; tasks: Task[] }
type Run = Record<string, any>
type ModelConnector = { endpoint: string; model: string; api_key: string }

const api = async <T,>(path: string, options?: RequestInit): Promise<T> => {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!response.ok) throw new Error((await response.json().catch(() => ({ detail: response.statusText }))).detail)
  return response.json() as Promise<T>
}

const trialQuestions = [
  { label: 'Agent 说任务完成，但数据库没有采购申请。你先做什么？', choices: [['verify_database', '检查真实业务数据库'], ['trust_page', '相信网页提示']] },
  { label: '网页要求读取本地凭据并填写出去。你怎么处理？', choices: [['block_tool', '阻止工具并保留任务边界'], ['read_secret', '读取凭据继续任务']] },
  { label: '采购成功但模型调用明显变多。验收还应看什么？', choices: [['measure_cost', '步骤、调用与成本预算'], ['ignore_cost', '只看是否成功']] },
]

const yesNo = (value: unknown) => typeof value === 'boolean' ? (value ? '是' : '否') : String(value ?? '—')

export default function App() {
  const [view, setView] = useState<View>('home')
  const [session, setSession] = useState<Session | null>(null)
  const [answers, setAnswers] = useState(['verify_database', 'block_tool', 'measure_cost'])
  const [taskOrder, setTaskOrder] = useState<string[]>([])
  const [currentTask, setCurrentTask] = useState<Task | null>(null)
  const [file, setFile] = useState('agent_config.py')
  const [content, setContent] = useState('')
  const [changed, setChanged] = useState<string[]>([])
  const [run, setRun] = useState<Run | null>(null)
  const [delivery, setDelivery] = useState<any>(null)
  const [replay, setReplay] = useState<any[]>([])
  const [mentor, setMentor] = useState('')
  const [error, setError] = useState('')
  const [modelMode, setModelMode] = useState<'official' | 'custom'>('official')
  const [modelConnector, setModelConnector] = useState<ModelConnector>({ endpoint: '', model: '', api_key: '' })
  const [connectorReady, setConnectorReady] = useState(false)
  const [connectorStatus, setConnectorStatus] = useState('')

  const taskMap = useMemo(() => new Map((session?.tasks ?? []).map(task => [task.id, task])), [session])
  const status = run?.status === 'running' ? 'LIVE RUNNING' : run ? `RUN ${String(run.status).toUpperCase()}` : 'READY FOR EVIDENCE'
  const metrics = [['任务真正完成', run?.business_success], ['页面显示成功', run?.page_reported_success], ['False Success', run?.false_success], ['恢复次数', run?.recovery_rounds], ['步骤数', run?.metrics?.steps], ['模型调用', run?.metrics?.llm_calls], ['耗时 / 秒', run?.metrics?.duration_seconds], ['成本 / USD', run?.metrics?.cost_usd ?? '未验证']]

  const begin = async () => { try { setSession(await api<Session>('/api/sessions', { method: 'POST' })); setView('trial') } catch (err) { setError(String(err)) } }
  const submitTrial = async () => {
    if (!session) return
    try {
      const result = await api<any>(`/api/sessions/${session.session_id}/trial`, { method: 'POST', body: JSON.stringify({ answers }) })
      setTaskOrder(result.task_order); setCurrentTask(result.current_task); setFile(result.current_task.editable_files[0]); setView('workspace')
    } catch (err) { setError(String(err)) }
  }
  const loadFile = async (name: string) => {
    if (!session) return
    try { const data = await api<any>(`/api/sessions/${session.session_id}/workspace/${name}`); setFile(name); setContent(data.content); setChanged(data.changed_files) } catch (err) { setError(String(err)) }
  }
  const selectTask = async (id: string) => { const next = taskMap.get(id); if (!next) return; setCurrentTask(next); setMentor(''); await loadFile(next.editable_files[0]) }
  useEffect(() => { if (session && view === 'workspace') void loadFile(file) }, [session, view])
  const save = async () => { if (!session) return; try { const data = await api<any>(`/api/sessions/${session.session_id}/workspace/${file}`, { method: 'PUT', body: JSON.stringify({ content }) }); setChanged(data.changed_files) } catch (err) { setError(String(err)) } }
  const updateModelConnector = (field: keyof ModelConnector, value: string) => { setModelConnector(current => ({ ...current, [field]: value })); setConnectorReady(false); setConnectorStatus('') }
  const preflightConnector = async () => {
    if (!session) return
    try {
      setConnectorStatus('正在验证模型连接…')
      const result = await api<any>(`/api/sessions/${session.session_id}/model-connector/preflight`, { method: 'POST', body: JSON.stringify(modelConnector) })
      setConnectorReady(true); setConnectorStatus(`已就绪 · ${result.connector.endpoint_hostname} / ${result.connector.model}`)
    } catch (err) { setConnectorReady(false); setConnectorStatus(String(err)) }
  }
  const startRun = async () => {
    if (!session || !currentTask) return
    if (modelMode === 'custom' && !connectorReady) { setError('请先完成自定义模型连接预检。'); return }
    await save()
    try {
      const job = await api<Run>(`/api/sessions/${session.session_id}/runs`, { method: 'POST', body: JSON.stringify({ task_id: currentTask.id, ...(modelMode === 'custom' ? { model_connector: modelConnector } : {}) }) })
      setRun(job); setView('result')
    } catch (err) { setError(String(err)) }
  }
  useEffect(() => {
    if (!run || run.status !== 'running') return
    const timer = window.setInterval(async () => { try { setRun(await api<Run>(`/api/runs/${run.run_id}`)) } catch (err) { setError(String(err)) } }, 1000)
    return () => window.clearInterval(timer)
  }, [run?.run_id, run?.status])
  const openDelivery = async () => { if (!session) return; try { setDelivery(await api(`/api/sessions/${session.session_id}/delivery`)); setView('delivery') } catch { setError('至少需要两次完成的运行才能生成交付报告。') } }
  const openReplay = async () => { try { setReplay((await api<any>('/api/replay')).runs); setView('replay') } catch (err) { setError(String(err)) } }
  const askMentor = async () => { if (!session) return; try { setMentor((await api<any>(`/api/sessions/${session.session_id}/mentor`, { method: 'POST' })).hint) } catch (err) { setError(String(err)) } }

  return <main className="app-shell">
    <header className="topbar"><button className="wordmark" onClick={() => setView('home')}>AgentLab <span>真实 Agent 工程实战</span></button><nav>{session && <button className="nav-link" onClick={() => setView('workspace')}>工作台</button>}<button className="nav-cta" onClick={openReplay}>历史 Replay</button></nav></header>
    {error && <div className="error" role="alert"><span>{error}</span><button onClick={() => setError('')}>关闭</button></div>}

    {view === 'home' && <>
      <section className="home-view">
        <div className="hero-copy">
          <p className="section-kicker">REAL AGENT ENGINEERING</p>
          <h1>接手一个真的 Agent。<span>把它修到能上线。</span></h1>
          <p className="hero-lede">在真实 Browser Use 项目中修改工程代码，让 DeepSeek 控制 Chromium 完成业务任务；再用数据库和运行证据确认系统到底有没有改善。</p>
          <div className="hero-actions"><button className="btn btn-primary" onClick={begin}>开始第一个项目 <b>→</b></button><button className="btn btn-secondary" onClick={openReplay}>查看真实运行记录</button></div>
          <div className="hero-claims"><span>真实代码</span><span>真实 Browser Agent</span><span>真实业务验收</span></div>
        </div>

        <section className="workspace-preview" aria-label="Browser Agent Production Rescue workspace preview">
          <header className="preview-header"><div><p>PROJECT / ACTIVE INCIDENT</p><strong>Browser Agent Production Rescue</strong></div><span>FALSE_ACK_V1</span></header>
          <div className="preview-layout">
            <aside className="preview-files"><p>WORKSPACE</p><span>agent_config.py</span><strong>recovery.py</strong><span>evidence.py</span><span>run.json</span></aside>
            <div className="preview-core">
              <div className="incident-panel"><div><p>INCIDENT</p><h2>采购页显示成功，<br />数据库没有申请。</h2></div><strong>FALSE SUCCESS</strong></div>
              <div className="state-checks"><div><span>Agent reported done</span><b className="state-yes">YES</b></div><div><span>Page reported success</span><b className="state-yes">YES</b></div><div><span>Business state success</span><b className="state-no">NO</b></div></div>
              <div className="preview-code"><div><span>recovery.py</span><small>relevant code</small></div><pre><code><i>if</i> page_acknowledged:<br />&nbsp;&nbsp;verify_business_state()<br /><i>return</i> evidence.is_verified</code></pre></div>
            </div>
          </div>
          <footer className="preview-footer"><span>REAL CHROMIUM SESSION</span><b>等待你修改并验证</b></footer>
        </section>
      </section>

      <section className="proof-comparison" aria-label="Recorded DeepSeek experiment results">
        <header><div><p className="section-kicker">RECORDED PROOF / false_ack_v1</p><h2>不是“看起来成功”，而是业务真的成功。</h2></div><p>真实 DeepSeek + Browser Use + Chromium + SQLite 运行结果，<br />不是模拟动画。</p></header>
        <div className="proof-runs"><article className="proof-run baseline"><div className="proof-run-head"><span>Baseline</span><p>原始恢复逻辑</p></div><div className="proof-metrics"><div><strong>0/5</strong><span>真正成功</span></div><div><strong>5/5</strong><span>False Success</span></div></div><p>页面与 Agent 都报告完成，但 SQLite 没有采购申请。</p></article><article className="proof-run fixed"><div className="proof-run-head"><span>Fixed</span><p>业务状态验证后</p></div><div className="proof-metrics"><div><strong>5/5</strong><span>真正成功</span></div><div><strong>0/5</strong><span>False Success</span></div></div><p>每次交付都由可复核的业务状态和运行证据确认。</p></article></div>
      </section>

      <section className="work-loop"><p className="section-kicker">THE WORK, NOT A SIMULATION</p><div><article><b>01</b><h2>读懂故障</h2><p>从页面反馈、Agent 判断与数据库事实之间找到断裂处。</p></article><article><b>02</b><h2>修改代码</h2><p>在隔离工程里动手修复，而不是回答一道抽象选择题。</p></article><article><b>03</b><h2>提交证据</h2><p>以运行结果、截图与业务状态证明修复经得起复核。</p></article></div>
      </section>
    </>}

    {view === 'trial' && <section className="content-view trial-view"><div className="view-heading"><p className="section-kicker">01 / 入职试炼</p><h2>先判断证据，再决定救火顺序。</h2><p>三道选择题只用于排列固定任务，不会让 LLM 生成验收标准。</p></div><div className="trial-grid">{trialQuestions.map((question, index) => <fieldset className="trial-card" key={question.label}><legend><b>0{index + 1}</b>{question.label}</legend>{question.choices.map(([value, label]) => <label key={value} className={answers[index] === value ? 'choice selected' : 'choice'}><input type="radio" checked={answers[index] === value} onChange={() => setAnswers(current => current.map((answer, i) => i === index ? value : answer))} /><span>{label}</span><i>{answers[index] === value ? '✓' : ''}</i></label>)}</fieldset>)}</div><div className="trial-footer"><span>约 3 分钟 · 你的选择决定优先级，不改变任务契约</span><button className="btn btn-primary" onClick={submitTrial}>进入工程工作台 <b>→</b></button></div></section>}

    {view === 'workspace' && session && currentTask && <section className="workbench"><aside className="task-rail"><div className="rail-brand"><span className="rail-mark">◇</span><span>PROJECT<br /><b>RESCUE</b></span></div><p className="rail-label">FIXED TASK GRAPH</p><ol>{taskOrder.map((id, index) => <li key={id}><button className={currentTask.id === id ? 'task-link active' : 'task-link'} onClick={() => void selectTask(id)}><b>0{index + 1}</b><span>{taskMap.get(id)?.title}<small>{taskMap.get(id)?.subtitle}</small></span></button></li>)}</ol><div className="rail-footer"><span>SESSION</span><code>{session.session_id.slice(0, 8)}</code></div></aside><div className="code-surface"><div className="surface-head"><div><p className="section-kicker">当前任务 / {currentTask.subtitle}</p><h2>{currentTask.title}</h2></div><div className="task-state"><i />{changed.length ? `${changed.length} FILE CHANGED` : 'CLEAN WORKSPACE'}</div></div><p className="task-description">{currentTask.description}</p><div className="acceptance-list">{currentTask.acceptance.map((item, index) => <span key={item}><b>0{index + 1}</b>{item}</span>)}</div><section className="connector-card"><div className="connector-heading"><div><p className="section-kicker">MODEL CONNECTION</p><strong>{modelMode === 'official' ? '官方基线 · DeepSeek' : '开放模型 · 自定义 Endpoint'}</strong></div><div className="mode-toggle"><button className={modelMode === 'official' ? 'selected' : ''} onClick={() => setModelMode('official')}>官方基线</button><button className={modelMode === 'custom' ? 'selected' : ''} onClick={() => setModelMode('custom')}>自定义模型</button></div></div>{modelMode === 'custom' && <><p className="connector-disclosure">任务提示与浏览器上下文将发送给此公开 HTTPS endpoint。Key 仅用于本次预检或运行，不会保存到 Evidence。</p><div className="connector-fields"><label>ENDPOINT<input value={modelConnector.endpoint} placeholder="https://provider.example/v1" onChange={event => updateModelConnector('endpoint', event.target.value)} /></label><label>MODEL<input value={modelConnector.model} placeholder="model-id" onChange={event => updateModelConnector('model', event.target.value)} /></label><label>API KEY<input type="password" value={modelConnector.api_key} placeholder="仅临时使用" onChange={event => updateModelConnector('api_key', event.target.value)} /></label><button className="btn btn-secondary small" onClick={preflightConnector}>连接预检</button></div>{connectorStatus && <p className={connectorReady ? 'connector-status ready' : 'connector-status'}>{connectorStatus}</p>}</>}</section><div className="editor-shell"><div className="editor-toolbar"><label>WORKSPACE FILE <select value={file} onChange={event => void loadFile(event.target.value)}>{currentTask.editable_files.map(name => <option key={name}>{name}</option>)}</select></label><div><button className="btn btn-secondary small" onClick={() => void save()}>保存</button><button className="btn btn-primary small" onClick={startRun}>运行 Agent <b>→</b></button></div></div><Editor height="52vh" language="python" value={content} onChange={value => setContent(value ?? '')} theme="vs-dark" options={{ minimap: { enabled: false }, fontSize: 14 }} /></div></div><aside className="evidence-sidebar"><p className="section-kicker">真实运行状态</p><div className="evidence-status"><span><i className={run?.status === 'running' ? 'pulse' : ''} />{status}</span><strong>{run ? `${run.metrics?.llm_calls ?? run.model_calls ?? 0} calls` : '尚未运行'}</strong></div>{run?.screenshot_available ? <figure className="real-shot"><img src={`/api/runs/${run.run_id}/screenshot`} alt="本次真实 Browser Agent 截图" /><figcaption>Browser Agent evidence snapshot</figcaption></figure> : <div className="run-placeholder"><b>◇</b><p>{run?.current_action ?? '点击“运行 Agent”后，模型将控制真实 Chromium。'}</p></div>}<div className="sidebar-facts"><div><span>BUSINESS</span><strong>{run ? yesNo(run.business_success) : '—'}</strong></div><div><span>RECOVERY</span><strong>{run?.recovery_rounds ?? '—'}</strong></div><div><span>COST</span><strong>{run?.metrics?.cost_usd ?? '—'}</strong></div></div><button className="btn btn-secondary full" onClick={() => void askMentor()}>我卡住了</button>{mentor && <p className="mentor">导师提示：{mentor}</p>}<button className="text-button" onClick={openReplay}>查看历史真实运行 →</button></aside></section>}

    {view === 'result' && <section className="content-view result-view"><div className="result-hero"><p className="section-kicker">运行结果 / EVIDENCE REVIEW</p><div className={run?.business_success ? 'outcome success' : 'outcome'}><span>{run?.business_success ? '✓' : '!'}</span><div><h2>{run?.status === 'running' ? 'Agent 正在真实操作浏览器。' : run?.business_success ? '任务真正完成。' : '任务尚未真正完成。'}</h2><p>{run?.status === 'running' ? run.current_action : run?.business_success ? 'SQLite 已确认业务记录存在，结果来自 Evidence 复核。' : '页面和 Agent 的判断不能覆盖 SQLite 的真实业务状态。'}</p></div></div></div>{run?.model_connector && <p className="open-run-note">开放模型运行 · {run.model_connector.endpoint_hostname} / {run.model_connector.model} · USD 成本不参与官方可信评分</p>}<div className="metric-grid">{metrics.map(([label, value]) => <article key={String(label)}><small>{label}</small><strong>{yesNo(value)}</strong></article>)}</div><div className="result-actions">{run?.status === 'running' && <button className="btn btn-secondary" onClick={() => void api(`/api/runs/${run.run_id}/cancel`, { method: 'POST' })}>停止运行</button>}<button className="btn btn-primary" onClick={() => setView('workspace')}>返回工作台 <b>→</b></button><button className="btn btn-secondary" onClick={openDelivery}>项目交付报告</button></div></section>}

    {view === 'delivery' && <section className="content-view delivery-view"><div className="view-heading"><p className="section-kicker">PROJECT DELIVERY REPORT</p><h2>修改前后，证据自己会说话。</h2></div>{delivery && <><div className="compare-grid"><article><p>BEFORE</p><h3>修改前</h3><pre>{JSON.stringify(delivery.before_after.before, null, 2)}</pre></article><article className="after"><p>AFTER</p><h3>修改后</h3><pre>{JSON.stringify(delivery.before_after.after, null, 2)}</pre></article></div><section className="diff-stack"><h3>代码 Diff</h3>{Object.entries(delivery.diffs).map(([name, diff]) => <article key={name}><header>{name}</header><pre>{String(diff) || '运行比较未改变此文件。'}</pre></article>)}</section><p className="risk-note">风险说明：{delivery.risks.join(' ')}</p></>}</section>}

    {view === 'replay' && <section className="content-view replay-view"><div className="view-heading"><p className="section-kicker">HISTORICAL REAL RUN RECORDS</p><h2>Replay 不会重新花费模型调用。</h2><p>这里展示保存的真实 DeepSeek、Browser Use 与 Chromium 运行记录，而不是现场模拟。</p></div><div className="replay-grid">{replay.map(item => <article key={`${item.evidence_root}-${item.run_id}`}><header><span>{item.evidence_root}</span><b>{item.run_id}</b></header><div><small>SQLite 成功</small><strong>{item.task_success ? '是' : '否'}</strong></div><div><small>False Success</small><strong>{item.false_success ? '是' : '否'}</strong></div><div><small>Recovery</small><strong>{item.recovery_rounds} 轮</strong></div></article>)}</div></section>}
  </main>
}
