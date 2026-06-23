#!/usr/bin/env bash
#
# Run the activity bot on your own machine (alternative to GitHub Actions).
# Schedule it with cron, e.g. once a day at 11:23:
#
#   crontab -e
#   23 11 * * * /full/path/to/Git_Bot/run_local.sh >> /full/path/to/Git_Bot/cron.log 2>&1
#
# For the push to work, the repo's "origin" remote must be authenticated
# (SSH key, or an HTTPS URL containing a Personal Access Token, or a
# configured git credential helper).
set -euo pipefail

cd "$(dirname "$0")"

# Get any commits that may have been made elsewhere (e.g. by Actions) first.
git pull --rebase --quiet || true

AUTO_PUSH=1 python3 scripts/commit_bot.py
