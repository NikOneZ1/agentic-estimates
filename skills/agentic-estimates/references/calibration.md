# Calibration

The log lives at `~/.claude/agentic-estimates/log.jsonl` (override with `AGENTIC_ESTIMATES_LOG`). It is one JSON object per line, stays local, and is never uploaded anywhere.

## Logging a finished unit

```bash
python3 <skill-dir>/scripts/calibrate.py log \
  --type build \
  --unit "Stripe checkout + webhook" \
  --est-agent 45 --actual-agent 31 \
  --est-human 15 --actual-human 25 \
  --project my-saas
```

- Minutes everywhere. `--type` is one of `build`, `research`, `human`, `wait`, `unknown`.
- Only `--type`, `--est-agent` and `--actual-agent` are required. For `human` and `wait` units, put the numbers in the matching fields instead.
- Log the midpoint of the range you gave as the estimate.
- Measure actual agent time as wall-clock: `date +%s` at the start and at the end.

You can log a whole plan at once by calling `log` once per unit. That's cheap, so do it as soon as the work is done, while the timings are still in context.

## Reading stats

```bash
python3 <skill-dir>/scripts/calibrate.py stats
```

This prints, per type and clock, the number of samples and the median actual/estimated ratio. A ratio of 0.6 for `build` means your build estimates run 40% high: multiply the anchors by 0.6. Ignore any ratio with fewer than 3 samples; it's noise.
