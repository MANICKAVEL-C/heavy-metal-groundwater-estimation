# 🌊 Groundwater Heavy Metal Intelligence System (GHMIS)
### Decision Support & Surrogate Sensing for Potable Aquifer Governance
**Smart India Hackathon (SIH25067) &middot; Ministry of Jal Shakti &middot; Govt. of India**  
**Team:** Manickavel C (ECE, 2nd Year), D Dhinesh Karthick | *Chennai Institute of Technology*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Standard](https://img.shields.io/badge/Standards-BIS_IS_10500%3A2012-green.svg)](https://bis.gov.in/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 📌 Executive Overview & Academic Rigor

In rural groundwater management across India (specifically coastal Tamil Nadu aquifers such as Ramanathapuram and Kadaladi), laboratory testing for toxic heavy metals ($\text{Cd}, \text{Pb}, \text{Ni}, \text{Fe}, \text{Mn}, \text{Cu}, \text{Zn}$) via ICP-MS or AAS is economically prohibitive (₹2,000–₹3,500/sample) and logistically slow.

**GHMIS** resolves this crisis with a **Dual-Paradigm Cyber-Physical Architecture**:
1. **Mode A (Analytical Laboratory Engine):** 100% deterministic, closed-form computation of Indian Standard **BIS IS 10500:2012** / WHO drinking water indices ($HPI, HEI, MI, C_{deg}$) with zero machine learning approximation error.
2. **Mode B (Surrogate IoT Sensing Engine):** Machine Learning models infer contamination risk and heavy metal exposure directly from low-cost physical probes ($\text{pH}, \text{TDS}, \text{EC}, \text{Season}$) with **$R^2 = 0.931$** on 5-fold cross-validation.

---

## 🚀 Key Modules & Capabilities

```
                  ┌────────────────────────────────────────────────────────┐
                  │      GROUNDWATER HEAVY METAL INTELLIGENCE SYSTEM       │
                  └────────────────────────────────────────────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
┌──────────────────┐               ┌───────────────────────┐             ┌────────────────────┐
│ 1. SINGLE FIELD  │               │    2. BATCH CSV       │             │  3. WHAT-IF SIM    │
│    ASSESSMENT    │               │     SCREENING         │             │    & REMEDIATION   │
├──────────────────┤               ├───────────────────────┤             ├────────────────────┤
│ • Exact BIS HPI  │               │ • Screen 50-500 wells │             │ • Interactive RO   │
│ • ML Proxy Risk  │               │ • Risk pie/bar stats  │             │   pH neutralizing  │
│ • SHAP XAI plots │               │ • CSV export report   │             │ • ₹/kL cost engine │
└──────────────────┘               └───────────────────────┘             └────────────────────┘
         │                                    │                                    │
         ▼                                    ▼                                    ▼
┌──────────────────┐               ┌───────────────────────┐             ┌────────────────────┐
│ 4. LIVE IOT EDGE │               │   5. GEOSTATISTICAL   │             │ 6. RESEARCH PAPER  │
│    TELEMETRY     │               │     KRIGING MAP       │             │    BLUEPRINT       │
├──────────────────┤               ├───────────────────────┤             ├────────────────────┤
│ • ESP32 firmware │               │ • Spatial Risk raster │             │ • IEEE / Springer  │
│ • Analog probes  │               │ • Uncertainty layer   │             │ • Benchmark table  │
│ • Real-time feed │               │ • Satellite overlay   │             │ • Zero circularity │
└──────────────────┘               └───────────────────────┘             └────────────────────┘
```

---

## 📊 Scientific Benchmarks & Model Performance

Surrogate models trained and evaluated on 5-Fold Cross-Validation:

| Model | Target Variable | 5-Fold $R^2$ (Mean $\pm$ Std) | MAE | RMSE |
| :--- | :---: | :---: | :---: | :---: |
| **Gradient Boosting Regressor** | Inferred HPI | **$0.931 \pm 0.031$** | **$4.384$** | **$5.751$** |
| **Random Forest Regressor** | Inferred HPI | **$0.917 \pm 0.027$** | **$4.708$** | **$6.294$** |
| **Ridge Regression (L2)** | Inferred HPI | $0.846 \pm 0.035$ | $6.918$ | $8.751$ |
| **Random Forest Proxy Cd** | Cadmium ($\text{Cd}$) | **$0.912 \pm 0.034$** | $0.0003$ | $0.0004$ |
| **Safety Classifier (RF)** | Safety Category | **$82.7\%$ Accuracy** | - | $82.2\%$ F1 |

---

## 🛠️ Repository Directory Structure

```
heavy-metal-groundwater-estimation/
├── app.py                      # Master Streamlit dashboard (Single, Batch, What-If, IoT, Map)
├── analytical_engine.py        # 100% Exact BIS IS 10500:2012 / WHO mathematical indices
├── remediation_engine.py       # Water engineering treatment advisor & cost calculator
├── iot_stream.py               # IoT telemetry stream simulator & hardware payload parser
├── folium_map.py               # Interactive Ordinary Kriging & uncertainty map
├── pdf_report.py               # Certified Field Inspection PDF report generator
├── theme.py                    # Scientific dark instrument panel design tokens
├── translations.py             # Complete bilingual English & Tamil UI dictionary
├── alert_system.py             # Simulation-safe multi-channel SMS/Email alerting
├── train_models.py             # Multi-model training and benchmarking script
├── firmware/
│   └── esp32_water_node.ino    # Production C++ firmware for ESP32 + pH/TDS/Temp sensors
├── docs/
│   └── RESEARCH_PAPER_GUIDE.md # IEEE/Springer publication manuscript blueprint
├── data/
│   └── tamilnadu_groundwater_WITH_INDICES.csv # 88 borewell historical dataset
└── requirements.txt
```

---

## ⚡ How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MANICKAVEL-C/heavy-metal-groundwater-estimation.git
   cd heavy-metal-groundwater-estimation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Dashboard:**
   ```bash
   streamlit run app.py
   ```
   Opens automatically at `http://localhost:8501`.

---

## 🌐 Deploy to Streamlit Cloud (Free)

1. Push your changes to GitHub:
   ```bash
   git add .
   git commit -m "Upgrade to research-grade decision support system"
   git push origin main
   ```
2. Go to [share.streamlit.io](https://share.streamlit.io) & connect your repository with main file `app.py`.
