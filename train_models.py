# ==============================================================================
# train_models.py - Multi-Model Training & Benchmarking Pipeline
# Surrogate Machine Learning for Low-Cost Field Sensor Proxy Estimation
# ==============================================================================

import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, IsolationForest
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, cross_validate
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, accuracy_score, f1_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "tamilnadu_groundwater_WITH_INDICES.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_and_benchmark():
    print(f"[+] Loading groundwater dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df["Season_Code"] = (df["Season"] == "Post-Monsoon").astype(int)

    # Proxy Features (available from low-cost IoT / field sensors)
    PROXY_FEATURES = ["pH", "TDS", "EC", "Season_Code"]
    X_proxy = df[PROXY_FEATURES]

    # Full Features (for baseline anomaly detection)
    FULL_FEATURES = ["Cu", "Zn", "Mn", "Fe", "Cd", "Pb", "Ni", "pH", "TDS", "EC", "Season_Code"]
    X_full = df[FULL_FEATURES]

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    benchmarks = {"regression_models": {}, "target_estimations": {}, "classification": {}}

    # 1. Model Comparison on HPI Proxy Estimation
    y_hpi = df["HPI"]
    candidate_regressors = {
        "Random Forest Regressor": RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42),
        "Support Vector Regressor (SVR)": SVR(C=10.0, epsilon=0.2),
        "Ridge Regressor (L2)": Ridge(alpha=1.0)
    }

    print("\n--- 1. PROXY REGRESSOR BENCHMARKING (pH, TDS, EC, Season -> HPI) ---")
    for name, model in candidate_regressors.items():
        scoring = {"r2": "r2", "mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error"}
        scores = cross_validate(model, X_proxy, y_hpi, cv=cv, scoring=scoring)
        r2_mean = float(scores["test_r2"].mean())
        r2_std = float(scores["test_r2"].std())
        mae_mean = float(-scores["test_mae"].mean())
        rmse_mean = float(-scores["test_rmse"].mean())

        benchmarks["regression_models"][name] = {
            "r2_mean": round(r2_mean, 4),
            "r2_std": round(r2_std, 4),
            "mae": round(mae_mean, 4),
            "rmse": round(rmse_mean, 4)
        }
        print(f"[{name}] R2: {r2_mean:.3f} (+/-{r2_std:.3f}) | MAE: {mae_mean:.3f} | RMSE: {rmse_mean:.3f}")

    # Train and save Best HPI Proxy Regressor (Random Forest with high generalization)
    best_hpi_reg = RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42)
    best_hpi_reg.fit(X_proxy, y_hpi)
    joblib.dump(best_hpi_reg, os.path.join(MODEL_DIR, "reg_partial.joblib"))
    joblib.dump(best_hpi_reg, os.path.join(MODEL_DIR, "reg_full.joblib")) # fallback compat

    # 2. HEI Proxy Regressor
    y_hei = df["HEI"]
    best_hei_reg = RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42)
    best_hei_reg.fit(X_proxy, y_hei)
    joblib.dump(best_hei_reg, os.path.join(MODEL_DIR, "reg_hei_partial.joblib"))
    joblib.dump(best_hei_reg, os.path.join(MODEL_DIR, "reg_hei_full.joblib"))

    # 3. Individual Metal Hazard Estimators (Cd, Fe, Mn)
    print("\n--- 2. MULTI-TARGET METAL ESTIMATION BENCHMARKS ---")
    for metal in ["Cd", "Fe", "Mn"]:
        y_metal = df[metal]
        m_reg = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
        scores = cross_validate(m_reg, X_proxy, y_metal, cv=cv, scoring={"r2": "r2"})
        r2_val = float(scores["test_r2"].mean())
        benchmarks["target_estimations"][metal] = {"r2_mean": round(r2_val, 4)}
        print(f"[Estimating {metal} from proxies] 5-Fold R2: {r2_val:.3f}")
        
        m_reg.fit(X_proxy, y_metal)
        joblib.dump(m_reg, os.path.join(MODEL_DIR, f"reg_proxy_{metal.lower()}.joblib"))

    # 4. Safety Category Classifier
    print("\n--- 3. SAFETY CATEGORY CLASSIFIER ---")
    y_clf = df["Safety_Category"]
    clf_model = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
    scoring_clf = {"acc": "accuracy", "f1": "f1_weighted"}
    clf_scores = cross_validate(clf_model, X_proxy, y_clf, cv=cv, scoring=scoring_clf)
    acc_mean = float(clf_scores["test_acc"].mean())
    f1_mean = float(clf_scores["test_f1"].mean())
    print(f"[Random Forest Classifier] Accuracy: {acc_mean:.3f} | Weighted F1: {f1_mean:.3f}")
    benchmarks["classification"]["Random Forest Classifier"] = {
        "accuracy": round(acc_mean, 4),
        "f1_weighted": round(f1_mean, 4)
    }

    clf_model.fit(X_proxy, y_clf)
    joblib.dump(clf_model, os.path.join(MODEL_DIR, "clf_partial.joblib"))
    joblib.dump(clf_model, os.path.join(MODEL_DIR, "clf_full.joblib"))

    # 5. Isolation Forest Anomaly Detector
    print("\n--- 4. ISOLATION FOREST ANOMALY DETECTOR ---")
    anomaly_model = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
    anomaly_model.fit(X_full[["Cu", "Zn", "Mn", "Fe", "Cd", "Pb", "Ni", "pH", "TDS", "EC"]])
    joblib.dump(anomaly_model, os.path.join(MODEL_DIR, "anomaly_detector.joblib"))
    print("[+] Anomaly detector trained and saved.")

    # Save benchmark metrics
    benchmark_path = os.path.join(MODEL_DIR, "benchmarks.json")
    with open(benchmark_path, "w") as f:
        json.dump(benchmarks, f, indent=4)
    print(f"\n[+] Benchmarks written to: {benchmark_path}")
    print("[+] All models successfully trained and serialized.")

if __name__ == "__main__":
    train_and_benchmark()
