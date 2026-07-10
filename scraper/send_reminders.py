"""
Gmail deadline reminders for Opportunity Radar.

The rules you asked for:
  - Starting 5 days before a deadline: one reminder email per day.
  - In the final 24 hours: three reminders per day.

How that works mechanically: GitHub Actions runs this script three times a
day (roughly 03:00, 11:00, 19:00 UTC). The script itself decides what to send:
  - deadline within 24 hours  -> email on ALL THREE runs (= thrice daily)
  - deadline within 5 days    -> email only on the FIRST run of the day
  - anything further out      -> silence

Emails are sent from YOUR OWN Gmail to YOUR OWN Gmail using an
"App Password" (a special 16-character password Google issues for robots —
your real password is never used or stored). Both values live in GitHub
Secrets, which are encrypted; they never appear in the code.
"""
import json
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "opportunities.json"

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
BOARD_URL = os.environ.get("BOARD_URL", "your GitHub Pages link")


def hours_left(deadline_str: str) -> float:
    # Deadlines treated as end-of-day IST (UTC+5:30), since you're in India.
    dl = datetime.fromisoformat(deadline_str + "T23:59:59+05:30")
    return (dl - datetime.now(timezone.utc)).total_seconds() / 3600


def is_first_run_of_day() -> bool:
    # The 03:00 UTC run is the "daily digest" run.
    return datetime.now(timezone.utc).hour < 8


def build_email(urgent, daily):
    lines = []
    if urgent:
        lines.append("🚨 FINAL CALL — closes within 24 hours:\n")
        for o, h in urgent:
            lines.append(f"  • {o['title']} ({o['org']}) — {h:.0f} hours left\n    {o['url']}\n")
    if daily:
        lines.append("\n⏳ Boarding — closes within 5 days:\n")
        for o, h in daily:
            lines.append(f"  • {o['title']} ({o['org']}) — {h/24:.1f} days left\n    {o['url']}\n")
    lines.append(f"\nFull board: {BOARD_URL}")
    lines.append("\nEstimated deadlines are projections from last cycle — verify on the link.")
    return "\n".join(lines)


def main():
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        sys.exit("GMAIL_ADDRESS / GMAIL_APP_PASSWORD secrets not set — see README step 4.")

    data = json.loads(DATA_FILE.read_text())
    urgent, daily = [], []
    for o in data:
        if not o.get("deadline"):
            continue
        h = hours_left(o["deadline"])
        if h < 0:
            continue
        if h <= 24:
            urgent.append((o, h))
        elif h <= 24 * 5:
            daily.append((o, h))

    # Cadence logic
    send_daily = daily and is_first_run_of_day()
    send_urgent = bool(urgent)  # every run
    if not (send_urgent or send_daily):
        print("Nothing due within the reminder window on this run. No email sent.")
        return

    urgent.sort(key=lambda x: x[1])
    daily.sort(key=lambda x: x[1])
    body = build_email(urgent if send_urgent else [], daily if send_daily else [])
    n_final = len(urgent) if send_urgent else 0
    subject = (
        f"🚨 {n_final} deadline(s) close in <24h — Opportunity Radar"
        if n_final
        else f"⏳ {len(daily)} deadline(s) within 5 days — Opportunity Radar"
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_ADDRESS

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        s.send_message(msg)
    print(f"Sent: {subject}")


if __name__ == "__main__":
    main()
