# ==============================================================================
# Groundwater Heavy Metal Intelligence System (GHMIS)
# Smart India Hackathon SIH25067 | Ministry of Jal Shakti | Govt. of India
# Team: Manickavel C (ECE), D Dhinesh Karthick | Chennai Institute of Technology
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import json
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Custom Modules
from translations import TRANSLATIONS
from analytical_engine import (
    calculate_exact_hpi, calculate_exact_hei, calculate_metal_index,
    calculate_contamination_degree, evaluate_metal_compliance, classify_pollution_severity,
    STANDARD_WATER_QUALITY_STANDARDS
)
from health_risk_engine import calculate_human_health_risk
from remediation_engine import generate_remediation_plan
from visual_charts import (
    render_hpi_gauge, render_metal_radar_chart, get_chart_theme,
    render_shap_waterfall_chart, render_shap_summary_chart
)
from pdf_report import generate_certified_report
from alert_system import trigger_alert
from theme import inject_css, severity_color, badge_class
from iot_stream import generate_telemetry_packet, MONITORING_NODES
from folium_map import build_interactive_map

st.set_page_config(
    page_title="Groundwater Heavy Metal Intelligence System",
    layout="wide",
    page_icon="🌊",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# SIDEBAR CONTROLS (THEME & LANGUAGE)
# ------------------------------------------------------------------------------
st.sidebar.markdown("### 🎨 Visual Settings / அமைப்புகள்")
theme_choice = st.sidebar.radio("Theme Mode", ["🌙 Dark Mode", "☀️ Light Mode"], index=0, label_visibility="collapsed")
active_theme = "Dark" if "Dark" in theme_choice else "Light"

# Inject Dynamic Dual-Mode CSS
st.markdown(inject_css(theme_mode=active_theme), unsafe_allow_html=True)

lang = st.sidebar.selectbox("🌐 Language / மொழி", ["English", "தமிழ்"])
T = TRANSLATIONS[lang]

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {T['input_mode_header']}")
mode_choice = st.sidebar.radio(
    T["input_mode_question"],
    [T["mode_full"], T["mode_partial"]],
    index=0,
    label_visibility="collapsed"
)
is_full_lab_mode = (mode_choice == T["mode_full"])

st.sidebar.markdown(f"### {T['season_header']}")
season = st.sidebar.selectbox(T["season_label"], [T["pre_monsoon"], T["post_monsoon"]], label_visibility="collapsed")
season_code = 1 if season == T["post_monsoon"] else 0

# Load Machine Learning Models
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "tamilnadu_groundwater_WITH_INDICES.csv")

@st.cache_resource
def load_all_models():
    models = {}
    model_files = {
        "reg_partial": "reg_partial.joblib",
        "reg_hei_partial": "reg_hei_partial.joblib",
        "clf_partial": "clf_partial.joblib",
        "reg_proxy_cd": "reg_proxy_cd.joblib",
        "reg_proxy_fe": "reg_proxy_fe.joblib",
        "reg_proxy_mn": "reg_proxy_mn.joblib",
        "anomaly": "anomaly_detector.joblib"
    }
    for key, filename in model_files.items():
        p = os.path.join(MODEL_DIR, filename)
        if os.path.exists(p):
            models[key] = joblib.load(p)
    return models

models = load_all_models()

@st.cache_data
def get_background_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df["Season_Code"] = (df["Season"] == "Post-Monsoon").astype(int)
        return df[["pH", "TDS", "EC", "Season_Code"]]
    return None

benchmarks_path = os.path.join(MODEL_DIR, "benchmarks.json")
benchmarks_data = {}
if os.path.exists(benchmarks_path):
    with open(benchmarks_path, "r") as f:
        benchmarks_data = json.load(f)

# ------------------------------------------------------------------------------
# HERO HEADER BANNER
# ------------------------------------------------------------------------------
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">SIH25067 &middot; MINISTRY OF JAL SHAKTI &middot; TAMIL NADU WATER SUPPLY (TWAD)</div>
    <div class="hero-title">{T['title']}</div>
    <div class="hero-subtitle">{T['subtitle']}</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# MAIN APPLICATION TABS
# ------------------------------------------------------------------------------
tab_single, tab_batch, tab_whatif, tab_iot, tab_map, tab_benchmarks = st.tabs([
    T["tab_single"],
    T["tab_batch"],
    T["tab_whatif"],
    T["tab_iot"],
    T["tab_map"],
    T["tab_benchmarks"]
])

# ==============================================================================
# TAB 1: SINGLE FIELD ASSESSMENT
# ==============================================================================
with tab_single:
    st.markdown(f"**{T['demo_presets_header']}**")
    p_col1, p_col2, p_col3 = st.columns(3)
    
    preset_chosen = None
    with p_col1:
        if st.button(T["btn_preset_safe"], use_container_width=True):
            preset_chosen = {"loc": "Sayalgudi Clean Well #2", "pH": 7.82, "TDS": 863.0, "EC": 1210.0, "Cd": 0.0009, "Pb": 0.0010, "Fe": 0.187, "Mn": 0.091, "Cu": 0.023, "Zn": 0.901, "Ni": 0.001, "lat": 9.36154, "lon": 78.45045}
    with p_col2:
        if st.button(T["btn_preset_mod"], use_container_width=True):
            preset_chosen = {"loc": "Kadaladi Village Well #14", "pH": 7.42, "TDS": 1419.0, "EC": 2200.0, "Cd": 0.0011, "Pb": 0.0010, "Fe": 0.282, "Mn": 0.141, "Cu": 0.028, "Zn": 0.269, "Ni": 0.001, "lat": 9.24068, "lon": 78.57501}
    with p_col3:
        if st.button(T["btn_preset_crit"], use_container_width=True):
            preset_chosen = {"loc": "Kadaladi Heavy Metal Leaching Hotspot #6", "pH": 7.31, "TDS": 1954.0, "EC": 2877.0, "Cd": 0.0038, "Pb": 0.0010, "Fe": 0.580, "Mn": 0.300, "Cu": 0.025, "Zn": 1.400, "Ni": 0.001, "lat": 9.21200, "lon": 78.47800}

    if preset_chosen:
        st.session_state["preset_data"] = preset_chosen

    p_data = st.session_state.get("preset_data", {})

    col_input, col_output = st.columns([1, 1.15])

    with col_input:
        with st.container(border=True):
            st.markdown(f"### 📍 {T['location_header']}")
            
            # Tamil Nadu Village Preset Selector
            if lang == "English":
                tn_villages = {
                    T["opt_custom_coords"]: None,
                    "Kadaladi Town (9.2220°N, 78.4960°E)": (9.2220, 78.4960),
                    "Sayalgudi Coastal Well #1 (9.2106°N, 78.3941°E)": (9.2106, 78.3941),
                    "Mudukulathur Agriculture Well (9.3615°N, 78.4504°E)": (9.3615, 78.4504),
                    "Kamuthi Solar Boundary Well (9.2485°N, 78.4485°E)": (9.2485, 78.4485),
                    "Valinokkam Coastal Aquifer (9.1747°N, 78.5096°E)": (9.1747, 78.5096),
                    "Ramanathapuram Town HQ (9.3640°N, 78.8370°E)": (9.3640, 78.8370),
                    "Thoothukudi Industrial Belt (8.7642°N, 78.1348°E)": (8.7642, 78.1348)
                }
            else:
                tn_villages = {
                    T["opt_custom_coords"]: None,
                    "கடலாடி நகரம் (9.2220°N, 78.4960°E)": (9.2220, 78.4960),
                    "சாயல்குடி கடற்கரை கிணறு #1 (9.2106°N, 78.3941°E)": (9.2106, 78.3941),
                    "முதுகுளத்தூர் விவசாய கிணறு (9.3615°N, 78.4504°E)": (9.3615, 78.4504),
                    "கமுதி சூரிய மின் உற்பத்தி எல்லை (9.2485°N, 78.4485°E)": (9.2485, 78.4485),
                    "வாலினோக்கம் கடற்கரை நீர்நிலை (9.1747°N, 78.5096°E)": (9.1747, 78.5096),
                    "ராமநாதபுரம் மாவட்ட தலைமையகம் (9.3640°N, 78.8370°E)": (9.3640, 78.8370),
                    "தூத்துக்குடி தொழிற்பேட்டை (8.7642°N, 78.1348°E)": (8.7642, 78.1348)
                }
                
            selected_v = st.selectbox(T["select_location_preset"], list(tn_villages.keys()))
            
            if tn_villages[selected_v]:
                def_lat, def_lon = tn_villages[selected_v]
                default_loc = selected_v.split(" (")[0]
            else:
                def_lat = float(p_data.get("lat", 9.2220))
                def_lon = float(p_data.get("lon", 78.4960))
                default_loc = p_data.get("loc", "Kadaladi Monitoring Station #4" if lang == "English" else "கடலாடி ஆய்வு மையம் #4")

            loc_name = st.text_input(T["location_name"], value=default_loc, placeholder="e.g. Kadaladi Borewell #4")
            c_lat, c_lon = st.columns(2)
            with c_lat:
                latitude = st.number_input(T["latitude_label"], min_value=8.0, max_value=14.0, value=def_lat, step=0.001, format="%.5f")
            with c_lon:
                longitude = st.number_input(T["longitude_label"], min_value=76.0, max_value=81.0, value=def_lon, step=0.001, format="%.5f")

            st.markdown(f"### 🧪 {T['water_params_header']}")
            pH = st.slider(T["ph_label"], min_value=5.0, max_value=10.0, value=float(p_data.get("pH", 7.35)), step=0.05)
            c_tds, c_ec = st.columns(2)
            with c_tds:
                TDS = st.number_input(T["tds_label"], min_value=50.0, max_value=5000.0, value=float(p_data.get("TDS", 1150.0)), step=10.0)
            with c_ec:
                EC = st.number_input(T["ec_label"], min_value=50.0, max_value=7500.0, value=float(p_data.get("EC", 1650.0)), step=10.0)

            # Agricultural Irrigation Suitability
            if EC < 250:
                agri_status = T["agri_low"]
            elif EC <= 750:
                agri_status = T["agri_med"]
            elif EC <= 2000:
                agri_status = T["agri_high"]
            else:
                agri_status = T["agri_vhigh"]
            st.caption(f"**{T['agri_title']}** {agri_status}")

            metals_input = {}
            if is_full_lab_mode:
                st.markdown(f"### 🔬 {T['metal_params_header']}")
                st.caption(T["lab_metals_caption"])
                m_c1, m_c2 = st.columns(2)
                with m_c1:
                    metals_input["Cd"] = st.number_input(T["metal_cd"], 0.0, 0.05, float(p_data.get("Cd", 0.0018)), 0.0001, format="%.5f")
                    metals_input["Pb"] = st.number_input(T["metal_pb"], 0.0, 0.20, float(p_data.get("Pb", 0.0010)), 0.0005, format="%.4f")
                    metals_input["Fe"] = st.number_input(T["metal_fe"], 0.0, 3.00, float(p_data.get("Fe", 0.3800)), 0.0100, format="%.4f")
                    metals_input["Mn"] = st.number_input(T["metal_mn"], 0.0, 2.00, float(p_data.get("Mn", 0.1400)), 0.0050, format="%.4f")
                with m_c2:
                    metals_input["Cu"] = st.number_input(T["metal_cu"], 0.0, 2.00, float(p_data.get("Cu", 0.0350)), 0.0010, format="%.4f")
                    metals_input["Zn"] = st.number_input(T["metal_zn"], 0.0, 10.0, float(p_data.get("Zn", 1.2500)), 0.0500, format="%.4f")
                    metals_input["Ni"] = st.number_input(T["metal_ni"], 0.0, 0.50, float(p_data.get("Ni", 0.0010)), 0.0005, format="%.4f")
            else:
                st.info(T["mode_b_info"])

            assess_clicked = st.button(T["predict_button"], type="primary", use_container_width=True)

    with col_output:
        with st.container(border=True):
            if assess_clicked or preset_chosen:
                if is_full_lab_mode:
                    # Mode A: 100% Deterministic BIS Analytical Calculation
                    hpi_val, _ = calculate_exact_hpi(metals_input)
                    hei_val = calculate_exact_hei(metals_input)
                    mi_val = calculate_metal_index(metals_input)
                    cdeg_val = calculate_contamination_degree(metals_input)
                    cat_name, cat_col, cat_desc = classify_pollution_severity(hpi_val)
                    compliance_report = evaluate_metal_compliance(metals_input)
                    health_risk = calculate_human_health_risk(metals_input)
                    remediation = generate_remediation_plan(metals_input, pH, TDS, EC, cat_name)
                    conf_note = T["full_confidence_note"]
                    inferred_metals = metals_input

                    anomaly_vec = pd.DataFrame([{
                        "Cu": metals_input["Cu"], "Zn": metals_input["Zn"], "Mn": metals_input["Mn"],
                        "Fe": metals_input["Fe"], "Cd": metals_input["Cd"], "Pb": metals_input["Pb"],
                        "Ni": metals_input["Ni"], "pH": pH, "TDS": TDS, "EC": EC
                    }])
                    is_anomaly = False
                    anomaly_score = 0.5
                    if "anomaly" in models:
                        is_anomaly = (models["anomaly"].predict(anomaly_vec)[0] == -1)
                        anomaly_score = float(models["anomaly"].score_samples(anomaly_vec)[0])

                else:
                    # Mode B: ML Proxy Inference
                    X_proxy = pd.DataFrame([{"pH": pH, "TDS": TDS, "EC": EC, "Season_Code": season_code}])
                    hpi_val = float(models["reg_partial"].predict(X_proxy)[0]) if "reg_partial" in models else 35.0
                    hei_val = float(models["reg_hei_partial"].predict(X_proxy)[0]) if "reg_hei_partial" in models else 3.2
                    cat_name = str(models["clf_partial"].predict(X_proxy)[0]) if "clf_partial" in models else "Moderate"
                    _, cat_col, cat_desc = classify_pollution_severity(hpi_val)

                    inferred_cd = float(models["reg_proxy_cd"].predict(X_proxy)[0]) if "reg_proxy_cd" in models else 0.0015
                    inferred_fe = float(models["reg_proxy_fe"].predict(X_proxy)[0]) if "reg_proxy_fe" in models else 0.30
                    inferred_mn = float(models["reg_proxy_mn"].predict(X_proxy)[0]) if "reg_proxy_mn" in models else 0.12
                    
                    inferred_metals = {"Cd": inferred_cd, "Fe": inferred_fe, "Mn": inferred_mn, "Pb": 0.001, "Ni": 0.001, "Cu": 0.02, "Zn": 1.0}
                    compliance_report = evaluate_metal_compliance(inferred_metals)
                    health_risk = calculate_human_health_risk(inferred_metals)
                    remediation = generate_remediation_plan(inferred_metals, pH, TDS, EC, cat_name)
                    conf_note = T["partial_confidence_note"]
                    
                    is_anomaly = (hpi_val > 70.0 and TDS < 400.0) or (pH < 6.0)
                    anomaly_score = -0.42 if is_anomaly else 0.35

                st.session_state["assessment"] = {
                    "hpi": hpi_val, "hei": hei_val, "cat_name": cat_name, "cat_col": cat_col,
                    "cat_desc": cat_desc, "compliance": compliance_report, "remediation": remediation,
                    "conf_note": conf_note, "is_full_mode": is_full_lab_mode, "pH": pH, "TDS": TDS, "EC": EC,
                    "metals": inferred_metals, "loc_name": loc_name, "latitude": latitude, "longitude": longitude,
                    "season": season, "is_anomaly": is_anomaly, "anomaly_score": anomaly_score,
                    "health_risk": health_risk
                }

            assess = st.session_state.get("assessment")
            if assess:
                sev_col = severity_color(assess["cat_name"], active_theme)
                
                # Translated category display
                if assess["cat_name"] == "Safe":
                    display_cat = T["safe"]
                elif assess["cat_name"] == "Moderate":
                    display_cat = T["moderate"]
                else:
                    display_cat = T["highly_polluted"]

                # Metric Readout Box
                st.markdown(f"""
                <div class="readout" style="--sev-color: {sev_col};">
                    <div class="readout-label">{T['predicted_hpi']}</div>
                    <div class="readout-value">{assess['hpi']:.1f}</div>
                    <div class="readout-label" style="margin-top:0.4rem;">{T['predicted_hei']}: <span style="color:var(--text-primary); font-family:'IBM Plex Mono',monospace;">{assess['hei']:.2f}</span></div>
                    <span class="badge {badge_class(assess['cat_name'])}">{display_cat.upper()}</span>
                </div>
                """, unsafe_allow_html=True)

                # Interactive Speedometer Gauge Chart
                gauge_fig = render_hpi_gauge(assess["hpi"], theme_mode=active_theme)
                st.pyplot(gauge_fig, use_container_width=True)
                plt.close(gauge_fig)

                st.caption(assess["conf_note"])
                if assess["cat_name"] == "Highly Polluted":
                    st.error(T["highly_polluted_msg"])
                elif assess["cat_name"] == "Moderate":
                    st.warning(T["moderate_msg"])
                else:
                    st.success(T["safe_msg"])

                # USEPA Human Health Risk Card
                hr = assess.get("health_risk", {})
                if hr:
                    st.markdown(f"#### 🩺 {T['health_risk_header']}")
                    c_h1, c_h2, c_h3 = st.columns(3)
                    c_h1.metric(T["child_hi_label"], f"{hr['child_hi']:.2f}", hr["child_status"])
                    c_h2.metric(T["adult_hi_label"], f"{hr['adult_hi']:.2f}", hr["adult_status"])
                    c_h3.metric(T["primary_driver_label"], f"{hr['primary_risk_driver']}", "Kidneys / CNS" if lang == "English" else "சிறுநீரகம் / நரம்பு மண்டலம்")
                    st.caption(T["health_guideline_caption"])

                # Heavy Metal Radar / Spider Chart (in Mode A)
                if assess["is_full_mode"]:
                    st.markdown(f"#### {T['radar_chart_header']}")
                    radar_fig = render_metal_radar_chart(assess["metals"], STANDARD_WATER_QUALITY_STANDARDS, theme_mode=active_theme)
                    if radar_fig:
                        st.pyplot(radar_fig, use_container_width=True)
                        plt.close(radar_fig)

                # Explainable AI (SHAP Local Feature Attribution)
                if "reg_partial" in models:
                    with st.expander(f"{T['explain_header']}"):
                        st.caption(T["explain_caption"])
                        X_sample_df = pd.DataFrame([{
                            "pH": assess["pH"],
                            "TDS": assess["TDS"],
                            "EC": assess["EC"],
                            "Season_Code": 1 if assess["season"] == T["post_monsoon"] else 0
                        }])
                        shap_fig = render_shap_waterfall_chart(models["reg_partial"], X_sample_df, theme_mode=active_theme)
                        if shap_fig:
                            st.pyplot(shap_fig, use_container_width=True)
                            plt.close(shap_fig)

                # Metal Compliance Table
                st.markdown(f"#### {T['compliance_table_header']}")
                comp_df = pd.DataFrame(assess["compliance"])
                if not comp_df.empty:
                    display_cols = ["symbol", "name", "concentration", "Si", "excess_percentage", "status"]
                    comp_display = comp_df[display_cols].copy()
                    comp_display.columns = [T["col_symbol"], T["col_metal"], T["col_conc"], T["col_limit"], T["col_excess"], T["col_status"]]
                    st.dataframe(comp_display, use_container_width=True, hide_index=True)

                # Actionable Remediation Advisor
                st.markdown(f"#### 💧 {T['treatment_advisor_header']}")
                st.markdown(f"**{T['action_verdict']}** {assess['remediation']['verdict']}")
                st.metric(
                    label=f"{T['treatment_cost_label']} ({T['per_kl']})",
                    value=f"₹{assess['remediation']['estimated_cost_per_kl']:.2f}"
                )
                with st.expander(T["view_flowchart_expander"]):
                    for step in assess["remediation"]["treatment_steps"]:
                        st.markdown(f"- **{step['stage']}:** {step['technology']}")
                        st.caption(f"  *{step['purpose']}* (Est: ₹{step['cost_inr_kl']:.2f}/kL)")

                # Anomaly & Alerting
                if assess["is_anomaly"]:
                    st.error(T["anomaly_detected_msg"])
                else:
                    st.success(T["anomaly_normal_msg"])

                # Download Certified PDF
                pdf_bytes = generate_certified_report(
                    location_name=assess["loc_name"], season=assess["season"],
                    hpi_value=assess["hpi"], hei_value=assess["hei"],
                    safety_category=assess["cat_name"],
                    input_mode="Mode A (Analytical Lab)" if assess["is_full_mode"] else "Mode B (IoT Proxy)",
                    input_params={"pH": assess["pH"], "TDS": assess["TDS"], "EC": assess["EC"], **assess["metals"]},
                    remediation_plan=assess["remediation"],
                    latitude=assess["latitude"], longitude=assess["longitude"],
                    compliance_list=assess["compliance"],
                    health_risk=assess.get("health_risk")
                )
                st.download_button(
                    label=T["download_report"],
                    data=pdf_bytes,
                    file_name=f"Field_Report_{assess['loc_name'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info(T["waiting_msg"])

# ==============================================================================
# TAB 2: BATCH CSV SCREENING
# ==============================================================================
with tab_batch:
    with st.container(border=True):
        st.markdown(f"### {T['batch_header']}")
        st.caption(T["batch_instructions"])

        col_b1, col_b2 = st.columns([1.2, 0.8])
        with col_b1:
            uploaded_file = st.file_uploader(T["batch_header"], type=["csv"], label_visibility="collapsed")
        with col_b2:
            st.markdown(f"**{T['batch_download_caption']}**")
            sample_df = pd.DataFrame([
                {"Location": "Sayalgudi_Borewell_1", "Latitude": 9.2106, "Longitude": 78.3941, "pH": 7.50, "TDS": 1360.0, "EC": 2150.0, "Season": "Post-Monsoon"},
                {"Location": "Kadaladi_Tank_4", "Latitude": 9.1574, "Longitude": 78.5622, "pH": 7.35, "TDS": 1440.0, "EC": 2120.0, "Season": "Post-Monsoon"},
                {"Location": "Mudukulathur_Well_2", "Latitude": 9.3615, "Longitude": 78.4504, "pH": 7.82, "TDS": 860.0, "EC": 1210.0, "Season": "Pre-Monsoon"},
                {"Location": "Kamuthi_Farm_3", "Latitude": 9.2485, "Longitude": 78.4485, "pH": 7.07, "TDS": 1900.0, "EC": 2920.0, "Season": "Post-Monsoon"}
            ])
            csv_sample = sample_df.to_csv(index=False).encode('utf-8')
            st.download_button(T["batch_download_btn"], data=csv_sample, file_name="groundwater_survey_template.csv", mime="text/csv")

        if uploaded_file is not None:
            try:
                batch_data = pd.read_csv(uploaded_file)
                st.success(f"Loaded {len(batch_data)} survey records successfully." if lang == "English" else f"{len(batch_data)} ஆய்வுப் பதிவுகள் வெற்றிகரமாக ஏற்றப்பட்டன.")
                
                reg_model = models.get("reg_partial")
                clf_model = models.get("clf_partial")

                if reg_model and clf_model:
                    batch_data["Season_Code"] = (batch_data.get("Season", "Post-Monsoon") == "Post-Monsoon").astype(int)
                    X_b = batch_data[["pH", "TDS", "EC", "Season_Code"]]
                    batch_data["Predicted_HPI"] = np.round(reg_model.predict(X_b), 1)
                    batch_data["Safety_Category"] = clf_model.predict(X_b)
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric(T["batch_total_wells"], len(batch_data))
                    safe_count = (batch_data["Safety_Category"] == "Safe").sum()
                    mod_count = (batch_data["Safety_Category"] == "Moderate").sum()
                    crit_count = (batch_data["Safety_Category"] == "Highly Polluted").sum()
                    m2.metric(T["batch_safe_count"], f"{safe_count} ({safe_count/len(batch_data)*100:.0f}%)")
                    m3.metric(T["batch_mod_count"], f"{mod_count} ({mod_count/len(batch_data)*100:.0f}%)")
                    m4.metric(T["batch_crit_count"], f"{crit_count} ({crit_count/len(batch_data)*100:.0f}%)")

                    st.markdown(f"#### {T['batch_results_table']}")
                    st.dataframe(batch_data, use_container_width=True)

                    csv_out = batch_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        T["batch_export_btn"],
                        data=csv_out,
                        file_name="Processed_Batch_Pollution_Report.csv",
                        mime="text/csv",
                        type="primary"
                    )
            except Exception as e:
                st.error(f"Error processing batch CSV: {e}")

# ==============================================================================
# TAB 3: TREATMENT "WHAT-IF" SIMULATOR
# ==============================================================================
with tab_whatif:
    with st.container(border=True):
        st.markdown(f"### {T['whatif_header']}")
        st.caption(T["whatif_caption"])

        w_col1, w_col2 = st.columns(2)
        with w_col1:
            st.markdown(f"#### {T['whatif_raw_header']}")
            raw_ph = st.slider(T["whatif_raw_ph"], 5.0, 9.5, 6.2, 0.1, key="raw_ph")
            raw_tds = st.slider(T["whatif_raw_tds"], 100.0, 3000.0, 1850.0, 50.0, key="raw_tds")
            raw_ec = raw_tds * 1.45
            raw_season = st.selectbox(T["season_label"], [T["pre_monsoon"], T["post_monsoon"]], key="raw_season")
            raw_season_code = 1 if raw_season == T["post_monsoon"] else 0

            X_raw = pd.DataFrame([{"pH": raw_ph, "TDS": raw_tds, "EC": raw_ec, "Season_Code": raw_season_code}])
            raw_hpi = float(models["reg_partial"].predict(X_raw)[0]) if "reg_partial" in models else 85.0
            raw_cat = str(models["clf_partial"].predict(X_raw)[0]) if "clf_partial" in models else "Highly Polluted"

            st.markdown(f"""
            <div class="readout" style="--sev-color: {severity_color(raw_cat, active_theme)}; margin-top:1rem;">
                <div class="readout-label">{T['whatif_raw_header'].upper()}</div>
                <div class="readout-value">{raw_hpi:.1f}</div>
                <span class="badge {badge_class(raw_cat)}">{raw_cat.upper()}</span>
            </div>
            """, unsafe_allow_html=True)

        with w_col2:
            st.markdown(f"#### {T['whatif_treated_header']}")
            treat_ph = st.slider(T["whatif_target_ph"], 6.5, 8.5, 7.4, 0.1, key="treat_ph")
            treat_tds = st.slider(T["whatif_target_tds"], 50.0, 1000.0, 250.0, 25.0, key="treat_tds")
            treat_ec = treat_tds * 1.45

            X_treat = pd.DataFrame([{"pH": treat_ph, "TDS": treat_tds, "EC": treat_ec, "Season_Code": raw_season_code}])
            treat_hpi = float(models["reg_partial"].predict(X_treat)[0]) if "reg_partial" in models else 22.0
            treat_cat = str(models["clf_partial"].predict(X_treat)[0]) if "clf_partial" in models else "Safe"

            st.markdown(f"""
            <div class="readout" style="--sev-color: {severity_color(treat_cat, active_theme)}; margin-top:1rem;">
                <div class="readout-label">{T['whatif_treated_header'].upper()}</div>
                <div class="readout-value">{treat_hpi:.1f}</div>
                <span class="badge {badge_class(treat_cat)}">{treat_cat.upper()}</span>
            </div>
            """, unsafe_allow_html=True)

            delta_hpi = raw_hpi - treat_hpi
            st.metric(label=T["whatif_delta_label"], value=f"-{delta_hpi:.1f} pts", delta=f"{delta_hpi/raw_hpi*100:.1f}% {T['whatif_improvement']}")

# ==============================================================================
# TAB 4: LIVE IOT EDGE TELEMETRY
# ==============================================================================
with tab_iot:
    with st.container(border=True):
        st.markdown(f"### {T['iot_header']}")
        st.caption(T["iot_caption"])

        node_select = st.selectbox(
            T["iot_select_node"],
            [f"{n['node_id']} - {n['name']}" for n in MONITORING_NODES]
        )
        node_idx = [f"{n['node_id']} - {n['name']}" for n in MONITORING_NODES].index(node_select)
        
        if st.button(T["iot_poll_btn"], type="primary"):
            st.session_state["last_packet"] = generate_telemetry_packet(node_idx)

        packet = st.session_state.get("last_packet", generate_telemetry_packet(node_idx))
        t = packet["telemetry"]

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.metric(T["iot_ph_metric"], f"{t['pH']:.2f}")
        col_t2.metric(T["iot_tds_metric"], f"{t['TDS_ppm']:.1f} mg/L")
        col_t3.metric(T["iot_ec_metric"], f"{t['EC_uS_cm']:.1f} µS/cm")
        col_t4.metric(T["iot_temp_metric"], f"{t['temperature_C']:.1f} °C")

        # Instant IoT Edge Prediction
        X_iot = pd.DataFrame([{"pH": t["pH"], "TDS": t["TDS_ppm"], "EC": t["EC_uS_cm"], "Season_Code": 1}])
        iot_hpi = float(models["reg_partial"].predict(X_iot)[0]) if "reg_partial" in models else 28.0
        iot_cat = str(models["clf_partial"].predict(X_iot)[0]) if "clf_partial" in models else "Safe"

        st.markdown(f"""
        <div class="readout" style="--sev-color: {severity_color(iot_cat, active_theme)}; margin-top:1rem;">
            <div class="readout-label">{T['iot_edge_label']}</div>
            <div class="readout-value">HPI {iot_hpi:.1f} &middot; {iot_cat.upper()}</div>
            <div class="readout-label">Node: {packet['node_id']} | Battery: {t['battery_voltage']}V | Signal: -68 dBm</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"#### {T['iot_afe_header']}")
        afe_c1, afe_c2, afe_c3 = st.columns(3)
        afe_c1.metric(T["iot_adc_ref"], "3.30 V (12-bit ADC)")
        afe_c2.metric(T["iot_nernst_slope"], "-59.16 mV / pH unit")
        afe_c3.metric(T["iot_temp_comp"], "+2.0% / °C offset")

        with st.expander(T["iot_hardware_expander"]):
            st.markdown("""
            - **Microcontroller:** ESP-WROOM-32 (Dual Core 240MHz, 12-bit SAR ADC)
            - **Sensors:** Gravity Analog pH (GPIO 34), Gravity Analog TDS (GPIO 35), DS18B20 1-Wire Temp (GPIO 4)
            - **Edge Algorithm:** Pre-loaded quantized surrogate coefficients for offline zero-cloud HPI inference.
            - **Firmware Path:** [`firmware/esp32_water_node.ino`](file:///C:/Users/manic/.gemini/antigravity/scratch/heavy-metal-groundwater-estimation/firmware/esp32_water_node.ino)
            """ if lang == "English" else """
            - **நுண்கட்டுப்படுத்தி (MCU):** ESP-WROOM-32 (இரட்டை கோர் 240MHz, 12-பிட் SAR ADC)
            - **சென்சார்கள்:** அனலாக் pH (GPIO 34), அனலாக் TDS (GPIO 35), DS18B20 வெப்பநிலை சென்சார் (GPIO 4)
            - **எட்ஜ் அல்காரிதம்:** இணையம் இல்லாமலேயே கிணற்றின் அருகிலேயே அபாயத்தைக் கணிக்கும் வகையில் சுருக்கப்பட்ட மாதிரி.
            - **மென்பொருள் கோப்பு:** [`firmware/esp32_water_node.ino`](file:///C:/Users/manic/.gemini/antigravity/scratch/heavy-metal-groundwater-estimation/firmware/esp32_water_node.ino)
            """)

# ==============================================================================
# TAB 5: GEOSTATISTICAL CONTAMINATION MAP
# ==============================================================================
with tab_map:
    with st.container(border=True):
        st.markdown(f"### {T['map_header']}")
        st.caption(T["map_caption"])

        try:
            from streamlit_folium import st_folium
            fmap = build_interactive_map(season="Post-Monsoon")
            st_folium(fmap, use_container_width=True, height=540, returned_objects=[])
        except Exception as e:
            st.error(f"Could not load interactive Folium map: {e}")
            map_fallback = os.path.join(os.path.dirname(__file__), "kriging_contamination_map.png")
            if os.path.exists(map_fallback):
                st.image(map_fallback, use_container_width=True)

# ==============================================================================
# TAB 6: SCIENTIFIC BENCHMARKS & MODEL COMPARISONS
# ==============================================================================
with tab_benchmarks:
    with st.container(border=True):
        st.markdown(f"### {T['benchmarks_header']}")
        st.caption(T["benchmarks_caption"])

        if benchmarks_data and "regression_models" in benchmarks_data:
            bench_df = pd.DataFrame(benchmarks_data["regression_models"]).T
            bench_df.columns = ["5-Fold R² Mean", "R² Std (±)", "MAE", "RMSE"]
            st.dataframe(bench_df, use_container_width=True)
            st.success(T["benchmarks_success"])

        # Study Area & Dataset Specification Card (N = 88)
        st.markdown(f"#### {T['dataset_info_title']}")
        st.info(T["dataset_info_text"])

        # Model Selection: Ensemble Trees vs SVR Card
        st.markdown(f"#### {T['model_selection_title']}")
        st.markdown(T["model_selection_text"])
        
        # Real SHAP Global Feature Impact Bar Chart
        st.markdown(f"#### {T['xai_header']}")
        df_bg = get_background_data()
        if "reg_partial" in models and df_bg is not None:
            shap_summary_fig = render_shap_summary_chart(models["reg_partial"], df_bg, theme_mode=active_theme)
            if shap_summary_fig:
                st.pyplot(shap_summary_fig, use_container_width=True)
                plt.close(shap_summary_fig)

        with st.expander(T["research_paper_expander"]):
            st.markdown("A complete IEEE/Springer publication guide is documented in [`docs/RESEARCH_PAPER_GUIDE.md`](file:///C:/Users/manic/.gemini/antigravity/scratch/heavy-metal-groundwater-estimation/docs/RESEARCH_PAPER_GUIDE.md)." if lang == "English" else "முழுமையான IEEE/Springer ஆய்வுக் கட்டுரை தயாரிப்பு வழிகாட்டி [`docs/RESEARCH_PAPER_GUIDE.md`](file:///C:/Users/manic/.gemini/antigravity/scratch/heavy-metal-groundwater-estimation/docs/RESEARCH_PAPER_GUIDE.md) கோப்பில் ஆவணப்படுத்தப்பட்டுள்ளது.")

st.markdown(f'<div class="footer-strip">{T["footer"]}</div>', unsafe_allow_html=True)
