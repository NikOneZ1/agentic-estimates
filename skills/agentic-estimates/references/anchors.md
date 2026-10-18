# Anchors

These are starting priors for a Claude Code-class agent with normal tools (file edit, shell, web search), working on one unit in one lane. They are deliberately ranges. Your own calibration log (`scripts/calibrate.py stats`) beats every number here. PRs with better data are welcome.

## Agent time (build / research)

| Unit | Agent time | Notes |
|---|---|---|
| Scaffold a project, config, boilerplate | 2–10 min | Faster with a template or CLI generator |
| CRUD endpoint with validation and tests | 5–15 min | Per resource |
| Database schema and migration | 5–20 min | Add human verification if real data is touched |
| UI screen or component from a description | 10–30 min | Plus human visual review, see below |
| UI polish to match a design or "make it feel good" | 20–90 min | Iteration-heavy, 2× loop multiplier |
| Auth with a hosted provider (Clerk, Supabase, Auth.js…) | 15–40 min | Plus human time for provider dashboard and keys |
| Payments (Stripe checkout and webhooks) | 30–90 min | Test mode only; live mode is a human step |
| Integration with a well-documented API | 15–45 min | |
| Integration with a poorly documented or undocumented API | 1–4 h | Treat as **unknown**, timebox it |
| Mechanical refactor across many files | 1–3 min per file | Highly parallel |
| Port or migration between frameworks | 3–10 min per module or endpoint | Parallel by module; integration cost is real |
| Tests for existing code | 5–20 min per module | |
| Bug with a clear repro | 5–30 min | |
| Bug without a repro, flaky or prod-only | timebox 30–120 min | **unknown**; often needs human reproduction |
| Performance work | 30 min–3 h | Profiling loops; depends on how fast you can measure |
| README, docs, changelog | 5–15 min | |
| Research or compare libraries and approaches | 10–30 min | Parallel subagents cut wall-clock further |
| Read and understand an unfamiliar mid-size codebase | 10–30 min | Parallel Explore agents help |
| Deploy with a CLI or MCP available | 5–20 min | |
| Native build cycle (Xcode, Android, Rust release) | 2–10 min per build | Compile time, not thinking time, dominates |

## Your time (human)

| Unit | Human time | Notes |
|---|---|---|
| Meaningful review of a diff | ~1 min per 50–150 changed lines | Skimming is faster but doesn't count as review |
| Product or architecture decision | 5–30 min | Faster if the agent frames 2–3 options with a recommendation |
| Visual or UX check of a screen | 3–10 min per screen | |
| Manual QA of a flow on a real device | 10–30 min per flow | |
| Create an account or API key with a third party | 5–20 min | Billing, 2FA or business verification push it to 30–60 min |
| Dashboard clicking without a CLI or MCP (DNS, OAuth app, store listing) | 10–45 min | Often removable by connecting a tool |
| App Store or Play listing (screenshots, copy, privacy forms) | 30–120 min | Agents can draft copy and generate screenshots |
| Final sign-off on anything legal, financial or brand-facing | 10–60 min | Never compress |

## Wait time (calendar)

| Wait | Typical | Notes |
|---|---|---|
| CI run | 3–20 min | Per push; many pushes add up |
| TestFlight processing | 10–60 min | |
| App Store review | ~1 day, up to several | Rejections add a full cycle |
| Google Play review (new app) | 1–7 days | |
| DNS propagation, SSL issuance | minutes to hours | |
| Google OAuth app verification (sensitive scopes) | days to weeks | |
| API access approval (enterprise APIs, some social APIs) | days to weeks | |
| Domain or business verification | hours to days | |
| Reply from another human | hours to days | Teammate, client, designer, support |
| Payment provider activation (live mode) | hours to days | |

## Multipliers

| Situation | Multiplier on agent time |
|---|---|
| Well-specified, familiar stack | 1.2–1.3× |
| Fuzzy requirements or UI taste involved | 1.5–2× |
| Unknown or undocumented territory | 2–3×, plus a timebox |
| Large existing codebase with unclear conventions | +10–30 min of upfront exploration |
| Parallel lanes merged at the end | +10–25% integration |
