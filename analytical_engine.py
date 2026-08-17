# ==============================================================================
# analytical_engine.py - Exact Hydrochemical & Heavy Metal Pollution Indices
# Standardized against BIS (IS 10500:2012) & WHO (4th Edition) Guidelines
# ==============================================================================
#
# SCIENTIFIC INTEGRITY NOTE:
# HPI, HEI, MI, and Cd are closed-form algebraic equations. When all heavy
# metals are analytically quantified via ICP-MS/AAS in a laboratory, these
# indices are computed with 100% mathematical precision with ZERO ML error.
#
# References:
# 1. Prasad, B., & Bose, J. M. (2001). Evaluation of heavy metal pollution in
#    groundwater using HPI. Environmental Geology, 40(6), 727-730.
# 2. Edet, A. E., & Offiong, O. E. (2002). Evaluation of water quality index in
#    Calabar, Nigeria. Environmental Geology, 42(7), 760-766.
# 3. Tamasi, G., & Cini, R. (2004). Heavy metals in drinking waters from
#    Mount Amiata. Science of The Total Environment, 327(1-3), 41-51.
# 4. Hakanson, L. (1980). An ecological risk index for aquatic pollution control.
#    Water Research, 14(8), 975-1001.
# ==============================================================================

from typing import Dict, Tuple, Any, List

# Standard Guidelines (Units in mg/L)
# Si: Permissible limit in drinking water (BIS IS 10500:2012 / WHO)
# Ii: Ideal permissible limit (typically 0 for toxic heavy metals)
# MAC: Maximum Admissible Concentration / Upper Threshold
# Toxicity_Weight: Relative weight inversely proportional to permissible limit (k / Si)
STANDARD_WATER_QUALITY_STANDARDS = {
    "Cd": {
        "name": "Cadmium",
        "symbol": "Cd",
        "Si": 0.003,
        "Ii": 0.0,
        "MAC": 0.010,
        "weight": 333.33,   # 1 / 0.003
        "health_impact": "Kidney damage, renal dysfunction, Itai-Itai disease, bone demineralization.",
        "category": "Heavy Metal (Group 1 Carcinogen)"
    },
    "Pb": {
        "name": "Lead",
        "symbol": "Pb",
        "Si": 0.010,
        "Ii": 0.0,
        "MAC": 0.050,
        "weight": 100.00,   # 1 / 0.010
        "health_impact": "Neurotoxicity, cognitive impairment in children, hypertension, anemia.",
        "category": "Heavy Metal (Cumulative Toxicant)"
    },
    "Ni": {
        "name": "Nickel",
        "symbol": "Ni",
        "Si": 0.020,
        "Ii": 0.0,
        "MAC": 0.070,
        "weight": 50.00,    # 1 / 0.020
        "health_impact": "Skin dermatitis (allergic contact), gastrointestinal irritation, lung fibrosis.",
        "category": "Heavy Metal (Trace Toxicant)"
    },
    "Cu": {
        "name": "Copper",
        "symbol": "Cu",
        "Si": 0.050,
        "Ii": 0.0,
        "MAC": 1.500,
        "weight": 20.00,    # 1 / 0.050
        "health_impact": "Gastrointestinal distress, liver toxicity (in excess), Wilson's disease aggravation.",
        "category": "Heavy Metal (Essential Micronutrient / Toxic in Excess)"
    },
    "Mn": {
        "name": "Manganese",
        "symbol": "Mn",
        "Si": 0.100,
        "Ii": 0.0,
        "MAC": 0.300,
        "weight": 10.00,    # 1 / 0.100
        "health_impact": "Neurological syndrome resembling Parkinsonism (Manganism), motor skill impairment.",
        "category": "Heavy Metal (Neurotoxicant in High Concentrations)"
    },
    "Fe": {
        "name": "Iron",
        "symbol": "Fe",
        "Si": 0.300,
        "Ii": 0.0,
        "MAC": 1.000,
        "weight": 3.33,     # 1 / 0.300
        "health_impact": "Hemochromatosis, metallic taste, pipe incrustation, bacterial biofilm growth.",
        "category": "Heavy Metal (Aesthetic & Organ Accumulation)"
    },
    "Zn": {
        "name": "Zinc",
        "symbol": "Zn",
        "Si": 5.000,
        "Ii": 0.0,
        "MAC": 15.000,
        "weight": 0.20,     # 1 / 5.000
        "health_impact": "Nausea, copper deficiency anemia at very high doses, astringent metallic taste.",
        "category": "Heavy Metal (Essential Mineral / Low Toxicity)"
    }
}

# Physical water parameters standards (BIS IS 10500:2012)
PHYSICAL_STANDARDS = {
    "pH": {"desirable_min": 6.5, "desirable_max": 8.5, "permissible_max": 8.5, "unit": "pH Units"},
    "TDS": {"desirable_max": 500.0, "permissible_max": 2000.0, "unit": "mg/L"},
    "EC": {"desirable_max": 750.0, "permissible_max": 3000.0, "unit": "µS/cm"},
}


def calculate_exact_hpi(metals: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    """
    Computes the exact analytical Heavy Metal Pollution Index (HPI)
    Formula: HPI = sum(Wi * Qi) / sum(Wi)
    where Qi = (|Mi - Ii| / (Si - Ii)) * 100
    and Wi = k / Si  (k = 1.0)
    """
    sum_w_q = 0.0
    sum_w = 0.0
    individual_qi = {}

    for symbol, concentration in metals.items():
        if symbol in STANDARD_WATER_QUALITY_STANDARDS:
            std = STANDARD_WATER_QUALITY_STANDARDS[symbol]
            Si = std["Si"]
            Ii = std["Ii"]
            Wi = std["weight"]

            Qi = (abs(concentration - Ii) / (Si - Ii)) * 100.0
            individual_qi[symbol] = Qi

            sum_w_q += Wi * Qi
            sum_w += Wi

    hpi = sum_w_q / sum_w if sum_w > 0 else 0.0
    return float(hpi), individual_qi


def calculate_exact_hei(metals: Dict[str, float]) -> float:
    """
    Computes Heavy Metal Evaluation Index (HEI)
    Formula: HEI = sum(Hc / Hmac)
    where Hc is monitored concentration, and Hmac is maximum admissible concentration.
    """
    hei = 0.0
    for symbol, concentration in metals.items():
        if symbol in STANDARD_WATER_QUALITY_STANDARDS:
            MAC = STANDARD_WATER_QUALITY_STANDARDS[symbol]["MAC"]
            hei += concentration / MAC
    return float(hei)


def calculate_metal_index(metals: Dict[str, float]) -> float:
    """
    Computes Metal Index (MI)
    Formula: MI = sum(Ci / MACi)
    Values > 1.0 indicate serious threshold breach.
    """
    return calculate_exact_hei(metals)


def calculate_contamination_degree(metals: Dict[str, float]) -> float:
    """
    Computes Contamination Degree (Cdeg / Cd - Hakanson 1980)
    Formula: Cdeg = sum(Cf_i) where Cf_i = (C_i / C_baseline) - 1
    """
    cdeg = 0.0
    for symbol, concentration in metals.items():
        if symbol in STANDARD_WATER_QUALITY_STANDARDS:
            Si = STANDARD_WATER_QUALITY_STANDARDS[symbol]["Si"]
            cf = (concentration / Si) - 1.0
            if cf > 0:
                cdeg += cf
    return float(cdeg)


def evaluate_metal_compliance(metals: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Generates a detailed compliance table for each heavy metal against
    BIS IS 10500:2012 / WHO permissible standards.
    """
    compliance_report = []

    for symbol, concentration in metals.items():
        if symbol in STANDARD_WATER_QUALITY_STANDARDS:
            std = STANDARD_WATER_QUALITY_STANDARDS[symbol]
            Si = std["Si"]
            MAC = std["MAC"]

            ratio = concentration / Si
            excess_pct = max(0.0, (concentration - Si) / Si * 100.0)

            if concentration <= Si:
                status = "COMPLIANT"
                badge = "Safe"
                severity = 0
            elif concentration <= MAC:
                status = "PERMISSIBLE LIMIT EXCEEDED"
                badge = "Warning"
                severity = 1
            else:
                status = "CRITICAL BREACH (> MAC)"
                badge = "Critical"
                severity = 2

            compliance_report.append({
                "symbol": symbol,
                "name": std["name"],
                "concentration": concentration,
                "Si": Si,
                "MAC": MAC,
                "ratio": ratio,
                "excess_percentage": excess_pct,
                "status": status,
                "badge": badge,
                "severity": severity,
                "health_impact": std["health_impact"],
                "category": std["category"]
            })

    # Sort by severity descending (most hazardous first)
    compliance_report.sort(key=lambda x: (x["severity"], x["excess_percentage"]), reverse=True)
    return compliance_report


def classify_pollution_severity(hpi: float) -> Tuple[str, str, str]:
    """
    Classifies HPI into international scientific risk categories:
    - Low Contamination / Safe: HPI < 30.0
    - Moderate Contamination: 30.0 <= HPI < 70.0 (or threshold < 100 in traditional literature)
    - Highly Polluted / Hazard: HPI >= 70.0 (Critical alert threshold)
    Returns: (category_name, hex_color, descriptive_summary)
    """
    if hpi < 30.0:
        return (
            "Safe",
            "#5C9271",
            "Water meets potable quality standards for heavy metals. Safe for domestic consumption."
        )
    elif hpi < 70.0:
        return (
            "Moderate",
            "#C99A44",
            "Moderate heavy metal accumulation detected. Regular monitoring and point-of-use filtration advised."
        )
    else:
        return (
            "Highly Polluted",
            "#C4602F",
            "CRITICAL HAZARD: Severe heavy metal contamination detected exceeding permissible health guidelines. Immediate cessation of direct drinking use required."
        )
