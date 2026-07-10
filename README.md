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

---

## Step 1 — Make a GitHub account and repository

GitHub is a website (github.com) where people store code. It will also *run* our robots and *host* our website, all free.

1. Go to **github.com** in your browser → click **Sign up** → follow the steps (email, password, username). If you already have an account, sign in.
2. Once logged in, click the **+** icon in the top-right corner → **New repository**.
3. In "Repository name" type: `opportunity-radar`
4. Select **Public** (required for free website hosting).
5. Click the green **Create repository** button.

## Step 2 — Upload these files

1. On the empty repository page, click the link that says **"uploading an existing file"**.
2. Open the `opportunity-radar` folder you downloaded from this chat on your computer. Select **everything inside it** and drag it into the browser window. **Important:** the `.github` folder starts with a dot, which some computers hide. On Mac, press `Cmd+Shift+.` in Finder to reveal hidden files, then drag `.github` in too. (If drag-and-drop refuses folders, use "choose your files" and re-create the folder paths — or easiest of all: install GitHub Desktop from desktop.github.com, which handles folders properly.)
3. Scroll down, click the green **Commit changes** button.

## Step 3 — Turn on the free website (GitHub Pages)

1. In your repository, click **Settings** (top menu, gear icon).
2. Left sidebar → **Pages**.
3. Under "Branch", pick **main**, folder **/ (root)**, click **Save**.
4. Wait 2 minutes, refresh the page. It will show your website address, something like:
   `https://YOURUSERNAME.github.io/opportunity-radar/`
5. Open it. That's your live board. Bookmark it, set it as your browser homepage.

## Step 4 — Give the email robot a key to your Gmail (safely)

We do NOT put your Gmail password anywhere. Google issues special 16-character robot passwords called **App Passwords** that only allow sending mail and can be revoked anytime.

1. Go to **myaccount.google.com** → **Security** (left sidebar).
2. Make sure **2-Step Verification** is ON (if not, turn it on — it asks for your phone number; this is required for app passwords to exist).
3. In the search bar at the top of that page, type **App passwords** and click the result.
4. Under "App name" type `opportunity-radar` → click **Create**.
5. Google shows a 16-character code like `abcd efgh ijkl mnop`. **Copy it now** — it's shown only once.

Now hand it to GitHub, encrypted:

6. Back in your GitHub repository → **Settings** → left sidebar → **Secrets and variables** → **Actions** → green **New repository secret** button.
7. Create **three** secrets, one at a time:
   - Name: `GMAIL_ADDRESS` → Secret: your full Gmail (e.g. `adu@gmail.com`)
   - Name: `GMAIL_APP_PASSWORD` → Secret: the 16-character code (spaces don't matter)
   - Name: `BOARD_URL` → Secret: your website address from Step 3

## Step 5 — Test it

1. In your repository, click the **Actions** tab (top menu).
2. If it asks you to enable workflows, click the green button to enable.
3. Click **"Opportunity Radar — daily update + reminders"** in the left list → **Run workflow** button (right side) → green **Run workflow**.
4. Wait ~1 minute, refresh. A green ✓ means: fresh listings scraped, and IF any deadline is within 5 days, an email is already in your inbox. A red ✗ means a step failed — click it to read which one (it's almost always a mistyped secret name).

From now on it runs automatically at **8:30 AM, 4:30 PM, and 12:30 AM IST** every day. Morning run = scrape + email. Other runs = email only if something closes within 24 hours (that's your "thrice a day in the last 24 hours").

---

## What about Firebase?

You asked for a Firebase backend, so here's the honest engineering advice: **Firebase's scheduled functions (the part that would run the daily scraper and emails) require the paid "Blaze" plan and a credit card.** GitHub Actions does the identical job free, which is why this project uses it. If you specifically want the site *hosted* on Firebase (that part IS free):

1. Install Node.js from **nodejs.org** (click the big green LTS button, run the installer, keep clicking Next).
2. Open Terminal (Mac: press `Cmd+Space`, type "Terminal", press Enter).
3. Type these lines one at a time, pressing Enter after each:
   ```
   npm install -g firebase-tools
   firebase login
   cd path/to/opportunity-radar
   firebase init hosting
   ```
   (During init: pick "Create a new project", public directory = `.` , single-page app = No.)
4. Type `firebase deploy`. Done — you get a `something.web.app` URL.
   The scraping/email robots still live on GitHub Actions either way.

## What this deliberately does NOT do (and why)

- **No LinkedIn/Instagram/podcast scraping.** LinkedIn's terms of service prohibit automated scraping and they ban accounts for it; social platforms actively block bots. The Simplify GitHub tracker this pulls from is community-maintained *for exactly this purpose* and covers postings faster than LinkedIn shows them anyway. For LinkedIn specifically: set up its built-in **job alerts** (search a role → toggle "Alert" on) — that's the legitimate version of the same thing.
- **Estimated deadlines.** Anything marked EST. on the board is projected from last year's cycle because the 2027 date isn't announced yet. The daily scrape replaces estimates with real listings as they post, but always click through before planning around a date.

## Editing the board yourself

Open `opportunities.json` on GitHub (click the file → pencil icon), add a block like the existing ones, commit. The site updates within a minute. Deadline format is `"YYYY-MM-DD"`, or `null` for rolling.
