"""
Daily updater for Opportunity Radar.

What it does, in plain words:
1. Downloads the latest internship list from the SimplifyJobs Summer-2027
   GitHub repository (a community-maintained list, updated daily, that
   permits this kind of use — unlike LinkedIn, which forbids scraping).
2. Merges any NEW active listings into our opportunities.json.
3. Rewrites data.js so the website shows the fresh data.

Run by GitHub Actions every day. You never run this by hand
(but you can: `python scraper/update_opportunities.py`).
"""
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "opportunities.json"
DATA_JS = ROOT / "data.js"

# Community trackers that publish machine-readable listing files.
# We try each URL until one works (repos sometimes rename branches).
SIMPLIFY_URLS = [
    f"https://raw.githubusercontent.com/SimplifyJobs/{season}/{branch}/.github/scripts/listings.json"
    for season in ("Summer2027-Internships", "Summer2026-Internships")
    for branch in ("dev", "main", "master")
]

MAX_SCRAPED = 40  # keep the board readable — newest N scraped roles only


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "opportunity-radar/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def load_current():
    return json.loads(DATA_FILE.read_text())


def pull_simplify():
    """Return fresh tech listings from the Simplify tracker, newest first."""
    raw = None
    for url in SIMPLIFY_URLS:
        try:
            raw = fetch_json(url)
            break
        except Exception as e:  # noqa: BLE001 — try next mirror
            print(f"  could not fetch {url}: {e}")
    if not raw:
        print("  Simplify tracker unreachable today; keeping existing data.")
        return []

    out = []
    for item in raw:
        if not item.get("active", False):
            continue
        title = item.get("title", "").strip()
        company = item.get("company_name", "").strip()
        link = item.get("url") or item.get("application_link") or ""
        posted = item.get("date_posted") or 0
        if not (title and company and link):
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", f"{company}-{title}".lower())[:60]
        out.append({
            "id": f"scr-{slug}",
            "section": "tech",
            "title": f"{title} — {company}",
            "org": company,
            "deadline": None,  # tracker roles are rolling; apply fast
            "confirmed": True,
            "url": link,
            "note": "Auto-scraped from the Simplify Summer-2027 tracker. Rolling — apply within days of posting.",
            "_posted": posted,
        })
    out.sort(key=lambda x: x["_posted"], reverse=True)
    for o in out:
        o.pop("_posted", None)
    return out[:MAX_SCRAPED]


def main():
    data = load_current()
    curated = [o for o in data if not o["id"].startswith("scr-")]
    print(f"{len(curated)} curated entries kept.")

    scraped = pull_simplify()
    print(f"{len(scraped)} active roles pulled from Simplify tracker.")

    merged = curated + scraped
    DATA_FILE.write_text(json.dumps(merged, indent=1))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    DATA_JS.write_text(
        f"// auto-generated {stamp}\nwindow.OPPORTUNITIES = " + json.dumps(merged) + ";"
    )
    print(f"Board now has {len(merged)} listings. Updated {stamp}.")


if __name__ == "__main__":
    main()
