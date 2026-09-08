
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

from src.profiling import profile_dataset
from src.detection import run_detection
from src.repair import run_repairs
from src.scoring import calculate_quality_score
from src.validation import validate_dataset
from src.reporting import (
    create_repair_log,
    generate_quality_report,
    save_quality_report,
)

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="DataFlow Quality — Intelligent Data Operations",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "theme" not in st.session_state:
    st.session_state.theme = "system"
if "explore_features" not in st.session_state:
    st.session_state.explore_features = False
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None

# =========================================================
# THEME
# =========================================================
theme = st.session_state.theme

if theme == "dark":
    palette = {
        "bg": "#070b12",
        "surface": "#0d131d",
        "surface2": "#121a25",
        "surface3": "#172130",
        "text": "#f6f8fb",
        "muted": "#8f9bab",
        "line": "rgba(255,255,255,.09)",
        "accent": "#7668f6",
        "accent2": "#55d9e9",
        "soft": "rgba(118,104,246,.10)",
        "shadow": "rgba(0,0,0,.34)",
        "hero": "#0b111a",
    }

elif theme == "light":
    palette = {
        "bg": "#e7ebf0",
        "surface": "#f0f3f6",
        "surface2": "#e9edf2",
        "surface3": "#dfe5eb",
        "text": "#0b1220",
        "muted": "#131415",  # changed: darker for better light-theme visibility
        "line": "rgba(15,23,42,.16)",
        "accent": "#5146d8",
        "accent2": "#07899b",
        "soft": "rgba(81,70,216,.09)",
        "shadow": "rgba(15,23,42,.14)",
        "hero": "#f4f6f8",
    }


else:
    palette = {
        "bg": "#e7ebf0",
        "surface": "#f0f3f6",
        "surface2": "#e9edf2",
        "surface3": "#dfe5eb",
        "text": "#0b1220",
        "muted": "#334155",
        "line": "rgba(15,23,42,.16)",
        "accent": "#5146d8",
        "accent2": "#07899b",
        "soft": "rgba(81,70,216,.09)",
        "shadow": "rgba(15,23,42,.14)",
        "hero": "#f4f6f8",
    }

# System mode follows the OS preference while keeping a softer, eye-friendly light surface.
if theme == "system":
    system_css = """
@media (prefers-color-scheme: dark) {
    :root {
        --bg:#080d14;
        --surface:#101720;
        --surface2:#151e29;
        --surface3:#1b2633;
        --text:#f8fafc;
        --muted:#b5c0ce;
        --line:rgba(255,255,255,.12);
        --accent:#8174ff;
        --accent2:#62dbea;
        --soft:rgba(129,116,255,.12);
        --shadow:rgba(0,0,0,.34);
    }
}
"""
else:
    system_css = ""

# =========================================================
# MASTERCLASS CSS
# =========================================================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {{
    --bg:{palette["bg"]};
    --surface:{palette["surface"]};
    --surface2:{palette["surface2"]};
    --surface3:{palette["surface3"]};
    --text:{palette["text"]};
    --muted:{palette["muted"]};
    --line:{palette["line"]};
    --accent:{palette["accent"]};
    --accent2:{palette["accent2"]};
    --soft:{palette["soft"]};
    --shadow:{palette["shadow"]};
}}
{system_css}

html, body, [class*="css"] {{
    font-family:"DM Sans",Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}}

.stApp {{
    color:var(--text);
    background:
        radial-gradient(900px 500px at 88% -4%, rgba(91,82,232,.12), transparent 62%),
        radial-gradient(800px 480px at -8% 30%, rgba(24,174,191,.075), transparent 64%),
        var(--bg);
}}

[data-testid="stHeader"] {{
    background:rgba(255,255,255,.02);
    border-bottom:1px solid var(--line);
}}

.block-container {{
    max-width:1500px;
    padding:1.05rem 2.2rem 5rem;
}}

#MainMenu, footer {{
    visibility:hidden;
}}

h1,h2,h3,h4,h5 {{
    font-family:"Manrope",Inter,sans-serif !important;
    color:var(--text) !important;
    letter-spacing:-.045em !important;
}}

p, li {{
    color:var(--muted);
}}

button {{
    font-family:"DM Sans",sans-serif !important;
}}

hr {{
    border:0 !important;
    border-top:1px solid var(--line) !important;
    margin:2rem 0 !important;
}}

.small-label {{
    color:var(--muted);
    text-transform:uppercase;
    letter-spacing:.16em;
    font-size:.66rem;
    font-weight:800;
}}

.topbar {{
    display:flex;
    align-items:center;
    justify-content:space-between;
    min-height:58px;
    padding:.35rem .15rem;
    margin-top:45px;   /* moves the navbar down */
    border-bottom:1px solid var(--line);
    background:var(--bg);
    box-shadow:none;
    position:relative;
    z-index:30;
}}

.logo {{
    display:flex;
    align-items:center;
    gap:.7rem;
    min-width:190px;
}}

.logo-mark {{
    width:37px;
    height:37px;
    display:grid;
    place-items:center;
    border-radius:12px;
    color:white;
    font-weight:900;
    font-size:.72rem;
    background:linear-gradient(135deg,#8376ff,#5449dc);
    box-shadow:0 8px 24px rgba(92,82,232,.28);
}}

.logo-title {{
    font-family:"Manrope",sans-serif;
    font-weight:800;
    color:var(--text);
    font-size:1rem;
    letter-spacing:-.035em;
}}

.logo-title span {{
    color:var(--muted);
    font-weight:500;
}}

.nav-hint {{
    text-align:center;
    color:var(--muted);
    font-size:.74rem;
}}

.nav-right {{
    display:flex;
    align-items:center;
    gap:.5rem;
}}

.pill {{
    display:inline-flex;
    align-items:center;
    gap:.4rem;
    padding:.48rem .7rem;
    border-radius:999px;
    background:var(--soft);
    border:1px solid color-mix(in srgb, var(--accent) 25%, transparent);
    color:var(--accent);
    font-size:.68rem;
    font-weight:800;
}}

.hero {{
    margin-top:1.1rem;
    min-height:575px;
    border:1px solid var(--line);
    border-radius:32px;
    overflow:hidden;
    position:relative;
    background:
        radial-gradient(580px 390px at 85% 25%, rgba(92,82,232,.16), transparent 68%),
        radial-gradient(480px 330px at 12% 92%, rgba(24,174,191,.09), transparent 68%),
        linear-gradient(145deg, color-mix(in srgb, var(--surface) 94%, transparent), var(--hero));
    box-shadow:0 28px 90px var(--shadow);
}}

.hero:before {{
    content:"";
    position:absolute;
    inset:0;
    background-image:
        linear-gradient(rgba(120,130,150,.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(120,130,150,.045) 1px, transparent 1px);
    background-size:44px 44px;
    mask-image:linear-gradient(to bottom, black, transparent 88%);
    pointer-events:none;
}}

.hero-inner {{
    position:relative;
    z-index:2;
    display:grid;
    grid-template-columns:1.02fr .98fr;
    gap:3.3rem;
    align-items:center;
    padding:5rem 4.1rem 3.5rem;
}}

.eyebrow {{
    display:inline-flex;
    align-items:center;
    gap:.5rem;
    padding:.42rem .72rem;
    border-radius:999px;
    border:1px solid color-mix(in srgb, var(--accent) 28%, transparent);
    background:var(--soft);
    color:var(--accent);
    font-size:.67rem;
    font-weight:800;
    letter-spacing:.11em;
    text-transform:uppercase;
}}

.hero-title {{
    font-family:"Manrope",sans-serif;
    font-size:clamp(3.15rem,6.2vw,6.4rem);
    line-height:.9;
    font-weight:800;
    letter-spacing:-.075em;
    margin:1.25rem 0 1.2rem;
    color:var(--text);
}}

.hero-title .gradient {{
    background:linear-gradient(100deg,var(--accent),#8e7cff 45%,var(--accent2));
    -webkit-background-clip:text;
    background-clip:text;
    color:transparent;
}}

.hero-copy {{
    max-width:650px;
    color:var(--muted);
    font-size:1.05rem;
    line-height:1.8;
}}

.hero-trust {{
    margin-top:1.25rem;
    display:flex;
    gap:1rem;
    flex-wrap:wrap;
    color:var(--muted);
    font-size:.72rem;
}}

.hero-trust span {{
    padding-right:1rem;
    border-right:1px solid var(--line);
}}

.hero-trust span:last-child {{ border-right:0; }}

.preview {{
    border:1px solid var(--line);
    border-radius:24px;
    padding:.65rem;
    background:rgba(8,13,22,.84);
    box-shadow:0 35px 100px rgba(0,0,0,.27);
    transform:perspective(1000px) rotateY(-4deg) rotateX(2deg);
    transition:transform .5s ease, box-shadow .5s ease;
}}

.preview:hover {{
    transform:perspective(1000px) rotateY(0) rotateX(0) translateY(-6px);
    box-shadow:0 45px 120px rgba(92,82,232,.20);
}}

.preview-bar {{
    display:flex;
    align-items:center;
    gap:5px;
    height:27px;
    padding:0 .5rem;
    color:#8490a1;
    font-size:.57rem;
}}

.dot {{ width:6px;height:6px;border-radius:50%;background:#3d4755; }}

.preview-main {{
    padding:1.05rem;
    border-radius:16px;
    background:#101824;
    border:1px solid rgba(255,255,255,.07);
}}

.preview-head {{
    display:flex;
    justify-content:space-between;
    align-items:center;
}}

.preview-head strong {{ color:#f7f8fb;font-size:.78rem; }}
.preview-head span {{ color:#63dfae;font-size:.58rem;font-weight:800; }}

.preview-score {{
    display:flex;
    gap:1rem;
    align-items:center;
    margin:1rem 0;
}}

.ring {{
    width:78px;height:78px;border-radius:50%;
    display:grid;place-items:center;
    background:conic-gradient(#58d7a0 0 94%, #253140 94%);
    position:relative;
}}

.ring:after {{
    content:"";position:absolute;inset:7px;border-radius:50%;background:#101824;
}}

.ring b {{ position:relative;z-index:2;color:#fff;font-size:1.05rem; }}

.preview-cards {{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:.55rem;
}}

.preview-card {{
    padding:.72rem;
    border:1px solid rgba(255,255,255,.07);
    border-radius:11px;
    background:rgba(255,255,255,.025);
}}

.preview-card small {{ display:block;color:#788596;font-size:.54rem; }}
.preview-card strong {{ display:block;color:#f1f4f8;font-size:.88rem;margin-top:.25rem; }}

.chart {{
    height:92px;
    margin-top:.7rem;
    border-radius:12px;
    position:relative;
    overflow:hidden;
    background:
        linear-gradient(180deg,rgba(118,104,246,.13),transparent),
        repeating-linear-gradient(90deg,transparent 0 44px,rgba(255,255,255,.035) 45px 46px);
}}

.chart:after {{
    content:"";
    position:absolute;
    left:-3%;
    right:-3%;
    top:49%;
    height:2px;
    background:linear-gradient(90deg,#6254e8,#8d7fff,#52d5e3,#55d9a0);
    transform:skewY(-7deg);
    box-shadow:0 0 22px rgba(118,104,246,.55);
}}

.section {{
    padding:4.4rem .5rem 0;
}}

.section-center {{
    text-align:center;
    max-width:790px;
    margin:auto;
}}

.section-center h2 {{
    font-size:clamp(2rem,4vw,3.35rem) !important;
    margin:.55rem 0 .8rem;
}}

.section-center p {{
    font-size:.98rem;
    line-height:1.75;
}}

.feature-grid {{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:1rem;
    margin-top:2rem;
}}

.feature-card {{
    min-height:215px;
    padding:1.45rem;
    border:1px solid var(--line);
    border-radius:22px;
    background:linear-gradient(145deg,var(--surface),var(--surface2));
    box-shadow:0 16px 45px var(--shadow);
    transition:transform .28s ease,border-color .28s ease,box-shadow .28s ease;
    position:relative;
    overflow:hidden;
}}

.feature-card:before {{
    content:"";
    position:absolute;
    width:120px;height:120px;
    right:-40px;top:-45px;
    border-radius:50%;
    background:var(--soft);
    filter:blur(2px);
}}

.feature-card:hover {{
    transform:translateY(-8px) translateX(2px);
    border-color:color-mix(in srgb, var(--accent) 35%, transparent);
    box-shadow:0 25px 60px var(--shadow);
}}

.feature-num {{
    color:var(--accent);
    font-size:.64rem;
    letter-spacing:.13em;
    font-weight:900;
}}

.feature-icon {{
    width:42px;height:42px;
    display:grid;place-items:center;
    border-radius:13px;
    margin:1rem 0;
    color:var(--accent);
    background:var(--soft);
    border:1px solid color-mix(in srgb, var(--accent) 20%, transparent);
    font-size:1rem;
}}

.feature-card h3 {{
    font-size:1rem !important;
    margin:0 0 .4rem;
}}

.feature-card p {{
    font-size:.76rem;
    line-height:1.65;
}}

.arrow {{
    display:inline-flex;
    margin-top:.7rem;
    color:var(--accent);
    font-size:.72rem;
    font-weight:800;
    transition:transform .25s ease;
}}

.feature-card:hover .arrow {{ transform:translateX(7px); }}

.split {{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:1rem;
    margin-top:2rem;
}}

.panel {{
    padding:2rem;
    min-height:330px;
    border:1px solid var(--line);
    border-radius:24px;
    background:linear-gradient(145deg,var(--surface),var(--surface2));
    box-shadow:0 18px 55px var(--shadow);
}}

.panel h3 {{ font-size:1.25rem !important;margin:.6rem 0; }}
.panel p {{ line-height:1.7;font-size:.82rem; }}

.timeline {{
    margin-top:1.2rem;
    display:grid;
    gap:.75rem;
}}

.step {{
    display:grid;
    grid-template-columns:42px 1fr;
    gap:.8rem;
    align-items:start;
    padding:.8rem;
    border:1px solid var(--line);
    border-radius:14px;
    background:var(--surface2);
}}

.step-num {{
    width:35px;height:35px;
    display:grid;place-items:center;
    border-radius:10px;
    background:var(--soft);
    color:var(--accent);
    font-weight:900;
    font-size:.7rem;
}}

.step strong {{ color:var(--text);font-size:.76rem; }}
.step span {{ display:block;color:var(--muted);font-size:.68rem;margin-top:.18rem;line-height:1.45; }}

.price-grid {{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:1rem;
    margin-top:2rem;
}}

.price-card {{
    padding:1.8rem;
    border:1px solid var(--line);
    border-radius:24px;
    background:var(--surface);
    box-shadow:0 16px 45px var(--shadow);
}}

.price-card.featured {{
    border-color:color-mix(in srgb,var(--accent) 40%, transparent);
    box-shadow:0 25px 65px rgba(92,82,232,.14);
    transform:translateY(-8px);
}}

.price-name {{ font-weight:800;color:var(--text); }}
.price {{
    font-family:"Manrope",sans-serif;
    font-size:2.8rem;
    font-weight:800;
    color:var(--text);
    margin:.7rem 0;
}}
.price small {{ font-size:.7rem;color:var(--muted);font-weight:500; }}
.price-card ul {{ padding-left:1.05rem;line-height:2;font-size:.75rem; }}

.quote {{
    margin-top:2rem;
    padding:2rem;
    border:1px solid var(--line);
    border-radius:24px;
    background:linear-gradient(135deg,var(--soft),var(--surface));
}}

.quote p {{ font-size:1.05rem;line-height:1.7;color:var(--text); }}
.quote span {{ color:var(--muted);font-size:.72rem; }}

.cta {{
    margin-top:4.5rem;
    padding:3.4rem;
    border-radius:28px;
    border:1px solid color-mix(in srgb,var(--accent) 22%, transparent);
    background:
        radial-gradient(500px 260px at 80% 0%,rgba(92,82,232,.18),transparent 70%),
        linear-gradient(135deg,var(--surface),var(--surface2));
    text-align:center;
    box-shadow:0 24px 75px var(--shadow);
}}

.cta h2 {{ font-size:clamp(2rem,4vw,3.1rem) !important;margin:.5rem 0; }}
.cta p {{ max-width:600px;margin:0 auto 1.3rem;line-height:1.7; }}

.footer {{
    margin-top:5rem;
    padding:2.5rem .5rem 1rem;
    border-top:1px solid var(--line);
}}

.footer-grid {{
    display:grid;
    grid-template-columns:2fr 1fr 1fr 1fr;
    gap:2rem;
}}

.footer-brand p {{ max-width:350px;font-size:.76rem;line-height:1.65; }}
.footer h4 {{ font-size:.75rem !important;letter-spacing:.01em !important; }}
.footer a {{ color:var(--muted);text-decoration:none;font-size:.72rem;display:block;margin:.55rem 0; }}
.footer-bottom {{ margin-top:2rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--muted);font-size:.66rem;display:flex;justify-content:space-between; }}

.workspace-shell {{
    margin-top:1rem;
    border:1px solid var(--line);
    border-radius:26px;
    background:var(--surface);
    box-shadow:0 20px 70px var(--shadow);
    overflow:hidden;
}}

.workspace-head {{
    padding:1.2rem 1.4rem;
    border-bottom:1px solid var(--line);
    display:flex;
    justify-content:space-between;
    gap:1rem;
    align-items:center;
}}

.workspace-title {{ color:var(--text);font-weight:800;font-family:"Manrope",sans-serif; }}
.workspace-sub {{ color:var(--muted);font-size:.7rem;margin-top:.2rem; }}

.dataset-chip {{
    display:inline-flex;
    padding:.5rem .72rem;
    border-radius:9px;
    color:var(--accent);
    background:var(--soft);
    border:1px solid color-mix(in srgb,var(--accent) 20%,transparent);
    font-size:.68rem;
    font-weight:800;
}}

[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {{
    display:none !important;
    width:0 !important;
}}

[data-testid="stFileUploader"] {{
    padding:.5rem;
    border-radius:20px;
    border:1px solid color-mix(in srgb,var(--accent) 20%,transparent);
    background:linear-gradient(145deg,var(--soft),transparent);
}}

[data-testid="stFileUploader"] section {{
    border:1px dashed color-mix(in srgb,var(--accent) 30%,transparent) !important;
    border-radius:15px !important;
    background:var(--surface2) !important;
}}

[data-testid="stMetric"] {{
    min-height:118px;
    padding:1rem !important;
    border:1px solid var(--line);
    border-radius:17px;
    background:linear-gradient(145deg,var(--surface),var(--surface2));
    box-shadow:0 12px 34px var(--shadow);
}}

[data-testid="stMetricLabel"] {{
    color:var(--muted) !important;
    font-size:.64rem !important;
    text-transform:uppercase;
    letter-spacing:.08em;
}}

[data-testid="stMetricValue"] {{
    color:var(--text) !important;
    font-family:"Manrope",sans-serif;
    font-size:1.55rem !important;
    font-weight:800;
}}

.stButton > button, .stDownloadButton > button {{
    border-radius:12px !important;
    min-height:42px;
    border:1px solid color-mix(in srgb,var(--text) 14%,transparent) !important;
    background:linear-gradient(135deg,var(--surface3),var(--surface)) !important;
    color:var(--text) !important;
    font-weight:850 !important;
    letter-spacing:.01em;
    box-shadow:0 8px 22px var(--shadow);
    transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease;
}}

.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color:color-mix(in srgb,var(--accent) 42%,transparent) !important;
    background:linear-gradient(135deg,var(--surface3),color-mix(in srgb,var(--accent) 9%,var(--surface))) !important;
    color:var(--text) !important;
}}

 .stButton > button:hover, .stDownloadButton > button:hover {{
    transform:translateY(-2px);
    box-shadow:0 14px 30px var(--shadow);
}}

/* Final blue CTA treatment: Start Filtering, Explore Now, and CSV Upload. */
.hero-cta-primary .stButton > button,
.hero-cta-secondary .stButton > button,
[data-testid="stFileUploader"] button {{
    background:linear-gradient(135deg,#8fd8ff 0%,#63bdf5 48%,#55cde4 100%) !important;
    border:1px solid rgba(58,150,208,.55) !important;
    color:#06233b !important;
    font-weight:900 !important;
    text-shadow:none !important;
    box-shadow:0 12px 28px rgba(61,164,216,.22), inset 0 1px 0 rgba(255,255,255,.55) !important;
}}

.hero-cta-primary .stButton > button:hover,
.hero-cta-secondary .stButton > button:hover,
[data-testid="stFileUploader"] button:hover {{
    background:linear-gradient(135deg,#a4e1ff 0%,#72c8fa 48%,#68d9ea 100%) !important;
    color:#031a2c !important;
    border-color:rgba(45,139,201,.72) !important;
    box-shadow:0 18px 38px rgba(61,164,216,.30), 0 0 0 4px rgba(99,194,241,.12) !important;
    transform:translateY(-2px) !important;
}}

[data-testid="stFileUploader"] {{
    border-color:rgba(91,187,238,.38) !important;
    background:linear-gradient(145deg,rgba(117,203,249,.12),transparent) !important;
}}

[data-testid="stFileUploader"] section {{
    border-color:rgba(91,187,238,.58) !important;
}}

[data-testid="stFileUploader"] button p,
[data-testid="stFileUploader"] button span,
[data-testid="stFileUploader"] button div {{
    color:#06233b !important;
    font-weight:900 !important;
}}

div[data-testid="stTabs"] button {{
    color:var(--muted) !important;
}}

div[data-testid="stTabs"] button[aria-selected="true"] {{
    color:var(--accent) !important;
}}

.stAlert {{
    border-radius:14px !important;
    border:1px solid var(--line) !important;
}}

[data-testid="stDataFrame"] {{
    border:1px solid var(--line);
    border-radius:15px;
    overflow:hidden;
}}

@media (max-width:1050px) {{
    .hero-inner {{ grid-template-columns:1fr; padding:3.4rem 2rem 2.5rem; }}
    .preview {{ transform:none; }}
    .feature-grid,.price-grid {{ grid-template-columns:1fr 1fr; }}
    .split {{ grid-template-columns:1fr; }}
    .footer-grid {{ grid-template-columns:1fr 1fr; }}
}}

@media (max-width:700px) {{
    .block-container {{ padding:1rem .7rem 3rem; }}
    .topbar {{ position:relative; }}
    .nav-hint {{ display:none; }}
    .hero {{ border-radius:22px; }}
    .hero-inner {{ padding:2.5rem 1.25rem 2rem; }}
    .hero-title {{ font-size:3.05rem; }}
    .feature-grid,.price-grid {{ grid-template-columns:1fr; }}
    .price-card.featured {{ transform:none; }}
    .preview-cards {{ grid-template-columns:1fr; }}
    .footer-grid {{ grid-template-columns:1fr; }}
    .footer-bottom {{ flex-direction:column;gap:.5rem; }}
}}

/* V2 — NAVBAR-ONLY + PREMIUM GOLD PRICING + LAPTOP SHOWCASE */
.nav-shell{{display:none!important}}
.pricing-card,.price-card,.pricing-featured,.plan-featured{{color:#172033!important}}
.pricing-card *,.price-card *,.pricing-featured *,.plan-featured *{{text-shadow:none!important}}
.pricing-card.featured,.price-card.featured,.pricing-featured,.plan-featured{{
background:radial-gradient(circle at 82% 8%,rgba(255,220,139,.34),transparent 24%),linear-gradient(145deg,#f8e9bb 0%,#d6b05c 48%,#9a6a22 100%)!important;border:1px solid rgba(101,68,14,.45)!important;box-shadow:0 28px 70px rgba(108,72,17,.25)!important}}
.pricing-card.featured h1,.pricing-card.featured h2,.pricing-card.featured h3,.price-card.featured h1,.price-card.featured h2,.price-card.featured h3,.pricing-featured h1,.pricing-featured h2,.pricing-featured h3,.plan-featured h1,.plan-featured h2,.plan-featured h3{{color:#241603!important}}
.pricing-card.featured p,.pricing-card.featured li,.pricing-card.featured span,.pricing-card.featured small,.price-card.featured p,.price-card.featured li,.price-card.featured span,.price-card.featured small,.pricing-featured p,.pricing-featured li,.pricing-featured span,.pricing-featured small,.plan-featured p,.plan-featured li,.plan-featured span,.plan-featured small{{color:#4a3007!important}}
.pricing-card.featured strong,.price-card.featured strong,.pricing-featured strong,.plan-featured strong{{color:#241603!important}}
div[style*="#246bff"],div[style*="#1978ff"]{{color:#2b1a04!important}}
div[style*="#246bff"] h1,div[style*="#246bff"] h2,div[style*="#246bff"] h3,div[style*="#1978ff"] h1,div[style*="#1978ff"] h2,div[style*="#1978ff"] h3{{color:#241603!important}}
div[style*="#246bff"] p,div[style*="#246bff"] span,div[style*="#1978ff"] p,div[style*="#1978ff"] span{{color:#4b3108!important}}

.laptop-showcase{{margin:38px auto 12px;max-width:1120px;position:relative;padding:22px 0 38px;animation:floatLaptop 7s ease-in-out infinite}}
.laptop-showcase:before{{content:"";position:absolute;width:72%;height:55%;left:14%;top:16%;background:radial-gradient(ellipse,rgba(55,137,255,.20),rgba(99,78,230,.10),transparent 70%);filter:blur(26px);pointer-events:none}}
.laptop-shell{{position:relative;z-index:1;width:min(82vw,920px);margin:auto;padding:13px 13px 0;border-radius:25px 25px 8px 8px;background:linear-gradient(145deg,#0b1019,#263447 52%,#0a0f17);box-shadow:0 42px 90px rgba(20,39,74,.28),inset 0 1px 0 rgba(255,255,255,.22);transform:perspective(1400px) rotateX(2deg)}}
.laptop-camera{{width:7px;height:7px;border-radius:50%;background:#05070b;margin:0 auto 8px}}
.laptop-screen{{overflow:hidden;border-radius:15px 15px 4px 4px;border:1px solid rgba(255,255,255,.09);background:linear-gradient(135deg,#111b2a,#09101b);min-height:380px}}
.laptop-ui-top{{height:42px;padding:0 18px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,.06);color:#aab7ca;font-size:12px}}
.laptop-ui-brand{{display:flex;align-items:center;gap:8px;font-weight:800;color:#eef4ff}}.laptop-ui-dot{{width:9px;height:9px;border-radius:50%;background:#69b8ff;box-shadow:0 0 18px #69b8ff}}
.laptop-ui-body{{display:grid;grid-template-columns:1.2fr .8fr;gap:12px;padding:18px}}
.laptop-panel{{padding:15px;border:1px solid rgba(255,255,255,.07);border-radius:14px;background:rgba(255,255,255,.035)}}
.laptop-kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}}.laptop-kpi{{padding:10px;border-radius:10px;background:rgba(255,255,255,.035)}}.laptop-kpi small{{display:block;color:#718097;font-size:9px}}.laptop-kpi strong{{display:block;color:#f5f8ff;font-size:17px;margin-top:5px}}
.laptop-chart{{height:170px;border-radius:12px;background:linear-gradient(180deg,rgba(63,133,255,.18),transparent),repeating-linear-gradient(0deg,transparent 0 32px,rgba(255,255,255,.045) 33px 34px),repeating-linear-gradient(90deg,transparent 0 70px,rgba(255,255,255,.04) 71px 72px);position:relative;overflow:hidden}}.laptop-chart:after{{content:"";position:absolute;left:-3%;right:-3%;top:48%;height:3px;background:linear-gradient(90deg,#3f8cff,#8165ff,#54d8e8,#61dfae);transform:skewY(-8deg);box-shadow:0 0 20px rgba(92,147,255,.6)}}
.laptop-score{{height:100%;min-height:205px;display:grid;place-items:center;text-align:center}}.laptop-ring{{width:130px;height:130px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(#64dfa9 0 94%,#243245 94% 100%);position:relative}}.laptop-ring:after{{content:"";position:absolute;inset:11px;border-radius:50%;background:#101927}}.laptop-ring strong{{position:relative;z-index:1;color:#fff;font-size:27px}}.laptop-ring span{{position:relative;z-index:1;color:#8fa0b7;font-size:10px;margin-top:-58px}}
.laptop-base{{width:min(94vw,1060px);height:20px;margin:-1px auto 0;border-radius:0 0 55% 55%;background:linear-gradient(180deg,#3a4758,#111923 55%,#060a10);box-shadow:0 20px 30px rgba(10,20,40,.25)}}
@keyframes floatLaptop{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}}}}
@media(max-width:780px){{.laptop-ui-body{{grid-template-columns:1fr}}.laptop-kpis{{grid-template-columns:repeat(2,1fr)}}.laptop-screen{{min-height:330px}}}}

/* Hero CTA polish: one standout action + one exploration action. */
.hero-cta-wrap {{ margin-top: 1.35rem; }}
.hero-cta-note {{ font-size:.68rem; color:var(--muted); margin-top:.55rem; letter-spacing:.01em; }}
.hero-cta-primary .stButton > button {{
    min-height:54px !important;
    padding:0 1.35rem !important;
    border-radius:16px !important;
    border:1px solid rgba(101,82,255,.65) !important;
    background:linear-gradient(135deg,#6657ff 0%,#3d8cff 52%,#32c8dc 100%) !important;
    color:#ffffff !important;
    font-weight:850 !important;
    letter-spacing:.01em !important;
    box-shadow:0 14px 34px rgba(74,92,235,.28), inset 0 1px 0 rgba(255,255,255,.25) !important;
    position:relative !important;
    overflow:hidden !important;
    transition:transform .22s ease,box-shadow .22s ease,filter .22s ease !important;
}}
.hero-cta-primary .stButton > button:before {{
    content:"" !important; position:absolute !important; inset:0 !important;
    background:linear-gradient(110deg,transparent 20%,rgba(255,255,255,.30) 48%,transparent 76%) !important;
    transform:translateX(-130%) !important; animation:ctaSweep 3.1s ease-in-out infinite !important;
}}
.hero-cta-primary .stButton > button:hover {{
    transform:translateY(-3px) scale(1.015) !important;
    filter:saturate(1.12) brightness(1.04) !important;
    box-shadow:0 20px 44px rgba(74,92,235,.38),0 0 0 5px rgba(91,105,255,.09) !important;
}}
.hero-cta-primary .stButton > button:active {{ transform:translateY(-1px) scale(.995) !important; }}
.hero-cta-secondary .stButton > button {{
    min-height:54px !important;
    padding:0 1.25rem !important;
    border-radius:16px !important;
    border:1px solid color-mix(in srgb,var(--accent) 38%,var(--line)) !important;
    background:color-mix(in srgb,var(--surface) 88%,var(--accent) 12%) !important;
    color:var(--text) !important;
    font-weight:800 !important;
    box-shadow:0 10px 24px var(--shadow) !important;
    transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease !important;
}}
.hero-cta-secondary .stButton > button:hover {{
    transform:translateY(-3px) !important;
    border-color:var(--accent) !important;
    box-shadow:0 16px 32px var(--shadow) !important;
}}
@keyframes ctaSweep {{ 0%,42%{{transform:translateX(-130%)}} 72%,100%{{transform:translateX(130%)}} }}

/* Developer footer: personal, clean, and intentionally copyright-free. */
.developer-footer {{
    margin-top:5rem; padding:1.9rem 0 1.25rem;
    border-top:1px solid var(--line);
    display:flex; align-items:center; justify-content:space-between; gap:2rem;
}}
.dev-profile {{ display:flex; align-items:center; gap:1rem; min-width:0; }}
.dev-avatar {{
    width:78px; height:78px; flex:0 0 78px; border-radius:50%;
    display:grid; place-items:center; font-weight:900; font-size:1.1rem;
    color:#f7f4ff; background:radial-gradient(circle at 35% 25%,#3b355f,#11131d 62%);
    border:3px solid #8658ff; box-shadow:0 0 0 5px rgba(134,88,255,.10),0 16px 35px var(--shadow);
}}
.dev-name {{ font-size:1.05rem; font-weight:900; letter-spacing:-.02em; color:var(--text); }}
.dev-name .dev-first {{ color:#4e8fff; }}
.dev-name .verified {{ display:inline-grid; place-items:center; width:20px; height:20px; margin-left:.3rem; border-radius:5px; background:#7054a7; color:#fff; font-size:.72rem; vertical-align:2px; }}
.dev-meta {{ margin-top:.25rem; color:var(--muted); font-size:.75rem; line-height:1.55; font-weight:650; }}
.dev-meta strong {{ color:var(--text); }}
.dev-signoff {{ text-align:right; color:var(--muted); font-size:.72rem; line-height:1.65; }}
.dev-signoff strong {{ color:var(--text); font-size:.8rem; }}
@media(max-width:780px){{ .developer-footer{{flex-direction:column;align-items:flex-start}}.dev-signoff{{text-align:left}}.dev-avatar{{width:66px;height:66px;flex-basis:66px}} }}

.explore-pulse {{ margin:1rem 0 0; padding:.75rem 1rem; border:1px solid color-mix(in srgb,var(--accent) 24%,var(--line)); border-radius:14px; background:color-mix(in srgb,var(--surface) 94%,var(--accent) 6%); display:flex; gap:.65rem; align-items:center; flex-wrap:wrap; color:var(--muted); font-size:.72rem; animation:exploreIn .45s ease both; }}
.explore-pulse strong {{ color:var(--text); }}
.explore-pulse span:first-child {{ color:var(--accent2); font-size:1rem; animation:exploreSpark 1.4s ease-in-out infinite; }}
@keyframes exploreIn {{ from{{opacity:0;transform:translateY(-8px)}} to{{opacity:1;transform:translateY(0)}} }}
@keyframes exploreSpark {{ 0%,100%{{transform:scale(1) rotate(0)}} 50%{{transform:scale(1.18) rotate(8deg)}} }}

/* Final polish: no glassy duplicate nav, stronger contrast in every theme. */
[data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display:none !important; }}

/* Eye-comfort mode: light/system use a soft gray canvas instead of harsh white. */
.stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    background:var(--bg) !important;
}}
.stMarkdown, .stCaption, .stText, label, p, li, td, th,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"],
[data-testid="stMarkdownContainer"] {{
    color:var(--text) !important;
}}
.stCaption, small, [data-testid="stCaptionContainer"] {{
    color:var(--muted) !important;
}}
.stTextInput input, .stTextArea textarea, .stNumberInput input,
[data-baseweb="select"] > div, [data-baseweb="input"] > div {{
    background:var(--surface) !important;
    color:var(--text) !important;
    border-color:var(--line) !important;
}}
.stDataFrame, [data-testid="stDataFrame"] {{
    border-color:var(--line) !important;
}}

.stButton > button, .stDownloadButton > button, div[data-testid="stFormSubmitButton"] button {{
    color:var(--text) !important;
    text-shadow:none !important;
    opacity:1 !important;
}}
.nav-right .pill {{ color:var(--text) !important; border-color:var(--line) !important; background:var(--surface) !important; }}
.logo-title, .logo-title span {{ opacity:1 !important; }}
.stFileUploader label, .stFileUploader section, .stFileUploader div {{ color:var(--text) !important; }}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================
def go(page: str):
    st.session_state.page = page
    st.rerun()

def nav_button(label: str, page: str):
    if st.button(label, key=f"nav_{page}", use_container_width=False):
        go(page)

def cycle_theme():
    order = ["light", "dark", "system"]
    current = st.session_state.get("theme", "system")
    st.session_state.theme = order[(order.index(current) + 1) % len(order)]
    st.rerun()


def render_topbar():
    labels = {
        "light": "☀ Light",
        "dark": "◐ Dark",
        "system": "◑ System",
    }
    st.markdown(
        """
        <div class="topbar">
            <div class="logo">
                <div class="logo-mark">DQ</div>
                <div class="logo-title">DataFlow <span>Quality</span></div>
            </div>
            <div class="nav-hint">Intelligent data operations for modern teams</div>
            <div class="nav-right"><span class="pill">● Live platform</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # One compact theme control: each click cycles Light → Dark → System.
    _, theme_col = st.columns([8.5, 1.15])
    with theme_col:
        if st.button(labels[st.session_state.theme], key="theme_cycle", use_container_width=True):
            cycle_theme()


def render_footer():
    st.markdown(
        """
        <div class="developer-footer">
          <div class="dev-profile">
            <div class="dev-avatar">RC</div>
            <div>
              <div class="dev-name"><span class="dev-first">CHADARASIPALLI</span> RAMCHARAN <span class="verified">✓</span></div>
              <div class="dev-meta">HE/HIM<br><strong>Web Developer &amp; AI Enthusiast</strong> | B.Tech CSE @ SPSU |<br>Leading Through Sport, Growing Through Code</div>
            </div>
          </div>
          <div class="dev-signoff"><strong>Built &amp; designed by RamCharan</strong><br>Turning intelligent ideas into useful software.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_hero():
    st.markdown(
        """
        <div class="hero">
          <div class="hero-inner">
            <div>
              <span class="eyebrow">✦ Intelligent data operations</span>
              <div class="hero-title">Clean data.<br><span class="gradient">Clear decisions.</span></div>
              <p class="hero-copy">Turn raw CSV files into trustworthy, analysis-ready datasets. Profile every column, expose hidden quality issues, repair them automatically, validate the result, and export a complete quality trail.</p>
              <div class="hero-trust">
                <span>Private by design</span>
                <span>Automated analysis</span>
                <span>Repair + validation</span>
                <span>Downloadable reports</span>
              </div>
            </div>
            <div class="preview">
              <div class="preview-bar"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span style="margin-left:.5rem">DataFlow Quality / Overview</span></div>
              <div class="preview-main">
                <div class="preview-head"><strong>Dataset health</strong><span>● ANALYSIS READY</span></div>
                <div class="preview-score">
                  <div class="ring"><b>94%</b></div>
                  <div><div style="color:#fff;font-weight:800;font-size:.9rem">Excellent quality</div><div style="color:#7d8999;font-size:.63rem;margin-top:.3rem">Ready for analysis</div></div>
                </div>
                <div class="preview-cards">
                  <div class="preview-card"><small>Completeness</small><strong>98%</strong></div>
                  <div class="preview-card"><small>Duplicates</small><strong>12</strong></div>
                  <div class="preview-card"><small>Outliers</small><strong>07</strong></div>
                </div>
                <div class="chart"></div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hero-cta-wrap">', unsafe_allow_html=True)
    cta1, cta2, _ = st.columns([1.15, 1.0, 1.75], gap="small")
    with cta1:
        st.markdown('<div class="hero-cta-primary">', unsafe_allow_html=True)
        if st.button("Start filtering  →", key="hero_filter", type="primary", use_container_width=True):
            go("Workspace")
        st.markdown('</div>', unsafe_allow_html=True)
    with cta2:
        st.markdown('<div class="hero-cta-secondary">', unsafe_allow_html=True)
        if st.button("Explore now  ↗", key="hero_explore", use_container_width=True):
            st.session_state.explore_features = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-cta-note">Start filtering opens the live workspace · Explore now jumps to the quality capabilities.</div></div>', unsafe_allow_html=True)

    if st.session_state.get("explore_features", False):
        st.markdown('<div id="quality-capabilities"></div>', unsafe_allow_html=True)

def render_features():
    st.markdown(
        """
        <div class="section">
          <div class="section-center">
            <div class="small-label">One quality system</div>
            <h2>Everything your dataset needs before the decision.</h2>
            <p>Six connected capabilities turn messy source data into a dataset your team can actually trust.</p>
          </div>
          <div class="feature-grid">
            <div class="feature-card"><div class="feature-num">01</div><div class="feature-icon">⌁</div><h3>Profiling</h3><p>Understand structure, types, completeness, uniqueness and useful column statistics at a glance.</p><span class="arrow">Explore profiling →</span></div>
            <div class="feature-card"><div class="feature-num">02</div><div class="feature-icon">⌁</div><h3>Detection</h3><p>Surface missing values, duplicates and statistical outliers before they quietly affect your analysis.</p><span class="arrow">Explore detection →</span></div>
            <div class="feature-card"><div class="feature-num">03</div><div class="feature-icon">✦</div><h3>Automated repair</h3><p>Apply repeatable corrections to missing values, duplicates, outliers and supported data types.</p><span class="arrow">Explore repair →</span></div>
            <div class="feature-card"><div class="feature-num">04</div><div class="feature-icon">◎</div><h3>Scoring</h3><p>Translate technical quality signals into one clear score and grade your team can understand.</p><span class="arrow">Explore scoring →</span></div>
            <div class="feature-card"><div class="feature-num">05</div><div class="feature-icon">✓</div><h3>Validation</h3><p>Check the repaired dataset against validation rules before it becomes the source for downstream work.</p><span class="arrow">Explore validation →</span></div>
            <div class="feature-card"><div class="feature-num">06</div><div class="feature-icon">↗</div><h3>Reporting</h3><p>Keep a quality report and repair log so every transformation has a visible, downloadable trail.</p><span class="arrow">Explore reporting →</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_home():
    render_hero()
    if st.session_state.get("explore_features", False):
        st.markdown("""
        <div class="explore-pulse"><span>✦</span><strong>Quality capabilities</strong><span>Profiling · Detection · Repair · Scoring · Validation · Reporting</span></div>
        """, unsafe_allow_html=True)
    render_features()

    st.markdown(
        """
        <div class="section">
          <div class="split">
            <div class="panel">
              <div class="small-label">Designed around your workflow</div>
              <h3>One workspace. No quality detective work.</h3>
              <p>Upload once and let the engine move through the complete lifecycle. The interface keeps the technical detail available without making the experience feel technical.</p>
              <div class="timeline">
                <div class="step"><div class="step-num">01</div><div><strong>Profile the source</strong><span>See the shape and health of the dataset before changes are made.</span></div></div>
                <div class="step"><div class="step-num">02</div><div><strong>Detect what matters</strong><span>Find quality issues that can affect analysis and reporting.</span></div></div>
                <div class="step"><div class="step-num">03</div><div><strong>Repair with a trail</strong><span>Apply corrections and retain a repair log for transparency.</span></div></div>
                <div class="step"><div class="step-num">04</div><div><strong>Validate the result</strong><span>Confirm the repaired dataset is ready for downstream use.</span></div></div>
              </div>
            </div>
            <div class="panel">
              <div class="small-label">Built for clarity</div>
              <h3>From noisy rows to a decision-ready asset.</h3>
              <p>DataFlow Quality makes data quality visible. Instead of a wall of technical output, you get a product-like journey from source file to final confidence.</p>
              <div class="quote"><p>“Good data quality should feel like a product, not a cleanup project.”</p><span>DataFlow Quality philosophy</span></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="cta">
          <div class="small-label">Ready when you are</div>
          <h2>Give your next dataset a clean start.</h2>
          <p>Upload a CSV and let the quality engine handle the inspection, repair, validation and reporting.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open the workspace →", key="home_workspace", use_container_width=True):
        go("Workspace")

def render_product():
    st.markdown('<div class="section"><div class="small-label">Product</div><h1>The quality layer between your data and every decision.</h1><p style="max-width:720px;font-size:1rem;line-height:1.8">A focused workspace that turns the existing Python quality engine into a polished product experience.</p></div>', unsafe_allow_html=True)
    render_features()
    st.markdown(
        """
        <div class="section">
          <div class="panel">
            <div class="small-label">Product architecture</div>
            <h3>Profile → Detect → Score → Repair → Validate → Report</h3>
            <p>Each stage is connected to the underlying application modules. The website layer changes the experience and navigation without replacing your working data-quality logic.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Launch workspace →", key="product_workspace"):
        go("Workspace")

def render_solutions():
    st.markdown('<div class="section"><div class="small-label">Solutions</div><h1>Quality workflows for teams that move fast.</h1><p style="max-width:720px;font-size:1rem;line-height:1.8">Use the same engine for analysts, operations teams, data teams and anyone who needs a dependable dataset before the next decision.</p></div>', unsafe_allow_html=True)
    cards = [
        ("Analytics teams", "Get clean source files before dashboards, models and reports are built."),
        ("Operations", "Make recurring CSV cleanup repeatable instead of manually fixing rows."),
        ("Data teams", "Expose quality signals and preserve repair evidence in one workflow."),
        ("Leadership", "Turn technical quality into a simple score and decision-ready summary."),
    ]
    cols = st.columns(4)
    for i, (title, desc) in enumerate(cards):
        with cols[i]:
            st.markdown(f'<div class="feature-card"><div class="feature-num">0{i+1}</div><div class="feature-icon">✦</div><h3>{title}</h3><p>{desc}</p><span class="arrow">Explore →</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section"><div class="panel"><div class="small-label">The outcome</div><h3>Less cleanup. More confidence.</h3><p>The goal is not more data tooling. It is a cleaner path from the file you received to the result you are willing to use.</p></div></div>', unsafe_allow_html=True)

def render_how():
    st.markdown('<div class="section"><div class="section-center"><div class="small-label">How it works</div><h2>A six-stage quality journey.</h2><p>Everything happens in one flow, with each stage visible enough to inspect and simple enough to understand.</p></div></div>', unsafe_allow_html=True)
    stages = [
        ("01","Profile","Map dataset structure, columns, missingness and statistics."),
        ("02","Detect","Identify missing values, duplicate rows and numerical outliers."),
        ("03","Score","Quantify quality and translate issues into a clear score."),
        ("04","Repair","Apply the existing repair engine to create a corrected dataset."),
        ("05","Validate","Check the repaired output and calculate the validation score."),
        ("06","Report","Generate a quality report and downloadable repair log."),
    ]
    for n, title, desc in stages:
        st.markdown(f'<div class="step" style="margin:.65rem 0"><div class="step-num">{n}</div><div><strong style="font-size:.9rem">{title}</strong><span style="font-size:.75rem">{desc}</span></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section"><div class="cta"><div class="small-label">Try the real workflow</div><h2>Upload a CSV and see every stage.</h2></div></div>', unsafe_allow_html=True)
    if st.button("Open workspace →", key="how_workspace"):
        go("Workspace")

def render_resources():
    st.markdown('<div class="section"><div class="small-label">Resources</div><h1>Understand the system. Get more from your data.</h1><p style="max-width:720px;font-size:1rem;line-height:1.8">A clean resource hub for the concepts behind data quality and the product workflow.</p></div>', unsafe_allow_html=True)
    resources = [
        ("Guide","Data quality fundamentals","Understand completeness, uniqueness, validity, consistency and accuracy."),
        ("Playbook","CSV cleanup workflow","A practical sequence for inspecting, repairing and validating source files."),
        ("Reference","Quality score","See how issue signals can be turned into a single decision-friendly metric."),
        ("Guide","Repair logs","Why transparent transformations matter when data changes."),
    ]
    cols = st.columns(2)
    for i, (kind, title, desc) in enumerate(resources):
        with cols[i % 2]:
            st.markdown(f'<div class="feature-card" style="margin-bottom:1rem"><div class="feature-num">{kind}</div><h3 style="margin-top:1rem">{title}</h3><p>{desc}</p><span class="arrow">Read resource →</span></div>', unsafe_allow_html=True)

def render_pricing():
    st.markdown('<div class="section"><div class="section-center"><div class="small-label">Pricing</div><h2>Start simple. Scale when the workflow becomes essential.</h2><p>A polished pricing experience for the product. The local app remains free to run with your existing pipeline.</p></div></div>', unsafe_allow_html=True)
    plans = [
        ("Starter","Free","For trying the quality workflow.",["CSV analysis","Quality score","Detection","Repair + validation","JSON report"]),
        ("Pro","$29","For analysts and small teams.",["Everything in Starter","Saved workflows","Team-ready reporting","Priority processing","Advanced quality views"]),
        ("Scale","Custom","For data-heavy organizations.",["Everything in Pro","Multiple workspaces","Custom rules","Governance support","Dedicated success"]),
    ]
    cols = st.columns(3)
    for i, (name, price, desc, features) in enumerate(plans):
        with cols[i]:
            featured = name == "Pro"
            st.markdown(f'<div class="price-card {"featured" if featured else ""}"><div class="small-label">{"Most popular" if featured else "Plan"}</div><div class="price-name">{name}</div><div class="price">{price} <small>{" / month" if price.startswith("$") else ""}</small></div><p>{desc}</p><ul>{"".join(f"<li>{x}</li>" for x in features)}</ul></div>', unsafe_allow_html=True)
            if name == "Starter":
                if st.button("Start free →", key="price_start", use_container_width=True):
                    go("Workspace")
            elif name == "Pro":
                if st.button("Start Pro →", key="price_pro", use_container_width=True):
                    go("Contact")
            else:
                if st.button("Talk to us →", key="price_scale", use_container_width=True):
                    go("Contact")

def render_about():
    st.markdown('<div class="section"><div class="small-label">About</div><h1>Data quality should feel calm.</h1><p style="max-width:760px;font-size:1.05rem;line-height:1.85">DataFlow Quality is designed around a simple idea: the interface should make complexity easier to understand, not add another layer of complexity.</p></div>', unsafe_allow_html=True)
    cols = st.columns(3)
    facts = [
        ("01","Clarity","Show the right information at the right moment."),
        ("02","Automation","Remove repetitive cleanup without hiding what changed."),
        ("03","Confidence","Validate the result before it reaches the next system."),
    ]
    for i,(n,t,d) in enumerate(facts):
        with cols[i]:
            st.markdown(f'<div class="feature-card"><div class="feature-num">{n}</div><div class="feature-icon">✦</div><h3>{t}</h3><p>{d}</p></div>', unsafe_allow_html=True)

def render_contact():
    st.markdown('<div class="section"><div class="section-center"><div class="small-label">Contact</div><h2>Let’s make your data workflow cleaner.</h2><p>Use this space as the product contact/demo surface. The workspace itself is ready to use immediately.</p></div></div>', unsafe_allow_html=True)
    with st.form("contact_form"):
        c1,c2 = st.columns(2)
        with c1:
            name = st.text_input("Name")
        with c2:
            email = st.text_input("Email")
        company = st.text_input("Company")
        message = st.text_area("What would you like to improve?")
        submitted = st.form_submit_button("Send request →", use_container_width=True)
        if submitted:
            if not name or not email:
                st.warning("Please add your name and email.")
            else:
                st.success(f"Thanks {name}. Your request has been captured for this demo experience.")

def run_workspace():
    st.markdown(
        """
        <div class="workspace-shell">
          <div class="workspace-head">
            <div><div class="workspace-title">Data Quality Workspace</div><div class="workspace-sub">Upload a CSV and run the complete quality pipeline.</div></div>
            <div class="dataset-chip">● Pipeline ready</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section" style="padding-top:2rem"><div class="small-label">01 · Source</div><h1>Bring your dataset.</h1><p style="max-width:700px">The interface is now a complete product shell, while your original Python engine remains responsible for the actual analysis.</p></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        key="workspace_upload",
        help="CSV files are processed by the existing DataFlow Quality pipeline.",
    )

    if uploaded_file is None and st.session_state.uploaded_df is None:
        st.markdown(
            """
            <div class="feature-card" style="margin-top:1.5rem;min-height:140px">
              <div class="feature-num">READY</div>
              <h3>Drop your CSV above to activate the workspace.</h3>
              <p>Once loaded, the dashboard below expands into live profiling, detection, scoring, repair, validation and reporting.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if uploaded_file is not None:
        try:
            st.session_state.uploaded_df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_name = uploaded_file.name
        except Exception as e:
            st.error(f"Unable to read the CSV: {e}")
            return

    df = st.session_state.uploaded_df
    filename = st.session_state.uploaded_name or "dataset.csv"

    st.success(f"✓ {filename} loaded successfully · {len(df):,} rows · {len(df.columns):,} columns")

    with st.spinner("Running the complete quality pipeline…"):
        try:
            profile = profile_dataset(df)
            detection = run_detection(df)
            scoring = calculate_quality_score(df, detection)
            repaired_df, repair_report = run_repairs(df)
            validation = validate_dataset(repaired_df)
            repair_log = create_repair_log(df, repaired_df, repair_report)
            quality_report = generate_quality_report(
                profile=profile,
                detection=detection,
                scoring=scoring,
                validation=validation,
                repair_report=repair_report,
            )
        except Exception as e:
            st.error(f"Unable to process the dataset: {e}")
            return

    st.markdown('<div class="section" style="padding-top:2.5rem"><div class="small-label">02 · Live dashboard</div><h1>Your dataset, decoded.</h1></div>', unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("Rows", f'{profile["dataset"]["rows"]:,}')
    with c2: st.metric("Columns", f'{profile["dataset"]["columns"]:,}')
    with c3: st.metric("Missing", f'{profile["missing_values"]["total"]:,}')
    with c4: st.metric("Duplicates", f'{detection["duplicates"]["duplicate_count"]:,}')
    with c5: st.metric("Quality", f'{scoring["score"]:.2f}')

    tabs = st.tabs([
        "Overview",
        "Profile",
        "Detection",
        "Repair",
        "Validation",
        "Report",
    ])

    with tabs[0]:
        st.subheader("Quality overview")
        a,b,c = st.columns(3)
        with a:
            st.metric("Overall score", f'{scoring["score"]:.2f}/100')
        with b:
            st.metric("Grade", scoring["grade"])
        with c:
            st.metric("Validation", f'{validation["validation_score"]:.2f}/100')

        if scoring["score"] >= 90:
            st.success("Excellent data quality — the dataset is in strong shape.")
        elif scoring["score"] >= 75:
            st.info("Good data quality — a few improvements may be useful.")
        elif scoring["score"] >= 50:
            st.warning("Fair data quality — improvement is recommended.")
        else:
            st.error("Poor data quality — repair is recommended.")

        st.subheader("Original data preview")
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)

    with tabs[1]:
        p1,p2 = st.columns(2)
        with p1:
            st.subheader("Dataset information")
            info = pd.DataFrame({
                "Metric":["Rows","Columns","Memory Usage (MB)","Total Missing Values","Duplicate Rows"],
                "Value":[
                    profile["dataset"]["rows"],
                    profile["dataset"]["columns"],
                    profile["dataset"]["memory_usage_mb"],
                    profile["missing_values"]["total"],
                    profile["duplicates"]["total_rows"],
                ],
            })
            st.dataframe(info, use_container_width=True, hide_index=True)
        with p2:
            st.subheader("Column statistics")
            column_stats = profile.get("column_statistics", {})
            if column_stats:
                stats_df = pd.DataFrame.from_dict(column_stats, orient="index")
                stats_df.index.name = "Column"
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.info("No column statistics returned.")

    with tabs[2]:
        st.subheader("Missing values")
        missing_rows = []
        for column, details in detection["missing_values"].items():
            if details["missing_count"] > 0:
                missing_rows.append({
                    "Column":column,
                    "Missing Count":details["missing_count"],
                    "Missing %":details["missing_percentage"],
                })
        if missing_rows:
            st.dataframe(pd.DataFrame(missing_rows), use_container_width=True, hide_index=True)
        else:
            st.success("No missing values detected.")

        st.subheader("Duplicate rows")
        duplicate_count = detection["duplicates"]["duplicate_count"]
        if duplicate_count:
            st.warning(f"{duplicate_count} duplicate rows detected.")
            st.dataframe(df[df.duplicated(keep=False)], use_container_width=True, hide_index=True)
        else:
            st.success("No duplicate rows detected.")

        st.subheader("Outliers")
        outlier_rows = []
        for column, details in detection["outliers"].items():
            outlier_rows.append({
                "Column":column,
                "Outlier Count":details["outlier_count"],
                "Lower Bound":round(details["lower_bound"],3),
                "Upper Bound":round(details["upper_bound"],3),
            })
        if outlier_rows:
            st.dataframe(pd.DataFrame(outlier_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No numerical columns available for outlier detection.")

        st.subheader("Score breakdown")
        penalties = scoring.get("penalties", {})
        penalty_df = pd.DataFrame({
            "Issue":["Missing Values","Duplicates","Outliers"],
            "Penalty":[
                penalties.get("missing_values",0),
                penalties.get("duplicates",0),
                penalties.get("outliers",0),
            ],
        })
        st.dataframe(penalty_df, use_container_width=True, hide_index=True)

    with tabs[3]:
        r1,r2,r3 = st.columns(3)
        with r1: st.metric("Original rows", repair_report["original_rows"])
        with r2: st.metric("Final rows", repair_report["final_rows"])
        with r3: st.metric("Total repaired", repair_report["total_repaired"])

        operations = repair_report.get("operations", {})
        if operations:
            op_df = pd.DataFrame([
                {"Operation":operation,"Details":str(details)}
                for operation,details in operations.items()
            ])
            st.dataframe(op_df, use_container_width=True, hide_index=True)

        st.subheader("Before vs after")
        before, after = st.columns(2)
        with before:
            st.caption("Original dataset")
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)
        with after:
            st.caption("Repaired dataset")
            st.dataframe(repaired_df.head(100), use_container_width=True, hide_index=True)

        st.subheader("Repair log")
        if not repair_log.empty:
            st.dataframe(repair_log, use_container_width=True, hide_index=True)
            st.download_button(
                "Download repair log",
                repair_log.to_csv(index=False),
                "repair_log.csv",
                "text/csv",
                use_container_width=True,
            )
        else:
            st.success("No changes were required.")

    with tabs[4]:
        v1,v2,v3 = st.columns(3)
        with v1: st.metric("Valid dataset", "Yes" if validation["valid"] else "No")
        with v2: st.metric("Validation score", f'{validation["validation_score"]:.2f}')
        with v3: st.metric("Passed rules", validation["passed_rules"])

        if validation["valid"]:
            st.success("Repaired dataset passed validation.")
        else:
            st.error(f'{validation["failed_rules"]} validation rules failed.')

        st.subheader("Repaired dataset")
        st.dataframe(repaired_df.head(100), use_container_width=True, hide_index=True)

    with tabs[5]:
        st.subheader("Quality report")
        report_path = save_quality_report(
            quality_report,
            "quality_report.json",
        )
        with open(report_path, "r", encoding="utf-8") as report_file:
            report_data = report_file.read()

        st.download_button(
            "Download quality report",
            report_data,
            "quality_report.json",
            "application/json",
            use_container_width=True,
        )

        st.json(quality_report)

    st.markdown(
        """
        <div class="cta">
          <div class="small-label">Pipeline complete</div>
          <h2>Your dataset has a quality trail.</h2>
          <p>Profile, detection, repair, validation and reporting have all been executed using the connected application engine.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# APP ROUTER
# =========================================================
render_topbar()

page = st.session_state.page

if page == "Workspace":
    run_workspace()
else:
    render_home()

if page != "Workspace":
    render_footer()
