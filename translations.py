# ==============================================================================
# translations.py - English / Tamil UI Text Dictionary
# Project: AI-Driven Assessment of Heavy Metal Pollution Indices
# ==============================================================================

TRANSLATIONS = {
    "English": {
        "title": "🌊 Groundwater Heavy Metal Intelligence System",
        "subtitle": "Ministry of Jal Shakti | Smart India Hackathon SIH25067 | Tamil Nadu Aquifers",
        "tab_single": "🧪 Single Field Assessment",
        "tab_batch": "📁 Batch CSV Screening",
        "tab_whatif": "🎛️ Treatment 'What-If' Simulator",
        "tab_iot": "📡 Live IoT Edge Telemetry",
        "tab_map": "🗺️ Geostatistical Risk Map",
        "tab_benchmarks": "📊 Model Benchmarks",

        "input_mode_header": "Operation Paradigm",
        "input_mode_question": "Select Assessment Workflow:",
        "mode_full": "Mode A: Analytical Laboratory Mode (Exact BIS 10500 Formulas)",
        "mode_partial": "Mode B: Low-Cost IoT Proxy Mode (Machine Learning Surrogate)",

        "season_header": "Seasonality",
        "season_label": "Sampling Season",
        "pre_monsoon": "Pre-Monsoon",
        "post_monsoon": "Post-Monsoon",

        "water_params_header": "Physicochemical Sensor Parameters",
        "metal_params_header": "Laboratory Heavy Metal Panel (mg/L)",
        "location_header": "Geographic Sample Coordinates",
        "location_name": "Location / Borewell ID",
        "latitude_label": "Latitude (°N)",
        "longitude_label": "Longitude (°E)",

        "predict_button": "⚡ Run Hydrochemical Assessment",
        "result_header": "Assessment Summary",
        "predicted_hpi": "Heavy Metal Pollution Index (HPI)",
        "predicted_hei": "Heavy Metal Evaluation Index (HEI)",
        "metal_index_label": "Metal Index (MI)",
        "contamination_degree": "Contamination Degree (Cd)",
        "safety_category": "Safety Classification",

        "full_confidence_note": "🔬 100% Deterministic BIS IS 10500:2012 / WHO Analytical Calculation (Zero ML Error).",
        "partial_confidence_note": "🤖 ML Surrogate Inference from pH, TDS, EC & Season (Gradient Boosting / RF 5-Fold R² = 0.931).",

        "safe": "Safe / Potable",
        "moderate": "Moderate Contamination",
        "highly_polluted": "CRITICAL HAZARD",

        "safe_msg": "✅ Water complies with BIS IS 10500 drinking standards for tested heavy metals.",
        "moderate_msg": "⚠️ Moderate metal accumulation detected. Point-of-use filtration recommended.",
        "highly_polluted_msg": "🚨 DANGER: Severe toxic heavy metal contamination exceeding permissible limits. Direct consumption prohibited!",

        "disclaimer": "Scientific Decision Support Tool for Jal Jeevan Mission & District Water Quality Officers.",
        "waiting_msg": "👈 Configure parameters and click **Run Hydrochemical Assessment** to view results.",

        "treatment_advisor_header": "💧 Actionable Remediation & Water Treatment Plan",
        "treatment_cost_label": "Estimated Community Treatment Cost",
        "per_kl": "per kiloliter (₹/1000 Liters)",
        "treatment_steps_label": "Recommended Treatment Flowchart:",

        "explain_header": "🔍 Explainable AI (SHAP Local Feature Attribution)",
        "explain_caption": "SHAP Waterfall Plot demonstrates how each sensor parameter influenced the predicted risk score.",
        "feature_importance_header": "🌐 Global Model Intelligence",
        "feature_importance_title": "Feature Importance Drivers",
        "feature_importance_caption": "Global importance of parameters in predicting groundwater contamination risk.",

        "download_report": "📄 Download Certified Field Inspection Report (PDF)",
        "alert_header": "🚨 Point-Source Anomaly & Emergency Alerting",
        "anomaly_detected_msg": "⚠️ ANOMALY FLAGGED: Water signature deviates from regional baseline — potential industrial dumping!",
        "anomaly_normal_msg": "✅ Normal Hydrochemical Pattern: Consistent with regional aquifer baselines.",
        "anomaly_score_label": "Isolation Forest Score (lower = anomalous)",
        "alert_expander_label": "Dispatch Emergency SMS / Email Notice",
        "alert_simulation_note": "Demo Simulation Mode active (safeguards live demo from network/token failures).",
        "alert_phone_label": "District Health Officer Phone",
        "alert_email_label": "Jal Shakti Officer Email",
        "alert_send_button": "📤 Dispatch Alert Notification",
        "alert_no_contact_warning": "No recipient contact provided — alert composed locally.",

        "batch_header": "📁 Bulk Borewell Assessment (Batch CSV Upload)",
        "batch_instructions": "Upload a CSV spreadsheet with columns: [Location, Latitude, Longitude, pH, TDS, EC, Season] to screen multiple villages at once.",
        "batch_run_btn": "🚀 Process Batch Borewell Records",

        "whatif_header": "🎛️ Interactive Counterfactual Treatment Simulator",
        "whatif_caption": "Simulate how chemical neutralization or membrane desalination alters predicted water safety.",

        "iot_header": "📡 Live IoT Edge Telemetry Stream",
        "iot_caption": "Real-time sensor telemetry stream from field ESP32 microcontrollers across Tamil Nadu borewells.",

        "map_header": "🗺️ Geostatistical Kriging & Regional Risk Surface",
        "map_caption": "Spatial Ordinary Kriging interpolation over Kadaladi aquifer with Prediction Uncertainty layer.",
        "footer": "Groundwater Heavy Metal Intelligence System | ECE Dept. | SIH25067 Ministry of Jal Shakti"
    },
    "தமிழ்": {
        "title": "🌊 நிலத்தடி நீர் கன உலோக நுண்ணறிவு அமைப்பு",
        "subtitle": "ஜல் சக்தி அமைச்சகம் | ஸ்மார்ட் இந்தியா ஹேக்கத்தான் SIH25067 | தமிழ்நாடு நிலத்தடி நீர்",
        "tab_single": "🧪 தனி மாதிரி மதிப்பீடு",
        "tab_batch": "📁 தொகுதி CSV திரையிடல்",
        "tab_whatif": "🎛️ நீர் சுத்திகரிப்பு மாதிரி உருவகப்படுத்துதல்",
        "tab_iot": "📡 நேரடி IoT சென்சார் தரவு",
        "tab_map": "🗺️ பிராந்திய மாசு வரைபடம்",
        "tab_benchmarks": "📊 மாதிரி ஒப்பீட்டு அளவீடுகள்",

        "input_mode_header": "செயல்பாட்டு முறை",
        "input_mode_question": "மதிப்பீட்டு முறையைத் தேர்ந்தெடுக்கவும்:",
        "mode_full": "முறை A: ஆய்வக பகுப்பாய்வு முறை (BIS 10500 துல்லிய சூத்திரங்கள்)",
        "mode_partial": "முறை B: குறைந்த விலை IoT சென்சார் முறை (ML கணிப்பு)",

        "season_header": "பருவநிலை",
        "season_label": "மாதிரி எடுக்கும் பருவம்",
        "pre_monsoon": "பருவமழைக்கு முன்",
        "post_monsoon": "பருவமழைக்குப் பின்",

        "water_params_header": "நீரின் இயற்பியல்-வேதியியல் அளவுருக்கள்",
        "metal_params_header": "ஆய்வக கன உலோக செறிவுகள் (mg/L)",
        "location_header": "புவியியல் இருப்பிட விவரங்கள்",
        "location_name": "இடம் / ஆழ்துளை கிணறு எண்",
        "latitude_label": "அட்சரேகை (°N)",
        "longitude_label": "தீர்க்கரேகை (°E)",

        "predict_button": "⚡ நீரின் தரத்தை மதிப்பிடுக",
        "result_header": "மதிப்பீட்டு சுருக்கம்",
        "predicted_hpi": "கன உலோக மாசு குறியீடு (HPI)",
        "predicted_hei": "கன உலோக மதிப்பீட்டுக் குறியீடு (HEI)",
        "metal_index_label": "உலோக குறியீடு (MI)",
        "contamination_degree": "மாசுபடுதல் அளவு (Cd)",
        "safety_category": "பாதுகாப்பு வகைப்பாடு",

        "full_confidence_note": "🔬 100% துல்லியமான BIS IS 10500:2012 / WHO ஆய்வக கணக்கீடு (பூஜ்ஜிய பிழை).",
        "partial_confidence_note": "🤖 pH, TDS, EC ஆகியவற்றிலிருந்து பெறப்பட்ட AI கணிப்பு (R² = 0.931).",

        "safe": "பாதுகாப்பானது / குடிக்க உகந்தது",
        "moderate": "மிதமான மாசுபாடு",
        "highly_polluted": "ஆபத்தானது / நச்சுத்தன்மை",

        "safe_msg": "✅ தண்ணீர் குடிப்பதற்கு பாதுகாப்பானது மற்றும் BIS தரநிலைகளுக்கு உட்பட்டது.",
        "moderate_msg": "⚠️ மிதமான உலோகம் கண்டறியப்பட்டுள்ளது. சுத்திகரிப்பு பரிந்துரைக்கப்படுகிறது.",
        "highly_polluted_msg": "🚨 எச்சரிக்கை: ஆபத்தான நச்சு கன உலோக மாசுபாடு! நேரடி நுகர்வு தடைசெய்யப்பட்டுள்ளது!",

        "disclaimer": "ஜல் ஜீவன் திட்டம் மற்றும் மாவட்ட நீர் தர அதிகாரிகளுக்கான முடிவு-ஆதரவு அமைப்பு.",
        "waiting_msg": "👈 அளவுருக்களை அமைத்து **நீரின் தரத்தை மதிப்பிடுக** பொத்தானை அழுத்தவும்.",

        "treatment_advisor_header": "💧 நீர் சுத்திகரிப்பு மற்றும் மறுசீரமைப்பு திட்டம்",
        "treatment_cost_label": "மதிப்பிடப்பட்ட சுத்திகரிப்பு செலவு",
        "per_kl": "ஒரு கிலோ லிட்டருக்கு (₹/1000 லிட்டர்)",
        "treatment_steps_label": "பரிந்துரைக்கப்பட்ட சுத்திகரிப்பு படிகள்:",

        "explain_header": "🔍 விளக்கக்கூடிய AI (SHAP உள்ளூர் காரணி விளக்கம்)",
        "explain_caption": "ஒவ்வொரு அளவுருவும் கணிப்பை எவ்வாறு பாதித்தது என்பதை SHAP வரைபடம் காட்டுகிறது.",
        "feature_importance_header": "🌐 உலகளாவிய மாதிரி நுண்ணறிவு",
        "feature_importance_title": "மாதிரியின் முக்கிய இயக்கிகள்",
        "feature_importance_caption": "நீர் மாசுபடுதலை கணிப்பதில் அளவுருக்களின் முக்கியத்துவம்.",

        "download_report": "📄 சான்றளிக்கப்பட்ட கள ஆய்வு அறிக்கையைப் பதிவிறக்கவும் (PDF)",
        "alert_header": "🚨 அவசர மாசு எச்சரிக்கை அமைப்பு",
        "anomaly_detected_msg": "⚠️ முரண்பாடு கண்டறியப்பட்டது — வழக்கத்திற்கு மாறான தொழில்துறை கழிவு மாசுபாடு!",
        "anomaly_normal_msg": "✅ வழக்கமான நீர்வள மாதிரி உறுதிப்படுத்தப்பட்டது.",
        "anomaly_score_label": "முரண்பாட்டு மதிப்பீடு",
        "alert_expander_label": "அவசர SMS / மின்னஞ்சல் அறிவிப்பை அனுப்பவும்",
        "alert_simulation_note": "டெமோ உருவகப்படுத்துதல் பயன்முறையில் உள்ளது.",
        "alert_phone_label": "சுகாதார அதிகாரி தொலைபேசி எண்",
        "alert_email_label": "ஜல் சக்தி அதிகாரி மின்னஞ்சல்",
        "alert_send_button": "📤 எச்சரிக்கை அறிவிப்பை அனுப்புக",
        "alert_no_contact_warning": "பெறுநர் விவரங்கள் வழங்கப்படவில்லை.",

        "batch_header": "📁 மொத்த ஆழ்துளை கிணறு மதிப்பீடு (CSV பதிவேற்றம்)",
        "batch_instructions": "ஒரே நேரத்தில் பல கிராமங்களின் நீர் மாதிரிகளை பகுப்பாய்வு செய்ய CSV கோப்பைப் பதிவேற்றவும்.",
        "batch_run_btn": "🚀 தொகுதி மாதிரிகளை செயலாக்குக",

        "whatif_header": "🎛️ நீர் சுத்திகரிப்பு மாதிரி உருவகப்படுத்துதல்",
        "whatif_caption": "சுத்திகரிப்பு முறைகள் நீரின் பாதுகாப்பை எவ்வாறு மீட்டெடுக்கின்றன என்பதை உருவகப்படுத்துங்கள்.",

        "iot_header": "📡 நேரடி IoT சென்சார் தரவு",
        "iot_caption": "தமிழ்நாடு ஆழ்துளை கிணறுகளில் உள்ள ESP32 சென்சார்களின் நேரடி தரவு.",

        "map_header": "🗺️ பிராந்திய மாசு வரைபடம் (க்ரிஜிங் முறை)",
        "map_caption": "கடலாடி நிலத்தடி நீரின் இடஞ்சார்ந்த க்ரிஜிங் வரைபடம் மற்றும் நிச்சயமற்ற தன்மை அடுக்கு.",
        "footer": "நிலத்தடி நீர் கன உலோக நுண்ணறிவு அமைப்பு | ECE துறை | SIH25067"
    }
}
