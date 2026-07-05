# AgentLab Supabase Setup

AgentLab supports two auth/data modes:

- Local development: `AUTH_MODE=dev`, SQLite, demo learner headers.
- Supabase production: `AUTH_MODE=supabase`, Supabase Auth JWT, Supabase Postgres via `DATABASE_URL`.

## Required Backend Environment

```env
AUTH_MODE=supabase
DATABASE_URL=postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_JWT_SECRET=<jwt-secret>
# or, when using asymmetric JWTs:
SUPABASE_JWKS_URL=https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json
ANTHROPIC_API_KEY=<anthropic-key>
AGENT_MODE=claude
SANDBOX_ALLOWED_ROOT=<absolute path containing allowed local submissions>
```

## Required Frontend Environment

```env
NEXT_PUBLIC_AUTH_MODE=supabase
NEXT_PUBLIC_API_URL=https://<api-host>
NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>
NEXT_PUBLIC_AGENT_REVIEW_MODE=claude
```

Do not put the Supabase service role key or database password in frontend env vars.

## Database Initialization

The backend initializes tables from `apps/api/app/schema.sql` on startup. For a new Supabase project:

1. Set backend `DATABASE_URL` to the Supabase Postgres connection string.
2. Start the API once or run `npm run seed`.
3. Confirm `/health` returns `{"status":"ok"}`.

The API enforces learner isolation using the Supabase JWT `sub` claim. Public passport pages remain accessible by slug.
