---
name: agentic-estimates
description: Realistic time estimates for work that AI agents will actually execute — split into agent time, human time and calendar time instead of one human-era number. Use this whenever the user asks how long something will take, wants an estimate, a timeline, a roadmap, a sprint plan, an MVP scope, "is this doable by Friday", "how many days/weeks", effort sizing, or a project plan — and also before you volunteer any duration yourself (e.g. "this would take 2–3 weeks"). Default to it even if the user doesn't say "estimate" but is clearly asking about time or effort.
---

# Agentic estimates

LLMs learned to estimate from a decade of human-written tickets, blog posts and forum answers — "that's a 2-week feature". When an agent is the one doing the work, those numbers are wrong in a specific, predictable way:

- **Writing code, scaffolding, refactoring, tests, docs, research** got 10–50× faster. Human-era estimates massively overstate these.
- **Human attention** (decisions, reviewing diffs, clicking through the app, getting API keys) barely got faster. It is now usually the bottleneck.
- **External latency** (CI, app store review, DNS, OAuth verification, waiting on another person) did not get faster at all.

So "divide by 10" is just as wrong as the original number. This is Amdahl's law: speed up one part and the remaining parts dominate. A good estimate makes that visible by reporting **three clocks** separately.

| Clock | What it measures | Typical speedup vs human era |
|---|---|---|
| **Agent time** | Wall-clock while agents work, after parallelization | 10–50× |
| **Your time** | Minutes of the human's focused attention | 1–2× |
| **Calendar time** | When it's actually done, including waits nobody can compress | often ~1× for the waiting parts |

## Workflow

Scale the effort to the question. "How long to add dark mode?" deserves a three-line answer using these clocks, not a table. A multi-week project plan deserves the full breakdown.

### 1. Check what you can actually use

Throughput depends on tools. Before estimating, look at what this session really has (don't assume):

- Can you spawn subagents or parallel sessions? How many lanes are realistic?
- Which MCP servers, CLIs (`gh`, `wrangler`, `vercel`, `stripe`, `xcodebuild`, `supabase`…) and API keys are available?
- Can you see and drive the result yourself (browser, simulator, test runner), or does a human have to check it?
- Is there an existing codebase to read, or is it greenfield?

Every step that needs a tool you don't have turns into **human time**. That's the most common hidden cost: "deploy" takes 3 minutes with a CLI and 40 minutes of the user clicking around a dashboard without one. Name these gaps explicitly; often the best advice is "connect X and this step disappears".

### 2. Break the work into units

Aim for units of roughly 5–60 agent-minutes. For each, tag its type:

- **build**: code, config, tests, docs, migrations. Agent-heavy.
- **research**: reading docs, comparing options, exploring an unfamiliar codebase. Agent-heavy and very parallel.
- **human**: decisions, review, manual QA on a device, accounts and credentials, anything with taste or authority.
- **wait**: CI, builds, store review, propagation, approvals, replies from other people.
- **unknown**: no repro, undocumented API, unclear requirements. Gets a timebox, not a point estimate.

Use the anchors in `references/anchors.md` as priors for each type. If calibration data exists (step 6), it overrides the anchors.

### 3. Map parallelism and the critical path

Independent build and research units can run in parallel lanes (subagents or separate sessions), so **agent time is the length of the critical path, not the sum**. Two limits keep this honest:

- **Review bandwidth.** One person can meaningfully supervise about 3–5 lanes. Past that, lanes queue on the human.
- **Integration cost.** Merging parallel work, fixing interfaces between pieces, re-running tests: add about 10–25% on top of the longest lane.

Also mark which waits can overlap with work. Submit to App Review, then build the landing page while it's in the queue.

### 4. Add iteration, then give ranges

First drafts are rarely final. Apply a loop multiplier to agent time: about 1.3× for well-specified work, 2× when requirements are fuzzy or there's UI polish, 3× for unknowns. Report **P50–P90 ranges**, not points. Underestimating is a real failure too: if someone promises a client "tomorrow" based on your number, that matters. Unknown units widen the range; they don't shrink it.

### 5. Sanity-check against both failure modes

- **Anchored on the human era?** If pure build work comes out in days or weeks, re-derive it bottom-up from units. "Weeks" for a CRUD app with auth is a human-era number.
- **Over-compressed?** If anything involves another party (Apple, Google, a client, a teammate, a bank), its calendar time stays whatever it is in the real world. Never compress waits.
- **Hidden human time?** Count accounts, keys, 2FA, billing setup, domain purchases, device testing, final visual review. These add up to hours, and agents routinely forget them.

### 6. Calibrate (this is what makes it better over time)

Without calibration you're just swapping one bias for another. A tiny log of estimated vs actual fixes that.

- Before giving an estimate, run `python3 <skill-dir>/scripts/calibrate.py stats` if the log exists. Multiply each type's anchors by its observed actual/estimated ratio. Mention it briefly ("adjusted using your last 14 tasks").
- When you go on to execute an estimated plan in the same session, record a start time (`date +%s`). When you finish, log the actual agent minutes per unit type with `python3 <skill-dir>/scripts/calibrate.py log ...` (see `references/calibration.md`). Ask the user for their own time only if it's cheap to ask. Don't nag.

## Output format

For a quick question, answer in one to three sentences that still separate the clocks:

> About 20–40 min of agent work, plus ~10 min of yours to check it on your phone. Nothing to wait on, so it can ship today.

For anything bigger, use this template (keep it tight and drop rows that add nothing):

```markdown
## Estimate: <task>

**Bottom line:** ~<agent range> of agent work · ~<your range> of your time · done in ~<calendar range>
<one sentence: what dominates the timeline and why>

| # | Unit | Type | Lane | Agent | You | Wait |
|---|------|------|------|-------|-----|------|
| 1 | …    | build | A   | 15–25m | –  | –    |
| 2 | …    | human | –   | –      | 10m | –   |
| 3 | …    | wait  | –   | –      | –  | 1–2d |

**Critical path:** 1 → 4 → 6 (<why these are serial>)
**Parallel lanes:** A: 1, 2 · B: 3, 5 · C: 7
**What I need from you:** <keys, accounts, decisions; in the order they unblock things>
**Where this could blow up:** <the unknowns, each with a timebox>
**Faster if:** <missing tools or access that would remove human steps>
**Human-era comparison:** a solo dev without agents would typically quote <X>; the gap is mostly <which units>.
```

The human-era line is there because users often hold that number in their head. Showing both, and where the difference comes from, makes the new estimate believable instead of looking like hype.

## Pitfalls

- **Don't inflate out of politeness or caution.** Padding belongs in the P90, not the P50.
- **Don't promise speed you can't deliver in this environment.** If there are no subagents, there's no parallelism. If you can't run the app, a human has to check it.
- **The person doing the work matters.** If the user says they'll write it by hand, estimate for a human and say so.
- **Calendar time is what people actually ask about.** "When will it be done" means calendar time. Lead with it if the waits dominate.
