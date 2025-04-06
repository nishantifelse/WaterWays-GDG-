import os
import base64
import time
import random
import serial
import requests
from flask import Flask, jsonify, render_template, request,redirect,url_for
import google.generativeai as genai
from io import BytesIO
from PIL import Image
from twilio.rest import Client


# --- Flask App Initialization ---
app = Flask(__name__)

# --- Google Gemini AI Setup ---
genai.configure(api_key="AIzaSyAGe4zEE1Zvug0afWttmTwiL0TfmykVJo4")  
model = genai.GenerativeModel("gemini-1.5-flash")

#Twillio
TWILIO_ACCOUNT_SID = "AC19fbd429c0f061191c4a902089c0b6e6"
TWILIO_AUTH_TOKEN = "a8f614dde4509511911bb207f900d9d7"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
RECIPIENT_WHATSAPP_NUMBER = "whatsapp:+916265715958"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


OPENWEATHER_API_KEY = "54578f079e5abf29184b4d8ca0a7e4c5"
CITY_NAME = "Jaipur"
OPENWEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={OPENWEATHER_API_KEY}&units=metric"

#Moisture_file
SOIL_MOISTURE_FILE = "soil_moisture.txt"
LAST_MODIFIED_TIME = 0  # Track last update time

# --- Water Pump Control Conditions ---
TEMP_THRESHOLD = 26  # Pump ON if temp >= 26°C
SOIL_MOISTURE_THRESHOLD = 71  # Pump ON if soil moisture < 71%
manual_mode = False  # Default auto
motor_status = "OFF"  # Default status

# --- Fetch Weather Data ---
def get_weather_data():
    try:
        response = requests.get(OPENWEATHER_URL)
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "wind_speed": data["wind"]["speed"],
            "humidity": data["main"]["humidity"],
            "weather_condition": data["weather"][0]["description"],
            "weather_icon": data["weather"][0]["icon"]
        }
    except Exception as e:
        print("Error fetching weather data:", e)
        return None

#twillio config   
def send_whatsapp_alert(message):
    """Send an alert via WhatsApp when conditions are met."""
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=RECIPIENT_WHATSAPP_NUMBER
        )
        print("WhatsApp Alert Sent!")
    except Exception as e:
        print("Error sending WhatsApp alert:", e)

# --- Read Soil Moisture from Arduino or Simulate ---

def get_soil_moisture():
    """Reads soil moisture from file efficiently without blocking Flask."""
    global LAST_MODIFIED_TIME, LAST_MOISTURE_VALUE

    try:
        
        current_modified_time = os.stat(SOIL_MOISTURE_FILE).st_mtime

        # If the file hasn't changed, return the last stored value
        if current_modified_time == LAST_MODIFIED_TIME:
            return LAST_MOISTURE_VALUE

        # Read updated moisture value
        with open(SOIL_MOISTURE_FILE, "r") as file:
            new_moisture = float(file.read().strip())

        
        LAST_MODIFIED_TIME = current_modified_time
        LAST_MOISTURE_VALUE = new_moisture

        return new_moisture

    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading soil moisture: {e}")
        return LAST_MOISTURE_VALUE  # Return last known value instead of default 100.0

# --- AI Soil Analysis Function (Without Saving File) ---
def analyze_soil(image_bytes, prompt):
    try:
        image_data = base64.b64encode(image_bytes).decode("utf-8")

        # Send image and prompt to Gemini
        response = model.generate_content(
            [{"text": prompt}, {"inline_data": {"mime_type": "image/png", "data": image_data}}]
        )

        return response.text if response else "Unable to generate response"
    except Exception as e:
        print("Error during AI analysis:", e)
        return "Error processing image"

# --- Prompts of soil analysis ---
SOIL_ANALYSIS_PROMPT = """
You are a soil and crops expert. Give a short soil analysis based on the given soil image.
Mention soil type, texture, and general fertility in simple terms.
Avoid bullet points or technical words. Keep it concise and understandable for farmers.
"""

SOIL_RECOMMENDATION_PROMPT = """
You are a soil and farming expert. Based on the given soil image, suggest practical recommendations.
Mention suitable crops, fertilizers, and watering tips in simple language for farmers.
Keep the response short and easy to understand.
"""

# --- API: AI Soil Analysis (Without File Saving) ---
@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    image_bytes = file.read()  # Read image without saving it

    try:
        analysis = analyze_soil(image_bytes, SOIL_ANALYSIS_PROMPT)
        recommendations = analyze_soil(image_bytes, SOIL_RECOMMENDATION_PROMPT)
        return jsonify({"analysis": analysis, "recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- API: Fetch Weather & Soil Data + Pump Control ---
@app.route("/update", methods=["GET"])
def update():
    global motor_status

    weather_data = get_weather_data()
    soil_moisture = get_soil_moisture()

    if weather_data:
        if not manual_mode:
            if weather_data["temperature"] >= TEMP_THRESHOLD or soil_moisture < SOIL_MOISTURE_THRESHOLD:
                motor_status = "ON"
                send_whatsapp_alert(f"🚨 Alert: Motor Turned ON! 🌡️ Temp: {weather_data['temperature']}°C, Soil Moisture: {soil_moisture}%")
            else:
                motor_status = "OFF"

        return jsonify({
            "temperature": weather_data["temperature"],
            "wind_speed": weather_data["wind_speed"],
            "humidity": weather_data["humidity"],
            "weather_condition": weather_data["weather_condition"],
            "soil_moisture": soil_moisture,
            "pump_status": motor_status,
            "manual_mode": manual_mode,
            "weather_icon": weather_data["weather_icon"]
        })
    


# --- Serve Static HTML Pages ---
@app.route("/")
def index():
    return render_template("home.html")

@app.route("/html/home.html")
def redirect_home():
    return redirect(url_for('index'))

@app.route("/<page>.html")
def render_page(page):
    return render_template(f"{page}.html")

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False) 
