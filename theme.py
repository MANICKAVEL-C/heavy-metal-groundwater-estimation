# ============================================================
# theme.py - Visual design system for the dashboard
# ============================================================
# DESIGN TOKENS (documented for the team, explain if asked in viva)
#
# Concept: "Groundwater instrument panel" - the dashboard should feel
# like a real scientific field instrument a government officer would
# use, not a generic web app. Every color and texture choice ties
# back to the actual subject matter.
#
# COLOR:
#   Deep Basin     #0A1418  - main background, evokes depth/night survey
#   Slate Surface  #13242C  - card/panel background
#   Slate Surface 2 #1A2E37 - hover/secondary surface
#   Aquifer Teal   #2A9D8F  - primary accent, interactive elements
#   Rust Alert     #B5502A  - "Highly Polluted" - evokes oxidized metal
#   Ochre Caution  #C99A44  - "Moderate" - mineral/soil tone
#   Moss Safe      #5C9271  - "Safe" - muted natural green
#   Text Primary   #E8EEF0
#   Text Muted     #7E93A0
#
# TYPE:
#   Display/headers: "Space Grotesk" - geometric, technical character
#   Body:            "IBM Plex Sans" - clean, engineered, readable
#   Data readouts:   "IBM Plex Mono" - for HPI numbers, ppm values,
#                    coordinates - like a real instrument's digital display
#
# SIGNATURE ELEMENT:
#   Topographic contour-line texture, subtly present in the hero
#   banner and card backgrounds - directly references the Kriging
#   spatial contamination maps that are the actual scientific output
#   of this project, rather than being purely decorative.
# ============================================================

import base64
import os

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")

def _b64(filename):
    with open(os.path.join(_ASSETS, filename), "rb") as f:
        return base64.b64encode(f.read()).decode()

_HERO_TEXTURE = _b64("contour_hero.png")
_CARD_TEXTURE = _b64("contour_card.png")


def inject_css():
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root {{
    --bg-deep: #0A1418;
    --surface: #13242C;
    --surface-2: #1A2E37;
    --border: #234049;
    --teal: #2A9D8F;
    --teal-soft: #2A9D8F33;
    --rust: #C4602F;
    --ochre: #C99A44;
    --moss: #5FA37A;
    --text-primary: #E8EEF0;
    --text-muted: #7E93A0;
}}

html, body, .stApp {{
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] * {{
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--teal) !important;
    margin-top: 1.2rem;
}}

/* ---------- Headings ---------- */
h1, h2, h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
}}
h3 {{
    font-size: 1.05rem !important;
    letter-spacing: 0.02em;
}}

/* ---------- Hero banner ---------- */
.hero {{
    position: relative;
    padding: 2.1rem 2.4rem 1.9rem 2.4rem;
    margin-bottom: 1.6rem;
    border-radius: 14px;
    background:
        linear-gradient(120deg, rgba(10,20,24,0.94) 0%, rgba(19,36,44,0.90) 100%),
        url("data:image/png;base64,{_HERO_TEXTURE}");
    background-size: cover;
    background-position: center;
    border: 1px solid var(--border);
    overflow: hidden;
}}
.hero-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--teal);
    margin-bottom: 0.5rem;
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

/* ---------- Section eyebrow labels ---------- */
.section-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--teal);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 1.6rem 0 1rem 0;
}}

/* ---------- Cards ---------- */
.panel {{
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}}

/* ---------- Result readout card ---------- */
.readout {{
    background:
        linear-gradient(120deg, rgba(19,36,44,0.97) 0%, rgba(19,36,44,0.90) 100%),
        url("data:image/png;base64,{_CARD_TEXTURE}");
    background-size: cover;
    border-radius: 14px;
    padding: 1.5rem 1.7rem;
    border-left: 5px solid var(--sev-color, var(--teal));
    border-top: 1px solid var(--border);
    border-right: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.1rem;
}}
.readout-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}}
.readout-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.6rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.7rem;
}}
.badge {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    color: #0A1418;
}}
.badge-safe {{ background-color: var(--moss); }}
.badge-moderate {{ background-color: var(--ochre); }}
.badge-polluted {{ background-color: var(--rust); }}

/* ---------- Buttons ---------- */
.stButton > button {{
    background-color: var(--teal) !important;
    color: #0A1418 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    transition: filter 0.15s ease;
}}
.stButton > button:hover {{
    filter: brightness(1.12);
}}
[data-testid="stDownloadButton"] button {{
    background-color: var(--surface-2) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--teal) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    background-color: var(--teal-soft) !important;
}}

/* ---------- Inputs ---------- */
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{
    background-color: var(--surface-2) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}}
.stSlider [data-baseweb="slider"] {{
    color: var(--teal) !important;
}}
label, .stRadio label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stSlider label {{
    color: var(--text-muted) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.88rem !important;
}}

/* ---------- Alerts (info/warning/error/success) ---------- */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}}

/* ---------- Caption / footer ---------- */
.stCaption, [data-testid="stCaptionContainer"] {{
    color: var(--text-muted) !important;
}}
.footer-strip {{
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    padding: 1.2rem 0 0.4rem 0;
    border-top: 1px solid var(--border);
    margin-top: 1.5rem;
}}

hr {{
    border-color: var(--border) !important;
}}
</style>
"""


def severity_color(category):
    return {"Safe": "#5FA37A", "Moderate": "#C99A44", "Highly Polluted": "#C4602F"}.get(category, "#2A9D8F")


def badge_class(category):
    return {"Safe": "badge-safe", "Moderate": "badge-moderate", "Highly Polluted": "badge-polluted"}.get(category, "badge-safe")
