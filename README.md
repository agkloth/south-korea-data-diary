# Pyeongtaek Data Project — Summer 2025

> 90 days. One city. One chart per day. All open source.

A daily data series about Pyeongtaek, South Korea — home to the world's largest US military base, Korea's #1 car export port, and the world's biggest Samsung semiconductor plant.

Every morning at 8am KST, a GitHub Action automatically:
1. Runs the Python chart generator
2. Saves the chart to `outputs/`
3. Writes a LinkedIn caption draft to `captions/`
4. Commits everything to this repo

I wake up, copy the caption, post the image. Done in 5 minutes.

---

## Setup guide (copy-paste, beginner friendly)

### Step 1 — Create your GitHub repo

1. Go to [github.com](https://github.com) and sign in (create a free account if needed)
2. Click the **+** in the top right → **New repository**
3. Name it `pyeongtaek-data`
4. Set it to **Public**
5. Click **Create repository**

---

### Step 2 — Upload these files

On your new repo page, click **uploading an existing file** and upload everything in this folder. Keep the folder structure exactly as-is.

Or if you have Git installed, run this in your terminal:

```bash
git clone https://github.com/YOUR_USERNAME/pyeongtaek-data.git
# copy all these files into the cloned folder
cd pyeongtaek-data
git add .
git commit -m "init: project setup"
git push
```

---

### Step 3 — Get your free AirKorea API key

This gives you live daily PM2.5 readings for Pyeongtaek.

1. Go to [data.go.kr](https://www.data.go.kr/en/index.do)
2. Create a free account (click Sign Up)
3. Search for **에어코리아** (AirKorea)
4. Click **대기오염정보 조회 서비스** → click **활용신청** (Apply for use)
5. Within 1–2 hours you'll receive an API key by email

---

### Step 4 — Add the API key to GitHub Secrets

This keeps your key private — it never appears in your code.

1. Go to your GitHub repo
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AIRKOREA_KEY`
5. Value: paste your API key from Step 3
6. Click **Add secret**

---

### Step 5 — Set your start date

Open `scripts/generate_daily.py` in GitHub (click the file, then the pencil icon to edit).

Find this line near the top:

```python
START_DATE = datetime.date(2025, 6, 2)
```

Change `2025, 6, 2` to your actual first day in Pyeongtaek. Then click **Commit changes**.

---

### Step 6 — Test it manually

1. Go to your repo → **Actions** tab
2. Click **Daily Pyeongtaek Chart** in the left sidebar
3. Click **Run workflow** → **Run workflow** (green button)
4. Wait ~60 seconds
5. Go back to your repo — you should see new files in `outputs/` and `captions/`

If it worked: you're done. It will now run automatically every morning at 8am KST.

---

### Step 7 — Your daily routine (5 minutes)

Every morning:
1. Open your GitHub repo
2. Open `captions/dayXX_caption.txt` → copy the text
3. Open `outputs/dayXX_chart.png` → download it
4. Post on LinkedIn: upload the image, paste the caption, edit the `[your link]` placeholder
5. Done

---

## Adding new chart functions (as the weeks progress)

Open `scripts/generate_daily.py` and find the `CHART_FUNCTIONS` dictionary near the bottom:

```python
CHART_FUNCTIONS = {
    1: chart_day01,
    2: chart_day02,
    ...
}
```

To add Day 8, write a new function `chart_day08(day)` that follows the same pattern as the existing ones, then add `8: chart_day08` to the dictionary.

Any day that doesn't have a specific function yet automatically falls back to the **air quality tracker** — so your repo always gets a daily commit even while you're building out future weeks.

---

## Data sources

| Portal | What it covers | URL |
|--------|---------------|-----|
| Pyeongtaek City Data | Population, housing, transport | pyeongtaek.go.kr/data |
| Korea Open Data Portal | 90+ Pyeongtaek datasets | data.go.kr |
| Gyeonggi Port Authority | Monthly cargo stats | gppc.or.kr/en |
| KOSIS | National statistics | kosis.kr/eng |
| AirKorea | Real-time PM2.5/PM10 | airkorea.or.kr |

---

## Tools used

- Python 3.11
- pandas, matplotlib, seaborn, requests
- GitHub Actions (free tier — 2,000 minutes/month, this uses ~2 min/day)
- All data: free Korean government open data

---

*Built during summer 2025 in Pyeongtaek, South Korea.*
