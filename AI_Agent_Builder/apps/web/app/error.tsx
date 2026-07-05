"use client";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <section className="panel">
      <span className="badge">错误</span>
      <h1>页面加载失败</h1>
      <p className="error">{error.message}</p>
      <button type="button" onClick={reset}>
        重试
      </button>
    </section>
  );
}
