# ==============================================================================
# theme.py - Dual-Mode Design System (Dark Instrument & Clean Light Lab)
# Project: AI-Driven Assessment of Heavy Metal Pollution Indices
# ==============================================================================

import base64
import os

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")

def _b64(filename):
    p = os.path.join(_ASSETS, filename)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

_HERO_TEXTURE = _b64("contour_hero.png")
_CARD_TEXTURE = _b64("contour_card.png")

def inject_css(theme_mode: str = "Dark"):
    is_dark = (theme_mode.lower() == "dark")
    
    if is_dark:
        # Dark Instrument Theme Tokens
        bg_deep = "#0A1418"
        surface = "#13242C"
        surface_2 = "#1A2E37"
        border = "#234049"
        border_subtle = "#192F38"
        teal = "#2A9D8F"
        teal_soft = "rgba(42, 157, 143, 0.20)"
        rust = "#C4602F"
        ochre = "#C99A44"
        moss = "#5FA37A"
        text_primary = "#E8EEF0"
        text_muted = "#8CA2B0"
        card_text_color = "#E8EEF0"
        hero_gradient = f"linear-gradient(120deg, rgba(10,20,24,0.95) 0%, rgba(19,36,44,0.92) 100%), url('data:image/png;base64,{_HERO_TEXTURE}')"
        readout_gradient = f"linear-gradient(120deg, rgba(19,36,44,0.98) 0%, rgba(19,36,44,0.90) 100%), url('data:image/png;base64,{_CARD_TEXTURE}')"
        badge_text_col = "#0A1418"
        shadow = "0 4px 20px rgba(0,0,0,0.35)"
    else:
        # Clean Scientific Light Theme Tokens
        bg_deep = "#F3F7F9"
        surface = "#FFFFFF"
        surface_2 = "#EDF4F7"
        border = "#CFDFE6"
        border_subtle = "#E4EEF2"
        teal = "#147A6E"
        teal_soft = "rgba(20, 122, 110, 0.12)"
        rust = "#B83A14"
        ochre = "#B3740E"
        moss = "#287D4E"
        text_primary = "#0E1E26"
        text_muted = "#4D6674"
        card_text_color = "#0E1E26"
        hero_gradient = f"linear-gradient(120deg, rgba(240,246,249,0.96) 0%, rgba(225,238,243,0.93) 100%), url('data:image/png;base64,{_HERO_TEXTURE}')"
        readout_gradient = f"linear-gradient(120deg, rgba(255,255,255,0.98) 0%, rgba(243,248,250,0.94) 100%), url('data:image/png;base64,{_CARD_TEXTURE}')"
        badge_text_col = "#FFFFFF"
        shadow = "0 4px 18px rgba(15,31,39,0.06)"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {{
    --bg-deep: {bg_deep};
    --surface: {surface};
    --surface-2: {surface_2};
    --border: {border};
    --border-subtle: {border_subtle};
    --teal: {teal};
    --teal-soft: {teal_soft};
    --rust: {rust};
    --ochre: {ochre};
    --moss: {moss};
    --text-primary: {text_primary};
    --text-muted: {text_muted};
    --card-text: {card_text_color};
    --shadow: {shadow};
}}

html, body, .stApp {{
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    transition: background-color 0.25s ease, color 0.25s ease;
}}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] * {{
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--teal) !important;
    margin-top: 1.1rem;
}}

/* ---------- Headings ---------- */
h1, h2, h3, h4 {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
}}
h3 {{
    font-size: 1.10rem !important;
    letter-spacing: 0.02em;
}}

/* ---------- Hero banner ---------- */
.hero {{
    position: relative;
    padding: 2.1rem 2.4rem 1.9rem 2.4rem;
    margin-bottom: 1.4rem;
    border-radius: 14px;
    background: {hero_gradient};
    background-size: cover;
    background-position: center;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    overflow: hidden;
}}
.hero-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--teal);
    font-weight: 600;
    margin-bottom: 0.45rem;
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.05rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.15;
    margin: 0 0 0.4rem 0;
}}
.hero-subtitle {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.92rem;
    color: var(--text-muted);
}}

/* ---------- Cards & Panels ---------- */
.panel {{
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
    color: var(--card-text) !important;
}}
.panel * {{
    color: var(--card-text);
}}

/* ---------- Result Readout Card ---------- */
.readout {{
    background: {readout_gradient};
    background-size: cover;
    border-radius: 14px;
    padding: 1.5rem 1.7rem;
    border-left: 6px solid var(--sev-color, var(--teal));
    border-top: 1px solid var(--border);
    border-right: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    box-shadow: var(--shadow);
    margin-bottom: 1.1rem;
}}
.readout-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-weight: 600;
    margin-bottom: 0.3rem;
}}
.readout-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.7rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.6rem;
}}
.badge {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 0.32rem 0.95rem;
    border-radius: 999px;
    color: {badge_text_col} !important;
}}
.badge-safe {{ background-color: var(--moss); }}
.badge-moderate {{ background-color: var(--ochre); }}
.badge-polluted {{ background-color: var(--rust); }}

/* ---------- Buttons ---------- */
.stButton > button {{
    background-color: var(--teal) !important;
    color: #FFFFFF !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    transition: filter 0.15s ease, transform 0.1s ease;
}}
.stButton > button:hover {{
    filter: brightness(1.10);
    transform: translateY(-1px);
}}
[data-testid="stDownloadButton"] button {{
    background-color: var(--surface-2) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--teal) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    background-color: var(--teal-soft) !important;
}}

/* ---------- Inputs, Sliders & Selectboxes ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{
    background-color: var(--surface-2) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}}
.stSelectbox svg {{
    fill: var(--text-primary) !important;
}}
label, .stRadio label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label {{
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}}

/* ---------- Tabs ---------- */
[data-baseweb="tab-list"] {{
    background-color: transparent !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 8px;
}}
[data-baseweb="tab"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    padding: 0.55rem 1rem !important;
    border-radius: 8px 8px 0 0 !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    color: var(--teal) !important;
    border-bottom: 3px solid var(--teal) !important;
}}

/* ---------- Metric Cards ---------- */
[data-testid="stMetricValue"] {{
    font-family: 'IBM Plex Mono', monospace !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricLabel"] {{
    font-family: 'IBM Plex Sans', sans-serif !important;
    color: var(--text-muted) !important;
}}

/* ---------- Dataframes & Tables ---------- */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}}

/* ---------- Footer & Dividers ---------- */
.footer-strip {{
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    padding: 1.4rem 0 0.5rem 0;
    border-top: 1px solid var(--border);
    margin-top: 1.8rem;
}}
hr {{
    border-color: var(--border) !important;
}}
</style>
"""

def severity_color(category: str, theme_mode: str = "Dark"):
    is_dark = (theme_mode.lower() == "dark")
    if is_dark:
        return {"Safe": "#5FA37A", "Moderate": "#C99A44", "Highly Polluted": "#C4602F"}.get(category, "#2A9D8F")
    else:
        return {"Safe": "#287D4E", "Moderate": "#B3740E", "Highly Polluted": "#B83A14"}.get(category, "#147A6E")

def badge_class(category: str):
    return {"Safe": "badge-safe", "Moderate": "badge-moderate", "Highly Polluted": "badge-polluted"}.get(category, "badge-safe")
