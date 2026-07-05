export function humanizeText(value: string | null | undefined) {
  return String(value ?? "")
    .replaceAll("Agent Command Queue", "AI 教练给你的下一步")
    .replaceAll("Review Agent", "作品检查员")
    .replaceAll("ReviewAgent", "作品检查员")
    .replaceAll("Agent Review", "AI 检查")
    .replaceAll("Quality Gate", "项目检查")
    .replaceAll("Review Gate", "项目检查")
    .replaceAll("质量门", "项目检查")
    .replaceAll("Evidence Store", "能力证据库")
    .replaceAll("Skill Passport", "求职能力报告")
    .replaceAll("Passport Version", "报告版本")
    .replaceAll("Evidence Items", "能力证据")
    .replaceAll("Independence Risk", "独立完成风险")
    .replaceAll("Process Evidence", "学习过程证据")
    .replaceAll("Skill Graph", "能力画像")
    .replaceAll("AI Dependency Score", "AI 代做风险分")
    .replaceAll("AI Dependency", "AI 代做风险")
    .replaceAll("Sandbox", "运行检查")
    .replaceAll("Project Lab", "项目画布")
    .replaceAll("MicroExerciseCoach", "小课教练")
    .replaceAll("Agent Tutor", "AI 项目教练")
    .replaceAll("Agent Trace", "学习过程记录")
    .replaceAll("Trace", "过程记录")
    .replaceAll("trace", "过程记录")
    .replaceAll("Agent 决策", "AI 教练判断")
    .replaceAll("course_progress", "课程进度")
    .replaceAll("rag_retrieval_quality", "检索质量")
    .replaceAll("engineering_quality", "工程质量")
    .replaceAll("missing_eval", "缺少评估")
    .replaceAll("submitted", "已提交")
    .replaceAll("unlisted", "未公开")
    .replaceAll("Rubric", "评分标准");
}

export function statusText(status: string | null | undefined) {
  const labels: Record<string, string> = {
    queued: "等待中",
    running: "进行中",
    succeeded: "已完成",
    failed: "失败",
    cancelled: "已取消",
    not_started: "还没开始",
    active: "进行中",
    done: "已完成",
    waiting: "等待中",
    review_completed: "检查完成",
    needs_revision: "需要修改",
    passed: "已通过",
    ai_reviewing: "AI 正在检查",
    completed: "已完成",
    in_progress: "进行中",
  };
  return labels[String(status ?? "")] ?? humanizeText(status);
}

export function submissionText(type: string) {
  const labels: Record<string, string> = {
    github_repo_url: "代码仓库",
    demo_url: "在线演示",
    readme_url: "项目说明",
    architecture_doc_url: "架构说明",
    evaluation_report_url: "测试和评估记录",
    reflection_text: "项目复盘",
  };
  return labels[type] ?? humanizeText(type);
}
