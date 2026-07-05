CREATE TABLE IF NOT EXISTS target_jobs (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  description TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT,
  role TEXT NOT NULL DEFAULT 'learner',
  selected_target_job_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (selected_target_job_id) REFERENCES target_jobs(id)
);

CREATE TABLE IF NOT EXISTS intake_assessments (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL UNIQUE,
  target_role TEXT NOT NULL,
  weekly_hours INTEGER NOT NULL,
  programming_level INTEGER NOT NULL,
  prompt_level INTEGER NOT NULL,
  rag_level INTEGER NOT NULL,
  tool_use_level INTEGER NOT NULL,
  deployment_level INTEGER NOT NULL,
  career_goal TEXT NOT NULL,
  constraints TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS learning_plans (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL UNIQUE,
  target_role TEXT NOT NULL,
  current_level TEXT NOT NULL,
  estimated_weeks INTEGER NOT NULL,
  summary TEXT NOT NULL,
  plan_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS planning_sessions (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  status TEXT NOT NULL,
  intent_json TEXT NOT NULL,
  context_json TEXT NOT NULL,
  plan_preview_json TEXT,
  missing_slot TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  confirmed_at TEXT,
  FOREIGN KEY (learner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS planning_messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  payload_json TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (session_id) REFERENCES planning_sessions(id)
);

CREATE TABLE IF NOT EXISTS planning_agent_runs (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  agent_name TEXT NOT NULL,
  input_json TEXT NOT NULL,
  output_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (session_id) REFERENCES planning_sessions(id)
);

CREATE TABLE IF NOT EXISTS agent_traces (
  id TEXT PRIMARY KEY,
  agent_run_id TEXT,
  learner_id TEXT NOT NULL,
  agent_name TEXT NOT NULL,
  runtime TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT,
  tool_names_json TEXT NOT NULL DEFAULT '[]',
  input_json TEXT NOT NULL,
  output_json TEXT NOT NULL,
  status TEXT NOT NULL,
  latency_ms INTEGER,
  parent_type TEXT,
  parent_id TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (agent_run_id) REFERENCES agent_runs(id),
  FOREIGN KEY (learner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS skill_nodes (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT,
  category TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_skill_requirements (
  id TEXT PRIMARY KEY,
  target_job_id TEXT NOT NULL,
  skill_node_id TEXT NOT NULL,
  required_level INTEGER NOT NULL,
  weight REAL NOT NULL DEFAULT 1,
  evidence_expectation TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (target_job_id) REFERENCES target_jobs(id),
  FOREIGN KEY (skill_node_id) REFERENCES skill_nodes(id)
);

CREATE TABLE IF NOT EXISTS project_templates (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  description TEXT,
  target_job_id TEXT,
  level TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY (target_job_id) REFERENCES target_jobs(id)
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  project_template_id TEXT NOT NULL,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  sort_order INTEGER NOT NULL,
  required_submission_types TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (project_template_id) REFERENCES project_templates(id)
);

CREATE TABLE IF NOT EXISTS course_modules (
  id TEXT PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL,
  skill_node_id TEXT,
  difficulty TEXT NOT NULL,
  estimated_minutes INTEGER NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 100,
  created_at TEXT NOT NULL,
  FOREIGN KEY (skill_node_id) REFERENCES skill_nodes(id)
);

CREATE TABLE IF NOT EXISTS course_lessons (
  id TEXT PRIMARY KEY,
  course_module_id TEXT NOT NULL,
  title TEXT NOT NULL,
  content_type TEXT NOT NULL,
  content_ref TEXT,
  body TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 100,
  created_at TEXT NOT NULL,
  FOREIGN KEY (course_module_id) REFERENCES course_modules(id)
);

CREATE TABLE IF NOT EXISTS task_course_modules (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  course_module_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 100,
  created_at TEXT NOT NULL,
  UNIQUE (task_id, course_module_id),
  FOREIGN KEY (task_id) REFERENCES tasks(id),
  FOREIGN KEY (course_module_id) REFERENCES course_modules(id)
);

CREATE TABLE IF NOT EXISTS course_progress (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  course_module_id TEXT NOT NULL,
  status TEXT NOT NULL,
  completed_at TEXT,
  updated_at TEXT NOT NULL,
  UNIQUE (learner_id, course_module_id),
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (course_module_id) REFERENCES course_modules(id)
);

CREATE TABLE IF NOT EXISTS course_exercises (
  id TEXT PRIMARY KEY,
  course_module_id TEXT NOT NULL,
  prompt TEXT NOT NULL,
  expected_keywords TEXT NOT NULL DEFAULT '[]',
  rubric_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  FOREIGN KEY (course_module_id) REFERENCES course_modules(id)
);

CREATE TABLE IF NOT EXISTS course_exercise_attempts (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  course_exercise_id TEXT NOT NULL,
  answer TEXT NOT NULL,
  score INTEGER NOT NULL,
  feedback TEXT NOT NULL,
  next_action TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (course_exercise_id) REFERENCES course_exercises(id)
);

CREATE TABLE IF NOT EXISTS learner_projects (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  project_template_id TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT,
  completed_at TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (project_template_id) REFERENCES project_templates(id)
);

CREATE TABLE IF NOT EXISTS tutor_sessions (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  learner_project_id TEXT NOT NULL,
  task_id TEXT,
  status TEXT NOT NULL,
  ai_dependency_score INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (learner_project_id) REFERENCES learner_projects(id),
  FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS tutor_messages (
  id TEXT PRIMARY KEY,
  tutor_session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  hint_level INTEGER,
  learning_signal TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (tutor_session_id) REFERENCES tutor_sessions(id)
);

CREATE TABLE IF NOT EXISTS tutor_agent_runs (
  id TEXT PRIMARY KEY,
  tutor_session_id TEXT NOT NULL,
  agent_name TEXT NOT NULL,
  input_json TEXT NOT NULL,
  output_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (tutor_session_id) REFERENCES tutor_sessions(id)
);

CREATE TABLE IF NOT EXISTS submissions (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  learner_project_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL,
  github_repo_url TEXT,
  demo_url TEXT,
  readme_url TEXT,
  architecture_doc_url TEXT,
  evaluation_report_url TEXT,
  source_repo_path TEXT,
  sandbox_command TEXT,
  reflection_text TEXT,
  latest_review_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (learner_project_id) REFERENCES learner_projects(id),
  FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS review_jobs (
  id TEXT PRIMARY KEY,
  submission_id TEXT NOT NULL,
  status TEXT NOT NULL,
  mode TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 100,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  created_at TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  review_id TEXT,
  FOREIGN KEY (submission_id) REFERENCES submissions(id)
);

CREATE TABLE IF NOT EXISTS agent_runs (
  id TEXT PRIMARY KEY,
  review_job_id TEXT,
  learner_id TEXT,
  agent_name TEXT,
  runtime TEXT,
  provider TEXT NOT NULL,
  model TEXT,
  mode TEXT NOT NULL,
  prompt_version TEXT,
  parent_type TEXT,
  parent_id TEXT,
  tool_names_json TEXT NOT NULL DEFAULT '[]',
  input_json TEXT,
  output_json TEXT,
  input_ref TEXT,
  output_ref TEXT,
  token_usage TEXT,
  cost_usd REAL,
  latency_ms INTEGER,
  status TEXT NOT NULL,
  error TEXT,
  created_at TEXT NOT NULL,
  finished_at TEXT,
  FOREIGN KEY (review_job_id) REFERENCES review_jobs(id),
  FOREIGN KEY (learner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS sandbox_runs (
  id TEXT PRIMARY KEY,
  review_job_id TEXT,
  submission_id TEXT NOT NULL,
  status TEXT NOT NULL,
  image TEXT,
  command TEXT,
  stdout_ref TEXT,
  stderr_ref TEXT,
  exit_code INTEGER,
  duration_ms INTEGER,
  created_at TEXT NOT NULL,
  finished_at TEXT,
  FOREIGN KEY (review_job_id) REFERENCES review_jobs(id),
  FOREIGN KEY (submission_id) REFERENCES submissions(id)
);

CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY,
  review_job_id TEXT NOT NULL,
  submission_id TEXT NOT NULL,
  reviewer_type TEXT NOT NULL,
  overall_score INTEGER NOT NULL,
  hiring_readiness TEXT NOT NULL,
  confidence REAL NOT NULL,
  summary TEXT,
  next_action TEXT NOT NULL,
  raw_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (review_job_id) REFERENCES review_jobs(id),
  FOREIGN KEY (submission_id) REFERENCES submissions(id)
);

CREATE TABLE IF NOT EXISTS coach_tasks (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  learner_project_id TEXT,
  review_id TEXT,
  source_type TEXT NOT NULL,
  title TEXT NOT NULL,
  reason TEXT NOT NULL,
  action_json TEXT NOT NULL,
  status TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 100,
  created_at TEXT NOT NULL,
  completed_at TEXT,
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (learner_project_id) REFERENCES learner_projects(id),
  FOREIGN KEY (review_id) REFERENCES reviews(id)
);

CREATE TABLE IF NOT EXISTS review_scores (
  id TEXT PRIMARY KEY,
  review_id TEXT NOT NULL,
  rubric_item_key TEXT NOT NULL,
  score INTEGER NOT NULL,
  max_score INTEGER NOT NULL DEFAULT 100,
  reason TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (review_id) REFERENCES reviews(id)
);

CREATE TABLE IF NOT EXISTS review_risk_flags (
  id TEXT PRIMARY KEY,
  review_id TEXT NOT NULL,
  type TEXT NOT NULL,
  severity TEXT NOT NULL,
  description TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (review_id) REFERENCES reviews(id)
);

CREATE TABLE IF NOT EXISTS evidence_items (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  project_template_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  submission_id TEXT NOT NULL,
  review_id TEXT NOT NULL,
  skill_node_id TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_url TEXT,
  score INTEGER NOT NULL,
  confidence REAL NOT NULL,
  evidence_text TEXT NOT NULL,
  risk_flags TEXT NOT NULL DEFAULT '[]',
  reviewer_type TEXT NOT NULL,
  is_verified INTEGER NOT NULL DEFAULT 0,
  is_passport_eligible INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (project_template_id) REFERENCES project_templates(id),
  FOREIGN KEY (task_id) REFERENCES tasks(id),
  FOREIGN KEY (submission_id) REFERENCES submissions(id),
  FOREIGN KEY (review_id) REFERENCES reviews(id),
  FOREIGN KEY (skill_node_id) REFERENCES skill_nodes(id)
);

CREATE TABLE IF NOT EXISTS learner_skill_scores (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  skill_node_id TEXT NOT NULL,
  score INTEGER NOT NULL,
  confidence REAL NOT NULL,
  evidence_count INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL,
  UNIQUE (learner_id, skill_node_id),
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (skill_node_id) REFERENCES skill_nodes(id)
);

CREATE TABLE IF NOT EXISTS skill_score_history (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  skill_node_id TEXT NOT NULL,
  evidence_item_id TEXT NOT NULL,
  previous_score INTEGER,
  new_score INTEGER NOT NULL,
  score_delta INTEGER NOT NULL,
  reason TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (skill_node_id) REFERENCES skill_nodes(id),
  FOREIGN KEY (evidence_item_id) REFERENCES evidence_items(id)
);

CREATE TABLE IF NOT EXISTS hiring_passports (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  visibility TEXT NOT NULL DEFAULT 'private',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS passport_snapshots (
  id TEXT PRIMARY KEY,
  hiring_passport_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  status TEXT NOT NULL,
  snapshot_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  published_at TEXT,
  UNIQUE (hiring_passport_id, version),
  FOREIGN KEY (hiring_passport_id) REFERENCES hiring_passports(id)
);

CREATE TABLE IF NOT EXISTS portfolio_exports (
  id TEXT PRIMARY KEY,
  learner_id TEXT NOT NULL,
  submission_id TEXT NOT NULL,
  export_type TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (learner_id) REFERENCES users(id),
  FOREIGN KEY (submission_id) REFERENCES submissions(id)
);
