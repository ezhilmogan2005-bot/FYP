/*
 * Intelligent Pesticide Sprinkler System - ESP32 Controller
 * 
 * Hardware Requirements:
 * - ESP32 Development Board
 * - ESP32-CAM Module (for image capture)
 * - DHT22 Temperature & Humidity Sensor
 * - Soil Moisture Sensor (Analog)
 * - 12V Diaphragm Pump with Relay Module
 * - SG90 Servo Motor
 * 
 * Pin Connections:
 * - DHT22: GPIO 4
 * - Soil Moisture: GPIO 34 (ADC)
 * - Relay (Pump): GPIO 18
 * - Servo Motor: GPIO 19
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <ESP32Servo.h>

// ============== CONFIGURATION ==============
// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Backend API Configuration
const char* backend_server = "http://192.168.1.100:5000";  // Update with your server IP
const int backend_port = 5000;

// Pin Definitions
#define DHT_PIN 4
#define SOIL_MOISTURE_PIN 34  // ADC pin
#define RELAY_PIN 18
#define SERVO_PIN 19

// Sensor Types
#define DHT_TYPE DHT22

// Safety Thresholds
const int SOIL_MOISTURE_MIN = 40;  // Minimum safe soil moisture (%)
const int SOIL_MOISTURE_MAX = 70;  // Maximum safe soil moisture (%)

// Timing Configuration
const unsigned long SENSOR_READ_INTERVAL = 5000;    // Read sensors every 5 seconds
const unsigned long API_CHECK_INTERVAL = 10000;     // Check API every 10 seconds
const unsigned long IMAGE_SEND_INTERVAL = 300000;   // Send image every 5 minutes

// ============== GLOBAL VARIABLES ==============
DHT dht(DHT_PIN, DHT_TYPE);
Servo sprayServo;

// Sensor Data
float temperature = 0.0;
float humidity = 0.0;
int soilMoisture = 0;

// System State
bool isSpraying = false;
unsigned long sprayStartTime = 0;
int sprayDuration = 0;
unsigned long lastSensorRead = 0;
unsigned long lastApiCheck = 0;
unsigned long lastImageSend = 0;

// ============== SETUP ==============
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("🌱 Intelligent Pesticide Sprinkler System");
  Serial.println("========================================\n");
  
  // Initialize pins
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Ensure pump is off initially
  
  // Initialize DHT sensor
  dht.begin();
  
  // Initialize Servo
  sprayServo.attach(SERVO_PIN);
  sprayServo.write(90);  // Center position
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("\n✅ System initialized successfully!");
  Serial.println("========================================\n");
}

// ============== MAIN LOOP ==============
void loop() {
  unsigned long currentMillis = millis();
  
  // Read sensors at regular intervals
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    readSensors();
    lastSensorRead = currentMillis;
  }
  
  // Check for spray commands from backend
  if (currentMillis - lastApiCheck >= API_CHECK_INTERVAL) {
    checkSprayCommand();
    sendSensorData();
    lastApiCheck = currentMillis;
  }
  
  // Send image for analysis periodically
  if (currentMillis - lastImageSend >= IMAGE_SEND_INTERVAL) {
    captureAndSendImage();
    lastImageSend = currentMillis;
  }
  
  // Handle spray timer
  if (isSpraying && (currentMillis - sprayStartTime >= sprayDuration * 1000)) {
    stopSpray();
  }
  
  // Maintain WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }
  
  delay(100);
}

// ============== SENSOR FUNCTIONS ==============
void readSensors() {
  // Read temperature and humidity
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  
  // Check if DHT readings are valid
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("⚠️  Failed to read from DHT sensor!");
    temperature = 0.0;
    humidity = 0.0;
  }
  
  // Read soil moisture (analog 0-4095, convert to percentage)
  int rawSoil = analogRead(SOIL_MOISTURE_PIN);
  // Map 0-4095 to 0-100% (lower value = wetter soil)
  soilMoisture = map(rawSoil, 0, 4095, 100, 0);
  soilMoisture = constrain(soilMoisture, 0, 100);
  
  // Print sensor readings
  Serial.println("\n📊 Sensor Readings:");
  Serial.printf("   Temperature: %.1f°C\n", temperature);
  Serial.printf("   Humidity: %.1f%%\n", humidity);
  Serial.printf("   Soil Moisture: %d%%\n", soilMoisture);
  Serial.printf("   Soil Moisture Safe: %s\n", isSoilMoistureSafe() ? "YES" : "NO");
}

bool isSoilMoistureSafe() {
  /*
   * Safety Check: Only allow spraying if soil moisture is within safe range.
   * This prevents:
   * - Plant damage from spraying on dry soil (< 40%)
   * - Pesticide dilution/wash-off on wet soil (> 70%)
   */
  return (soilMoisture >= SOIL_MOISTURE_MIN && soilMoisture <= SOIL_MOISTURE_MAX);
}

// ============== NETWORK FUNCTIONS ==============
void connectToWiFi() {
  Serial.printf("\n📡 Connecting to WiFi: %s\n", ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.printf("   IP Address: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n❌ WiFi Connection Failed!");
  }
}

void sendSensorData() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(backend_server) + "/sensors/update";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = soilMoisture;
  
  String payload;
  serializeJson(doc, payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 200) {
    Serial.println("📤 Sensor data sent successfully");
  } else {
    Serial.printf("⚠️  Failed to send sensor data. HTTP Code: %d\n", httpCode);
  }
  
  http.end();
}

void checkSprayCommand() {
  /*
   * Check backend for spray commands.
   * Only activates pump if:
   * 1. Backend sends "START_SPRAY" command
   * 2. Soil moisture is within safe range (40-70%)
   */
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  String url = String(backend_server) + "/control/status";
  
  http.begin(url);
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String response = http.getString();
    
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (!error) {
      const char* command = doc["spray_status"]["last_command"];
      int duration = doc["spray_status"]["spray_duration"] | 5;
      
      if (command && strcmp(command, "START") == 0 && !isSpraying) {
        // Backend requests spray - check safety conditions
        Serial.println("\n🚿 Backend requests SPRAY");
        
        if (isSoilMoistureSafe()) {
          startSpray(duration);
        } else {
          Serial.printf("   ❌ SPRAY DENIED - Soil moisture %d%% outside safe range (40-70%%)\n", soilMoisture);
        }
      }
      else if (command && strcmp(command, "STOP") == 0 && isSpraying) {
        stopSpray();
      }
    }
  }
  
  http.end();
}

// ============== ACTUATOR FUNCTIONS ==============
void startSpray(int duration) {
  /*
   * Start pesticide spraying
   * 
   * @param duration: Spray duration in seconds (determined by infection level)
   *                   - Low infection (< 25%): 3 seconds
   *                   - Moderate infection (25-50%): 5 seconds
   *                   - High infection (50-75%): 8 seconds
   *                   - Severe infection (> 75%): 10 seconds
   */
  
  if (isSpraying) return;
  
  Serial.println("\n" + String("=")*50);
  Serial.println("🚿 STARTING PESTICIDE SPRAY");
  Serial.printf("   Duration: %d seconds\n", duration);
  Serial.printf("   Soil Moisture: %d%%\n", soilMoisture);
  Serial.println(String("=")*50 + "\n");
  
  // Activate pump via relay
  digitalWrite(RELAY_PIN, HIGH);
  
  // Move servo to spray position (can be adjusted based on target area)
  sprayServo.write(45);  // Spray left
  delay(500);
  sprayServo.write(135); // Spray right
  delay(500);
  sprayServo.write(90);  // Center
  
  isSpraying = true;
  sprayStartTime = millis();
  sprayDuration = duration;
}

void stopSpray() {
  if (!isSpraying) return;
  
  Serial.println("\n" + String("=")*50);
  Serial.println("🛑 STOPPING PESTICIDE SPRAY");
  Serial.println(String("=")*50 + "\n");
  
  // Turn off pump
  digitalWrite(RELAY_PIN, LOW);
  
  // Return servo to center
  sprayServo.write(90);
  
  isSpraying = false;
  sprayDuration = 0;
}

// ============== IMAGE CAPTURE ==============
void captureAndSendImage() {
  /*
   * Capture image from ESP32-CAM and send to backend for analysis.
   * This function uses ESP32-CAM library to capture and transmit images.
   * 
   * Note: In a real implementation, integrate ESP32-CAM code here.
   * For this example, we assume image capture is handled separately.
   */
  Serial.println("\n📸 Capturing leaf image...");
  
  // TODO: Implement ESP32-CAM image capture and transmission
  // This would involve:
  // 1. Initialize camera (OV2640)
  // 2. Capture frame buffer
  // 3. Encode to JPEG
  // 4. Send to backend /analyze endpoint via HTTP POST
  // 5. Handle response with disease detection results
  
  Serial.println("   (ESP32-CAM integration required)");
  Serial.println("   Image capture not implemented in this example");
  
  /*
  Example ESP32-CAM capture code:
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  // ... other pin configurations
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  
  // Send image data to backend
  HTTPClient http;
  http.begin(String(backend_server) + "/analyze");
  http.addHeader("Content-Type", "image/jpeg");
  int httpCode = http.POST(fb->buf, fb->len);
  
  esp_camera_fb_return(fb);
  */
}
