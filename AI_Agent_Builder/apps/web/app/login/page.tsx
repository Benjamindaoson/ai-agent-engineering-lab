import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase-server";

async function signIn(formData: FormData) {
  "use server";
  const supabase = await createSupabaseServerClient();
  if (!supabase) {
    redirect("/login?error=supabase_not_configured");
  }
  const email = String(formData.get("email") || "");
  const password = String(formData.get("password") || "");
  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) {
    redirect(`/login?error=${encodeURIComponent(error.message)}`);
  }
  redirect("/jobs");
}

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const params = await searchParams;
  const supabaseConfigured = Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY);
  const devMode = process.env.NEXT_PUBLIC_AUTH_MODE !== "supabase";

  return (
    <section className="panel">
      <h1>登录</h1>
      {devMode ? <p className="muted">当前是开发模式，系统会自动使用演示学员身份。</p> : null}
      {!supabaseConfigured ? <p className="error">尚未配置 Supabase URL 和 anon key。</p> : null}
      {params.error ? <p className="error">{params.error}</p> : null}
      <form action={signIn}>
        <label>
          邮箱
          <input name="email" type="email" required />
        </label>
        <label>
          密码
          <input name="password" type="password" required />
        </label>
        <button type="submit" disabled={!supabaseConfigured}>
          登录
        </button>
      </form>
    </section>
  );
}
