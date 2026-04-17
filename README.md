# Rosterfy Shift Checker
An automated Python script that monitors a Rosterfy website for new volunteer shifts and sends instant notifications via Discord and your phone.

It includes:
- Polling the Rosterfy API for new shift listings
- Persistent tracking of seen shifts via `seen_ids.json` committed to the repo
- Discord webhook notifications for new shifts and script status
- Phone push notifications via ntfy
- GitHub Actions automation triggered every 15 minutes via cron-job.org

This project demonstrates practical automation concepts such as API polling, external webhook integrations, persistent state management, and reliable scheduled execution with GitHub Actions and cron-jobs.

---

# 📒 Table of Contents
- [Installation](#-installation)
- [Usage](#️-usage)
- [Project Structure](#-project-structure)
- [Example Output](#-example-output)
- [Requirements](#-requirements)

---

# 📦 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/rosterfy-checker.git
   cd rosterfy-checker
   ```

2. Install dependencies:
   ```bash
   pip install requests pytz
   ```

3. Set up your environment variables (see [Usage](#️-usage) for details):
   ```bash
   export ROSTERFY_URL=your_rosterfy_api_url
   export ROSTERFY_HEADERS='{"Authorization": "Bearer your_token"}'
   export EVENTS_WEBHOOK_URL=your_discord_events_webhook
   export STATUS_WEBHOOK_URL=your_discord_status_webhook
   export NTFY_TOPIC=your_ntfy_topic_url
   ```

---

# 🛠️ Usage

Run the script manually:
```bash
python spark_script.py
```

The script will:
- Exit silently if run outside of 8am–9pm Melbourne time
- Poll the Rosterfy API for current shifts
- Compare against previously seen shift IDs stored in `seen_ids.json`
- Send notifications for any new shifts found
- Update and commit `seen_ids.json` back to the repo

**Automated execution** is handled by GitHub Actions, triggered every 15 minutes by [cron-job.org](https://cron-job.org). To set this up:

1. Generate a GitHub Personal Access Token with the `workflow` scope
2. Create a cronjob on cron-job.org with:
   - **URL:** `https://api.github.com/repos/{owner}/{repo}/actions/workflows/rosterfy.yml/dispatches`
   - **Method:** POST
   - **Headers:** `Authorization: Bearer {your_PAT}` and `Accept: application/vnd.github+json`
   - **Body:** `{"ref":"main"}`

Add the following secrets to your GitHub Actions repository settings:

| Secret | Description |
|---|---|
| `ROSTERFY_URL` | Rosterfy API endpoint |
| `ROSTERFY_HEADERS` | JSON string of request headers including auth token |
| `EVENTS_WEBHOOK_URL` | Discord webhook for new shift alerts |
| `STATUS_WEBHOOK_URL` | Discord webhook for script status messages |
| `NTFY_TOPIC` | ntfy topic URL for phone notifications |

---

# 📁 Project Structure

```
rosterfy-checker/
├── spark_script.py       # Main polling and notification script
├── .github/
│   └── workflows/
│       └── rosterfy.yml  # GitHub Actions workflow
├── seen_ids.json         # Persisted shift IDs (auto-updated)
└── README.md             # This file
```

---

# 📊 Example Output

Discord status channel:
```
🚀 Script started at 2026-03-28 09:00:01
⏹ Script finished at 2026-03-28 09:00:03
```

Discord events channel when a new shift is found:
```
🚨 NEW SHIFT FOUND
Event Staff - Grand Prix
📍 Melbourne
🕒 2026-04-05T08:00:00
```

---

# 📜 Requirements

```
requests
pytz
```

Install with:
```bash
pip install requests pytz
```

---

# 🤝 Contributing and Future Improvements
 
Contributions are welcome! Whether it's improving the documentation or adding features like:
- Storing seen IDs in a database (e.g. Supabase) instead of committing to the repo
- Filtering shifts by location or event type before notifying
- A web dashboard to view shift history
- Richer notification formatting with event details and sign-up links
- Notifications when you are accepted for a shift you've applied for
 
Feel free to open issues or pull requests 🎉
