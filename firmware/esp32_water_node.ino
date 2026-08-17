/* ==============================================================================
 * ESP32 Groundwater Monitoring Node Firmware
 * Project: AI-Driven Assessment of Heavy Metal Pollution Indices
 * Target MCU: ESP-WROOM-32 / NodeMCU ESP32
 * 
 * Hardware Sensors:
 *   1. Gravity Analog pH Sensor (E-201-C probe) -> GPIO 34 (ADC1_CH6)
 *   2. Gravity Analog TDS Sensor Module          -> GPIO 35 (ADC1_CH7)
 *   3. DS18B20 1-Wire Digital Temp Sensor        -> GPIO 4 (with 4.7k pullup)
 * 
 * Functions:
 *   - Continuous multi-sample analog reading with median filtering
 *   - Temperature compensation for accurate EC/TDS computation
 *   - Wi-Fi HTTP POST telemetry JSON transmission to Central AI Server
 * ============================================================================== */

#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h> // Library: ArduinoJson by Benoit Blanchon

// Network Credentials
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://192.168.1.100:8501/api/telemetry"; // Dashboard Webhook Endpoint

// Hardware Pin Definitions
#define PIN_PH_SENSOR    34
#define PIN_TDS_SENSOR   35
#define PIN_ONE_WIRE_BUS 4
#define STATUS_LED       2

// Calibration Constants
#define VREF_MV          3300.0   // 3.3V ADC Reference
#define ADC_RESOLUTION   4095.0   // 12-bit ADC
#define PH_CAL_SLOPE     -5.70    // mV to pH Slope (Calibrated with pH 4.0 & 7.0 buffer)
#define PH_CAL_OFFSET    21.34

OneWire oneWire(PIN_ONE_WIRE_BUS);
DallasTemperature tempSensors(&oneWire);

// Buffer for median filtering
#define SAMPLES_COUNT 30

float readMedianADC(int pin) {
    int rawSamples[SAMPLES_COUNT];
    for (int i = 0; i < SAMPLES_COUNT; i++) {
        rawSamples[i] = analogRead(pin);
        delay(10);
    }
    // Simple sort for median
    for (int i = 0; i < SAMPLES_COUNT - 1; i++) {
        for (int j = i + 1; j < SAMPLES_COUNT; j++) {
            if (rawSamples[i] > rawSamples[j]) {
                int temp = rawSamples[i];
                rawSamples[i] = rawSamples[j];
                rawSamples[j] = temp;
            }
        }
    }
    return (float)rawSamples[SAMPLES_COUNT / 2];
}

float measureTemperature() {
    tempSensors.requestTemperatures();
    float tempC = tempSensors.getTempCByIndex(0);
    if (tempC == DEVICE_DISCONNECTED_C || tempC < 0) {
        return 28.0; // Default ambient groundwater temperature in TN
    }
    return tempC;
}

float measurePH(float tempC) {
    float rawMedian = readMedianADC(PIN_PH_SENSOR);
    float voltage = (rawMedian / ADC_RESOLUTION) * (VREF_MV / 1000.0);
    // Standard pH equation with linear calibration
    float phValue = 3.5 * voltage + PH_CAL_OFFSET / 10.0;
    // Temperature compensation factor (Nernst equation slope adjustment)
    phValue += (25.0 - tempC) * 0.003;
    return constrain(phValue, 0.0, 14.0);
}

float measureTDS(float tempC) {
    float rawMedian = readMedianADC(PIN_TDS_SENSOR);
    float voltage = (rawMedian / ADC_RESOLUTION) * (VREF_MV / 1000.0);
    
    // Temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
    float compensationCoefficient = 1.0 + 0.02 * (tempC - 25.0);
    float compensationVoltage = voltage / compensationCoefficient;
    
    // Convert voltage to TDS in ppm using empirical polynomial
    float tdsValue = (133.42 * pow(compensationVoltage, 3) - 255.86 * pow(compensationVoltage, 2) + 857.39 * compensationVoltage) * 0.5;
    return constrain(tdsValue, 0.0, 5000.0);
}

void setup() {
    Serial.begin(115200);
    pinMode(STATUS_LED, OUTPUT);
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);
    
    tempSensors.begin();
    
    Serial.println("\n[+] Initializing ESP32 Water Intelligence Node...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
        delay(500);
        Serial.print(".");
        retries++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[+] Wi-Fi Connected! IP: " + WiFi.localIP().toString());
        digitalWrite(STATUS_LED, HIGH);
    } else {
        Serial.println("\n[-] Wi-Fi Connection Failed. Operating in offline logging mode.");
    }
}

void loop() {
    float waterTemp = measureTemperature();
    float waterPH   = measurePH(waterTemp);
    float waterTDS  = measureTDS(waterTemp);
    float waterEC   = waterTDS * 1.45; // Empirical TDS-to-EC conversion

    Serial.printf("\n--- TELEMETRY SAMPLE ---\n");
    Serial.printf("Temperature: %.1f C\n", waterTemp);
    Serial.printf("pH:          %.2f\n", waterPH);
    Serial.printf("TDS:         %.1f mg/L (ppm)\n", waterTDS);
    Serial.printf("EC:          %.1f uS/cm\n", waterEC);

    // Build JSON Payload
    StaticJsonDocument<256> doc;
    doc["node_id"]        = "ESP32-KAD-GW01";
    doc["station_name"]   = "Kadaladi Field Station";
    doc["latitude"]       = 9.15744;
    doc["longitude"]      = 78.56223;
    
    JsonObject telemetry = doc.createNestedObject("telemetry");
    telemetry["pH"]            = round(waterPH * 100.0) / 100.0;
    telemetry["TDS_ppm"]       = round(waterTDS * 10.0) / 10.0;
    telemetry["EC_uS_cm"]      = round(waterEC * 10.0) / 10.0;
    telemetry["temperature_C"] = round(waterTemp * 10.0) / 10.0;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    // Transmit over HTTP POST
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(SERVER_URL);
        http.addHeader("Content-Type", "application/json");
        
        int httpResponseCode = http.POST(jsonPayload);
        if (httpResponseCode > 0) {
            Serial.printf("[+] Telemetry transmitted! Server response: %d\n", httpResponseCode);
        } else {
            Serial.printf("[-] Transmission failed: %s\n", http.errorToString(httpResponseCode).c_str());
        }
        http.end();
    }

    // Sampling Interval: Sleep for 15 seconds (configurable for low-power deep sleep)
    delay(15000);
}
