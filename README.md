# South Korea Data Diary

**Live portfolio:** [agkloth.github.io/south-korea-data-diary](https://agkloth.github.io/south-korea-data-diary)

A data journalism project documenting Pyeongtaek, South Korea through original analysis and interactive visualizations — built live during the summer of 2026.

Pyeongtaek is one of the fastest-growing cities in South Korea, home to the world's largest US military base (Camp Humphreys), Korea's #1 car export port, and the world's biggest Samsung semiconductor plant. Almost no public data analysis exists on this city. This project changes that.

---

## Charts

| Chart | Description | Live |
|-------|-------------|------|
| City Portrait | Key stats: population, area, foreign residents, enterprises | [View →](https://agkloth.github.io/south-korea-data-diary/outputs/2026-05-03_city-portrait.html) |
| Gyeonggi Cities | Population ranking across all Gyeonggi Province cities | [View →](https://agkloth.github.io/south-korea-data-diary/outputs/2026-05-03_gyeonggi-cities.html) |
| Three Engines | Port, military base, and semiconductor plant by the numbers | [View →](https://agkloth.github.io/south-korea-data-diary/outputs/2026-05-03_three-engines.html) |
| Camp Humphreys | Size comparison and economic footprint | [View →](https://agkloth.github.io/south-korea-data-diary/outputs/2026-05-03_camp-humphreys.html) |
| Population Growth | Pyeongtaek's growth from 342k to 640k (2000–2024) | [View →](https://agkloth.github.io/south-korea-data-diary/outputs/2026-05-03_population-growth.html) |
| Port Cargo | Monthly cargo volume, Pyeongtaek Port 2023 | [View →](https://agkloth.github.io/south-korea-data-diary/outputs/2026-05-03_port-cargo.html) |
| Air Quality | Live PM2.5 tracker — updated daily | [View →](https://agkloth.github.io/south-korea-data-diary/outputs/2026-05-03_air-quality.html) |

---

## How it works

Every chart is generated automatically via **GitHub Actions** — no manual runs needed.

```
GitHub Actions (daily trigger)
    → scripts/generate_daily.py
        → Pulls live data (AirKorea API, KOSIS, GPPC)
        → Generates interactive Plotly HTML chart
        → Writes LinkedIn caption draft
    → Commits outputs/ and captions/ to repo
    → GitHub Pages publishes live URLs automatically
```

To generate a chart on demand: **Actions tab → Daily South Korea Chart → Run workflow → pick a chart**.

---

## Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Chart generation |
| Plotly | Interactive HTML charts |
| pandas | Data processing |
| GitHub Actions | Automated daily runs |
| GitHub Pages | Live chart hosting |
| AirKorea API | Live PM2.5 data |
| KOSIS | Korean national statistics |
| GPPC | Pyeongtaek Port cargo data |

All tools are free and open source.

---

## Data sources

| Source | What it covers | URL |
|--------|---------------|-----|
| Pyeongtaek City Portal | Population, housing, business, transport | pyeongtaek.go.kr/data |
| KOSIS | Korean national statistics | kosis.kr/eng |
| Korea Open Data Portal | 90+ Pyeongtaek datasets | data.go.kr |
| Gyeonggi Port Authority | Monthly cargo volume | gppc.or.kr/en |
| AirKorea | Real-time PM2.5/PM10 | airkorea.or.kr |

---

## Project structure

```
south-korea-data-diary/
├── .github/
│   └── workflows/
│       └── daily_chart.yml     # GitHub Actions workflow
├── scripts/
│   └── generate_daily.py       # Chart generator (Plotly)
├── outputs/                    # Generated HTML charts
├── captions/                   # LinkedIn caption drafts
├── data/                       # Cached data (air quality log)
├── index.html                  # Portfolio landing page
└── README.md
```

---

*Built in Pyeongtaek, South Korea · Summer 2026*
