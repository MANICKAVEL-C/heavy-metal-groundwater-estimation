# ============================================================
# WEEK 4 - STAGE 7: Streamlit Dashboard (Hackathon-Ready)
# Project: AI-Driven Assessment of Heavy Metal Pollution Indices
# Team: Manickavel C, D Dhinesh Karthick
# ============================================================
#
# VISUAL DESIGN: "Groundwater Instrument Panel" theme - see theme.py
# for the full design token documentation (colors, type, signature
# element).
#
# IMPORTANT: prediction results are persisted in st.session_state
# (see the "prediction" key) rather than relying on the transient
# return value of st.button(). This is necessary because Streamlit
# reruns the entire script on ANY widget interaction, and st.button()
# only returns True on the exact run it was clicked - typing into the
# alert phone/email fields afterward would otherwise silently wipe
# the whole results section. This was caught via live browser testing.
#
# HOW TO RUN:
#   pip install -r requirements.txt
#   streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from translations import TRANSLATIONS
from pdf_report import generate_field_report, get_recommended_action
from alert_system import trigger_alert
from theme import inject_css, severity_color, badge_class

st.set_page_config(page_title="Groundwater Pollution Intelligence", layout="wide", page_icon="\U0001F30A")
st.markdown(inject_css(), unsafe_allow_html=True)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

@st.cache_resource
def load_models():
    return {
        "reg_full": joblib.load(os.path.join(MODEL_DIR, "reg_full.joblib")),
        "reg_partial": joblib.load(os.path.join(MODEL_DIR, "reg_partial.joblib")),
        "reg_hei_full": joblib.load(os.path.join(MODEL_DIR, "reg_hei_full.joblib")),
        "reg_hei_partial": joblib.load(os.path.join(MODEL_DIR, "reg_hei_partial.joblib")),
        "clf_full": joblib.load(os.path.join(MODEL_DIR, "clf_full.joblib")),
        "clf_partial": joblib.load(os.path.join(MODEL_DIR, "clf_partial.joblib")),
        "anomaly": joblib.load(os.path.join(MODEL_DIR, "anomaly_detector.joblib")),
    }

models = load_models()

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
lang = st.sidebar.selectbox("Language / \u0bae\u0bca\u0bb4\u0bbf", ["English", "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd"])
T = TRANSLATIONS[lang]

st.sidebar.markdown(f"### {T['input_mode_header']}")
mode = st.sidebar.radio(T["input_mode_question"], [T["mode_full"], T["mode_partial"]], label_visibility="collapsed")
use_full = mode == T["mode_full"]

st.sidebar.markdown(f"### {T['season_header']}")
season = st.sidebar.selectbox(T["season_label"], [T["pre_monsoon"], T["post_monsoon"]], label_visibility="collapsed")
season_code = 1 if season == T["post_monsoon"] else 0

# ------------------------------------------------------------
# HERO BANNER
# ------------------------------------------------------------
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">SIH25067 &middot; MINISTRY OF JAL SHAKTI &middot; TAMIL NADU</div>
    <div class="hero-title">{T['title'].replace('\U0001F30A ', '')}</div>
    <div class="hero-subtitle">{T['subtitle'].split('|')[-1].strip() if '|' in T['subtitle'] else T['subtitle']}</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# INPUT SECTION
# ------------------------------------------------------------
st.markdown(f'<div class="section-eyebrow">FIELD INPUT</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1.15])

with col1:
    st.markdown(f'<div class="panel">', unsafe_allow_html=True)
    st.markdown(f"**{T['location_header']}**")
    location_name = st.text_input(T["location_name"], value="", label_visibility="collapsed",
                                    placeholder=T["location_name"])
    coord_col1, coord_col2 = st.columns(2)
    with coord_col1:
        latitude = st.number_input(T["latitude_label"], min_value=9.05, max_value=9.42,
                                     value=9.222, step=0.001, format="%.5f")
    with coord_col2:
        longitude = st.number_input(T["longitude_label"], min_value=78.30, max_value=78.68,
                                      value=78.496, step=0.001, format="%.5f")

    st.markdown(f"**{T['water_params_header']}**")
    pH = st.slider("pH", 6.0, 9.0, 7.5, 0.1)
    TDS = st.number_input("TDS (mg/L)", min_value=100.0, max_value=3000.0, value=800.0, step=10.0)
    EC = st.number_input("EC (\u00b5S/cm)", min_value=150.0, max_value=4500.0, value=1200.0, step=10.0)

    metals = {}
    if use_full:
        st.markdown(f"**{T['metal_params_header']}**")
        c1, c2 = st.columns(2)
        with c1:
            metals["Cu"] = st.number_input("Copper (Cu)", 0.0, 1.0, 0.02, 0.001, format="%.4f")
            metals["Mn"] = st.number_input("Manganese (Mn)", 0.0, 1.0, 0.15, 0.001, format="%.4f")
            metals["Cd"] = st.number_input("Cadmium (Cd)", 0.0, 0.02, 0.001, 0.0001, format="%.5f")
            metals["Ni"] = st.number_input("Nickel (Ni)", 0.0, 0.1, 0.001, 0.0001, format="%.5f")
        with c2:
            metals["Zn"] = st.number_input("Zinc (Zn)", 0.0, 5.0, 0.5, 0.01, format="%.4f")
            metals["Fe"] = st.number_input("Iron (Fe)", 0.0, 1.0, 0.30, 0.001, format="%.4f")
            metals["Pb"] = st.number_input("Lead (Pb)", 0.0, 0.1, 0.001, 0.0001, format="%.5f")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="panel">', unsafe_allow_html=True)
    predict_clicked = st.button(T["predict_button"], type="primary", use_container_width=True)

    if predict_clicked:
        if use_full:
            X = pd.DataFrame([{
                "Cu": metals["Cu"], "Zn": metals["Zn"], "Mn": metals["Mn"],
                "Fe": metals["Fe"], "Cd": metals["Cd"], "Pb": metals["Pb"],
                "Ni": metals["Ni"], "pH": pH, "TDS": TDS, "EC": EC,
                "Season_Code": season_code
            }])
            hpi_pred = float(models["reg_full"].predict(X)[0])
            hei_pred = float(models["reg_hei_full"].predict(X)[0])
            safety_pred_raw = models["clf_full"].predict(X)[0]
            confidence_note = T["full_confidence_note"]
            input_mode_label = T["mode_full"]
        else:
            X = pd.DataFrame([{"pH": pH, "TDS": TDS, "EC": EC, "Season_Code": season_code}])
            hpi_pred = float(models["reg_partial"].predict(X)[0])
            hei_pred = float(models["reg_hei_partial"].predict(X)[0])
            safety_pred_raw = models["clf_partial"].predict(X)[0]
            confidence_note = T["partial_confidence_note"]
            input_mode_label = T["mode_partial"]

        # Persist everything needed downstream (SHAP, PDF, alert) in
        # session_state - see module docstring for why this matters.
        st.session_state["prediction"] = {
            "X": X, "hpi_pred": hpi_pred, "hei_pred": hei_pred, "safety_pred_raw": safety_pred_raw,
            "confidence_note": confidence_note, "input_mode_label": input_mode_label,
            "use_full": use_full, "metals": dict(metals), "pH": pH, "TDS": TDS, "EC": EC,
            "location_name": location_name, "season": season,
            "latitude": latitude, "longitude": longitude,
        }
        st.session_state.pop("last_alert_result", None)

    pred = st.session_state.get("prediction")
    if pred:
        cat_display_map = {"Safe": T["safe"], "Moderate": T["moderate"], "Highly Polluted": T["highly_polluted"]}
        safety_display = cat_display_map.get(pred["safety_pred_raw"], pred["safety_pred_raw"])
        sev_color = severity_color(pred["safety_pred_raw"])
        badge_cls = badge_class(pred["safety_pred_raw"])

        st.markdown(f"""
        <div class="readout" style="--sev-color: {sev_color};">
            <div class="readout-label">{T['predicted_hpi']}</div>
            <div class="readout-value">{pred['hpi_pred']:.1f}</div>
            <div class="readout-label" style="margin-top:0.5rem;">{T['predicted_hei']}: <span style="color:var(--text-primary); font-family:'IBM Plex Mono',monospace;">{pred['hei_pred']:.2f}</span></div>
            <span class="badge {badge_cls}">{safety_display.upper()}</span>
        </div>
        """, unsafe_allow_html=True)

        st.info(pred["confidence_note"])

        if pred["safety_pred_raw"] == "Highly Polluted":
            st.error(T["highly_polluted_msg"])
        elif pred["safety_pred_raw"] == "Moderate":
            st.warning(T["moderate_msg"])
        else:
            st.success(T["safe_msg"])

        st.caption(T["disclaimer"])
    else:
        st.info(T["waiting_msg"])
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# SHAP EXPLAINABILITY + PDF + ALERT (persisted across reruns via
# session_state - see note above on why this is necessary)
# ------------------------------------------------------------
pred = st.session_state.get("prediction")
if pred:
    X = pred["X"]
    hpi_pred = pred["hpi_pred"]
    safety_pred_raw = pred["safety_pred_raw"]
    use_full_pred = pred["use_full"]
    metals_pred = pred["metals"]
    reg_model = models["reg_full"] if use_full_pred else models["reg_partial"]

    st.markdown(f'<div class="section-eyebrow">MODEL EXPLANATION</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel">', unsafe_allow_html=True)
    st.caption(T["explain_caption"])
    try:
        explainer = shap.TreeExplainer(reg_model)
        shap_vals = explainer(X)
        fig, ax = plt.subplots(figsize=(7.5, 3.6))
        fig.patch.set_facecolor("#13242C")
        ax.set_facecolor("#13242C")
        shap.plots.waterfall(shap_vals[0], show=False, max_display=8)
        fig.axes[0].tick_params(colors="#E8EEF0")
        for text in fig.axes[0].texts:
            text.set_color("#E8EEF0")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except Exception as e:
        st.warning(f"Could not generate SHAP explanation: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-eyebrow">FIELD REPORT</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel">', unsafe_allow_html=True)
    input_params_for_pdf = dict(metals_pred) if use_full_pred else {}
    input_params_for_pdf.update({"pH": pred["pH"], "TDS": pred["TDS"], "EC": pred["EC"]})
    recommended_action = get_recommended_action(safety_pred_raw)

    pdf_buffer = generate_field_report(
        location_name=pred["location_name"], season=pred["season"], hpi_value=hpi_pred,
        hei_value=pred.get("hei_pred"), safety_category=safety_pred_raw,
        input_mode=pred["input_mode_label"], input_params=input_params_for_pdf,
        recommended_action=recommended_action,
        latitude=pred.get("latitude"), longitude=pred.get("longitude"),
    )
    st.download_button(label=T["download_report"], data=pdf_buffer,
                         file_name=f"field_report_{pred['location_name'] or 'sample'}.pdf",
                         mime="application/pdf", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------
    # ANOMALY DETECTION + ALERT SYSTEM (full-data mode only -
    # the anomaly model was trained on all 7 metals + pH/TDS/EC)
    # --------------------------------------------------------
    if use_full_pred:
        st.markdown(f'<div class="section-eyebrow">{T["alert_header"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="panel">', unsafe_allow_html=True)

        anomaly_X = pd.DataFrame([{
            "Cu": metals_pred["Cu"], "Zn": metals_pred["Zn"], "Mn": metals_pred["Mn"],
            "Fe": metals_pred["Fe"], "Cd": metals_pred["Cd"], "Pb": metals_pred["Pb"],
            "Ni": metals_pred["Ni"], "pH": pred["pH"], "TDS": pred["TDS"], "EC": pred["EC"],
        }])
        anomaly_pred = models["anomaly"].predict(anomaly_X)[0]  # -1 = anomaly, 1 = normal
        anomaly_score = float(models["anomaly"].score_samples(anomaly_X)[0])
        is_anomaly = anomaly_pred == -1

        if is_anomaly:
            st.error(T["anomaly_detected_msg"])
        else:
            st.success(T["anomaly_normal_msg"])
        st.caption(f"{T['anomaly_score_label']}: {anomaly_score:.3f}")

        with st.expander(T["alert_expander_label"], expanded=is_anomaly):
            st.caption(T["alert_simulation_note"])
            col_a, col_b = st.columns(2)
            with col_a:
                phone = st.text_input(T["alert_phone_label"], placeholder="+91XXXXXXXXXX", key="alert_phone")
            with col_b:
                email = st.text_input(T["alert_email_label"], placeholder="officer@tn.gov.in", key="alert_email")

            if st.button(T["alert_send_button"], use_container_width=True, key="alert_send_btn"):
                alert_result = trigger_alert(
                    location_name=pred["location_name"], hpi_value=hpi_pred,
                    safety_category=safety_pred_raw, anomaly_score=anomaly_score,
                    season=pred["season"], phone_number=phone or None, email_address=email or None,
                )
                st.session_state["last_alert_result"] = alert_result

            if st.session_state.get("last_alert_result"):
                alert_result = st.session_state["last_alert_result"]
                st.code(alert_result["message"], language=None)
                for r in alert_result["results"]:
                    if r.get("simulated"):
                        st.info(f"{r['channel']}: {r['detail']}")
                    elif r.get("sent"):
                        st.success(f"{r['channel']}: Sent successfully.")
                    else:
                        st.warning(f"{r['channel']}: {r.get('error', 'Not sent.')}")
                if not phone and not email:
                    st.warning(T["alert_no_contact_warning"])
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# FEATURE IMPORTANCE (global model insight - always visible,
# not tied to a specific prediction, unlike the SHAP chart above
# which explains one single sample)
# ------------------------------------------------------------
st.markdown(f'<div class="section-eyebrow">{T["feature_importance_header"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="panel">', unsafe_allow_html=True)
st.markdown(f"**{T['feature_importance_title']}**")
st.caption(T["feature_importance_caption"])

fi_tab_full, fi_tab_partial = st.tabs(["Full Metal Panel Model", "Partial Data Model"])

def _render_importance_chart(model, feature_names):
    importances = model.feature_importances_
    order = np.argsort(importances)[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    fig.patch.set_facecolor("#13242C")
    ax.set_facecolor("#13242C")
    bars = ax.barh([feature_names[i] for i in order][::-1], importances[order][::-1],
                    color="#2A9D8F")
    ax.set_xlabel("Relative Importance", color="#E8EEF0")
    ax.tick_params(colors="#E8EEF0")
    for spine in ax.spines.values():
        spine.set_color("#234049")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with fi_tab_full:
    _render_importance_chart(models["reg_full"],
                               ["Cu", "Zn", "Mn", "Fe", "Cd", "Pb", "Ni", "pH", "TDS", "EC", "Season"])
with fi_tab_partial:
    _render_importance_chart(models["reg_partial"], ["pH", "TDS", "EC", "Season"])

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# CONTAMINATION MAP (Interactive Folium + Static fallback)
# ------------------------------------------------------------
st.markdown(f'<div class="section-eyebrow">REGIONAL MAP</div>', unsafe_allow_html=True)
st.markdown(f'<div class="panel">', unsafe_allow_html=True)
st.markdown(f"**{T['map_header']}**")
st.caption(T["map_caption"])

tab_interactive, tab_static = st.tabs(["\U0001F310 Interactive Map", "\U0001F5BC\uFE0F Static View"])

with tab_interactive:
    st.caption("Click any marker for that location's historical reading. Use the layer "
                "control (top-right) to toggle between the contamination heatmap and the "
                "prediction-uncertainty map, or switch to satellite view.")
    try:
        from streamlit_folium import st_folium
        from folium_map import build_interactive_map

        @st.cache_resource
        def get_map():
            return build_interactive_map()

        st_folium(get_map(), use_container_width=True, height=520, returned_objects=[])
    except Exception as e:
        st.error(f"Interactive map could not be loaded: {e}")
        st.info("Falling back to static view below.")
        map_path = os.path.join(os.path.dirname(__file__), "kriging_contamination_map.png")
        if os.path.exists(map_path):
            st.image(map_path, use_container_width=True)

with tab_static:
    map_path = os.path.join(os.path.dirname(__file__), "kriging_contamination_map.png")
    if os.path.exists(map_path):
        st.image(map_path, use_container_width=True)
    else:
        st.warning("Contamination map image not found.")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer-strip">{T["footer"]}</div>', unsafe_allow_html=True)
