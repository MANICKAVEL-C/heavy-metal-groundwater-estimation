# ==============================================================================
# remediation_engine.py - Actionable Water Remediation & Treatment Advisor
# Decision Support System for Heavy Metal Decontamination & Potability Restoration
# ==============================================================================

from typing import Dict, List, Any

def generate_remediation_plan(
    metals: Dict[str, float],
    pH: float,
    TDS: float,
    EC: float,
    safety_category: str
) -> Dict[str, Any]:
    """
    Generates a structured, actionable water engineering remediation plan
    based on the exact chemical and physical profile of the groundwater.
    """
    treatment_steps = []
    primary_technologies = []
    chemicals_required = []
    estimated_cost_per_kl = 0.0  # INR per 1000 Liters

    # 1. Base Filtration & Disinfection (Baseline)
    treatment_steps.append({
        "stage": "Stage 1: Pre-Filtration & Particulate Removal",
        "technology": "Dual Media Sand & Activated Carbon Filter (5-micron cartridge)",
        "purpose": "Removes suspended solids, turbidity, organic trace matter, and protects downstream membranes.",
        "cost_inr_kl": 2.50
    })
    estimated_cost_per_kl += 2.50
    primary_technologies.append("Sand & Activated Carbon Pre-Filtration")

    # 2. pH Correction (Corrosive or Excess Alkaline)
    if pH < 6.5:
        treatment_steps.append({
            "stage": "Stage 2: pH Neutralization & Acid Buffer Neutralization",
            "technology": "Calcite (Calcium Carbonate) / Corosex neutralizing filter bed or Sodium Hydroxide (NaOH) chemical dosing",
            "purpose": f"Raises acidic pH ({pH:.2f}) to neutral range (7.0 - 7.6) to prevent heavy metal pipe leaching and corrosion.",
            "cost_inr_kl": 3.00
        })
        estimated_cost_per_kl += 3.00
        chemicals_required.append("Food-grade Calcite / Sodium Hydroxide (NaOH)")
        primary_technologies.append("Neutralization Media Filter")
    elif pH > 8.5:
        treatment_steps.append({
            "stage": "Stage 2: Alkaline Stabilization",
            "technology": "Weak acid dosing (Hydrochloric / Citric acid injection)",
            "purpose": f"Lowers high pH ({pH:.2f}) into desirable BIS drinking range (6.5 - 8.5).",
            "cost_inr_kl": 2.00
        })
        estimated_cost_per_kl += 2.00
        chemicals_required.append("Dilute Hydrochloric Acid (Food Grade)")

    # 3. High Iron (Fe) or Manganese (Mn) Oxidation
    fe_val = metals.get("Fe", 0.0)
    mn_val = metals.get("Mn", 0.0)
    if fe_val > 0.30 or mn_val > 0.10:
        treatment_steps.append({
            "stage": "Stage 3: Catalytic Oxidation & Iron/Manganese Removal",
            "technology": "Cascade Aeration followed by Manganese Greensand Plus / Birm Filter Bed + Sodium Hypochlorite injection",
            "purpose": f"Oxidizes soluble ferrous Fe(II) and Mn(II) into insoluble Fe(III)/Mn(IV) precipitates and filters them out (Fe: {fe_val:.3f} mg/L, Mn: {mn_val:.3f} mg/L).",
            "cost_inr_kl": 4.50
        })
        estimated_cost_per_kl += 4.50
        chemicals_required.append("Sodium Hypochlorite (NaOCl) / Potassium Permanganate (KMnO4)")
        primary_technologies.append("Catalytic Greensand Oxidation Bed")

    # 4. Critical Heavy Metals: Cadmium (Cd), Lead (Pb), Nickel (Ni)
    cd_val = metals.get("Cd", 0.0)
    pb_val = metals.get("Pb", 0.0)
    ni_val = metals.get("Ni", 0.0)
    has_toxic_metals = (cd_val > 0.003 or pb_val > 0.010 or ni_val > 0.020)

    if has_toxic_metals or safety_category == "Highly Polluted":
        treatment_steps.append({
            "stage": "Stage 4: Advanced Heavy Metal Separation",
            "technology": "High-Pressure Reverse Osmosis (RO) with Polyamide Thin-Film Composite Membranes (TFC) + Chelation Ion Exchange Resin (Amberlite/Purolite)",
            "purpose": f"98.5% rejection of divalent toxic cations (Cd²⁺: {cd_val:.4f} mg/L, Pb²⁺: {pb_val:.4f} mg/L). Chelation resin provides safety polishing.",
            "cost_inr_kl": 12.00
        })
        estimated_cost_per_kl += 12.00
        chemicals_required.append("Antiscalant (Phosphonate based) + Resin Regenerant (NaCl / Dilute Acid)")
        primary_technologies.append("Reverse Osmosis (RO) + Heavy Metal Chelating Resin")
    elif TDS > 1000.0 or safety_category == "Moderate":
        treatment_steps.append({
            "stage": "Stage 4: Desalination & Partial Demineralization",
            "technology": "Low-Pressure Brackish Water Reverse Osmosis (BWRO) or Nanofiltration (NF)",
            "purpose": f"Reduces elevated TDS ({TDS:.0f} mg/L) and moderate trace metal concentrations to potable limits (< 300 mg/L).",
            "cost_inr_kl": 8.00
        })
        estimated_cost_per_kl += 8.00
        primary_technologies.append("Nanofiltration / Low-Pressure RO")

    # 5. Final Disinfection & Mineral Remineralization
    treatment_steps.append({
        "stage": "Stage 5: Mineral Remineralization & UV Disinfection",
        "technology": "Remineralization Post-Filter (Ca/Mg cartridge) + Ultraviolet (UV) C-band Chamber (254nm)",
        "purpose": "Restores essential electrolytes (Ca, Mg) for taste and ensures 99.99% pathogen inactivation.",
        "cost_inr_kl": 1.50
    })
    estimated_cost_per_kl += 1.50
    primary_technologies.append("UV Disinfection & Mineral Cartridge")

    # Community Plant Sizing & CAPEX Estimates
    plant_recommendations = {
        "household_unit": {
            "capacity": "25 - 50 Liters/Hour (LPH)",
            "recommended_for": "Individual Household / Field Testing Booth",
            "capex_inr": "₹15,000 - ₹25,000",
            "power_draw": "60 Watts"
        },
        "community_kiosk": {
            "capacity": "500 - 1,000 Liters/Hour (LPH)",
            "recommended_for": "Village Water ATM / Gram Panchayat Water Kiosk (serving 500 - 1,500 people)",
            "capex_inr": "₹2,50,000 - ₹4,50,000",
            "power_draw": "1.5 - 2.5 kW (Solar PV Compatible)"
        },
        "district_scheme": {
            "capacity": "5,000 - 10,000 Liters/Hour (LPH)",
            "recommended_for": "Centralized Jal Jeevan Mission Rural Piped Water Scheme",
            "capex_inr": "₹12,00,000 - ₹22,00,000",
            "power_draw": "7.5 - 12 kW"
        }
    }

    # Summary advisory text
    if safety_category == "Safe":
        verdict = "Water is potable. Standard sediment filtration and UV disinfection recommended for microbial safety."
    elif safety_category == "Moderate":
        verdict = "Point-of-use or community filtration required. Sand-carbon prefiltration and low-pressure membrane treatment will restore water to pristine quality."
    else:
        verdict = "HIGH HAZARD: Direct consumption strictly prohibited. Immediate deployment of community-scale Reverse Osmosis and Ion Exchange chelating unit required under Jal Jeevan Mission."

    return {
        "safety_category": safety_category,
        "verdict": verdict,
        "estimated_cost_per_kl": round(estimated_cost_per_kl, 2),
        "primary_technologies": primary_technologies,
        "treatment_steps": treatment_steps,
        "chemicals_required": chemicals_required,
        "plant_recommendations": plant_recommendations
    }
