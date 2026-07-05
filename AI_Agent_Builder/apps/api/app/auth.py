from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Header, HTTPException, status

from .config import settings
from .db import DbConnection, get_conn
from .utils import now_iso


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str
    display_name: str | None
    role: str = "learner"


def ensure_user(
    conn: DbConnection,
    *,
    user_id: str,
    email: str,
    display_name: str | None,
    role: str = "learner",
) -> AuthUser:
    now = now_iso()
    existing = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE users
            SET email = ?, display_name = COALESCE(?, display_name), updated_at = ?
            WHERE id = ?
            """,
            (email, display_name, now, user_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO users (id, email, display_name, role, selected_target_job_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, email, display_name, role, None, now, now),
        )
    return AuthUser(id=user_id, email=email, display_name=display_name, role=role)


def require_user(
    authorization: str | None = Header(default=None),
    x_agentlab_learner_id: str | None = Header(default=None),
    x_agentlab_user_email: str | None = Header(default=None),
    x_agentlab_user_name: str | None = Header(default=None),
) -> AuthUser:
    if settings.auth_mode == "supabase":
        user = _user_from_supabase_jwt(authorization)
    else:
        learner_id = x_agentlab_learner_id or settings.demo_learner_id
        email = x_agentlab_user_email or settings.demo_learner_email
        display_name = x_agentlab_user_name or settings.demo_learner_name
        user = AuthUser(id=learner_id, email=email, display_name=display_name)

    with get_conn() as conn:
        return ensure_user(
            conn,
            user_id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
        )


def _user_from_supabase_jwt(authorization: str | None) -> AuthUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization bearer token is required.",
        )
    token = authorization.split(" ", 1)[1].strip()
    claims = _decode_supabase_token(token)
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing sub claim.")
    email = claims.get("email") or f"{user_id}@supabase.local"
    metadata = claims.get("user_metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}
    display_name = metadata.get("full_name") or metadata.get("name") or email.split("@")[0]
    role = _role_from_claims(claims)
    return AuthUser(id=str(user_id), email=str(email), display_name=str(display_name), role=role)


def _decode_supabase_token(token: str) -> dict[str, Any]:
    audience = "authenticated"
    try:
        if settings.supabase_jwks_url:
            jwks_client = jwt.PyJWKClient(settings.supabase_jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience=audience,
                options={"verify_aud": True},
            )
        if not settings.supabase_jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_JWT_SECRET or SUPABASE_JWKS_URL is required when AUTH_MODE=supabase.",
            )
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience=audience,
            options={"verify_aud": True},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Supabase token.") from exc


def _role_from_claims(claims: dict[str, Any]) -> str:
    app_metadata = claims.get("app_metadata") or {}
    if isinstance(app_metadata, dict):
        role = app_metadata.get("agentlab_role") or app_metadata.get("role")
        if role in {"learner", "mentor", "admin"}:
            return str(role)
    return "learner"
