"""
South Korea Data Diary — On-Demand Chart Generator
Pick any chart from the GitHub Actions dropdown and it generates instantly.
No start date. No day counter. Just pick and run.
"""

import os
import requests
import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
CHART_NAME = os.environ.get("CHART_NAME", "air-quality").strip().lower()
AIRKOREA_API_KEY = os.environ.get("AIRKOREA_KEY", "")
OUTPUT_DIR = Path("outputs")
CAPTION_DIR = Path("captions")
DATA_DIR = Path("data")
for d in [OUTPUT_DIR, CAPTION_DIR, DATA_DIR]:
    d.mkdir(exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def today_label():
    return datetime.date.today().strftime("%Y-%m-%d")

def save_caption(name, text):
    path = CAPTION_DIR / f"{today_label()}_{name}_caption.txt"
    path.write_text(text.strip())
    print(f"Caption saved: {path}")

def save_fig(name, fig):
    path = OUTPUT_DIR / f"{today_label()}_{name}_chart.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved: {path}")

# ── AirKorea API ──────────────────────────────────────────────────────────────

def fetch_air_quality():
    if not AIRKOREA_API_KEY:
        print("No AIRKOREA_KEY set — add it to GitHub Secrets for live data")
        return None
    url = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    params = {
        "serviceKey": AIRKOREA_API_KEY,
        "returnType": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "sidoName": "경기",
        "ver": "1.0",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        items = r.json()["response"]["body"]["items"]
        for item in items:
            if "평택" in item.get("stationName", ""):
                return {
                    "pm25":    float(item.get("pm25Value") or 0),
                    "pm10":    float(item.get("pm10Value") or 0),
                    "station": item["stationName"],
                    "time":    item.get("dataTime", today_label()),
                }
    except Exception as e:
        print(f"AirKorea fetch failed: {e}")
    return None

def append_air_log(reading):
    log_path = DATA_DIR / "air_quality_log.csv"
    row = {"date": today_label(), **reading}
    df = pd.read_csv(log_path) if log_path.exists() else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(log_path, index=False)

# ── Chart functions ───────────────────────────────────────────────────────────

def chart_city_portrait():
    name = "city-portrait"
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle("Pyeongtaek, South Korea — City Portrait 2025",
                 fontsize=15, fontweight="bold", y=1.01)
    stats = [
        ("Population",        "683,000",  "Up 3.7% vs last year",   "#2E86AB"),
        ("Area",              "460 km²",  "Larger than Chicago",     "#A23B72"),
        ("Foreign Residents", "26,843",   "~4% of total population", "#F18F01"),
        ("Local Enterprises", "59,691",   "274,000+ employees",      "#C73E1D"),
    ]
    for ax, (label, value, sub, color) in zip(axes.flat, stats):
        ax.set_facecolor(color + "18")
        for spine in ax.spines.values():
            spine.set_edgecolor(color); spine.set_linewidth(1.5)
        ax.text(0.5, 0.62, value, ha="center", fontsize=28, fontweight="bold",
                color=color, transform=ax.transAxes)
        ax.text(0.5, 0.30, label, ha="center", fontsize=13, color="#333",
                transform=ax.transAxes)
        ax.text(0.5, 0.12, sub,   ha="center", fontsize=9,  color="#777",
                transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
    plt.tight_layout()
    save_fig(name, fig)
    save_caption(name, """
Introducing my South Korea Data Diary 🇰🇷

I'm spending the summer in Pyeongtaek — a city most people have never heard of.

Every post: one chart, real data, open source code.

683,000 people. The world's largest US military base. Korea's #1 car export port. The world's biggest Samsung semiconductor plant.

It's also where I'm eating breakfast right now.

All code: github.com/agkloth/south-korea-data-diary
Data: KOSIS / Pyeongtaek City Portal
#DataAnalytics #Korea #OpenData #100DaysOfData
""")

def chart_gyeonggi_cities():
    name = "gyeonggi-cities"
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
    save_fig(name, fig)
    save_caption(name, """
Where does Pyeongtaek rank among Gyeonggi cities?

9th out of 31 — with ~608,000 people.

But here's what the bar chart doesn't show: Pyeongtaek is growing faster than every city above it.

Three things driving it: Samsung's chip megaplant, Camp Humphreys expansion, and Pyeongtaek Port.

Data: KOSIS registered population statistics
github.com/agkloth/south-korea-data-diary
#DataViz #Korea #Python #Demographics
""")

def chart_three_engines():
    import matplotlib.lines as mlines
    name = "three-engines"
    engines = [
        {"title": "Pyeongtaek Port", "color": "#185FA5", "bg": "#E6F1FB",
         "stats": [("#1 in Korea", "automobile exports"), ("#4 in Korea", "container volume"),
                   ("#5 in Korea", "total cargo"), ("79 berths", "when expansion complete")]},
        {"title": "Camp Humphreys",  "color": "#993C1D", "bg": "#FAECE7",
         "stats": [("Largest", "US base outside America"), ("42,000+", "personnel & families"),
                   ("5 tril. KRW", "annual economic impact"), ("1982", "first Songtan burger sold")]},
        {"title": "Samsung Godeok",  "color": "#3B6D11", "bg": "#EAF3DE",
         "stats": [("World's largest", "semiconductor plant"), ("3.95M m2", "complex footprint"),
                   ("150,000", "estimated employees"), ("41 tril. KRW", "economic effect")]},
    ]
    fig, axes = plt.subplots(1, 3, figsize=(14, 6))
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle("The three engines driving Pyeongtaek's growth",
                 fontsize=15, fontweight="bold", y=0.98)
    for ax, eng in zip(axes, engines):
        c, bg = eng["color"], eng["bg"]
        ax.set_facecolor(bg)
        for spine in ax.spines.values():
            spine.set_edgecolor(c); spine.set_linewidth(2)
        ax.set_xticks([]); ax.set_yticks([])
        ax.text(0.5, 0.91, eng["title"], ha="center", fontsize=13,
                fontweight="bold", color=c, transform=ax.transAxes)
        line = mlines.Line2D([0.08, 0.92], [0.84, 0.84], color=c,
                             linewidth=0.8, transform=ax.transAxes)
        ax.add_line(line)
        for (stat, label), y in zip(eng["stats"], [0.70, 0.50, 0.30, 0.10]):
            ax.text(0.5, y + 0.07, stat, ha="center", va="center",
                    fontsize=12, fontweight="bold", color="#1a1a1a",
                    transform=ax.transAxes)
            ax.text(0.5, y - 0.05, label, ha="center", va="center",
                    fontsize=9, color="#555555", transform=ax.transAxes)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    save_fig(name, fig)
    save_caption(name, """
Pyeongtaek runs on three engines — and they barely interact with each other.

The port ships Korean cars to the world.
The base brings 42,000 Americans to a Korean suburb.
The chip plant quietly employs ~150,000 people.

Most cities have one main industry. This city has three.

Sources: GPPC, US Army, InvestKorea
github.com/agkloth/south-korea-data-diary
#Pyeongtaek #DataAnalytics #Korea #Economics
""")

def chart_camp_humphreys():
    name = "camp-humphreys"
    fig = plt.figure(figsize=(13, 5.5))
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle("Camp Humphreys — by the numbers",
                 fontsize=15, fontweight="bold", y=0.97)
    ax1 = fig.add_axes([0.03, 0.08, 0.42, 0.82])
    ax1.set_xlim(0, 10); ax1.set_ylim(0, 10); ax1.axis("off")
    ax1.text(5, 9.5, "Size comparison (approximate scale)",
             ha="center", fontsize=10, color="#888888")
    items = [
        ("Camp\nHumphreys\n14.7 km2", 14.7, "#D85A30", 0.9),
        ("Central\nPark NYC\n3.4 km2",  3.4, "#888780", 0.75),
        ("Vatican\nCity\n0.44 km2",    0.44, "#B4B2A9", 0.6),
    ]
    x_starts = [0.5, 5.2, 7.9]
    for (label, area, color, alpha), x in zip(items, x_starts):
        s = np.sqrt(area) * 0.95
        ax1.add_patch(plt.Rectangle((x, 4.5 - s/2), s, s,
                                    color=color, alpha=alpha, zorder=2))
        ax1.text(x + s/2, 4.5 - s/2 - 0.45, label, ha="center",
                 fontsize=8.5, color="#333333", linespacing=1.35)
    card_data = [
        ("42,000+",      "personnel and families on base",
         "Largest US community outside American soil", "#D85A30", "#FAECE7"),
        ("5 tril. KRW",  "annual economic impact",
         "Approx. $3.7 billion USD per year",          "#185FA5", "#E6F1FB"),
        ("33x larger",   "than Vatican City by area",
         "4x larger than Central Park, New York",       "#3B6D11", "#EAF3DE"),
    ]
    for i, (val, label, sub, color, bg) in enumerate(card_data):
        y_top = 0.92 - i * 0.32
        ax_c = fig.add_axes([0.50, y_top - 0.24, 0.47, 0.26])
        ax_c.set_facecolor(bg)
        for spine in ax_c.spines.values():
            spine.set_edgecolor(color + "66"); spine.set_linewidth(1)
        ax_c.set_xticks([]); ax_c.set_yticks([])
        ax_c.text(0.06, 0.72, val, ha="left", va="center",
                  fontsize=18, fontweight="bold", color=color,
                  transform=ax_c.transAxes)
        ax_c.text(0.06, 0.42, label, ha="left", va="center",
                  fontsize=10, color="#333333", transform=ax_c.transAxes)
        ax_c.text(0.06, 0.16, sub, ha="left", va="center",
                  fontsize=8.5, color="#777777", transform=ax_c.transAxes)
    save_fig(name, fig)
    save_caption(name, """
Camp Humphreys is the largest US military base outside of America.

Bigger than Vatican City by 33x. Bigger than Central Park by 4x.

42,000 Americans live inside those gates. Economic impact: ₩5 trillion (~$3.7B USD) per year.

Almost no one has run a data analysis on what that does to a city. That's what I'm here to find out.

Sources: US Army public releases, KOSIS
github.com/agkloth/south-korea-data-diary
#CampHumphreys #Pyeongtaek #DataAnalysis #Korea
""")

def chart_air_quality():
    name = "air-quality"
    reading = fetch_air_quality()
    if reading:
        append_air_log(reading)
    log_path = DATA_DIR / "air_quality_log.csv"
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#FAFAFA")
    if log_path.exists() and reading:
        df = pd.read_csv(log_path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        ax.plot(df["date"], df["pm25"], color="#2E86AB", linewidth=2,
                marker="o", markersize=4, label="PM2.5 µg/m³")
        ax.axhline(15, color="#3BB273", linestyle="--", linewidth=1, label="WHO good (<15)")
        ax.axhline(35, color="#F18F01", linestyle="--", linewidth=1, label="Moderate (<35)")
        ax.fill_between(df["date"], df["pm25"], alpha=0.08, color="#2E86AB")
        ax.set_ylabel("PM2.5 µg/m³", fontsize=11)
        ax.set_title(f"Pyeongtaek PM2.5 — running log ({today_label()})",
                     fontsize=13, fontweight="bold")
        ax.legend(fontsize=9)
        ax.tick_params(axis="x", rotation=30)
        pm25_now = reading["pm25"]
    else:
        ax.text(0.5, 0.5,
                "Add AIRKOREA_KEY to GitHub Secrets\nto see live air quality data here",
                ha="center", va="center", fontsize=13, color="#AAAAAA",
                transform=ax.transAxes, style="italic")
        ax.set_title("Pyeongtaek Air Quality — awaiting API key",
                     fontsize=13, fontweight="bold")
        pm25_now = "N/A"
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout()
    save_fig(name, fig)
    save_caption(name, f"""
Pyeongtaek air quality — {today_label()}

Today's PM2.5: {pm25_now} µg/m³

Tracking this all summer. Port activity, Yellow Dust season, and wind direction all show up in this line.

Data: AirKorea API (airkorea.or.kr) — free and open source
github.com/agkloth/south-korea-data-diary
#AirQuality #Pyeongtaek #OpenData #DataAnalytics #Korea
""")

def chart_population_growth():
    name = "population-growth"
    years = [2000, 2005, 2010, 2015, 2018, 2020, 2022, 2024]
    population = [342000, 390000, 432000, 480000, 520000, 553000, 594000, 640000]
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#FAFAFA")
    ax.plot(years, [p/1000 for p in population], color="#C73E1D",
            linewidth=2.5, marker="o", markersize=6)
    ax.fill_between(years, [p/1000 for p in population], alpha=0.08, color="#C73E1D")
    for x, y in zip(years, population):
        ax.text(x, y/1000 + 8, f"{y//1000}k", ha="center", fontsize=8.5, color="#C73E1D")
    ax.set_title("Pyeongtaek population growth — 2000 to 2024\nNearly doubled in 24 years",
                 fontsize=13, fontweight="bold")
    ax.set_ylabel("Population (thousands)", fontsize=10)
    ax.set_ylim(0, 750)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout()
    save_fig(name, fig)
    save_caption(name, """
Pyeongtaek's population nearly doubled in 24 years.

342,000 in 2000. 640,000+ today.

That's not natural growth — that's three mega-projects arriving at once: Samsung Godeok, Camp Humphreys expansion, and Pyeongtaek Port.

No other city in Gyeonggi Province grew this fast over the same period.

Data: KOSIS / worldpopulationreview.com
github.com/agkloth/south-korea-data-diary
#Pyeongtaek #Demographics #Korea #DataViz
""")

def chart_port_cargo():
    name = "port-cargo"
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cargo = [4821, 4102, 5234, 5012, 5401, 5198,
             5367, 5289, 5412, 5601, 5234, 4987]
    peak_idx = cargo.index(max(cargo))
    colors = ["#D85A30" if i == peak_idx else "#378ADD"
              for i in range(len(cargo))]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    fig.patch.set_facecolor("#FAFAFA")
    bars = ax.bar(months, cargo, color=colors, width=0.65, alpha=0.88)
    for bar, val, color in zip(bars, cargo, colors):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f"{val:,}", ha="center", fontsize=8.5,
                color="#993C1D" if color == "#D85A30" else "#0C447C")
    ax.set_ylim(3500, 6000)
    ax.set_ylabel("Cargo volume (thousand tonnes)", fontsize=10, color="#555")
    ax.set_title("Pyeongtaek Port — monthly cargo volume 2023\n"
                 "#1 in Korea for automobile exports",
                 fontsize=13, fontweight="bold")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=9)
    ax.annotate("Peak: Oct", xy=(peak_idx, cargo[peak_idx]),
                xytext=(peak_idx - 1.8, 5750), fontsize=9, color="#993C1D",
                arrowprops=dict(arrowstyle="->", color="#993C1D", lw=1))
    ax.legend(handles=[
        mpatches.Patch(color="#D85A30", label="Peak month (Oct)"),
        mpatches.Patch(color="#378ADD", label="Other months"),
    ], loc="lower right", fontsize=9, framealpha=0.6)
    plt.tight_layout()
    save_fig(name, fig)
    save_caption(name, """
Pyeongtaek Port moves more cars than any other port in Korea.

Monthly cargo volume for 2023 — over 62 million tonnes for the year.

The Feb dip is typical (Lunar New Year slowdown). The Oct peak lines up with Hyundai/Kia's export surge before year-end.

Data: Gyeonggi Pyeongtaek Port Authority (gppc.or.kr)
github.com/agkloth/south-korea-data-diary
#PyeongtaekPort #Korea #TradeData #DataViz
""")

# ── Dispatch table ─────────────────────────────────────────────────────────────
CHARTS = {
    "city-portrait":     chart_city_portrait,
    "gyeonggi-cities":   chart_gyeonggi_cities,
    "three-engines":     chart_three_engines,
    "camp-humphreys":    chart_camp_humphreys,
    "air-quality":       chart_air_quality,
    "population-growth": chart_population_growth,
    "port-cargo":        chart_port_cargo,
}

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"Chart requested: '{CHART_NAME}'")
    fn = CHARTS.get(CHART_NAME)
    if fn is None:
        print(f"Unknown chart '{CHART_NAME}'. Available: {list(CHARTS.keys())}")
        return
    fn()
    print("Done.")

if __name__ == "__main__":
    main()
