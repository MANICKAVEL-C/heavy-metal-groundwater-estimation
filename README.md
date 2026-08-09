# Heavy Metal Pollution Assessment Dashboard

## How to run locally
1. Install dependencies:
   pip install -r requirements.txt

2. Run the app:
   streamlit run app.py

3. It opens automatically in your browser at http://localhost:8501

## How to deploy for free (Streamlit Community Cloud)
1. Push this whole `dashboard` folder to a GitHub repository
2. Go to https://share.streamlit.io
3. Sign in with GitHub, click "New app"
4. Select your repo, set main file to `app.py`
5. Deploy — you'll get a public URL to share/demo

## Folder contents
- app.py                        -> the dashboard application
- theme.py                        -> visual design system (colors, fonts, CSS)
- translations.py                -> English/Tamil UI text dictionary
- pdf_report.py                  -> PDF field report generator
- folium_map.py                   -> interactive Kriging map (Folium)
- alert_system.py                 -> contamination alert composer (SMS/Email, simulation-safe)
- models/                       -> 5 trained ML models (regression x2, classification x2, anomaly detector)
- data/                            -> sample dataset with coordinates (for the interactive map)
- assets/                          -> contour-texture background images (design signature element)
- kriging_contamination_map.png -> static spatial contamination map image (fallback view)
- requirements.txt              -> Python packages needed

## New in this version (hackathon-readiness features)

**1-2-5. SHAP explainability, PDF report, Tamil toggle** — carried over from the previous
version, already tested and working.

**3. Interactive Folium map** — the "Interactive Map" tab shows a real pan/zoom map with:
a Kriging contamination-risk overlay and a prediction-uncertainty overlay (toggle between
them via the layer control, top-right), a satellite-view base layer option, and a
clickable marker per sample location showing that location's historical HPI, safety
category, and key metal readings in a popup. A "Static View" tab keeps the original
image as a fallback. Verified: the map component loads correctly (confirmed via its
dedicated iframe and zero server-side errors); actual map tiles require live internet
access, which this development sandbox blocks but a normal machine will not.

**4. Contamination alert system** — ships in SIMULATION MODE by default (see
alert_system.py). It composes the exact real alert message (location, HPI, anomaly
score, recommended action) and displays it in the dashboard WITHOUT requiring live
Twilio/SMTP credentials. This is a deliberate safety choice: a hackathon demo that
depends on a live SMS API key or email login is a real failure risk (expired credits,
wrong credentials, blocked ports). The real sending logic is fully implemented and will
work if you set SIMULATION_MODE = False and provide real credentials via environment
variables (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, ALERT_SMTP_USER,
ALERT_SMTP_PASSWORD) - documented at the top of alert_system.py.

## Important bug found and fixed during this update
The original single-button prediction flow broke as soon as the user typed into the
new phone/email alert fields: Streamlit's st.button() only returns True on the exact
run it was clicked, so typing into ANY other widget afterward triggered a rerun where
the entire results section (metric, SHAP, PDF, alert) would silently vanish. This was
caught through actual browser-automation testing (not just launching the app) and fixed
by persisting prediction results in st.session_state, so they now survive any number of
follow-up interactions. Verified via a full automated browser test: predict -> fill
phone -> fill email -> click send alert, with the results section confirmed still
visible and the alert message correctly composed at every step.

## What was tested (Claude verified before handing this off)
- App launches successfully with Streamlit (HTTP 200, no errors) with all new imports
- Prediction logic verified with a clean water sample (correctly predicted "Safe", HPI ~19-29)
- Prediction logic verified with a polluted water sample (correctly predicted "Highly Polluted", HPI ~99.2)
- Both full-data and partial-data (cheap parameters only) prediction modes tested and agree on the same sample's pollution severity
- SHAP waterfall plot generation tested directly - confirms Cd as dominant contributor
- PDF report generation tested directly - verified all fields render correctly via text extraction
- Tamil translation dictionary loads and returns correct strings; toggle tested live in browser
- Visual design verified via real headless-browser automation (Playwright): exact computed
  CSS colors, fonts, and textures confirmed matching design spec across all 3 severity states
- Folium map: verified 44 markers + 44 popups + 2 image overlays + layer control present
  in the generated map HTML structure; component embed confirmed via iframe inspection
- Anomaly detector: verified correctly flags a known "Highly Polluted" sample as anomalous
  (score -0.643) via live browser test
- Alert system: verified full flow end-to-end (predict -> anomaly flagged -> enter contact
  info -> send -> correct message composed and displayed) via browser automation, including
  confirming the session-state bug fix holds under realistic multi-step interaction
