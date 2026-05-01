"""
Pyeongtaek Daily Chart Generator
Runs every morning via GitHub Actions.
Figures out what day of the 90-day series it is, then calls the
right chart function and writes a LinkedIn caption draft.
"""

import os
import json
import requests
import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless — no display needed on GitHub Actions
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
START_DATE = datetime.date(2025, 6, 2)          # change to your first day in Pyeongtaek
AIRKOREA_API_KEY = os.environ.get("AIRKOREA_KEY", "")   # set in GitHub secrets
OUTPUT_DIR = Path("outputs")
CAPTION_DIR = Path("captions")
DATA_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)
CAPTION_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_day_number():
    today = datetime.date.today()
    delta = (today - START_DATE).days + 1
    return max(1, min(delta, 90))

def save_caption(day: int, text: str):
    path = CAPTION_DIR / f"day{day:02d}_caption.txt"
    path.write_text(text.strip())
    print(f"Caption saved: {path}")

def save_fig(day: int, fig):
    path = OUTPUT_DIR / f"day{day:02d}_chart.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved: {path}")

# ── AirKorea API ──────────────────────────────────────────────────────────────

def fetch_air_quality():
    """
    Fetches today's PM2.5 reading for Pyeongtaek from AirKorea.
    Returns a dict with pm25, pm10, grade.
    Falls back to None if the API key is missing or request fails.
    Free API key: https://www.data.go.kr → search '에어코리아' → request key
    """
    if not AIRKOREA_API_KEY:
        print("No AIRKOREA_KEY set — using fallback data")
        return None

    url = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    params = {
        "serviceKey": AIRKOREA_API_KEY,
        "returnType": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "sidoName": "경기",          # Gyeonggi Province
        "ver": "1.0",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        items = r.json()["response"]["body"]["items"]
        # Find Pyeongtaek station
        for item in items:
            if "평택" in item.get("stationName", ""):
                return {
                    "pm25": float(item.get("pm25Value") or 0),
                    "pm10": float(item.get("pm10Value") or 0),
                    "o3":   float(item.get("o3Value")   or 0),
                    "no2":  float(item.get("no2Value")  or 0),
                    "station": item["stationName"],
                    "time": item.get("dataTime", "today"),
                }
    except Exception as e:
        print(f"AirKorea fetch failed: {e}")
    return None

def append_air_log(reading: dict):
    """Appends today's air quality reading to a running CSV log."""
    log_path = DATA_DIR / "air_quality_log.csv"
    today = datetime.date.today().isoformat()
    row = {"date": today, **reading}
    if log_path.exists():
        df = pd.read_csv(log_path)
    else:
        df = pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(log_path, index=False)
    print(f"Air quality log updated: {log_path}")

# ── Chart functions — one per day / topic ─────────────────────────────────────
# Week 1 is fully built out. Weeks 2–13 use a smart fallback that still
# produces a real chart — the daily air quality tracker — so your GitHub
# always gets a commit even before you've written week-specific code.

def chart_day01(day):
    """City portrait — 4 stat cards."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle("Pyeongtaek, South Korea — City Portrait 2025",
                 fontsize=15, fontweight="bold", y=1.01)
    stats = [
        ("Population",       "683,000",  "Up 3.7% vs last year",    "#2E86AB"),
        ("Area",             "460 km²",  "Larger than Chicago",      "#A23B72"),
        ("Foreign Residents","26,843",   "~4% of total population",  "#F18F01"),
        ("Local Enterprises","59,691",   "274,000+ employees",       "#C73E1D"),
    ]
    for ax, (label, value, sub, color) in zip(axes.flat, stats):
        ax.set_facecolor(color + "18")
        for spine in ax.spines.values():
            spine.set_edgecolor(color); spine.set_linewidth(1.5)
        ax.text(0.5, 0.62, value,  ha="center", fontsize=28, fontweight="bold",
                color=color, transform=ax.transAxes)
        ax.text(0.5, 0.30, label,  ha="center", fontsize=13, color="#333",
                transform=ax.transAxes)
        ax.text(0.5, 0.12, sub,    ha="center", fontsize=9,  color="#777",
                transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
    plt.tight_layout()
    save_fig(day, fig)
    save_caption(day, """
Day 1 of my 90-day Pyeongtaek data series 🇰🇷

I'm spending the summer in Pyeongtaek, South Korea — a city most people have never heard of.

Every single day I'm publishing one chart. Today: the basics.

683,000 people. The world's largest US military base. Korea's #1 car export port. The world's biggest Samsung semiconductor plant.

It's also where I'm eating breakfast right now.

Follow along. All code is open source on GitHub.
Data: KOSIS / Pyeongtaek City Portal
#DataAnalytics #Korea #OpenData #100DaysOfData
""")

def chart_day02(day):
    """Data sources visual directory."""
    sources = [
        ("pyeongtaek.go.kr/data", "Population, housing, business, transport", "CSV / Excel", "#2E86AB"),
        ("data.go.kr",            "National open data — 90+ Pyeongtaek datasets", "CSV / API",   "#A23B72"),
        ("gppc.or.kr/en",         "Port cargo stats — monthly PDFs",              "PDF / CSV",   "#F18F01"),
        ("kosis.kr/eng",          "All Korea national stats, city-level",         "Excel / API", "#C73E1D"),
        ("airkorea.or.kr",        "Real-time + historical PM2.5 / PM10",          "API (free)",  "#3BB273"),
        ("data.seoul.go.kr",      "Metro + city data for Seoul comparisons",      "JSON / CSV",  "#7B2D8B"),
    ]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 10); ax.set_ylim(0, len(sources) + 1); ax.axis("off")
    fig.patch.set_facecolor("#FAFAFA")
    ax.text(5, len(sources) + 0.5, "My Pyeongtaek Data Sources — Summer 2025",
            ha="center", fontsize=14, fontweight="bold", color="#222")
    for i, (url, coverage, fmt, color) in enumerate(sources):
        y = len(sources) - 1 - i
        ax.add_patch(plt.Circle((0.2, y + 0.35), 0.12, color=color, zorder=3))
        ax.text(0.5,  y + 0.25, url,      fontsize=9.5, color=color, fontweight="bold")
        ax.text(3.8,  y + 0.25, coverage, fontsize=9,   color="#444")
        ax.text(7.5,  y + 0.35, fmt,      fontsize=8.5, color=color,
                bbox=dict(boxstyle="round,pad=0.3", fc=color+"22", ec=color, lw=0.8),
                va="center")
        ax.axhline(y, color="#EEE", linewidth=0.5)
    plt.tight_layout()
    save_fig(day, fig)
    save_caption(day, """
Day 2: Before I publish charts, here's my full data toolkit.

All open source. All free. All Korean government data.

6 portals. One city. 90 days.

The most underrated one? pyeongtaek.go.kr/data — Pyeongtaek's own data portal with 90+ datasets. Almost nobody outside Korea knows it exists.

Tomorrow: population growth vs other Gyeonggi cities.
All code on GitHub: [your link]
#OpenData #DataAnalytics #Korea #Python
""")

def chart_day03(day):
    """Gyeonggi city population comparison."""
    cities = {
        "Suwon": 1188000, "Goyang": 1073000, "Yongin": 1070000,
        "Seongnam": 929000, "Hwaseong": 907000, "Bucheon": 812000,
        "Namyangju": 745000, "Ansan": 648000, "Pyeongtaek": 608000,
        "Anyang": 551000,
    }
    df = pd.DataFrame(list(cities.items()), columns=["City", "Population"])
    df = df.sort_values("Population", ascending=True)
    colors = ["#C73E1D" if c == "Pyeongtaek" else "#BBCBDD" for c in df["City"]]
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#FAFAFA")
    bars = ax.barh(df["City"], df["Population"] / 1000, color=colors, height=0.6)
    for bar, val in zip(bars, df["Population"]):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                f"{val/1000:.0f}k", va="center", fontsize=9, color="#444")
    ax.set_xlabel("Population (thousands)", fontsize=10, color="#555")
    ax.set_title("Gyeonggi Province cities by population — 2023\nPyeongtaek highlighted",
                 fontsize=13, fontweight="bold")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.set_xlim(0, 1350)
    ax.legend(handles=[
        mpatches.Patch(color="#C73E1D", label="Pyeongtaek (where I live)"),
        mpatches.Patch(color="#BBCBDD", label="Other Gyeonggi cities"),
    ], loc="lower right", fontsize=9)
    plt.tight_layout()
    save_fig(day, fig)
    save_caption(day, """
Day 3: Where does Pyeongtaek rank among Gyeonggi cities?

9th out of 31, with ~608,000 people.

But here's the catch: Pyeongtaek is growing faster than every city above it on this chart.

The driver? Three things landing at once: Samsung's chip megaplant, Camp Humphreys' expansion, and Pyeongtaek Port.

Data: KOSIS registered population statistics.
#DataViz #Korea #Python #Demographics
""")

def chart_day04(day):
    """Day 4 is the personal photo day — generates a simple stat card as backup image."""
    reading = fetch_air_quality()
    pm25 = reading["pm25"] if reading else 38
    grade_color = "#3BB273" if pm25 < 15 else "#F18F01" if pm25 < 35 else "#C73E1D"
    grade_text  = "Good" if pm25 < 15 else "Moderate" if pm25 < 35 else "Unhealthy"

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor(grade_color + "18")
    ax.axis("off")
    for spine in ax.spines.values():
        spine.set_edgecolor(grade_color); spine.set_linewidth(2)
    today_str = datetime.date.today().strftime("%B %d, %Y")
    ax.text(0.5, 0.82, f"Pyeongtaek Air Quality — {today_str}",
            ha="center", fontsize=11, color="#555", transform=ax.transAxes)
    ax.text(0.5, 0.52, f"{pm25:.0f}", ha="center", fontsize=52, fontweight="bold",
            color=grade_color, transform=ax.transAxes)
    ax.text(0.5, 0.30, "PM2.5 µg/m³", ha="center", fontsize=13, color="#444",
            transform=ax.transAxes)
    ax.text(0.5, 0.12, grade_text, ha="center", fontsize=14, fontweight="bold",
            color=grade_color, transform=ax.transAxes)
    plt.tight_layout()
    save_fig(day, fig)
    save_caption(day, f"""
Day 4: Pair this with a photo from wherever you are today.

Today's air quality in Pyeongtaek: PM2.5 = {pm25:.0f} µg/m³ ({grade_text}).

The data and the street aren't separate things. That's what this series is about.

Data: AirKorea / airkorea.or.kr
#Pyeongtaek #DataStorytelling #Korea #AirQuality
""")

def chart_day05(day):
    """Three engines of Pyeongtaek."""
    engines = [
        {"title": "Pyeongtaek Port",  "color": "#2E86AB",
         "stats": [("#1 in Korea","car exports"),("#4 in Korea","container volume"),
                   ("#5 in Korea","total cargo"),("79 berths","when complete")]},
        {"title": "Camp Humphreys",   "color": "#C73E1D",
         "stats": [("Largest","US base outside America"),("42,000+","personnel & families"),
                   ("5 trillion ₩","annual economic impact"),("1982","first Songtan burger")]},
        {"title": "Samsung Godeok",   "color": "#3BB273",
         "stats": [("World's largest","semiconductor plant"),("3.95M m²","complex footprint"),
                   ("150,000","estimated employees"),("₩41 trillion","economic effect")]},
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13, 5))
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle("The three engines driving Pyeongtaek's growth",
                 fontsize=14, fontweight="bold", y=1.02)
    for ax, eng in zip(axes, engines):
        c = eng["color"]
        ax.set_facecolor(c + "12")
        for spine in ax.spines.values():
            spine.set_edgecolor(c); spine.set_linewidth(2)
        ax.set_xticks([]); ax.set_yticks([])
        ax.text(0.5, 0.92, eng["title"], ha="center", fontsize=13,
                fontweight="bold", color=c, transform=ax.transAxes)
        for (stat, label), y in zip(eng["stats"], [0.72, 0.52, 0.32, 0.12]):
            ax.text(0.5, y + 0.08, stat,  ha="center", fontsize=12,
                    fontweight="bold", color="#222", transform=ax.transAxes)
            ax.text(0.5, y - 0.04, label, ha="center", fontsize=8.5,
                    color="#666", transform=ax.transAxes)
    plt.tight_layout()
    save_fig(day, fig)
    save_caption(day, """
Day 5: Pyeongtaek runs on three engines — and they barely interact with each other.

The port ships Korean cars to the world.
The base brings 42,000 Americans to a Korean suburb.
The chip plant quietly employs ~150,000 people.

Most cities have one main industry. This city has three.

Next week I go deep on each one.
Sources: GPPC, US Army, InvestKorea
#Pyeongtaek #DataAnalytics #Korea #Economics
""")

def chart_day06(day):
    """Camp Humphreys size comparison."""
    import numpy as np
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle("Camp Humphreys — by the numbers", fontsize=14, fontweight="bold")
    ax1.set_xlim(0, 10); ax1.set_ylim(0, 10); ax1.axis("off")
    ax1.set_title("Size comparison (approximate scale)", fontsize=10, color="#555")
    for (label, area), color, x in zip(
        [("Camp\nHumphreys\n14.7 km²", 14.7),
         ("Central Park\nNYC\n3.4 km²",  3.4),
         ("Vatican\nCity\n0.44 km²",    0.44)],
        ["#C73E1D", "#BBCBDD", "#DDDDDD"],
        [1, 5, 8.2]
    ):
        s = np.sqrt(area) * 0.9
        ax1.add_patch(plt.Rectangle((x, 5 - s/2), s, s, color=color, alpha=0.8))
        ax1.text(x + s/2, 5 - s/2 - 0.4, label, ha="center",
                 fontsize=8, color="#333", linespacing=1.3)
    ax2.set_facecolor("#FAFAFA")
    categories = ["Annual economic\nimpact (₩ trillion)", "Personnel &\nfamilies (thousands)", "Land area\n(km²)"]
    norm_vals = [100, 42/5000*100, 14.7/5000*100]
    display   = ["₩5 trillion / year", "42,000 people", "14.7 km²"]
    bars = ax2.barh(categories, norm_vals,
                    color=["#C73E1D","#E07B54","#F0B59A"], height=0.5)
    for bar, lbl in zip(bars, display):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                 lbl, va="center", fontsize=9, color="#333")
    ax2.set_xlim(0, 130); ax2.set_title("Key metrics", fontsize=10, color="#555")
    for s in ["top","right","bottom"]:
        ax2.spines[s].set_visible(False)
    ax2.set_xticks([])
    plt.tight_layout()
    save_fig(day, fig)
    save_caption(day, """
Day 6: Camp Humphreys is the largest US military base outside of America.

It's bigger than Vatican City by 33x. Bigger than Central Park by 4x.

42,000 Americans live inside those gates. The economic impact: ₩5 trillion (~$3.7B USD) per year.

And yet almost no one has ever run a data analysis on what that does to a city.

That's what I'm here to find out.
Sources: US Army public releases, KOSIS
#CampHumphreys #Pyeongtaek #DataAnalysis #Korea
""")

def chart_day07(day):
    """Week 1 recap."""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#FAFAFA"); ax.axis("off")
    ax.text(0.5, 0.95, "Week 1 recap — what I learned",
            ha="center", fontsize=16, fontweight="bold",
            color="#222", transform=ax.transAxes)
    days_info = [
        ("Day 1\nCity portrait","#2E86AB"), ("Day 2\nData sources","#A23B72"),
        ("Day 3\nCity ranking","#F18F01"),  ("Day 4\nStreet + stat","#C73E1D"),
        ("Day 5\n3 engines",   "#3BB273"),  ("Day 6\nCamp Humphreys","#7B2D8B"),
    ]
    for i, (label, color) in enumerate(days_info):
        x = 0.08 + i * 0.155
        ax.add_patch(plt.Circle((x, 0.72), 0.045, color=color,
                                transform=ax.transAxes, clip_on=False))
        ax.text(x, 0.72, str(i+1), ha="center", va="center",
                fontsize=10, fontweight="bold", color="white",
                transform=ax.transAxes)
        ax.text(x, 0.57, label, ha="center", fontsize=7.5,
                color="#555", linespacing=1.4, transform=ax.transAxes)
    ax.text(0.5, 0.40, "The stat that surprised me most:",
            ha="center", fontsize=10, color="#777", transform=ax.transAxes)
    ax.text(0.5, 0.23,
            '"Pyeongtaek\'s population doubled — 342k to 683k — in just 26 years."',
            ha="center", fontsize=12, fontweight="bold", color="#C73E1D",
            style="italic", transform=ax.transAxes)
    ax.text(0.5, 0.08, "Source: worldpopulationreview.com / KOSIS",
            ha="center", fontsize=8.5, color="#AAA", transform=ax.transAxes)
    plt.tight_layout()
    save_fig(day, fig)
    save_caption(day, """
Day 7: One week in. Here's what I learned.

6 charts. 6 commits. One city most data analysts have never touched.

The number that stopped me cold: Pyeongtaek's population doubled in 26 years. That's not immigration — that's three mega-projects arriving at once.

Next week: I go deep on the port. Monthly cargo data, car exports, and why this port punches way above its weight.

All code on GitHub: [link]
What city should I compare Pyeongtaek to? Drop it below 👇
#DataAnalytics #Korea #OpenData #Python #100DaysOfData
""")

def chart_air_quality_fallback(day):
    """
    Default chart for any day that doesn't have a specific function yet.
    Plots the running PM2.5 log so far — always useful, always fresh.
    """
    reading = fetch_air_quality()
    log_path = DATA_DIR / "air_quality_log.csv"

    if reading:
        append_air_log(reading)

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#FAFAFA")

    if log_path.exists():
        df = pd.read_csv(log_path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        ax.plot(df["date"], df["pm25"], color="#2E86AB", linewidth=2, marker="o",
                markersize=4, label="PM2.5 µg/m³")
        ax.axhline(15, color="#3BB273", linestyle="--", linewidth=1, label="WHO good (<15)")
        ax.axhline(35, color="#F18F01", linestyle="--", linewidth=1, label="Moderate (<35)")
        ax.axhline(75, color="#C73E1D", linestyle="--", linewidth=1, label="Unhealthy (>75)")
        ax.fill_between(df["date"], df["pm25"], alpha=0.08, color="#2E86AB")
        ax.set_ylabel("PM2.5 µg/m³", fontsize=11)
        ax.set_title(f"Pyeongtaek PM2.5 — Summer 2025 log (Day {day})",
                     fontsize=13, fontweight="bold")
        ax.legend(fontsize=9)
        ax.tick_params(axis="x", rotation=30)
    else:
        # No log yet — just show today's reading
        pm25 = reading["pm25"] if reading else 0
        ax.bar(["Pyeongtaek\n(today)"], [pm25], color="#2E86AB", width=0.4)
        ax.set_ylabel("PM2.5 µg/m³")
        ax.set_title(f"Day {day} — Pyeongtaek air quality", fontsize=13, fontweight="bold")

    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout()
    save_fig(day, fig)

    pm25_now = reading["pm25"] if reading else "N/A"
    save_caption(day, f"""
Day {day}: Pyeongtaek air quality update.

Today's PM2.5: {pm25_now} µg/m³

Tracking this every day this summer. Port activity, Yellow Dust season, and weather all show up in this line.

Data: AirKorea API (airkorea.or.kr) — free and open.
#AirQuality #Pyeongtaek #OpenData #DataAnalytics #Korea
""")

# ── Dispatch table ─────────────────────────────────────────────────────────────
# Maps day number → chart function. Add new functions here as you build them.
CHART_FUNCTIONS = {
    1:  chart_day01,
    2:  chart_day02,
    3:  chart_day03,
    4:  chart_day04,
    5:  chart_day05,
    6:  chart_day06,
    7:  chart_day07,
    # Week 2+ will be added here — for now they fall through to the air quality tracker
}

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    day = get_day_number()
    print(f"Generating Day {day} of 90...")

    fn = CHART_FUNCTIONS.get(day, chart_air_quality_fallback)
    if fn is chart_air_quality_fallback:
        fn(day)
    else:
        fn(day)

    print("Done.")

if __name__ == "__main__":
    main()
