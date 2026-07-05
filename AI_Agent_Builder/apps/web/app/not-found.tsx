import Link from "next/link";

export default function NotFound() {
  return (
    <section className="panel">
      <span className="badge">404</span>
      <h1>页面不存在</h1>
      <p className="muted">你访问的 AgentLab 页面不存在。</p>
      <Link className="button" href="/">
        返回工作台
      </Link>
    </section>
  );
}
