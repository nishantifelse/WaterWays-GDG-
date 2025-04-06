# 🌊 Waterways – Smart Irrigation and Soil Monitoring System

Waterways is an AI-powered, IoT-enabled platform designed to assist small and marginal farmers by automating irrigation, analyzing soil conditions, and recommending optimal pesticide usage. It integrates sensors, machine learning APIs, and weather data to make agriculture smarter and more sustainable.

---

## 📦 Features

### ✅ AI-Driven Sprinkler System
- Automatic and manual control of sprinkler zones (e.g., Front Lawn, Garden)
- Soil moisture-based smart irrigation using ESP32 + sensors
- Custom schedule setting for specific days and times

### ✅ Soil Analysis System
- Upload soil images (JPG/PNG) for instant analysis
- AI-based recommendations using Gemini 1.5 Flash API
- Pesticide recommendations based on visual cues

### ✅ Weather-Integrated Decisions
- Real-time weather data from OpenWeather API to avoid overwatering
- Soil and environment-aware suggestions

---

## 🔧 Tech Stack

### Frontend:
- HTML, CSS, JavaScript

### Backend:
- Python (Flask)
- Node.js (optional for additional backend services)

### APIs:
- *Gemini 1.5 Flash API* – For AI soil image analysis and pesticide suggestions
- *OpenWeather API* – For real-time weather data integration

### Hardware:
- ESP32 Dev Module (Microcontroller)
- Soil Moisture Sensor
- Relay Module
- Flame Sensor
- AC Motor
- USB Cable
- Connecting Wires

---

## 📁 Project Structure
SENSOR/ │ ├── pycache/ ├── .venv/ │ ├── js/ │ ├── dashboard.js │ ├── home.js │ ├── soil-analysis.js │ └── script.js │ ├── static/ │ ├── photos/icons/ │ ├── WATERWAYS_logo-preview.png │ ├── WATERWAYS-logo.png │ ├── ai-driven-sprinkler.css │ ├── dashboard.css │ ├── home.css │ ├── soil-analysis.css │ └── styles.css │ ├── templates/ │ ├── ai-driven-sprinkler.html │ ├── dashboard.html │ ├── home.html │ ├── login.html │ └── soil-analysis.html │ ├── arduino.py # Serial communication with ESP32 ├── water.py # Main Flask backend app ├── soil_moisture.txt # Stores live soil moisture data


## Getting Started

### 1. Clone the repository

`bash
git clone https://github.com/nishantifelse/WaterWays-GDG-
cd waterways
Install dependencies

bash-

python3 -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
pip install -r requirements.txt

Create a requirements.txt using:

bash-

pip freeze > requirements.txt

Run the Flask app
bash

#insure that all the library is downloaded and then run both water.py and auduino.py same time 

python water.py 
python auduino.py #run both water.py and auduino.py same time 

App will be hosted at: http://127.0.0.1:5000

Flash ESP32 Code
Use Arduino IDE to upload your ESP32 sketch to collect soil moisture data and control relays.

How It Works
🧠 AI Sprinkler System
Reads moisture data from ESP32.

Decides whether to activate sprinkler based on thresholds and schedules.

Manual override supported from frontend.

🧪 Soil Analysis
Upload soil image → Gemini 1.5 Flash API analyzes texture/color/patterns.

Receives nutrient, health, and pesticide suggestions.

☁ Weather-Aware Logic
Uses OpenWeather API to fetch rain forecast.

Skips irrigation if rain is expected.
