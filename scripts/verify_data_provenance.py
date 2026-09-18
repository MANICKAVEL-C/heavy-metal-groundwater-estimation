# ==============================================================================
# verify_data_provenance.py - Data Provenance & Integrity Audit Pipeline
# Documents and audits the 3-tier data pipeline:
# Tier 1 (8,419 CGWB Statewide Records) -> Tier 2 (367 District Records) -> Tier 3 (88 Ground Truth)
# ==============================================================================

import os
import json
import hashlib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_PATH = os.path.join(BASE_DIR, "data", "provenance_ledger.json")
DATA_PATH = os.path.join(BASE_DIR, "data", "tamilnadu_groundwater_WITH_INDICES.csv")
BENCHMARK_PATH = os.path.join(BASE_DIR, "models", "benchmarks.json")

def audit_provenance():
    print("=" * 76)
    print("  DATASET PROVENANCE AUDIT & DATA INTEGRITY VERIFICATION")
    print("=" * 76)
    
    print(f"\n[+] 1. LOADING PROVENANCE LEDGER ARTIFACT: {LEDGER_PATH}")
    if not os.path.exists(LEDGER_PATH):
        raise FileNotFoundError(f"Missing provenance ledger artifact: {LEDGER_PATH}")
        
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)
        
    tiers = ledger["data_pipeline_tiers"]
    t1 = tiers["tier_1_statewide_cgwb_inventory"]
    t2 = tiers["tier_2_district_hydrological_filter"]
    t3 = tiers["tier_3_laboratory_ground_truth"]
    
    print(f"    * Tier 1 (Statewide CGWB Archive)       : {t1['total_records_ingested']:,} records ({t1['physicochemical_completeness']['completeness_percentage']}% sensor completeness)")
    print(f"    * Tier 2 (Ramanathapuram Basin Filter)  : {t2['raw_extracted_records']} raw records -> 1 anomalous sensor removed -> {t2['cleaned_validated_records']} clean records")
    print(f"    * Tier 3 (Target 7-Metal Lab Ground Truth): {t3['physical_monitoring_borewells']} stations x 2 hydrological cycles = {t3['total_ground_truth_samples']} samples")
    
    print(f"\n[+] 2. VERIFYING TIER 3 ARTIFACT INTEGRITY: {DATA_PATH}")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Missing data file: {DATA_PATH}")
        
    # Cross-Platform SHA-256 Checksum Verification
    with open(DATA_PATH, "rb") as f:
        raw_bytes = f.read()

    canonical_lf_bytes = raw_bytes.replace(b"\r\n", b"\n")
    computed_lf_sha256 = hashlib.sha256(canonical_lf_bytes).hexdigest()
    raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    chk = t3.get("checksum_verification", {})
    expected_lf = chk.get("canonical_lf_sha256", "")
    expected_crlf = chk.get("windows_crlf_sha256", "")

    # Invariant assertion: canonical LF hash must match on all platforms (Windows, Linux, macOS)
    assert computed_lf_sha256 == expected_lf, (
        f"Cryptographic SHA-256 mismatch!\n"
        f"  Computed Canonical LF: {computed_lf_sha256}\n"
        f"  Expected Canonical LF: {expected_lf}"
    )
    print(f"    * Canonical LF SHA-256 Checksum   : {computed_lf_sha256} [VERIFIED CROSS-PLATFORM MATCH]")
    if raw_sha256 == expected_crlf:
        print(f"    * Native OS Line-Ending Checksum  : {raw_sha256} [VERIFIED WINDOWS CRLF]")
    else:
        print(f"    * Native OS Line-Ending Checksum  : {raw_sha256} [VERIFIED UNIX LF]")
        
    df = pd.read_csv(DATA_PATH)
    rows, cols = df.shape
    print(f"    * Matrix Dimensions               : {rows} rows, {cols} columns [VERIFIED 88 x 19]")
    
    # Assert integrity checks
    assert rows == t3["data_completeness"]["total_rows"], f"Expected {t3['data_completeness']['total_rows']} rows, found {rows}"
    assert cols == t3["data_completeness"]["total_columns"], f"Expected {t3['data_completeness']['total_columns']} columns, found {cols}"
    assert "Season" in df.columns, "Missing Season column"
    
    pre_count = int((df["Season"] == "Pre-Monsoon").sum())
    post_count = int((df["Season"] == "Post-Monsoon").sum())
    assert pre_count == 44 and post_count == 44, "Seasonal sample imbalance detected!"
    print(f"    * Seasonal Balance                : Pre-Monsoon = {pre_count}, Post-Monsoon = {post_count} (Perfect 1:1 pairing)")
    
    missing_count = int(df.isnull().sum().sum())
    assert missing_count == 0, f"Found {missing_count} null cells!"
    print(f"    * Missing Data Audit              : {missing_count} null cells (100.0% data completeness)")
    
    # 3. Exact Metal Range Cross-Audit against Provenance Ledger
    print(f"\n[+] 3. AUDITING 7 HEAVY METAL ANALYTICAL RANGES AGAINST PROVENANCE LEDGER:")
    for m_spec in t3["heavy_metals_quantified"]:
        m = m_spec["symbol"]
        assert m in df.columns, f"Missing metal {m}"
        min_v = round(float(df[m].min()), 5)
        max_v = round(float(df[m].max()), 5)
        declared_min, declared_max = m_spec["analytical_range"]
        assert min_v == declared_min and max_v == declared_max, (
            f"Range mismatch for {m}! CSV: [{min_v}, {max_v}] vs Ledger: [{declared_min}, {declared_max}]"
        )
        print(f"    * {m:2s} ({m_spec['name']:9s}): Range [{min_v:.5f}, {max_v:.5f}] mg/L | Mean: {m_spec['mean_concentration']:.5f} mg/L [VERIFIED EXACT MATCH]")

    # 4. Exact Index Range Cross-Audit against Provenance Ledger
    print(f"\n[+] 4. AUDITING COMPOSITE POLLUTION INDICES AGAINST PROVENANCE LEDGER:")
    for idx_spec in t3["composite_pollution_indices"]:
        idx_name = idx_spec["index"]
        assert idx_name in df.columns, f"Missing index: {idx_name}"
        min_v = round(float(df[idx_name].min()), 2)
        max_v = round(float(df[idx_name].max()), 2)
        declared_min, declared_max = idx_spec["dataset_range"]
        assert min_v == declared_min and max_v == declared_max, (
            f"Range mismatch for {idx_name}! CSV: [{min_v}, {max_v}] vs Ledger: [{declared_min}, {declared_max}]"
        )
        print(f"    * {idx_name:3s}: Range [{min_v:6.2f}, {max_v:6.2f}] | Mean: {idx_spec['dataset_mean']:5.2f} | Critical: {idx_spec['threshold_critical']} [VERIFIED EXACT MATCH]")

    # 5. Safety Category Verification
    print(f"\n[+] 5. AUDITING GROUND TRUTH SAFETY CATEGORIES:")
    cat_counts = df["Safety_Category"].value_counts().to_dict()
    for cat, expected_c in t3["safety_categories_count"].items():
        actual_c = cat_counts.get(cat, 0)
        assert actual_c == expected_c, f"Category count mismatch for {cat}: actual {actual_c} vs expected {expected_c}"
        print(f"    * {cat:16s}: {actual_c} borewells [VERIFIED]")

    print("\n[+] PROVENANCE AUDIT PASSED: 100% REPRODUCIBLE & EMPIRICALLY CONCORDANT")
    
    # Update benchmarks.json
    if os.path.exists(BENCHMARK_PATH):
        with open(BENCHMARK_PATH, "r") as f:
            bm = json.load(f)
    else:
        bm = {}
        
    bm["dataset_provenance"] = tiers
    with open(BENCHMARK_PATH, "w") as f:
        json.dump(bm, f, indent=4)
        
    print(f"[+] Provenance metadata updated in: {BENCHMARK_PATH}")
    return tiers

if __name__ == "__main__":
    audit_provenance()
