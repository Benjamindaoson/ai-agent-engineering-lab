import { apiGet, apiPost, type Job } from "@/lib/api";
import { redirect } from "next/navigation";

async function selectJob(formData: FormData) {
  "use server";
  const targetJobId = String(formData.get("target_job_id"));
  await apiPost("/api/jobs/select", { target_job_id: targetJobId });
  redirect("/projects");
}

export default async function JobsPage() {
  const data = await apiGet<{ jobs: Job[] }>("/api/jobs");

  return (
    <section className="panel">
      <h1>选择目标岗位</h1>
      <p className="muted">系统会按目标岗位要求评估你的项目证据和能力图谱。</p>
      {data.jobs.length === 0 ? <p className="muted">暂时没有可选岗位。</p> : null}
      <form action={selectJob}>
        <div className="grid">
          {data.jobs.map((job) => (
            <label className="panel" key={job.id}>
              <span>
                <input name="target_job_id" type="radio" value={job.id} required /> {job.title}
              </span>
              <span className="muted">{job.description}</span>
            </label>
          ))}
        </div>
        <button type="submit">进入项目实战</button>
      </form>
    </section>
  );
}
