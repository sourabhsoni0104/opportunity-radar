 # Opportunity Radar — setup guide (assume you know nothing)

This folder contains a complete, self-updating deadline tracker:

| File | What it is |
|---|---|
| `index.html` | The website. A "departures board" of every opportunity, deadline, countdown, and prep guide. |
| `opportunities.json` | The data — 52 curated opportunities. The scraper adds to it daily. |
| `data.js` | Same data, in the format the website reads. Auto-regenerated. |
| `scraper/update_opportunities.py` | The robot that checks the internet every morning for new internship postings and adds them to the board. |
| `scraper/send_reminders.py` | The robot that emails your Gmail: daily from 5 days before each deadline, three times a day in the last 24 hours. |
| `.github/workflows/radar.yml` | The alarm clock that wakes both robots up on schedule — for free, on GitHub's computers, so nothing runs on your laptop. |

Total cost: ₹0. Total setup time: ~20 minutes, once. After that it runs itself forever.

