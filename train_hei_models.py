import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("/home/claude/project/dashboard/data/tamilnadu_groundwater_WITH_INDICES.csv")
df["Season_Code"] = (df["Season"] == "Post-Monsoon").astype(int)

FULL_FEATURES = ["Cu", "Zn", "Mn", "Fe", "Cd", "Pb", "Ni", "pH", "TDS", "EC", "Season_Code"]
PARTIAL_FEATURES = ["pH", "TDS", "EC", "Season_Code"]

X_full = df[FULL_FEATURES]
X_partial = df[PARTIAL_FEATURES]
y_hei = df["HEI"]

reg_hei_full = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=6)
reg_hei_full.fit(X_full, y_hei)

reg_hei_partial = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=6)
reg_hei_partial.fit(X_partial, y_hei)

joblib.dump(reg_hei_full, "/home/claude/project/dashboard/models/reg_hei_full.joblib")
joblib.dump(reg_hei_partial, "/home/claude/project/dashboard/models/reg_hei_partial.joblib")

# Quick sanity check
from sklearn.model_selection import cross_val_score
r2_full = cross_val_score(RandomForestRegressor(n_estimators=200, random_state=42, max_depth=6),
                            X_full, y_hei, cv=5, scoring="r2")
r2_partial = cross_val_score(RandomForestRegressor(n_estimators=200, random_state=42, max_depth=6),
                               X_partial, y_hei, cv=5, scoring="r2")
print(f"HEI full-data R²: {r2_full.mean():.3f} (+/-{r2_full.std():.3f})")
print(f"HEI partial-data R²: {r2_partial.mean():.3f} (+/-{r2_partial.std():.3f})")
print("HEI models trained and saved.")
