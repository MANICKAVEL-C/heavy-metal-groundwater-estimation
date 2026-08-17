# ==============================================================================
# iot_stream.py - IoT Sensor Stream Ingestion & Edge Telemetry Simulator
# Connects low-cost physical water quality sensor nodes (ESP32/LoRaWAN) to AI
# ==============================================================================

import time
import random
from datetime import datetime
from typing import Dict, Any, List

# Simulated Monitoring Stations across Ramanathapuram / Kadaladi Aquifer
MONITORING_NODES = [
    {"node_id": "NODE-KAD-01", "name": "Kadaladi South Borewell #1", "lat": 9.15744, "lon": 78.56223, "depth_m": 42},
    {"node_id": "NODE-KAD-02", "name": "Sayalgudi Community Tank #3", "lat": 9.21065, "lon": 78.39414, "depth_m": 35},
    {"node_id": "NODE-KAD-03", "name": "Mudukulathur Agriculture Well", "lat": 9.36154, "lon": 78.45045, "depth_m": 50},
    {"node_id": "NODE-KAD-04", "name": "Valinokkam Coastal Aquifer", "lat": 9.17471, "lon": 78.50966, "depth_m": 28},
    {"node_id": "NODE-KAD-05", "name": "Kamuthi Solar Plant Boundary", "lat": 9.24851, "lon": 78.44854, "depth_m": 45}
]

def generate_telemetry_packet(node_index: int = 0) -> Dict[str, Any]:
    """
    Simulates a live JSON packet received from an ESP32 hardware node
    measuring analog pH, TDS, Electrical Conductivity, and Temperature.
    """
    node = MONITORING_NODES[node_index % len(MONITORING_NODES)]
    
    # Realistic sensor jitter around ambient baseline
    base_ph = random.uniform(6.8, 7.8)
    base_tds = random.uniform(450.0, 1600.0)
    base_ec = base_tds * random.uniform(1.4, 1.55)
    temp_c = random.uniform(27.5, 31.5)
    battery_v = random.uniform(3.7, 4.15)
    rssi_dbm = random.randint(-75, -55)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "node_id": node["node_id"],
        "station_name": node["name"],
        "latitude": node["lat"],
        "longitude": node["lon"],
        "depth_meters": node["depth_m"],
        "timestamp": timestamp,
        "telemetry": {
            "pH": round(base_ph, 2),
            "TDS_ppm": round(base_tds, 1),
            "EC_uS_cm": round(base_ec, 1),
            "temperature_C": round(temp_c, 1),
            "battery_voltage": round(battery_v, 2),
            "rssi_dbm": rssi_dbm,
            "status": "ONLINE"
        }
    }


def parse_hardware_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses and validates incoming HTTP POST or MQTT JSON telemetry from physical hardware.
    """
    required_fields = ["pH", "TDS", "EC"]
    telemetry = payload.get("telemetry", payload)
    
    for field in required_fields:
        if field not in telemetry and f"{field}_ppm" not in telemetry and f"{field}_uS_cm" not in telemetry:
            raise ValueError(f"Missing required sensor field: {field}")
            
    ph_val = float(telemetry.get("pH", 7.0))
    tds_val = float(telemetry.get("TDS", telemetry.get("TDS_ppm", 500.0)))
    ec_val = float(telemetry.get("EC", telemetry.get("EC_uS_cm", tds_val * 1.45)))
    
    return {
        "pH": ph_val,
        "TDS": tds_val,
        "EC": ec_val,
        "latitude": payload.get("latitude", 9.222),
        "longitude": payload.get("longitude", 78.496),
        "station_name": payload.get("station_name", "Field Edge Sensor Node"),
        "timestamp": payload.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    }
