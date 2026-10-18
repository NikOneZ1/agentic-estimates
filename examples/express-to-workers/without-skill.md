## Short answer

For one experienced developer who knows the codebase, plan on **about 4–8 weeks**. Most likely it lands around **5–6 weeks**.

- **Best case: about 3 weeks.** This assumes you use an ORM or query builder that supports D1 (Drizzle, Kysely or Prisma), your Postgres usage is plain, and the tests mostly call over HTTP.
- **Worst case: 10+ weeks.** This applies if you write a lot of raw SQL that depends on Postgres features (JSONB, arrays, CTEs with locking, `SELECT ... FOR UPDATE`, triggers or functions, full-text search) or if your code relies on interactive transactions.

Two developers would shorten this by maybe 30–40%, not 50%. Schema and data work is hard to split.

The Express to Hono part is the easy part. **Postgres to D1 is where the time and risk are.** D1 is SQLite, so this is a database engine change, not just a driver swap.

## Where the effort goes

| Phase | Estimate | Notes |
|---|---|---|
| 1. Audit and spike | 2–4 days | List Postgres-specific SQL, Node-only dependencies and middleware. Port 2–3 representative endpoints end to end on Workers + D1. |
| 2. Scaffold and infra | 1–2 days | `wrangler` config, D1 bindings, secrets, environments (dev/staging/prod), CI deploys. |
| 3. Schema port | 2–6 days | Rewrite migrations for SQLite. Handle types (UUID, `timestamptz`, JSONB, enums, arrays, `numeric`), defaults and constraints. |
| 4. Data layer rewrite | 5–15 days | **Widest range.** It depends on how much SQL is raw and Postgres-flavoured, and on how you use transactions. |
| 5. Routes and middleware | 4–8 days | About 40 endpoints. Mostly mechanical: `req/res` becomes `c`, and validation moves to `@hono/zod-validator` or similar. Replace middleware such as cors, helmet, auth and logging. |
| 6. Tests | 4–8 days | Move Jest to Vitest with `@cloudflare/vitest-pool-workers`. Swap supertest for `app.request()`. Replace Postgres fixtures with D1 seeding. |
| 7. Data migration and cutover | 3–5 days | Export Postgres, transform, import to D1. Dry runs, verification, a short write freeze or dual-run, a rollback plan. |
| Buffer | about 15–20% | For surprises in phases 3–4. |

## Things that commonly blow up the estimate

**Database (D1/SQLite):**
- **Transactions:** D1 has no interactive `BEGIN ... COMMIT` where you run JS logic between statements. You get `db.batch([...])`, which is atomic but has no read-then-decide step. Any "read, check, then write" flows inside a transaction need redesigning, for example with conditional SQL, a Durable Object for coordination, or optimistic concurrency.
- **No row locking:** no `SELECT FOR UPDATE` and no advisory locks.
- **Types:** these need explicit handling.
  - JSONB becomes `TEXT` with `json_*` functions.
  - Arrays become join tables or JSON.
  - `timestamptz` becomes ISO text or epoch integers.
  - UUIDs are generated in app code with `crypto.randomUUID()`.
  - SQLite has no `numeric` precision, which matters for money.
- **Features with no equivalent:** `ILIKE`, `DISTINCT ON`, window/CTE edge cases, `tsvector` full-text search (FTS5 is the alternative), PL/pgSQL functions and triggers, `LISTEN/NOTIFY`, materialized views.
- **Limits:**
  - A D1 database tops out at 10 GB.
  - A single database handles writes one at a time, so write-heavy workloads may need sharding.
  - There are limits on statement size and bound parameters, which affect bulk inserts.

**Runtime (Workers):**
- **Node-only packages:** `pg`, native `bcrypt` (use `bcryptjs` or Web Crypto), `multer` and disk uploads (use R2), `fs`, `express-session` with a Postgres or Redis store (use KV, D1 or JWTs), `passport` strategies, `winston` file transports. `nodejs_compat` helps, but not with all of these.
- **No long-running process:** cron jobs and queues inside the Express process move to Cron Triggers and Queues. In-memory caches and rate limiters move to KV, Durable Objects or Workers rate limiting.
- **CPU time limits:** check for heavy endpoints such as report generation, image processing or big JSON transforms.

## Recommended plan: split it into two migrations

I'd strongly suggest **not** changing the framework, runtime and database all at once.

**Step A: Express to Hono on Workers, still on Postgres (via Hyperdrive). About 2–3 weeks.**
- Port routes, middleware and tests to Hono and Vitest on Workers.
- Connect to your existing Postgres through **Cloudflare Hyperdrive**, with `postgres.js` or `pg` under `nodejs_compat`.
- Ship it. Run the old and new APIs in parallel behind a route or proxy, comparing responses, then cut over.
- This removes all the runtime and framework risk while your SQL stays the same.

**Step B: Postgres to D1. About 2–5 weeks.**
- Port the schema and rewrite the data layer behind a repository/DAO interface (if you don't have one, add it in Step A).
- Run the same Vitest suite against D1.
- Migrate the data, verify row counts and checksums, then cut over with a rollback path to Hyperdrive and Postgres.

Total effort is roughly the same or slightly more. The benefits:
- Each step can ship and be rolled back on its own.
- Step A gives you real Workers production experience before you touch data.
- After Step A you can **decide whether D1 is worth it at all**. Hyperdrive + Postgres may be good enough, and it avoids the transaction and type rewrite entirely.

## Practical tips

- **Use Drizzle or Kysely for the data layer** if you aren't already. Both target Postgres and D1, which makes Step B much smaller.
- **Turn the existing Jest suite into black-box HTTP contract tests first.** Requests in, status and body out, run against the current Express app. Then the same tests confirm the Hono version behaves identically. This is the best safety net you can have.
- **Port the 3 hardest endpoints first during the spike,** not the easiest ones. They will tell you whether you're closer to 4 weeks or 10.
- **Use AI help for the mechanical parts.** Route handler conversion and test rewrites go well with it and can shorten phases 5–6 noticeably. Schema and transaction redesign still need careful human review.

## To tighten the estimate, I'd want to know

1. How do you access the database today: raw `pg` queries, Knex, Prisma, TypeORM or Sequelize?
2. How big is the database (GB, largest tables), and roughly what share of traffic is writes?
3. Do you use transactions with logic between statements, row locks, JSONB, arrays, full-text search, triggers or stored functions?
4. Auth and sessions: JWT, sessions with a store, or Passport?
5. Any file uploads, background jobs, cron, WebSockets or long-running requests?
6. Can you tolerate a short write freeze at cutover, or do you need zero downtime?

If you can share the repo, or just `package.json`, the migrations folder and a couple of typical route files, I can turn this into a per-endpoint breakdown with a much narrower range.
