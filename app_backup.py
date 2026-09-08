import json
from pathlib import Path

import pandas as pd
import streamlit as st

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


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DataForge Analytics | Data Quality Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            linear-gradient(
                180deg,
                #f7fbff 0%,
                #ffffff 38%,
                #f8fbff 100%
            );
        color: #172033;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1rem;
        padding-bottom: 4rem;
    }

    /* Hide Streamlit chrome */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* ======================================================
       NAVIGATION
       ====================================================== */

    .top-nav {
        width: 100%;
        min-height: 76px;
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #e7edf5;
        border-radius: 18px;
        padding: 14px 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 8px 30px rgba(31, 55, 88, 0.06);
        margin-bottom: 30px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1687e8, #2563eb);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 22px;
        font-weight: 800;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22);
    }

    .brand-name {
        font-size: 20px;
        font-weight: 800;
        color: #142033;
        line-height: 1;
    }

    .brand-subtitle {
        font-size: 9px;
        letter-spacing: 2px;
        color: #738096;
        margin-top: 3px;
    }

    .nav-links {
        display: flex;
        gap: 34px;
        align-items: center;
        color: #3f4b5f;
        font-size: 15px;
        font-weight: 500;
    }

    .nav-link {
        color: #3f4b5f;
        text-decoration: none;
    }

    .nav-link:hover {
        color: #2563eb;
    }

    /* ======================================================
       HERO
       ====================================================== */

    .hero {
        position: relative;
        overflow: hidden;
        min-height: 610px;
        padding: 78px 65px 70px;
        border-radius: 30px;
        border: 1px solid #e2eaf4;
        background:
            radial-gradient(
                circle at 82% 42%,
                rgba(79, 155, 255, 0.16),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #ffffff 0%,
                #f4f9ff 52%,
                #eef7ff 100%
            );
        box-shadow:
            0 30px 80px rgba(39, 74, 113, 0.08);
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 48% 52%;
        align-items: center;
        gap: 20px;
    }

    .eyebrow {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background: #eef4ff;
        color: #3c5ab5;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.4px;
        margin-bottom: 22px;
    }

    .hero-title {
        font-size: clamp(48px, 5vw, 78px);
        line-height: 0.98;
        letter-spacing: -3px;
        font-weight: 800;
        color: #111a2b;
        margin: 0 0 25px 0;
    }

    .hero-title span {
        color: #2563eb;
    }

    .hero-description {
        max-width: 610px;
        font-size: 19px;
        line-height: 1.65;
        color: #5c687a;
        margin-bottom: 30px;
    }

    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 9px;
        margin-bottom: 32px;
    }

    .pill {
        background: white;
        border: 1px solid #e2e9f2;
        padding: 8px 13px;
        border-radius: 999px;
        color: #526075;
        font-size: 12px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(32, 63, 98, 0.04);
    }

    .hero-note {
        color: #788598;
        font-size: 13px;
        margin-top: 14px;
    }

    /* ======================================================
       LAPTOP
       ====================================================== */

    .laptop-area {
        position: relative;
        min-height: 440px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .laptop-glow {
        position: absolute;
        width: 450px;
        height: 300px;
        background: rgba(67, 144, 255, 0.13);
        filter: blur(55px);
        border-radius: 50%;
    }

    .laptop {
        position: relative;
        width: 600px;
        max-width: 100%;
        z-index: 2;
    }

    .laptop-screen {
        background: #101827;
        border: 8px solid #111827;
        border-bottom-width: 12px;
        border-radius: 18px 18px 8px 8px;
        padding: 8px;
        box-shadow: 0 30px 50px rgba(18, 41, 71, 0.22);
    }

    .dashboard-window {
        background: #f8fafc;
        border-radius: 8px;
        padding: 14px;
        min-height: 310px;
    }

    .dashboard-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 13px;
    }

    .dashboard-title {
        font-weight: 800;
        font-size: 16px;
        color: #172033;
    }

    .dashboard-badge {
        background: #eaf9ef;
        color: #18884a;
        border-radius: 999px;
        padding: 4px 9px;
        font-size: 9px;
        font-weight: 700;
    }

    .dashboard-cards {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 10px;
    }

    .dash-card {
        background: white;
        border: 1px solid #e9eef5;
        border-radius: 7px;
        padding: 9px;
    }

    .dash-label {
        color: #7c8798;
        font-size: 8px;
        margin-bottom: 3px;
    }

    .dash-value {
        color: #172033;
        font-weight: 800;
        font-size: 15px;
    }

    .dash-change {
        color: #20a05a;
        font-size: 7px;
        margin-top: 3px;
    }

    .dashboard-middle {
        display: grid;
        grid-template-columns: 1.55fr 1fr;
        gap: 9px;
    }

    .chart-box,
    .quality-box {
        background: white;
        border: 1px solid #e9eef5;
        border-radius: 7px;
        padding: 10px;
        min-height: 135px;
    }

    .chart-title {
        font-size: 9px;
        font-weight: 700;
        color: #344054;
        margin-bottom: 12px;
    }

    .fake-chart {
        height: 85px;
        position: relative;
        overflow: hidden;
    }

    .fake-line {
        position: absolute;
        width: 120%;
        height: 70px;
        left: -5%;
        top: 14px;
        border-bottom: 3px solid #4c8bf5;
        border-radius: 50%;
        transform: rotate(-5deg);
        opacity: 0.85;
    }

    .quality-circle {
        width: 82px;
        height: 82px;
        margin: 12px auto 5px;
        border-radius: 50%;
        border: 9px solid #d8f5e4;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #1e9a59;
        font-size: 20px;
        font-weight: 800;
    }

    .quality-caption {
        text-align: center;
        color: #718096;
        font-size: 8px;
    }

    .laptop-base {
        height: 22px;
        background: linear-gradient(
            180deg,
            #9ca5b1,
            #626b76
        );
        width: 112%;
        margin-left: -6%;
        border-radius: 2px 2px 18px 18px;
        box-shadow: 0 15px 25px rgba(35, 52, 72, 0.20);
    }

    /* ======================================================
       TRUSTED
       ====================================================== */

    .trusted {
        text-align: center;
        padding: 55px 20px;
    }

    .trusted-label {
        color: #7c8798;
        font-size: 14px;
        margin-bottom: 24px;
    }

    .trusted-logos {
        display: flex;
        justify-content: center;
        gap: 65px;
        flex-wrap: wrap;
        color: #8290a2;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: -0.5px;
    }

    /* ======================================================
       SECTION
       ====================================================== */

    .section {
        padding: 75px 10px;
    }

    .section-kicker {
        color: #4568c5;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 800;
        margin-bottom: 13px;
    }

    .section-title {
        font-size: clamp(34px, 4vw, 52px);
        line-height: 1.05;
        letter-spacing: -2px;
        color: #131d2f;
        font-weight: 800;
        margin: 0 0 18px;
    }

    .section-description {
        max-width: 700px;
        color: #687589;
        line-height: 1.7;
        font-size: 16px;
        margin-bottom: 35px;
    }

    /* ======================================================
       FEATURE CARDS
       ====================================================== */

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
    }

    .feature-card {
        background: white;
        border: 1px solid #e6ecf4;
        border-radius: 18px;
        padding: 27px;
        min-height: 205px;
        box-shadow: 0 10px 35px rgba(31, 57, 88, 0.045);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 45px rgba(31, 57, 88, 0.09);
    }

    .feature-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: #eef4ff;
        color: #3568d5;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 18px;
    }

    .feature-card h3 {
        color: #1c2738;
        font-size: 18px;
        margin: 0 0 9px;
    }

    .feature-card p {
        color: #738096;
        line-height: 1.6;
        font-size: 14px;
        margin: 0;
    }

    /* ======================================================
       WORKFLOW
       ====================================================== */

    .workflow {
        background: #f2f7ff;
        border: 1px solid #e0e9f7;
        border-radius: 28px;
        padding: 55px;
    }

    .steps {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 25px;
    }

    .step {
        position: relative;
    }

    .step-number {
        width: 43px;
        height: 43px;
        border-radius: 50%;
        background: #2563eb;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        margin-bottom: 18px;
    }

    .step h3 {
        color: #1c2738;
        font-size: 17px;
        margin-bottom: 8px;
    }

    .step p {
        color: #738096;
        font-size: 14px;
        line-height: 1.6;
    }

    /* ======================================================
       SOLUTIONS
       ====================================================== */

    .solution-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 22px;
    }

    .solution-card {
        background: white;
        border: 1px solid #e4ebf3;
        border-radius: 20px;
        padding: 32px;
        min-height: 220px;
    }

    .solution-card h3 {
        font-size: 21px;
        color: #172033;
        margin-bottom: 12px;
    }

    .solution-card p {
        color: #718096;
        line-height: 1.65;
        font-size: 14px;
    }

    .solution-list {
        margin-top: 18px;
        color: #4e5c70;
        font-size: 13px;
        line-height: 2;
    }

    /* ======================================================
       PRICING
       ====================================================== */

    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
    }

    .pricing-card {
        background: white;
        border: 1px solid #e2e9f2;
        border-radius: 20px;
        padding: 30px;
    }

    .pricing-card.featured {
        border: 2px solid #4e67d8;
        box-shadow: 0 20px 50px rgba(64, 88, 196, 0.12);
    }

    .pricing-name {
        color: #526075;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .pricing-price {
        font-size: 42px;
        font-weight: 800;
        color: #172033;
        letter-spacing: -2px;
    }

    .pricing-price span {
        font-size: 13px;
        color: #7a8798;
        letter-spacing: 0;
    }

    .pricing-description {
        color: #738096;
        font-size: 13px;
        line-height: 1.5;
        min-height: 42px;
        margin: 10px 0 20px;
    }

    .pricing-list {
        color: #566477;
        font-size: 13px;
        line-height: 2.1;
    }

    /* ======================================================
       CTA
       ====================================================== */

    .cta {
        padding: 75px 50px;
        text-align: center;
        border-radius: 30px;
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(72, 137, 255, 0.28),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #eff6ff,
                #f8fbff
            );
        border: 1px solid #dce8f8;
    }

    .cta h2 {
        font-size: clamp(36px, 4vw, 55px);
        letter-spacing: -2px;
        color: #172033;
        margin-bottom: 15px;
    }

    .cta p {
        color: #6c798c;
        font-size: 16px;
        margin-bottom: 28px;
    }

    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {
        margin-top: 70px;
        padding: 45px 10px 25px;
        border-top: 1px solid #e3e9f1;
    }

    .footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 40px;
    }

    .footer h4 {
        color: #283449;
        font-size: 14px;
        margin-bottom: 15px;
    }

    .footer p,
    .footer li {
        color: #7a8799;
        font-size: 13px;
        line-height: 1.9;
    }

    .footer ul {
        padding: 0;
        list-style: none;
    }

    .footer-bottom {
        border-top: 1px solid #e6ebf2;
        margin-top: 30px;
        padding-top: 20px;
        color: #8b96a6;
        font-size: 12px;
        display: flex;
        justify-content: space-between;
        gap: 20px;
        flex-wrap: wrap;
    }

    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        border-radius: 11px;
        min-height: 44px;
        font-weight: 700;
        border: 1px solid #d8e0eb;
        background: white;
        color: #263449;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #8ca8d9;
        color: #1d4ed8;
        transform: translateY(-1px);
    }

    /* ======================================================
       DASHBOARD
       ====================================================== */

    .dashboard-header {
        background: white;
        border: 1px solid #e2e9f2;
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(31, 57, 88, 0.04);
    }

    .dashboard-title {
        font-size: 30px;
        font-weight: 800;
        color: #172033;
    }

    .dashboard-subtitle {
        color: #738096;
        margin-top: 5px;
    }

    .metric-card {
        background: white;
        border: 1px solid #e3eaf2;
        border-radius: 16px;
        padding: 20px;
        min-height: 110px;
    }

    .metric-label {
        color: #778397;
        font-size: 12px;
        margin-bottom: 7px;
    }

    .metric-value {
        color: #172033;
        font-size: 29px;
        font-weight: 800;
    }

    .metric-small {
        color: #778397;
        font-size: 11px;
        margin-top: 4px;
    }

    .upload-box {
        background: #f8fbff;
        border: 1px dashed #b9c9df;
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 20px;
    }

    /* ======================================================
       RESPONSIVE
       ====================================================== */

    @media (max-width: 1000px) {

        .hero-grid {
            grid-template-columns: 1fr;
        }

        .hero {
            padding: 45px 30px;
        }

        .laptop-area {
            min-height: 350px;
        }

        .feature-grid,
        .pricing-grid,
        .steps {
            grid-template-columns: 1fr 1fr;
        }

        .solution-grid {
            grid-template-columns: 1fr;
        }

        .nav-links {
            display: none;
        }

        .trusted-logos {
            gap: 30px;
        }
    }

    @media (max-width: 650px) {

        .feature-grid,
        .pricing-grid,
        .steps,
        .solution-grid {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 45px;
        }

        .hero {
            padding: 35px 20px;
        }

        .workflow {
            padding: 30px 20px;
        }

        .footer-grid {
            grid-template-columns: 1fr 1fr;
        }

        .dashboard-cards {
            grid-template-columns: 1fr 1fr;
        }

        .dashboard-middle {
            grid-template-columns: 1fr;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False


# ============================================================
# NAVIGATION
# ============================================================

def navigate(page_name):
    st.session_state.page = page_name


# ============================================================
# TOP NAVIGATION
# ============================================================

st.markdown(
    """
    <div class="top-nav">

        <div class="brand">
            <div class="brand-icon">D</div>

            <div>
                <div class="brand-name">DataForge</div>
                <div class="brand-subtitle">ANALYTICS</div>
            </div>
        </div>

        <div class="nav-links">
            <span class="nav-link">Product</span>
            <span class="nav-link">Solutions</span>
            <span class="nav-link">Pricing</span>
            <span class="nav-link">Resources</span>
            <span class="nav-link">Blog</span>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown("## 🔍 DataForge")

    st.caption("Automated Data Quality Platform")

    selected_page = st.radio(
        "Navigation",
        [
            "Home",
            "Analyze Dataset",
            "About",
        ],
        index=[
            "Home",
            "Analyze Dataset",
            "About",
        ].index(st.session_state.page),
    )

    st.session_state.page = selected_page

    st.divider()

    st.caption(
        "Your data quality engine for detecting, "
        "repairing, validating and reporting data issues."
    )


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "Home":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        """
        <section class="hero">

            <div class="hero-grid">

                <div>

                    <div class="eyebrow">
                        AI-ready data quality infrastructure
                    </div>

                    <h1 class="hero-title">
                        Transform Data
                        <br>
                        Into <span>Confident Decisions</span>
                    </h1>

                    <p class="hero-description">
                        Automatically profile, detect, score, repair,
                        validate and report data-quality issues
                        before they impact your analysis.
                    </p>

                    <div class="hero-pills">
                        <span class="pill">✓ Missing Values</span>
                        <span class="pill">✓ Duplicates</span>
                        <span class="pill">✓ Outliers</span>
                        <span class="pill">✓ Validation</span>
                        <span class="pill">✓ Automated Repair</span>
                    </div>

                </div>

                <div class="laptop-area">

                    <div class="laptop-glow"></div>

                    <div class="laptop">

                        <div class="laptop-screen">

                            <div class="dashboard-window">

                                <div class="dashboard-top">
                                    <div class="dashboard-title">
                                        Data Quality Analytics
                                    </div>

                                    <div class="dashboard-badge">
                                        ANALYSIS READY
                                    </div>
                                </div>

                                <div class="dashboard-cards">

                                    <div class="dash-card">
                                        <div class="dash-label">
                                            Quality Score
                                        </div>
                                        <div class="dash-value">
                                            96%
                                        </div>
                                        <div class="dash-change">
                                            ↑ Excellent
                                        </div>
                                    </div>

                                    <div class="dash-card">
                                        <div class="dash-label">
                                            Completeness
                                        </div>
                                        <div class="dash-value">
                                            98%
                                        </div>
                                        <div class="dash-change">
                                            ↑ Healthy
                                        </div>
                                    </div>

                                    <div class="dash-card">
                                        <div class="dash-label">
                                            Records
                                        </div>
                                        <div class="dash-value">
                                            10.2K
                                        </div>
                                        <div class="dash-change">
                                            ↑ Processed
                                        </div>
                                    </div>

                                    <div class="dash-card">
                                        <div class="dash-label">
                                            Repaired
                                        </div>
                                        <div class="dash-value">
                                            127
                                        </div>
                                        <div class="dash-change">
                                            ✓ Complete
                                        </div>
                                    </div>

                                </div>

                                <div class="dashboard-middle">

                                    <div class="chart-box">

                                        <div class="chart-title">
                                            Quality Trend
                                        </div>

                                        <div class="fake-chart">
                                            <div class="fake-line"></div>
                                        </div>

                                    </div>

                                    <div class="quality-box">

                                        <div class="chart-title">
                                            Dataset Readiness
                                        </div>

                                        <div class="quality-circle">
                                            96%
                                        </div>

                                        <div class="quality-caption">
                                            Ready for analysis
                                        </div>

                                    </div>

                                </div>

                            </div>

                        </div>

                        <div class="laptop-base"></div>

                    </div>

                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # HERO BUTTONS
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    button1, button2, spacer = st.columns([1.3, 1.3, 3])

    with button1:

        if st.button(
            "🚀 Start Free Analysis",
            use_container_width=True,
        ):
            st.session_state.page = "Analyze Dataset"
            st.rerun()

    with button2:

        if st.button(
            "▶ View Product",
            use_container_width=True,
        ):
            st.session_state.page = "Analyze Dataset"
            st.rerun()

    st.markdown(
        """
        <div class="hero-note">
            No account required • Upload a CSV • Get results instantly
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # TRUSTED
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="trusted">

            <div class="trusted-label">
                Built for modern data teams
            </div>

            <div class="trusted-logos">
                <span>Data Teams</span>
                <span>Analytics</span>
                <span>Research</span>
                <span>Operations</span>
                <span>Engineering</span>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    st.markdown(
        """
        <section class="section">

            <div class="section-kicker">
                One platform
            </div>

            <h2 class="section-title">
                Everything you need for
                <br>
                trusted data.
            </h2>

            <p class="section-description">
                Turn messy datasets into analysis-ready data
                with a complete automated quality workflow.
            </p>

            <div class="feature-grid">

                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3>Dataset Profiling</h3>
                    <p>
                        Understand your dataset structure,
                        columns, types, statistics and
                        completeness at a glance.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🚨</div>
                    <h3>Smart Detection</h3>
                    <p>
                        Detect missing values, duplicates,
                        outliers and other common
                        data-quality problems.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🛠️</div>
                    <h3>Automated Repair</h3>
                    <p>
                        Repair common quality issues and
                        produce a clean dataset without
                        manually editing every row.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <h3>Quality Scoring</h3>
                    <p>
                        Get a simple quality score and
                        understand exactly which issues
                        affect your dataset.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">✅</div>
                    <h3>Validation</h3>
                    <p>
                        Validate the repaired dataset and
                        verify whether quality rules have
                        been satisfied.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Reporting</h3>
                    <p>
                        Generate repair logs and downloadable
                        quality reports for transparent
                        data operations.
                    </p>
                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------------

    st.markdown(
        """
        <section class="section">

            <div class="workflow">

                <div class="section-kicker">
                    How it works
                </div>

                <h2 class="section-title">
                    From messy data
                    <br>
                    to trusted data.
                </h2>

                <div class="steps">

                    <div class="step">
                        <div class="step-number">01</div>
                        <h3>Upload</h3>
                        <p>
                            Upload your CSV dataset directly
                            into the platform.
                        </p>
                    </div>

                    <div class="step">
                        <div class="step-number">02</div>
                        <h3>Analyze</h3>
                        <p>
                            Profile the dataset and detect
                            quality problems automatically.
                        </p>
                    </div>

                    <div class="step">
                        <div class="step-number">03</div>
                        <h3>Repair</h3>
                        <p>
                            Automatically repair supported
                            data-quality issues.
                        </p>
                    </div>

                    <div class="step">
                        <div class="step-number">04</div>
                        <h3>Validate</h3>
                        <p>
                            Validate the repaired dataset
                            and download the final report.
                        </p>
                    </div>

                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SOLUTIONS
    # --------------------------------------------------------

    st.markdown(
        """
        <section class="section">

            <div class="section-kicker">
                Solutions
            </div>

            <h2 class="section-title">
                Built for every team
                <br>
                working with data.
            </h2>

            <div class="solution-grid">

                <div class="solution-card">
                    <h3>📈 Analytics Teams</h3>
                    <p>
                        Start analysis with confidence by
                        understanding and cleaning your
                        datasets before building dashboards.
                    </p>

                    <div class="solution-list">
                        ✓ Faster analysis<br>
                        ✓ Cleaner datasets<br>
                        ✓ Transparent quality scores
                    </div>
                </div>

                <div class="solution-card">
                    <h3>🤖 Data & ML Teams</h3>
                    <p>
                        Prepare structured datasets for
                        downstream machine-learning and
                        analytical workflows.
                    </p>

                    <div class="solution-list">
                        ✓ Consistent inputs<br>
                        ✓ Automated validation<br>
                        ✓ Repair history
                    </div>
                </div>

                <div class="solution-card">
                    <h3>🏢 Business Operations</h3>
                    <p>
                        Improve the reliability of operational
                        datasets without requiring every
                        team member to understand Python.
                    </p>

                    <div class="solution-list">
                        ✓ Simple upload workflow<br>
                        ✓ Clear quality indicators<br>
                        ✓ Downloadable reports
                    </div>
                </div>

                <div class="solution-card">
                    <h3>🔬 Researchers</h3>
                    <p>
                        Inspect datasets systematically before
                        using them for research and statistical
                        analysis.
                    </p>

                    <div class="solution-list">
                        ✓ Profiling<br>
                        ✓ Statistical detection<br>
                        ✓ Reproducible repair logs
                    </div>
                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # PRICING
    # --------------------------------------------------------

    st.markdown(
        """
        <section class="section">

            <div class="section-kicker">
                Pricing
            </div>

            <h2 class="section-title">
                Start free.
                <br>
                Scale when you need to.
            </h2>

            <p class="section-description">
                These plans are presented as the product
                experience for now. Billing can be connected
                later when the application is deployed.
            </p>

            <div class="pricing-grid">

                <div class="pricing-card">

                    <div class="pricing-name">
                        Free
                    </div>

                    <div class="pricing-price">
                        $0
                        <span>/month</span>
                    </div>

                    <div class="pricing-description">
                        For individuals exploring data quality.
                    </div>

                    <div class="pricing-list">
                        ✓ CSV analysis<br>
                        ✓ Profiling<br>
                        ✓ Detection<br>
                        ✓ Quality scoring<br>
                        ✓ Basic reports
                    </div>

                </div>

                <div class="pricing-card featured">

                    <div class="pricing-name">
                        Professional
                    </div>

                    <div class="pricing-price">
                        $29
                        <span>/month</span>
                    </div>

                    <div class="pricing-description">
                        For analysts and growing data teams.
                    </div>

                    <div class="pricing-list">
                        ✓ Everything in Free<br>
                        ✓ Automated repair<br>
                        ✓ Validation<br>
                        ✓ Repair logs<br>
                        ✓ Advanced reporting
                    </div>

                </div>

                <div class="pricing-card">

                    <div class="pricing-name">
                        Enterprise
                    </div>

                    <div class="pricing-price">
                        Custom
                    </div>

                    <div class="pricing-description">
                        For organizations with larger
                        data-quality requirements.
                    </div>

                    <div class="pricing-list">
                        ✓ Custom workflows<br>
                        ✓ Custom rules<br>
                        ✓ Team access<br>
                        ✓ Enterprise support<br>
                        ✓ Custom integrations
                    </div>

                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CTA
    # --------------------------------------------------------

    st.markdown(
        """
        <section class="cta">

            <div class="section-kicker">
                Get started
            </div>

            <h2>
                Make your data
                <br>
                ready for decisions.
            </h2>

            <p>
                Upload a dataset and discover its quality
                in minutes.
            </p>

        </section>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2, 2, 3])

    with c1:

        if st.button(
            "🚀 Start Free Analysis",
            use_container_width=True,
        ):
            st.session_state.page = "Analyze Dataset"
            st.rerun()

    with c2:

        if st.button(
            "🔍 Analyze a Dataset",
            use_container_width=True,
        ):
            st.session_state.page = "Analyze Dataset"
            st.rerun()

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    st.markdown(
        """
        <footer class="footer">

            <div class="footer-grid">

                <div>
                    <div class="brand">
                        <div class="brand-icon">D</div>

                        <div>
                            <div class="brand-name">
                                DataForge
                            </div>

                            <div class="brand-subtitle">
                                ANALYTICS
                            </div>
                        </div>
                    </div>

                    <br>

                    <p>
                        Automated data quality infrastructure
                        for reliable analytics and decision making.
                    </p>
                </div>

                <div>
                    <h4>Product</h4>
                    <ul>
                        <li>Data Profiling</li>
                        <li>Detection</li>
                        <li>Repair</li>
                        <li>Validation</li>
                    </ul>
                </div>

                <div>
                    <h4>Company</h4>
                    <ul>
                        <li>About</li>
                        <li>Solutions</li>
                        <li>Pricing</li>
                        <li>Contact</li>
                    </ul>
                </div>

                <div>
                    <h4>Resources</h4>
                    <ul>
                        <li>Documentation</li>
                        <li>Blog</li>
                        <li>Guides</li>
                        <li>Support</li>
                    </ul>
                </div>

            </div>

            <div class="footer-bottom">

                <span>
                    © 2026 DataForge Analytics.
                    All rights reserved.
                </span>

                <span>
                    Built with Python • Pandas • Streamlit
                </span>

            </div>

        </footer>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ANALYZE DATASET PAGE
# ============================================================

elif st.session_state.page == "Analyze Dataset":

    st.markdown(
        """
        <div class="dashboard-header">

            <div class="dashboard-title">
                Data Quality Dashboard
            </div>

            <div class="dashboard-subtitle">
                Upload a dataset and run the complete
                data-quality pipeline.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="upload-box">

            <h3 style="margin-top:0;color:#172033;">
                📂 Upload your dataset
            </h3>

            <p style="color:#718096;">
                CSV files are currently supported.
                Your dataset will be profiled, analyzed,
                scored, repaired and validated.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload a CSV dataset to begin analysis.",
    )

    if uploaded_file is None:

        st.info(
            "👆 Choose a CSV file above to start."
        )

        st.markdown(
            """
            ### The analysis pipeline

            **1. Profile** → Understand the dataset

            **2. Detect** → Find quality problems

            **3. Score** → Calculate the quality score

            **4. Repair** → Automatically repair supported issues

            **5. Validate** → Verify the repaired dataset

            **6. Report** → Generate downloadable results
            """
        )

    else:

        try:

            # ------------------------------------------------
            # LOAD DATA
            # ------------------------------------------------

            df = pd.read_csv(uploaded_file)

            st.success(
                f"Dataset loaded successfully: "
                f"{uploaded_file.name}"
            )

            # ------------------------------------------------
            # RUN PIPELINE
            # ------------------------------------------------

            with st.spinner(
                "Running complete data-quality pipeline..."
            ):

                profile = profile_dataset(df)

                detection = run_detection(df)

                scoring = calculate_quality_score(
                    df,
                    detection,
                )

                repaired_df, repair_report = run_repairs(
                    df
                )

                validation = validate_dataset(
                    repaired_df
                )

                repair_log = create_repair_log(
                    df,
                    repaired_df,
                    repair_report,
                )

                quality_report = generate_quality_report(
                    profile=profile,
                    detection=detection,
                    scoring=scoring,
                    validation=validation,
                    repair_report=repair_report,
                )

            # =================================================
            # SUMMARY
            # =================================================

            st.markdown(
                "## 📊 Quality Overview"
            )

            dataset_info = profile.get(
                "dataset",
                {},
            )

            missing_info = profile.get(
                "missing_values",
                {},
            )

            duplicate_info = detection.get(
                "duplicates",
                {},
            )

            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            Rows
                        </div>
                        <div class="metric-value">
                            {dataset_info.get("rows", len(df))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c2:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            Columns
                        </div>
                        <div class="metric-value">
                            {dataset_info.get("columns", len(df.columns))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c3:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            Missing Values
                        </div>
                        <div class="metric-value">
                            {missing_info.get("total", int(df.isna().sum().sum()))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c4:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            Duplicate Rows
                        </div>
                        <div class="metric-value">
                            {duplicate_info.get("duplicate_count", int(df.duplicated().sum()))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c5:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">
                            Quality Score
                        </div>
                        <div class="metric-value">
                            {scoring.get("score", 0):.2f}
                        </div>
                        <div class="metric-small">
                            {scoring.get("grade", "N/A")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # =================================================
            # SCORE
            # =================================================

            st.divider()

            st.markdown("## 🎯 Data Quality Score")

            score_col1, score_col2, score_col3 = st.columns(3)

            with score_col1:

                st.metric(
                    "Overall Score",
                    f"{scoring.get('score', 0):.2f}/100",
                )

            with score_col2:

                st.metric(
                    "Grade",
                    scoring.get("grade", "N/A"),
                )

            with score_col3:

                st.metric(
                    "Validation Score",
                    f"{validation.get('validation_score', 0):.2f}/100",
                )

            score = float(
                scoring.get("score", 0)
            )

            if score >= 90:

                st.success(
                    "🟢 Excellent data quality."
                )

            elif score >= 75:

                st.info(
                    "🔵 Good data quality."
                )

            elif score >= 50:

                st.warning(
                    "🟡 Fair data quality. Improvement recommended."
                )

            else:

                st.error(
                    "🔴 Poor data quality. Repair recommended."
                )

            # =================================================
            # ORIGINAL DATA
            # =================================================

            st.divider()

            st.markdown("## 👀 Original Dataset")

            st.dataframe(
                df.head(100),
                use_container_width=True,
                hide_index=True,
            )

            # =================================================
            # DETECTION
            # =================================================

            st.divider()

            st.markdown("## 🔎 Detection Results")

            tab1, tab2, tab3 = st.tabs(
                [
                    "Missing Values",
                    "Duplicates",
                    "Outliers",
                ]
            )

            # ------------------------------------------------
            # MISSING
            # ------------------------------------------------

            with tab1:

                missing_values = detection.get(
                    "missing_values",
                    {},
                )

                missing_rows = []

                for column, details in missing_values.items():

                    count = details.get(
                        "missing_count",
                        0,
                    )

                    if count > 0:

                        missing_rows.append(
                            {
                                "Column": column,
                                "Missing Count": count,
                                "Missing %": details.get(
                                    "missing_percentage",
                                    0,
                                ),
                            }
                        )

                if missing_rows:

                    st.dataframe(
                        pd.DataFrame(missing_rows),
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.success(
                        "✅ No missing values detected."
                    )

            # ------------------------------------------------
            # DUPLICATES
            # ------------------------------------------------

            with tab2:

                duplicate_count = duplicate_info.get(
                    "duplicate_count",
                    int(df.duplicated().sum()),
                )

                if duplicate_count:

                    st.warning(
                        f"{duplicate_count} duplicate rows detected."
                    )

                    duplicate_rows = df[
                        df.duplicated(
                            keep=False
                        )
                    ]

                    st.dataframe(
                        duplicate_rows,
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.success(
                        "✅ No duplicate rows detected."
                    )

            # ------------------------------------------------
            # OUTLIERS
            # ------------------------------------------------

            with tab3:

                outlier_data = detection.get(
                    "outliers",
                    {},
                )

                outlier_rows = []

                for column, details in outlier_data.items():

                    outlier_rows.append(
                        {
                            "Column": column,
                            "Outlier Count": details.get(
                                "outlier_count",
                                0,
                            ),
                            "Lower Bound": details.get(
                                "lower_bound",
                                None,
                            ),
                            "Upper Bound": details.get(
                                "upper_bound",
                                None,
                            ),
                        }
                    )

                if outlier_rows:

                    st.dataframe(
                        pd.DataFrame(outlier_rows),
                        use_container_width=True,
                        hide_index=True,
                    )

                else:

                    st.info(
                        "No numerical outlier information available."
                    )

            # =================================================
            # SCORING
            # =================================================

            st.divider()

            st.markdown(
                "## ⚖️ Quality Score Breakdown"
            )

            penalties = scoring.get(
                "penalties",
                {},
            )

            penalty_df = pd.DataFrame(
                {
                    "Issue": [
                        "Missing Values",
                        "Duplicates",
                        "Outliers",
                    ],
                    "Penalty": [
                        penalties.get(
                            "missing_values",
                            0,
                        ),
                        penalties.get(
                            "duplicates",
                            0,
                        ),
                        penalties.get(
                            "outliers",
                            0,
                        ),
                    ],
                }
            )

            st.dataframe(
                penalty_df,
                use_container_width=True,
                hide_index=True,
            )

            # =================================================
            # REPAIR
            # =================================================

            st.divider()

            st.markdown(
                "## 🛠️ Automated Repair"
            )

            r1, r2, r3 = st.columns(3)

            with r1:

                st.metric(
                    "Original Rows",
                    repair_report.get(
                        "original_rows",
                        len(df),
                    ),
                )

            with r2:

                st.metric(
                    "Final Rows",
                    repair_report.get(
                        "final_rows",
                        len(repaired_df),
                    ),
                )

            with r3:

                st.metric(
                    "Total Repaired",
                    repair_report.get(
                        "total_repaired",
                        0,
                    ),
                )

            operations = repair_report.get(
                "operations",
                {},
            )

            if operations:

                operation_rows = []

                for operation, details in operations.items():

                    operation_rows.append(
                        {
                            "Operation": operation,
                            "Details": str(details),
                        }
                    )

                st.dataframe(
                    pd.DataFrame(operation_rows),
                    use_container_width=True,
                    hide_index=True,
                )

            # =================================================
            # BEFORE AFTER
            # =================================================

            st.divider()

            st.markdown(
                "## 🔄 Before vs After"
            )

            before_col, after_col = st.columns(2)

            with before_col:

                st.markdown("### Original")

                st.dataframe(
                    df.head(100),
                    use_container_width=True,
                    hide_index=True,
                )

            with after_col:

                st.markdown("### Repaired")

                st.dataframe(
                    repaired_df.head(100),
                    use_container_width=True,
                    hide_index=True,
                )

            # =================================================
            # REPAIR LOG
            # =================================================

            st.divider()

            st.markdown(
                "## 📝 Repair Log"
            )

            if (
                repair_log is not None
                and not repair_log.empty
            ):

                st.dataframe(
                    repair_log,
                    use_container_width=True,
                    hide_index=True,
                )

                repair_log_csv = repair_log.to_csv(
                    index=False
                )

                st.download_button(
                    "⬇️ Download Repair Log",
                    data=repair_log_csv,
                    file_name="repair_log.csv",
                    mime="text/csv",
                    use_container_width=False,
                )

            else:

                st.success(
                    "✅ No changes were required."
                )

            # =================================================
            # VALIDATION
            # =================================================

            st.divider()

            st.markdown(
                "## ✅ Post-Repair Validation"
            )

            v1, v2, v3 = st.columns(3)

            with v1:

                st.metric(
                    "Valid Dataset",
                    "Yes"
                    if validation.get(
                        "valid",
                        False,
                    )
                    else "No",
                )

            with v2:

                st.metric(
                    "Validation Score",
                    f"{validation.get('validation_score', 0):.2f}",
                )

            with v3:

                st.metric(
                    "Passed Rules",
                    validation.get(
                        "passed_rules",
                        0,
                    ),
                )

            if validation.get(
                "valid",
                False,
            ):

                st.success(
                    "✅ Repaired dataset passed validation."
                )

            else:

                st.error(
                    f"❌ {validation.get('failed_rules', 0)} "
                    "validation rules failed."
                )

            # =================================================
            # QUALITY REPORT
            # =================================================

            st.divider()

            st.markdown(
                "## 📄 Quality Report"
            )

            report_path = save_quality_report(
                quality_report,
                "quality_report.json",
            )

            report_file_path = Path(
                report_path
            )

            if report_file_path.exists():

                report_data = report_file_path.read_text(
                    encoding="utf-8"
                )

                st.download_button(
                    "⬇️ Download Quality Report",
                    data=report_data,
                    file_name="quality_report.json",
                    mime="application/json",
                    use_container_width=False,
                )

            st.success(
                "🎉 Complete data-quality analysis finished."
            )

        except Exception as error:

            st.error(
                "Unable to process the dataset."
            )

            st.exception(error)


# ============================================================
# ABOUT PAGE
# ============================================================

elif st.session_state.page == "About":

    st.markdown(
        """
        <section class="section">

            <div class="section-kicker">
                About DataForge
            </div>

            <h1 class="section-title">
                Better data starts
                <br>
                with better quality.
            </h1>

            <p class="section-description">
                DataForge is an automated data-quality and
                repair platform designed to help teams understand
                the health of structured datasets before those
                datasets are used for analysis, reporting or
                decision making.
            </p>

            <div class="feature-grid">

                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3>Profile</h3>
                    <p>
                        Understand dataset structure,
                        statistics and completeness.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <h3>Understand</h3>
                    <p>
                        Detect the problems affecting
                        data quality.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🛠️</div>
                    <h3>Repair</h3>
                    <p>
                        Automatically fix supported
                        quality issues.
                    </p>
                </div>

            </div>

        </section>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "🚀 Start Analyzing Data",
        use_container_width=False,
    ):

        st.session_state.page = "Analyze Dataset"
        st.rerun()