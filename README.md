# agentic-estimates

**A Claude Code skill that stops AI agents from quoting human-era timelines.**

Ask an agent how long something takes and you'll hear "2–3 weeks", and then watch the same agent build it in an afternoon. Models learned to estimate from a decade of human tickets and blog posts. They don't account for the fact that *they* are the ones doing the work, often in parallel, with MCP servers, CLIs and subagents.

The obvious fix, "just divide by 10", is wrong too. Writing code got 10–50× faster. Reviewing it, making decisions, getting API keys and waiting on App Review did not. Speed up one part and the rest dominates (Amdahl's law).

So this skill makes the agent report **three clocks** instead of one number:

| Clock | What it measures | Speedup vs human era |
|---|---|---|
| 🤖 **Agent time** | Wall-clock while agents work, after parallelization | 10–50× |
| 🧑 **Your time** | Minutes of your attention: decisions, review, keys, QA | 1–2× |
| 📅 **Calendar time** | When it's actually done, including waits nobody can compress | ~1× for the waiting parts |

## What it does

1. **Checks what the agent can actually use.** Subagents, MCP servers, CLIs, a browser or simulator. Every missing tool becomes a human step, and it tells you which tool to connect to remove that step.
2. **Breaks the work into units** tagged `build` / `research` / `human` / `wait` / `unknown`.
3. **Maps the critical path.** Agent time is the longest lane, not the sum, capped by how many lanes one human can actually review.
4. **Gives P50–P90 ranges** with an iteration multiplier and timeboxes for unknowns.
5. **Sanity-checks both ways.** It catches "weeks for a CRUD app" (anchored on the human era) and "App Review in 2 hours" (over-compressed).
6. **Calibrates to you.** A tiny local log of estimated vs actual feeds back into future estimates, so after a dozen tasks the numbers are *yours*, not a prior.

## Before / after

Same model, same prompt, with and without the skill. Full answers are in [`examples/`](examples).

| Prompt | Without skill | With skill |
|---|---|---|
| [Habit-tracker SaaS MVP](examples/habit-saas): Next.js, Google login, Stripe $5/mo, dashboard, Vercel | "30–50 hours, 1–1.5 weeks full-time" | **~2–4.5h agent · ~2.5–4.5h you** · MVP live in **1 day**, real payments in 1–3 days (Stripe activation) |
| [Express + Postgres → Hono on Workers + D1](examples/express-to-workers): 40 endpoints, 12k LOC | "4–8 weeks for one experienced dev" | **~4–8h agent · ~4–7h you** · cutover-ready in **~1 week** (code review and staging soak set the pace) |
| [macOS menu bar Spotify app on the Mac App Store](examples/macos-menubar) | "1–3 days of work, 1–2 weeks to the store" | **~2–3h agent · ~2–3h you** · on the store in **2–4 days** (App Review sets the pace) |

Look at the last row: calendar time barely moved. That's the point. The skill doesn't just shrink numbers. It compresses the code and keeps Apple's review queue at whatever it really is. With the skill, the agent also checked its environment before answering ("Vercel CLI and Stripe CLI aren't installed; with them, deploy goes from 30 min of your clicking to 5") and listed exactly what it needed from the human, in unblock order.

## Install

**As a plugin (recommended):**

```
/plugin marketplace add NikOneZ1/agentic-estimates
/plugin install agentic-estimates@agentic-estimates
```

**As a plain skill:**

```bash
git clone https://github.com/NikOneZ1/agentic-estimates
cp -r agentic-estimates/skills/agentic-estimates ~/.claude/skills/
```

Then just ask "how long will X take?", "plan this MVP" or "can we ship this by Friday?". The skill triggers on any time or effort question.

## Calibration

Estimates improve when the agent knows how fast *you* actually ship. When an estimated plan gets executed in the same session, the agent logs the actual agent minutes per unit type to `~/.claude/agentic-estimates/log.jsonl`. The log stays local and is never uploaded. Before the next estimate it reads the median actual/estimated ratio:

```bash
python3 ~/.claude/skills/agentic-estimates/scripts/calibrate.py stats
```

```
14 logged units

type      clock      n  actual/est
build     agent      9        0.62
research  agent      3        0.80
human     human      2        1.70  (too few samples, ignore)
```

That reads as "your build estimates run ~40% high, and your own time runs higher than expected". This is the honest version of the whole idea.

## Files

```
skills/agentic-estimates/
├── SKILL.md                  # the method and output format
├── references/anchors.md     # starting priors: agent / human / wait times per unit type
├── references/calibration.md # how the log works
└── scripts/calibrate.py      # stdlib-only log + stats
examples/                     # before/after runs on real prompts
```

## Contributing

The anchors in [`references/anchors.md`](skills/agentic-estimates/references/anchors.md) are priors, not truth. The most useful PRs are **real data**: `calibrate.py stats` output plus your stack and setup (how many parallel lanes, which MCPs). Over time that can turn the anchors from guesses into medians.

## License

MIT
