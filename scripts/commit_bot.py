#!/usr/bin/env python3
"""Daily activity bot.

Runs once per day (via GitHub Actions or a local cron job). Using the
constraints in config.json it decides whether to make commits *today*, then
makes a small, natural-looking number of them. The goal is steady activity
without committing literally every single day.

Rules enforced:
  * Never leave more than `max_gap_days` between two active days.
  * Aim for roughly `target_active_days_min`..`target_active_days_max`
    active days per calendar month.
  * On an active day, make 1..`max_commits_per_day` commits.

IMPORTANT: GitHub's contribution graph only counts a commit when the
commit's AUTHOR email is connected to your GitHub account, the repo is NOT a
fork, and the commit is on the default branch. So `author_email` in
config.json must be an email verified on your account (the easiest choice is
your `username@users.noreply.github.com` address).
"""

import json
import os
import random
import string
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    with open(os.path.join(ROOT, "config.json"), encoding="utf-8") as fh:
        return json.load(fh)


def git(*args, check=False):
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit(f"git {' '.join(args)} failed")
    return result.stdout.strip()


def commit_dates(tz):
    """Set of local-date objects on which commits were authored."""
    dates = set()
    for line in git("log", "--pretty=format:%aI").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            dt = datetime.fromisoformat(line)
        except ValueError:
            continue
        dates.add(dt.astimezone(tz).date())
    return dates


def main():
    cfg = load_config()
    tz = timezone(timedelta(hours=cfg.get("utc_offset_hours", 0)))
    now = datetime.now(tz)
    today = now.date()

    # Single source of truth for identity -> this controls the green squares.
    git("config", "user.name", cfg["author_name"])
    git("config", "user.email", cfg["author_email"])

    dates = commit_dates(tz)
    if today in dates:
        print(f"{today}: already committed today - nothing to do.")
        return

    last_active = max(dates) if dates else None
    gap = (today - last_active).days if last_active else None
    active_this_month = sum(
        1 for d in dates if (d.year, d.month) == (today.year, today.month)
    )

    must_commit = gap is None or gap >= cfg["max_gap_days"]

    if must_commit:
        decision = True
        reason = "no history yet" if gap is None else f"max gap reached (gap={gap})"
    elif active_this_month >= cfg["target_active_days_max"]:
        decision = False
        reason = f"monthly target met ({active_this_month})"
    else:
        p = cfg["commit_probability"]
        if today.weekday() >= 5:  # Saturday / Sunday
            p *= cfg.get("weekend_probability_factor", 1.0)
        decision = random.random() < p
        reason = f"probability roll (p={p:.2f})"

    print(
        f"{today}: gap={gap} active_this_month={active_this_month} "
        f"-> {'COMMIT' if decision else 'skip'} ({reason})"
    )
    if not decision:
        return

    n = random.randint(cfg["min_commits_per_day"], cfg["max_commits_per_day"])
    activity_file = os.path.join(ROOT, cfg["activity_file"])
    rel = os.path.relpath(activity_file, ROOT)
    for i in range(1, n + 1):
        token = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        stamp = now.strftime("%Y-%m-%d %H:%M:%S %z")
        with open(activity_file, "a", encoding="utf-8") as fh:
            fh.write(f"- {stamp} | {token}\n")
        msg = random.choice(cfg["commit_messages"])
        git("add", rel)
        git("commit", "-m", msg, check=True)
        print(f"  commit {i}/{n}: {msg}")

    if os.environ.get("AUTO_PUSH") == "1":
        git("push", check=True)
        print("  pushed to remote.")


if __name__ == "__main__":
    main()
