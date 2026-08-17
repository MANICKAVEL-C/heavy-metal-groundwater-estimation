# ==============================================================================
# health_risk_engine.py - USEPA Standard Human Health Risk Assessment
# Quantifies Toxicological Hazard Quotient (HQ) & Hazard Index (HI)
# Standard: USEPA Risk Assessment Guidance for Superfund (RAGS, Part A)
# ==============================================================================

from typing import Dict, Any

# USEPA Oral Reference Dose (RfD in mg/kg/day) from USEPA IRIS Database
ORAL_REFERENCE_DOSES = {
    "Cd": 0.0005,   # Cadmium - Renal damage threshold
    "Pb": 0.0035,   # Lead - Neurotoxicity threshold
    "Ni": 0.0200,   # Nickel
    "Cu": 0.0400,   # Copper
    "Mn": 0.1400,   # Manganese
    "Fe": 0.7000,   # Iron
    "Zn": 0.3000    # Zinc
}

def calculate_human_health_risk(metals: Dict[str, float]) -> Dict[str, Any]:
    """
    Computes Chronic Daily Intake (CDI) and Hazard Quotient (HQ) for
    both Children (high vulnerability) and Adults.
    
    Formula:
      CDI = (C * IR * EF * ED) / (BW * AT)
      HQ  = CDI / RfD
      HI  = sum(HQ_i)  (Hazard Index)
      
    Parameters:
      Adults:   IR = 2.0 L/day, BW = 70 kg
      Children: IR = 1.0 L/day, BW = 15 kg
      EF = 365 days/yr, ED = 30 yrs (adult) / 6 yrs (child), AT = ED * 365
    """
    adult_hq = {}
    child_hq = {}
    adult_cdi = {}
    child_cdi = {}

    adult_hi = 0.0
    child_hi = 0.0

    for symbol, conc in metals.items():
        if symbol in ORAL_REFERENCE_DOSES:
            rfd = ORAL_REFERENCE_DOSES[symbol]
            
            # CDI in mg/kg-day
            cdi_adult = (conc * 2.0) / 70.0
            cdi_child = (conc * 1.0) / 15.0
            
            hq_a = cdi_adult / rfd
            hq_c = cdi_child / rfd
            
            adult_cdi[symbol] = cdi_adult
            child_cdi[symbol] = cdi_child
            adult_hq[symbol] = hq_a
            child_hq[symbol] = hq_c
            
            adult_hi += hq_a
            child_hi += hq_c

    # Risk Categorization
    # HI < 1.0: No significant non-carcinogenic health risk
    # HI >= 1.0: Potential adverse health effects (Action required)
    # HI >= 4.0: Severe toxicological danger
    
    child_status = "CRITICAL TOXIC HAZARD" if child_hi >= 3.0 else ("ELEVATED RISK" if child_hi >= 1.0 else "SAFE")
    adult_status = "CRITICAL TOXIC HAZARD" if adult_hi >= 3.0 else ("ELEVATED RISK" if adult_hi >= 1.0 else "SAFE")

    return {
        "adult_hi": round(adult_hi, 2),
        "child_hi": round(child_hi, 2),
        "adult_status": adult_status,
        "child_status": child_status,
        "adult_hq_breakdown": {k: round(v, 3) for k, v in adult_hq.items()},
        "child_hq_breakdown": {k: round(v, 3) for k, v in child_hq.items()},
        "primary_risk_driver": max(child_hq, key=child_hq.get) if child_hq else "None",
        "child_cdi": {k: round(v, 6) for k, v in child_cdi.items()}
    }
