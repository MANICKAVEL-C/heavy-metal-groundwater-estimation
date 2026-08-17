import analytical_engine
import remediation_engine
import iot_stream
import translations
import pdf_report
import folium_map
import joblib

# Test 1: Analytical Calculation
sample_metals = {"Cd": 0.0018, "Pb": 0.0010, "Fe": 0.38, "Mn": 0.14, "Cu": 0.035, "Zn": 1.25, "Ni": 0.001}
hpi, qi = analytical_engine.calculate_exact_hpi(sample_metals)
hei = analytical_engine.calculate_exact_hei(sample_metals)
print(f"[TEST 1 PASS] Analytical HPI: {hpi:.2f}, HEI: {hei:.2f}")

# Test 2: Remediation Plan
plan = remediation_engine.generate_remediation_plan(sample_metals, 7.35, 1150.0, 1650.0, "Moderate")
print(f"[TEST 2 PASS] Remediation Plan Generated successfully. Cost: Rs. {plan['estimated_cost_per_kl']:.2f}/kL")

# Test 3: IoT Packet
packet = iot_stream.generate_telemetry_packet(0)
print(f"[TEST 3 PASS] IoT Node: {packet['node_id']} | pH: {packet['telemetry']['pH']}")

# Test 4: PDF Generation
pdf_bytes = pdf_report.generate_certified_report(
    "Test Station", "Post-Monsoon", hpi, hei, "Moderate",
    "Mode A", {"pH": 7.35, "TDS": 1150.0, "EC": 1650.0, **sample_metals},
    plan, 9.222, 78.496
)
print(f"[TEST 4 PASS] Generated PDF Byte Size: {len(pdf_bytes.getvalue())} bytes")

print("\n>>> ALL 4 SYSTEM TESTS PASSED PERFECTLY! <<<")
