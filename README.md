# 🌱 Intelligent Pesticide Sprinkler System

A comprehensive IoT-based smart agriculture system that detects plant diseases using AI-powered image segmentation and automates pesticide spraying based on environmental conditions.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Hardware Setup](#hardware-setup)
- [Project Structure](#project-structure)

## 🔍 Overview

The Intelligent Pesticide Sprinkler System is designed to help farmers:
- Monitor environmental conditions (temperature, humidity, soil moisture)
- Detect plant diseases using AI image analysis
- Automatically calculate optimal pesticide spray duration
- Safely control pesticide application based on soil conditions

### Key Safety Features

✅ **Soil Moisture Check**: Only allows spraying when soil moisture is between 40-70% to prevent:
- Plant damage from spraying on dry soil
- Pesticide dilution/wash-off on wet soil

🤖 **AI-Powered Detection**: Uses U-Net architecture for precise disease segmentation

⚙️ **Smart Spray Logic**: Automatically adjusts spray duration based on infection severity

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Mobile App    │◄────►│   Flask Backend  │◄────►│   ESP32 + IoT   │
│   (Flutter)     │      │   (Python/AI)    │      │   (C++/Arduino) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
       │                          │                         │
       │                    ┌─────┴─────┐                   │
       │                    │           │                   │
       │              ┌─────▼────┐ ┌───▼────┐         ┌─────▼─────┐
       │              │  U-Net   │ │  API   │         │  Sensors  │
       │              │  Model   │ │  Endp. │         │  & Pump   │
       │              └──────────┘ └────────┘         └───────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 2.3.3
- **AI/ML**: TensorFlow 2.13.0 (U-Net Model)
- **Image Processing**: Pillow, OpenCV, NumPy, SciPy
- **Utilities**: Flask-CORS, Werkzeug, python-dotenv

### IoT Firmware
- **Platform**: ESP32 (Arduino Framework)
- **Libraries**: WiFi, HTTPClient, DHT, ESP32Servo
- **Sensors**: DHT22 (Temp/Humidity), Soil Moisture, ESP32-CAM

### Mobile App
- **Framework**: Flutter 3.0+
- **Language**: Dart
- **Packages**: http, image_picker

## ✨ Features

### 1. Real-time Sensor Monitoring
- Temperature and humidity readings (DHT22)
- Soil moisture percentage (analog sensor)
- Automatic data transmission to backend

### 2. AI Disease Detection
- U-Net image segmentation for precise disease area detection
- Support for multiple crop diseases:
  - Wheat Brown Rust
  - Tomato Early Blight
  - Rice Blast
  - Potato Late Blight
- Confidence scoring and infection percentage calculation

### 3. Smart Spray Control
- **Safety-first approach**: Soil moisture validation (40-70% safe range)
- **Adaptive spray duration**:
  - No infection (0%): 0 seconds
  - Low (0-25%): 3 seconds
  - Moderate (25-50%): 5 seconds
  - High (50-75%): 8 seconds
  - Severe (75%+): 10 seconds

### 4. Mobile Dashboard
- Real-time sensor data visualization
- Manual spray controls (Start/Stop)
- Leaf scanning for disease analysis
- Treatment recommendations with pesticide info

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js and npm (for Flutter)
- Arduino IDE with ESP32 board support
- Flutter SDK

### 1. Clone the Repository

```bash
git clone <repository-url>
cd intelligent-pesticide-sprinkler
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The server will start on `http://0.0.0.0:5000`

### 3. IoT Firmware Setup

1. Open `firmware/esp32_controller.ino` in Arduino IDE
2. Install required libraries:
   - WiFi (built-in)
   - HTTPClient (built-in)
   - ArduinoJson
   - DHT sensor library
   - ESP32Servo
3. Update WiFi credentials in the code:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
4. Update backend server IP:
   ```cpp
   const char* backend_server = "http://192.168.1.100:5000";
   ```
5. Upload to ESP32 board

### 4. Mobile App Setup

```bash
cd mobile_app

# Install dependencies
flutter pub get

# Run on emulator/device
flutter run
```

**Note**: Update the API URL in `main.dart` to match your backend IP:
```dart
final String apiUrl = 'http://192.168.1.100:5000';
```

## 🚀 Usage

### Starting the System

1. **Start Backend Server**
   ```bash
   cd backend
   python app.py
   ```

2. **Power On ESP32**
   - The device will connect to WiFi automatically
   - Sensor readings will be sent to backend every 5 seconds

3. **Open Mobile App**
   - View real-time sensor data
   - Check spray conditions
   - Scan leaves for disease analysis

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and available endpoints |
| `/analyze` | POST | Analyze leaf image for disease |
| `/sensors` | GET | Get latest sensor readings |
| `/sensors/update` | POST | Update sensor data (from IoT) |
| `/control/spray` | POST | Control spray pump |
| `/control/status` | GET | Get spray system status |

### Example API Usage

**Analyze Image:**
```bash
curl -X POST http://localhost:5000/analyze \
  -F "image=@leaf_sample.jpg" \
  -F "soil_moisture=55"
```

**Control Spray:**
```bash
curl -X POST http://localhost:5000/control/spray \
  -H "Content-Type: application/json" \
  -d '{"command": "START", "duration": 5, "soil_moisture": 55}'
```

## 🔌 Hardware Setup

### Components Required

- **ESP32 Development Board** (DevKit v1 or similar)
- **ESP32-CAM Module** (for image capture)
- **DHT22** Temperature & Humidity Sensor
- **Soil Moisture Sensor** (Analog, capacitive recommended)
- **12V Diaphragm Pump**
- **Relay Module** (5V, for pump control)
- **Servo Motor** (SG90 or similar, for spray angle)
- **Power Supply** (12V for pump, 5V for ESP32)

### Wiring Diagram

```
ESP32 Pin Connections:

DHT22 Sensor:
  VCC  → 3.3V
  DATA → GPIO 4
  GND  → GND

Soil Moisture Sensor:
  VCC  → 3.3V
  SIG  → GPIO 34 (ADC)
  GND  → GND

Relay Module (Pump):
  VCC  → 5V
  IN   → GPIO 18
  GND  → GND

Servo Motor:
  VCC  → 5V
  SIG  → GPIO 19
  GND  → GND
```

### ESP32-CAM Connections

The ESP32-CAM can be connected separately or integrated with the main ESP32. For separate operation:
- Flash the ESP32-CAM with camera firmware
- Connect via UART or use separate WiFi connection
- Send captured images to backend `/analyze` endpoint

## 📁 Project Structure

```
intelligent-pesticide-sprinkler/
├── backend/
│   ├── app.py                    # Flask API server
│   ├── model.py                  # U-Net model implementation
│   ├── spray_logic.py            # Spray duration calculation logic
│   ├── requirements.txt          # Python dependencies
│   └── uploads/                  # Uploaded images storage
├── firmware/
│   └── esp32_controller.ino      # ESP32 Arduino code
├── mobile_app/
│   ├── lib/
│   │   └── main.dart             # Flutter app main file
│   └── pubspec.yaml              # Flutter dependencies
└── README.md                     # This file
```

## 🧪 Testing

### Test Spray Duration Logic

```bash
cd backend
python spray_logic.py
```

### Test Backend API

```bash
# Run in terminal 1
python backend/app.py

# Test endpoints
curl http://localhost:5000/sensors
curl http://localhost:5000/control/status
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
FLASK_ENV=development
FLASK_PORT=5000
UPLOAD_FOLDER=uploads
MODEL_PATH=path/to/unet_model.h5
```

### Adjusting Thresholds

Modify safety thresholds in:

- **Backend** (`app.py`):
  ```python
  moisture_safe = 40 <= soil_moisture <= 70
  ```

- **ESP32** (`firmware/esp32_controller.ino`):
  ```cpp
  const int SOIL_MOISTURE_MIN = 40;
  const int SOIL_MOISTURE_MAX = 70;
  ```

## 📊 Disease Detection Model

The system uses a U-Net architecture for semantic segmentation:

- **Input**: 256x256 RGB images
- **Output**: Binary segmentation mask (diseased vs healthy areas)
- **Metrics**: Infection percentage calculated from diseased pixel count

For production use, replace the dummy segmentation in `model.py` with a trained model:

```python
def __init__(self, model_path='models/unet_plant_disease.h5'):
    self.model = unet_model()
    if model_path:
        self.model.load_weights(model_path)
```

## 🛡️ Safety Features

1. **Double Moisture Check**: 
   - Backend validates before approving spray
   - ESP32 validates before activating pump

2. **Automatic Timeout**: 
   - Spray automatically stops after calculated duration
   - Emergency stop via mobile app or backend

3. **Servo Positioning**: 
   - Automatic angle adjustment for optimal coverage
   - Returns to safe position after spraying

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- U-Net architecture: Ronneberger et al. (2015)
- ESP32 community for excellent libraries
- Flutter team for the amazing framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for Smart Agriculture**
