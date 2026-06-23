# Git_Bot — automated GitHub activity bot

A tiny bot that keeps a repository (and your contribution graph) steadily
active. It runs once a day and decides — with a bit of randomness — whether
to make commits, so your history looks natural instead of a perfect green
wall.

**What it guarantees**

- Never more than **3 days** between active days (configurable).
- Roughly **20–21 active days per month** (configurable).
- **1–3 commits** on each active day.

It runs for free on **GitHub Actions** — once it's set up there is nothing to
keep running on your own computer.

> Honest note: these are automated commits whose only purpose is to show
> activity. They count toward your contribution graph only when the commit
> author email is one connected to your GitHub account (see step 1). Use this
> on your own repositories.

---

## How the contribution graph actually works

For a commit to turn a square green, **all** of these must be true:

1. The commit **author email** is verified/connected to your GitHub account.
2. The repository is **not a fork** (forks don't count — use a normal repo).
3. The commit is on the repository's **default branch** (`main`).

That's why step 1 below is the most important one.

---

## Setup (GitHub Actions — recommended)

### 1. Edit `config.json`

Open [config.json](config.json) and set:

- `"author_name"` — your name.
- `"author_email"` — **an email connected to your GitHub account.**
  The safest choice is your GitHub *noreply* address. Find it at
  **GitHub → Settings → Emails** — with "Keep my email addresses private"
  enabled it looks like `12345678+yourusername@users.noreply.github.com`
  (or simply `yourusername@users.noreply.github.com`). Paste it exactly.
- `"utc_offset_hours"` — your timezone offset so the green squares land on
  the correct day. Example: Kenya/EAT = `3`, UK = `0`, US Eastern = `-5`.

You can tune the activity numbers too — see [Tuning](#tuning) below.

### 2. Create a new repository on GitHub

- Go to <https://github.com/new>.
- Name it anything, e.g. **`daily-activity`**.
- **Private is fine** (your own private contributions still count — see
  "Make private activity visible" below if you want others to see it).
- Do **not** check "Add a README" and do **not** create it as a fork — create
  an **empty** repo. Click **Create repository**.

### 3. Push this folder to that repository

In a terminal, from inside this `Git_Bot` folder, run (replace the URL with
your new repo's URL):

```bash
git init -b main
git add -A
git commit -m "Add activity bot"
git remote add origin https://github.com/YOURUSERNAME/daily-activity.git
git push -u origin main
```

> The repo has already been `git init`-ed for you, so `git init -b main` may
> say it reinitialized — that's fine.

### 4. Give the workflow permission to push

On GitHub: **your repo → Settings → Actions → General →
Workflow permissions →** select **"Read and write permissions"** → **Save**.

(Without this the daily job can't push its commits.)

### 5. Test it now

On GitHub: **your repo → Actions tab → "Daily Activity" → Run workflow**.
After ~30 seconds, refresh the repo — you should see a new commit. Done.

From now on it runs automatically every day at the scheduled time and commits
on ~20–21 days each month, never skipping more than ~2 days in a row.

---

## Make private activity visible (optional)

If your repo is **private** but you want the green squares to show on your
public profile: **GitHub → Settings → Profile →** check
**"Include private contributions on my profile"**. (Or just make the repo
public.) Either way, *you* always see your own private contributions when
logged in.

---

## Tuning

All knobs live in [config.json](config.json):

| Setting | Meaning | Default |
|---|---|---|
| `max_gap_days` | Force a commit once this many days have passed since the last active day. | `3` |
| `target_active_days_min` / `_max` | Aim for this many active days per month. | `20` / `21` |
| `commit_probability` | Chance of committing on a normal day that isn't forced. Higher = more active days. | `0.72` |
| `weekend_probability_factor` | Multiplier applied to the probability on Sat/Sun (lower = quieter weekends, more realistic). | `0.55` |
| `min_commits_per_day` / `max_commits_per_day` | How many commits on an active day. | `1` / `3` |
| `commit_messages` | Pool of commit messages chosen at random. | — |

The bot reads the repo's own git history to make its decisions, so there is
no extra state file to manage — just edit, commit, and push.

---

## Running locally instead (alternative)

If you'd rather run it from your own machine instead of GitHub Actions, use
[run_local.sh](run_local.sh) with cron. Your `origin` remote must be
authenticated (SSH key or a Personal Access Token in the HTTPS URL):

```bash
chmod +x run_local.sh
crontab -e
# add this line (use full absolute paths):
23 11 * * * /full/path/to/Git_Bot/run_local.sh >> /full/path/to/Git_Bot/cron.log 2>&1
```

You can use both Actions and local cron together — the script pulls before it
commits, so they won't clash.

---

## Stopping / pausing

- **Pause temporarily:** GitHub → Actions tab → "Daily Activity" → "⋯" →
  **Disable workflow**.
- **Stop completely:** delete the repository, or delete
  `.github/workflows/daily-activity.yml`.
- **Local cron:** run `crontab -e` and remove the line.

---

## Notes & limitations

- GitHub runs scheduled jobs in **UTC** and may **delay** them by a few
  minutes (sometimes more) during busy periods — normal, not a problem here.
- GitHub auto-disables scheduled workflows after **60 days of no repo
  activity**; since this bot commits regularly, that won't happen.
- Test changes any time with **Actions → Run workflow** (`workflow_dispatch`).
