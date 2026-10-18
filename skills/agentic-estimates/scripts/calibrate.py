#!/usr/bin/env python3
"""Local calibration log for agentic-estimates: estimated vs actual minutes per unit type."""

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

TYPES = ("build", "research", "human", "wait", "unknown")
CLOCKS = ("agent", "human", "wait")
MIN_SAMPLES = 3


def log_path() -> Path:
    override = os.environ.get("AGENTIC_ESTIMATES_LOG")
    return Path(override).expanduser() if override else Path.home() / ".claude" / "agentic-estimates" / "log.jsonl"


def read_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def cmd_log(args: argparse.Namespace) -> int:
    entry = {"ts": int(time.time()), "type": args.type, "unit": args.unit, "project": args.project}
    for clock in CLOCKS:
        est, actual = getattr(args, f"est_{clock}"), getattr(args, f"actual_{clock}")
        if est is not None and actual is not None:
            entry[f"est_{clock}"] = est
            entry[f"actual_{clock}"] = actual
    if not any(f"est_{c}" in entry for c in CLOCKS):
        print("error: give at least one --est-X/--actual-X pair", file=sys.stderr)
        return 2
    path = log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps({k: v for k, v in entry.items() if v is not None}) + "\n")
    print(f"logged to {path}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    entries = read_entries(log_path())
    if args.project:
        entries = [e for e in entries if e.get("project") == args.project]
    if not entries:
        print("no calibration data yet; use the anchors as-is")
        return 0

    rows = []
    for t in TYPES:
        for clock in CLOCKS:
            ratios = [
                e[f"actual_{clock}"] / e[f"est_{clock}"]
                for e in entries
                if e.get("type") == t and e.get(f"est_{clock}")
            ]
            if ratios:
                rows.append((t, clock, len(ratios), statistics.median(ratios)))

    print(f"{len(entries)} logged units\n")
    print(f"{'type':<10}{'clock':<8}{'n':>4}  {'actual/est':>10}")
    for t, clock, n, ratio in rows:
        note = "" if n >= MIN_SAMPLES else "  (too few samples, ignore)"
        print(f"{t:<10}{clock:<8}{n:>4}  {ratio:>10.2f}{note}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_log = sub.add_parser("log", help="append one finished unit")
    p_log.add_argument("--type", required=True, choices=TYPES)
    p_log.add_argument("--unit", default="")
    p_log.add_argument("--project", default=None)
    for clock in CLOCKS:
        p_log.add_argument(f"--est-{clock}", type=float, help="estimated minutes")
        p_log.add_argument(f"--actual-{clock}", type=float, help="actual minutes")
    p_log.set_defaults(func=cmd_log)

    p_stats = sub.add_parser("stats", help="median actual/estimated ratio per type and clock")
    p_stats.add_argument("--project", default=None)
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
