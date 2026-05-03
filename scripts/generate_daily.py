"""
South Korea Data Diary — On-Demand Interactive Chart Generator
Generates polished Plotly HTML charts + LinkedIn caption drafts.
"""

import os, requests, datetime
import pandas as pd
from pathlib import Path

CHART_NAME       = os.environ.get("CHART_NAME", "city-portrait").strip().lower()
AIRKOREA_API_KEY = os.environ.get("AIRKOREA_KEY", "")
OUTPUT_DIR       = Path("outputs")
CAPTION_DIR      = Path("captions")
DATA_DIR         = Path("data")
for d in [OUTPUT_DIR, CAPTION_DIR, DATA_DIR]:
    d.mkdir(exist_ok=True)

BLUE   = "#185FA5"; CORAL  = "#D85A30"; GREEN  = "#3B6D11"
GRAY   = "#888780"; BG     = "#FAFAFA"; GRID   = "#E8E6E0"
BLUE_A  = "rgba(24,95,165,0.12)"
CORAL_A = "rgba(216,90,48,0.12)"
GREEN_A = "rgba(59,109,17,0.12)"
CORAL_F = "rgba(216,90,48,0.15)"
BLUE_F  = "rgba(24,95,165,0.12)"

FONT   = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

def today_label():
    return datetime.date.today().strftime("%Y-%m-%d")

def base_layout(**overrides):
    layout = dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family=FONT, color="#222222"),
        hoverlabel=dict(bgcolor="white", bordercolor="#cccccc",
                        font_size=13, font_family=FONT),
    )
    layout.update(overrides)
    return layout

def save_html(name, fig):
    import plotly.io as pio
    path = OUTPUT_DIR / f"{today_label()}_{name}.html"
    fig.write_html(str(path), include_plotlyjs="cdn", full_html=True,
                   config={"displayModeBar": True, "displaylogo": False,
                           "modeBarButtonsToRemove": ["lasso2d","select2d"]})
    print(f"HTML saved: {path}")

def save_caption(name, text):
    path = CAPTION_DIR / f"{today_label()}_{name}_caption.txt"
    path.write_text(text.strip())
    print(f"Caption saved: {path}")

def source_note(fig):
    fig.add_annotation(
        text="South Korea Data Diary · github.com/agkloth/south-korea-data-diary",
        xref="paper", yref="paper", x=0.5, y=-0.10,
        showarrow=False, font=dict(size=10, color="#AAAAAA"),
        xanchor="center"
    )

def fetch_air_quality():
    if not AIRKOREA_API_KEY:
        print("No AIRKOREA_KEY — add to GitHub Secrets for live data")
        return None
    url = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    params = dict(serviceKey=AIRKOREA_API_KEY, returnType="json",
                  numOfRows="100", pageNo="1", sidoName="경기", ver="1.0")
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        for item in r.json()["response"]["body"]["items"]:
            if "평택" in item.get("stationName",""):
                return dict(pm25=float(item.get("pm25Value") or 0),
                            pm10=float(item.get("pm10Value") or 0),
                            station=item["stationName"],
                            time=item.get("dataTime", today_label()))
    except Exception as e:
        print(f"AirKorea failed: {e}")
    return None

def append_air_log(reading):
    log = DATA_DIR / "air_quality_log.csv"
    row = {"date": today_label(), **reading}
    df = pd.read_csv(log) if log.exists() else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(log, index=False)

# ─────────────────────────────────────────────────────────────────────────────

def chart_city_portrait():
    import plotly.graph_objects as go
    name = "city-portrait"
    stats = [
        ("Population",        "683,000",  "Up 3.7% vs last year",   BLUE,  BLUE_A,  0.0, 0.5),
        ("Area",              "460 km²",  "Larger than Chicago",    "#A23B72","rgba(162,59,114,0.10)",0.5,0.5),
        ("Foreign Residents", "26,843",   "~4% of total population","#BA7517","rgba(186,117,23,0.10)",0.0,0.0),
        ("Local Enterprises", "59,691",   "274,000+ employees",     CORAL, CORAL_A, 0.5, 0.0),
    ]
    fig = go.Figure()
    for label, value, sub, color, bg, x, y in stats:
        fig.add_shape(type="rect", xref="paper", yref="paper",
                      x0=x+0.025, y0=y+0.05, x1=x+0.475, y1=y+0.45,
                      fillcolor=bg, line=dict(color=color, width=2))
        fig.add_annotation(text=f"<b>{value}</b>", xref="paper", yref="paper",
                           x=x+0.25, y=y+0.325, showarrow=False,
                           font=dict(size=34, color=color, family=FONT), xanchor="center")
        fig.add_annotation(text=label, xref="paper", yref="paper",
                           x=x+0.25, y=y+0.215, showarrow=False,
                           font=dict(size=15, color="#333333", family=FONT), xanchor="center")
        fig.add_annotation(text=sub, xref="paper", yref="paper",
                           x=x+0.25, y=y+0.115, showarrow=False,
                           font=dict(size=11, color="#888888", family=FONT), xanchor="center")
    source_note(fig)
    fig.update_layout(**base_layout(
        title=dict(text="<b>Pyeongtaek, South Korea — City Portrait 2025</b>",
                   x=0.5, xanchor="center", font=dict(size=20, family=FONT)),
        height=500, width=900,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(t=70, b=55, l=20, r=20)
    ))
    save_html(name, fig)
    save_caption(name, """
Introducing my South Korea Data Diary 🇰🇷

I'm spending the summer in Pyeongtaek — a city most people have never heard of.

Every post: one interactive chart, real open-source data.

683,000 people. World's largest US military base. Korea's #1 car export port. World's biggest Samsung semiconductor plant.

It's also where I'm eating breakfast right now.

github.com/agkloth/south-korea-data-diary
Data: KOSIS / Pyeongtaek City Portal
#DataAnalytics #Korea #OpenData #100DaysOfData
""")

def chart_gyeonggi_cities():
    import plotly.graph_objects as go
    name = "gyeonggi-cities"
    cities = {"Suwon":1188,"Goyang":1073,"Yongin":1070,"Seongnam":929,
              "Hwaseong":907,"Bucheon":812,"Namyangju":745,"Ansan":648,
              "Pyeongtaek":608,"Anyang":551}
    df = pd.DataFrame(list(cities.items()), columns=["City","Pop"])
    df = df.sort_values("Pop", ascending=True)
    colors   = [CORAL if c=="Pyeongtaek" else BLUE for c in df["City"]]
    opacities= [1.0 if c=="Pyeongtaek" else 0.55 for c in df["City"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Pop"], y=df["City"], orientation="h",
        marker=dict(color=colors, opacity=opacities,
                    line=dict(color="white", width=0.5)),
        text=[f"  {v:,}k" for v in df["Pop"]],
        textposition="outside",
        textfont=dict(size=12, color="#444444", family=FONT),
        hovertemplate="<b>%{y}</b><br>Population: %{x:,}k<extra></extra>",
        width=0.65,
    ))
    fig.add_annotation(x=640, y="Pyeongtaek", text="  📍 I live here",
                       xanchor="left", font=dict(size=12, color=CORAL, family=FONT),
                       showarrow=False, xref="x", yref="y")
    source_note(fig)
    fig.update_layout(**base_layout(
        title=dict(text="<b>Gyeonggi Province — population by city (2023)</b><br>"
                        "<span style='font-size:13px;color:#777777'>Pyeongtaek: 9th largest, fastest growing</span>",
                   x=0.5, xanchor="center", font=dict(size=18, family=FONT)),
        height=520, width=900,
        xaxis=dict(title="Population (thousands)", range=[0,1380],
                   showgrid=True, gridcolor=GRID, tickfont=dict(size=12)),
        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
        margin=dict(t=110, b=60, l=110, r=80),
        showlegend=False,
    ))
    save_html(name, fig)
    save_caption(name, """
Pyeongtaek ranks 9th out of 31 Gyeonggi cities by population.

But it's growing faster than every city above it on this chart.

Three things driving it: Samsung's chip megaplant, Camp Humphreys expansion, and Pyeongtaek Port.

Data: KOSIS registered population statistics
github.com/agkloth/south-korea-data-diary
#DataViz #Korea #Python #Demographics
""")

def chart_three_engines():
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    name = "three-engines"
    engines = [
        dict(title="🚢  Pyeongtaek Port", color=BLUE, bg=BLUE_A,
             stats=[("#1 in Korea","automobile exports"),("#4 in Korea","container volume"),
                    ("#5 in Korea","total cargo"),("79 berths","when expansion complete")]),
        dict(title="🪖  Camp Humphreys",  color=CORAL, bg=CORAL_A,
             stats=[("Largest","US base outside America"),("42,000+","personnel & families"),
                    ("5 tril. KRW","annual economic impact"),("1982","first Songtan burger")]),
        dict(title="💻  Samsung Godeok", color=GREEN, bg=GREEN_A,
             stats=[("World's largest","semiconductor plant"),("3.95M m²","complex footprint"),
                    ("150,000","estimated employees"),("41 tril. KRW","economic effect")]),
    ]
    fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.06,
                        subplot_titles=[e["title"] for e in engines])
    for col, eng in enumerate(engines, 1):
        for i, (stat, label) in enumerate(eng["stats"]):
            y = 3 - i
            fig.add_trace(go.Scatter(x=[0.5], y=[y+0.28], mode="text",
                text=[f"<b>{stat}</b>"],
                textfont=dict(size=15, color="#111111", family=FONT),
                hovertemplate=f"<b>{stat}</b><br>{label}<extra></extra>",
                showlegend=False), row=1, col=col)
            fig.add_trace(go.Scatter(x=[0.5], y=[y-0.02], mode="text",
                text=[label], textfont=dict(size=11, color="#666666", family=FONT),
                showlegend=False, hoverinfo="skip"), row=1, col=col)
        xkey = "xaxis" if col==1 else f"xaxis{col}"
        ykey = "yaxis" if col==1 else f"yaxis{col}"
        fig.update_layout(**{xkey: dict(visible=False, range=[0,1]),
                             ykey: dict(visible=False, range=[-0.5,3.8])})
        fig.add_shape(type="rect", xref=f"x{col}", yref=f"y{col}",
                      x0=0, y0=-0.5, x1=1, y1=3.75,
                      fillcolor=eng["bg"], line=dict(color=eng["color"], width=2),
                      layer="below")
    for ann in fig.layout.annotations:
        ann.font = dict(size=14, color="#222222", family=FONT)
    source_note(fig)
    fig.update_layout(**base_layout(
        title=dict(text="<b>The three engines driving Pyeongtaek's growth</b>",
                   x=0.5, xanchor="center", font=dict(size=18, family=FONT)),
        height=440, width=980,
        margin=dict(t=90, b=55, l=20, r=20),
    ))
    save_html(name, fig)
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
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    name = "camp-humphreys"
    fig = make_subplots(rows=1, cols=2, column_widths=[0.45,0.55],
                        subplot_titles=["Size comparison","Key metrics"],
                        horizontal_spacing=0.10)
    for label, area, color, opacity in [
        ("Camp Humphreys",14.7,CORAL,1.0),
        ("Central Park NYC",3.4,GRAY,0.7),
        ("Vatican City",0.44,"#B4B2A9",0.6)]:
        fig.add_trace(go.Scatter(
            x=[area], y=[0.5], mode="markers+text",
            marker=dict(size=area**0.5*38, color=color, opacity=opacity,
                        line=dict(color="white",width=1)),
            text=[f"<b>{label}</b><br>{area} km²"],
            textposition="bottom center", textfont=dict(size=11, family=FONT),
            hovertemplate=f"<b>{label}</b><br>{area} km²<extra></extra>",
            showlegend=False), row=1, col=1)
    for metric, val, color in [
        ("Land area (km²)",14.7,GREEN),
        ("Personnel (thousands)",42,CORAL),
        ("Economic impact (bil. USD)",3.7,BLUE)]:
        fig.add_trace(go.Bar(
            x=[val], y=[metric], orientation="h",
            marker=dict(color=color, opacity=0.85, line=dict(color="white",width=0.5)),
            text=[f"<b>{val}</b>"], textposition="outside",
            textfont=dict(size=13, family=FONT),
            hovertemplate=f"<b>{metric}</b>: {val}<extra></extra>",
            width=0.45, showlegend=False), row=1, col=2)
    fig.update_xaxes(visible=False, row=1, col=1)
    fig.update_yaxes(visible=False, row=1, col=1)
    fig.update_xaxes(showgrid=True, gridcolor=GRID, range=[0,52],
                     tickfont=dict(size=12), row=1, col=2)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=12), row=1, col=2)
    source_note(fig)
    fig.update_layout(**base_layout(
        title=dict(text="<b>Camp Humphreys — by the numbers</b><br>"
                        "<span style='font-size:13px;color:#777777'>Largest US military base outside America</span>",
                   x=0.5, xanchor="center", font=dict(size=18, family=FONT)),
        height=440, width=960,
        margin=dict(t=110, b=60, l=20, r=80),
        showlegend=False,
    ))
    save_html(name, fig)
    save_caption(name, """
Camp Humphreys is the largest US military base outside of America.

Bigger than Vatican City by 33x. Bigger than Central Park by 4x.

42,000 Americans live inside those gates. Economic impact: ~$3.7 billion USD per year.

Almost no one has run a data analysis on what that does to a city. That's what I'm here to find out.

Sources: US Army public releases, KOSIS
github.com/agkloth/south-korea-data-diary
#CampHumphreys #Pyeongtaek #DataAnalysis #Korea
""")

def chart_population_growth():
    import plotly.graph_objects as go
    name = "population-growth"
    years = [2000,2005,2010,2015,2018,2020,2022,2024]
    pop   = [342, 390, 432, 480, 520, 553, 594, 640]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=pop, mode="lines+markers",
        line=dict(color=CORAL, width=3, shape="spline"),
        marker=dict(size=9, color=CORAL, line=dict(color="white",width=2)),
        fill="tozeroy", fillcolor=CORAL_F,
        hovertemplate="<b>%{x}</b><br>Population: %{y}k<extra></extra>",
        showlegend=False,
    ))
    for yr, label, y_pos, ax, ay in [
        (2011,"Samsung Godeok\nbreaking ground",445, 45,-30),
        (2017,"Camp Humphreys\nexpansion complete",535, 45,-30)]:
        fig.add_vline(x=yr, line_dash="dot", line_color="#CCCCCC", line_width=1.5)
        fig.add_annotation(x=yr, y=y_pos, text=label, showarrow=True,
                           arrowhead=2, arrowcolor="#AAAAAA", arrowwidth=1,
                           font=dict(size=10, color="#555555", family=FONT),
                           bgcolor="white", bordercolor="#CCCCCC",
                           borderwidth=1, ax=ax, ay=ay)
    source_note(fig)
    fig.update_layout(**base_layout(
        title=dict(text="<b>Pyeongtaek population growth — 2000 to 2024</b><br>"
                        "<span style='font-size:13px;color:#777777'>Nearly doubled in 24 years</span>",
                   x=0.5, xanchor="center", font=dict(size=18, family=FONT)),
        height=460, width=960,
        xaxis=dict(title="Year", tickvals=years, showgrid=False,
                   tickfont=dict(size=12)),
        yaxis=dict(title="Population (thousands)", range=[0,720],
                   showgrid=True, gridcolor=GRID, tickfont=dict(size=12)),
        margin=dict(t=100, b=70, l=75, r=40),
    ))
    save_html(name, fig)
    save_caption(name, """
Pyeongtaek's population nearly doubled in 24 years.

342,000 in 2000. 640,000+ today.

That's not natural growth — that's three mega-projects arriving at once.

Hover over the chart to explore every data point.

Data: KOSIS / worldpopulationreview.com
github.com/agkloth/south-korea-data-diary
#Pyeongtaek #Demographics #Korea #DataViz
""")

def chart_port_cargo():
    import plotly.graph_objects as go
    name = "port-cargo"
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    cargo  = [4821,4102,5234,5012,5401,5198,5367,5289,5412,5601,5234,4987]
    peak_idx = cargo.index(max(cargo))
    colors    = [CORAL if i==peak_idx else BLUE for i in range(len(cargo))]
    opacities = [1.0 if i==peak_idx else 0.65 for i in range(len(cargo))]
    avg = sum(cargo)/len(cargo)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months, y=cargo,
        marker=dict(color=colors, opacity=opacities,
                    line=dict(color="white",width=0.8)),
        text=[f"{v:,}" for v in cargo],
        textposition="outside", textfont=dict(size=11, color="#444444", family=FONT),
        hovertemplate="<b>%{x}</b><br>%{y:,} thousand tonnes<extra></extra>",
        width=0.65,
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color="#AAAAAA", line_width=1.5,
                  annotation_text=f"  Avg: {avg:,.0f}",
                  annotation_position="right",
                  annotation_font=dict(size=11, color="#888888", family=FONT))
    source_note(fig)
    fig.update_layout(**base_layout(
        title=dict(text="<b>Pyeongtaek Port — monthly cargo volume 2023</b><br>"
                        "<span style='font-size:13px;color:#777777'>#1 in Korea for automobile exports · Feb dip = Lunar New Year · Oct peak = pre year-end surge</span>",
                   x=0.5, xanchor="center", font=dict(size=18, family=FONT)),
        height=480, width=980,
        xaxis=dict(showgrid=False, tickfont=dict(size=12)),
        yaxis=dict(title="Cargo (thousand tonnes)", range=[3400,6200],
                   showgrid=True, gridcolor=GRID, tickfont=dict(size=12)),
        margin=dict(t=110, b=70, l=90, r=110),
        showlegend=False,
    ))
    save_html(name, fig)
    save_caption(name, """
Pyeongtaek Port moves more cars than any other port in Korea.

Monthly cargo volume 2023 — over 62 million tonnes for the year.

Feb dip: Lunar New Year slowdown. Oct peak: Hyundai/Kia pre year-end export surge.

Hover over any bar for exact figures.

Data: Gyeonggi Pyeongtaek Port Authority (gppc.or.kr)
github.com/agkloth/south-korea-data-diary
#PyeongtaekPort #Korea #TradeData #DataViz
""")

def chart_air_quality():
    import plotly.graph_objects as go
    name = "air-quality"
    reading = fetch_air_quality()
    if reading:
        append_air_log(reading)
    log_path = DATA_DIR / "air_quality_log.csv"
    fig = go.Figure()
    if log_path.exists() and reading:
        df = pd.read_csv(log_path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["pm25"], mode="lines+markers",
            line=dict(color=BLUE, width=2.5),
            marker=dict(size=7, color=BLUE, line=dict(color="white",width=1.5)),
            fill="tozeroy", fillcolor=BLUE_F,
            hovertemplate="<b>%{x|%b %d}</b><br>PM2.5: %{y} µg/m³<extra></extra>",
            showlegend=False,
        ))
        for level, color, label in [
            (15,GREEN,"WHO good (15)"),
            (35,"#BA7517","Moderate (35)"),
            (75,CORAL,"Unhealthy (75)")]:
            fig.add_hline(y=level, line_dash="dot", line_color=color, line_width=1.2,
                          annotation_text=f"  {label}",
                          annotation_position="right",
                          annotation_font=dict(size=10, color=color, family=FONT))
        pm25_now = reading["pm25"]
    else:
        fig.add_annotation(
            text="Add AIRKOREA_KEY to GitHub Secrets<br>to see live Pyeongtaek air quality data",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color="#AAAAAA", family=FONT))
        pm25_now = "N/A"
    source_note(fig)
    fig.update_layout(**base_layout(
        title=dict(text=f"<b>Pyeongtaek PM2.5 — {today_label()}</b><br>"
                        "<span style='font-size:13px;color:#777777'>Hover over any point for exact reading · WHO good threshold = 15 µg/m³</span>",
                   x=0.5, xanchor="center", font=dict(size=18, family=FONT)),
        height=460, width=960,
        xaxis=dict(title="Date", showgrid=False, tickfont=dict(size=12)),
        yaxis=dict(title="PM2.5 (µg/m³)", showgrid=True, gridcolor=GRID, tickfont=dict(size=12)),
        margin=dict(t=110, b=70, l=75, r=130),
    ))
    save_html(name, fig)
    save_caption(name, f"""
Pyeongtaek air quality — {today_label()}

Today's PM2.5: {pm25_now} µg/m³

Tracking this all summer. Port activity, Yellow Dust season, and wind direction all show up in this line.

Hover over the chart to explore every reading.

Data: AirKorea API (airkorea.or.kr)
github.com/agkloth/south-korea-data-diary
#AirQuality #Pyeongtaek #OpenData #Korea
""")

CHARTS = {
    "city-portrait":     chart_city_portrait,
    "gyeonggi-cities":   chart_gyeonggi_cities,
    "three-engines":     chart_three_engines,
    "camp-humphreys":    chart_camp_humphreys,
    "population-growth": chart_population_growth,
    "port-cargo":        chart_port_cargo,
    "air-quality":       chart_air_quality,
}

def main():
    print(f"Generating: '{CHART_NAME}'")
    fn = CHARTS.get(CHART_NAME)
    if not fn:
        print(f"Unknown. Options: {list(CHARTS.keys())}"); return
    fn()
    print("Done.")

if __name__ == "__main__":
    main()
