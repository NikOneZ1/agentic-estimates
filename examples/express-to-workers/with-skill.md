## Estimate: Express + Postgres → Hono on Cloudflare Workers + D1 (40 endpoints, ~12k LOC, Jest)

**Bottom line:** ~4–8h of agent work (P90 ~11h) · ~4–7h of your time · cutover-ready in ~1 week (P90 ~2 weeks)
Porting the code isn't what sets the timeline. Three things do: you reviewing a diff of roughly 10k lines, changing the database engine (Postgres → SQLite/D1, including moving live data), and a staging soak you shouldn't skip.

I haven't seen the repo yet (it isn't open in this session), so these numbers come from your description. Unit 1 replaces the guesswork with a real inventory, and I'd re-issue the estimate after it. I have no calibration history for you yet, so I used default anchors.

| # | Unit | Type | Lane | Agent | You | Wait |
|---|------|------|------|-------|-----|------|
| 1 | Recon: list endpoints, middleware, Postgres-specific SQL (JSONB, arrays, enums, transactions, FTS), Node-only deps (bcrypt, multer, fs, pg) | research | A–C | 15–30m | – | – |
| 2 | Decisions: D1 vs. keeping Postgres via Hyperdrive, ORM (Drizzle vs. raw), transaction strategy, cutover style (downtime window vs. dual-run) | human | – | – | 30–60m | – |
| 3 | Cloudflare account, API token for wrangler, create D1 database (staging + prod) | human | – | – | 10–20m | – |
| 4 | Scaffold Hono worker, wrangler config, D1 binding, Vitest with `@cloudflare/vitest-pool-workers` | build | A | 10–20m | – | – |
| 5 | Translate the schema to SQLite DDL and D1 migrations | build | A | 15–40m | – | – |
| 6 | Port the data-access layer (pg queries → D1/Drizzle) and shared middleware (auth, validation, errors, CORS) | build | A | 30–60m | – | – |
| 7 | Port 40 endpoints and their Jest/supertest tests → Hono + Vitest (~10 endpoints per lane) | build | A–D | 45–130m | – | – |
| 8 | Data migration script: Postgres export → transform → D1 import, plus a dry run on a copy | build | E | 30–60m | – | 10m–2h (import, depends on size) |
| 9 | Postgres-isms with no direct D1 equivalent (interactive transactions, JSONB queries, FTS, LISTEN/NOTIFY, cron/background jobs) | unknown | – | timebox 1–3h | 15–30m (decisions) | – |
| 10 | Integration: merge lanes, run the full suite, fix cross-lane breakage | build | A | 20–45m | – | CI 3–20m × several pushes |
| 11 | Review the diff (go deep on data layer + auth, spot-check endpoints since the ported tests guard parity) | human | – | – | 2–4h | – |
| 12 | Deploy to staging, run a parity-diff script that replays requests against old and new APIs and compares responses | build | A | 20–40m | 30–60m (click-through) | – |
| 13 | Staging soak (real or shadow traffic) | wait | – | – | – | 2–5 days |
| 14 | Cutover: freeze writes, final data sync, switch routes/DNS, monitor, keep rollback ready | human | – | 15–30m | 30–60m | minutes–hours (DNS) |

**Critical path:** 1 → 2 → 4 → 5 → 6 → 7 → 10 → 11 → 12 → 13 → 14. The schema and shared data layer have to exist before the endpoint lanes can start, and the soak can't start until the review is done.
**Parallel lanes:** A: 4, 5, 6, 10, 12 · A–D: 7, split by resource (~10 endpoints each) · E: 8, running alongside 7. Four or five lanes is about all one reviewer can keep up with.
**Rough plan by day:**
- **Day 1:** recon, decisions, scaffold, schema, data layer, parallel endpoint port. Agent work, with you around for the decisions.
- **Day 2:** integration, your review, staging deploy, parity diff.
- **Days 3–5+:** soak in staging, dry-run the data migration twice.
- **Cutover:** in a low-traffic window.

**What I need from you (in unblock order):**
1. Repo access in this session.
2. The decision on D1 vs. Hyperdrive (see below).
3. A Cloudflare API token, or `npx wrangler login`. wrangler isn't installed globally here, but npx works.
4. A read-only Postgres connection string, or a dump, for the data migration. pg_dump/psql aren't installed here, so I'd use Node's `pg` or you'd install them.
5. Your cutover window.

**Where this could blow up:**
- **Transactions.** D1 has no interactive BEGIN/COMMIT, only atomic `batch()`. Multi-step writes that read in between need a redesign. Part of the unit 9 timebox, up to 3h.
- **Heavy Postgres features.** JSONB operators, arrays, full-text search, window-heavy reporting queries. Each one needs a SQLite rewrite or a different design. Also unit 9.
- **D1 limits.** 10 GB per database and a single writer. If your data or write load is near that, D1 is the wrong target, and the plan changes.
- **Node-only code.** Native bcrypt, filesystem uploads, long-running jobs. These map to WebCrypto/bcryptjs, R2 and Cron Triggers/Queues. Usually 15–45m each, more if they're everywhere.
- **Data volume and downtime tolerance.** A large dataset or a zero-downtime requirement turns the cutover into a dual-write project, adding ~2–4h of agent work and more calendar time.

**Faster if:**
- **You keep Postgres and use Hyperdrive instead of D1.** This is the biggest lever. Units 5, 8 and most of 9 disappear, there's no data migration, and the cutover becomes a routing switch. Roughly 40% less agent time, about half your review, and a much safer rollback. Worth deciding before anything else, unless you have a specific reason to want D1 (cost, edge reads, staying all-Cloudflare).
- **Your Jest tests are thorough.** Good tests make the review much lighter, because ported tests passing is real evidence of parity.
- **You connect a Cloudflare token.** Then I can create D1, deploy and tail logs myself through wrangler and the Cloudflare MCP, instead of you clicking through the dashboard.

**Human-era comparison:** a solo dev without agents would typically quote 3–6 weeks. Almost all of the gap is in units 6–8 and 10: hand-porting 40 endpoints, rewriting tests and writing the migration script, which shrink from weeks to hours. Review, the soak and the cutover take about as long as they always did, and they're why this is still about a week and not a day.
