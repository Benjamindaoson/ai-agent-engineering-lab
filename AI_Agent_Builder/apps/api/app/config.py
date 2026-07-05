from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parents[3]
API_DIR = Path(__file__).resolve().parents[1]


class Settings:
    root_dir: Path = ROOT_DIR
    app_env: str = os.getenv("APP_ENV", "development")
    agent_mode: str = os.getenv("AGENT_MODE", "mock")
    planner_runtime: str = os.getenv("PLANNER_RUNTIME", "rule")
    tutor_runtime: str = os.getenv("TUTOR_RUNTIME", "rule")
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{API_DIR / 'agentlab.db'}")
    auth_mode: str = os.getenv("AUTH_MODE", "dev")
    supabase_url: str | None = os.getenv("SUPABASE_URL")
    supabase_jwt_secret: str | None = os.getenv("SUPABASE_JWT_SECRET")
    supabase_jwks_url: str | None = os.getenv("SUPABASE_JWKS_URL")
    demo_learner_id: str = os.getenv("DEMO_LEARNER_ID", "learner-demo")
    demo_learner_email: str = os.getenv("DEMO_LEARNER_EMAIL", "learner@example.com")
    demo_learner_name: str = os.getenv("DEMO_LEARNER_NAME", "Demo Learner")
    claude_model: str | None = os.getenv("CLAUDE_MODEL")
    claude_review_max_turns: int = int(os.getenv("CLAUDE_REVIEW_MAX_TURNS", "1"))
    sandbox_backend: str = os.getenv("SANDBOX_BACKEND", "local")
    sandbox_timeout_seconds: int = int(os.getenv("SANDBOX_TIMEOUT_SECONDS", "45"))
    sandbox_default_command: str = os.getenv("SANDBOX_DEFAULT_COMMAND", "python -m unittest discover -s tests -q")
    sandbox_allowed_root: Path = Path(os.getenv("SANDBOX_ALLOWED_ROOT", str(ROOT_DIR))).resolve()

    @property
    def database_path(self) -> Path:
        parsed = urlparse(self.database_url)
        if parsed.scheme and parsed.scheme != "sqlite":
            return API_DIR / "agentlab.db"
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.removeprefix("sqlite:///")).resolve()
        return Path(self.database_url).resolve()

    @property
    def database_driver(self) -> str:
        return "postgres" if self.database_url.startswith(("postgresql://", "postgres://")) else "sqlite"


settings = Settings()
