#define SOIL_MOISTURE_SENSOR 4  // Analog pin for soil moisture sensor
#define MOTOR_RELAY_PIN 27      // Digital pin connected to motor relay

const int DRY_SOIL_VALUE = 4095;  // Completely dry soil reading
const int WET_SOIL_VALUE = 1500;  // Fully wet soil reading

bool manualOverride = false;  // Track manual mode status
bool motorState = false;      // Current motor state

float previousMoisture = 50.0;  // Start from 50% to avoid jumps

// Function to map soil moisture reading to percentage
float mapSoilMoistureToPercentage(int rawValue) {
  if (rawValue >= DRY_SOIL_VALUE) return 0.0;   // Fully dry
  if (rawValue <= WET_SOIL_VALUE) return 100.0; // Fully wet

  return (1.0 - float(rawValue - WET_SOIL_VALUE) / (DRY_SOIL_VALUE - WET_SOIL_VALUE)) * 100.0;
}

// Function to gradually update moisture percentage
float smoothMoisture(float newMoisture) {
  previousMoisture = (previousMoisture * 0.9) + (newMoisture * 0.1);  // Weighted average
  return previousMoisture;
}

void setup() {
  Serial.begin(115200);
  pinMode(MOTOR_RELAY_PIN, OUTPUT);
  digitalWrite(MOTOR_RELAY_PIN, LOW);  // Keep motor off initially
}

void loop() {
  // Read soil moisture sensor value
  int rawValue = analogRead(SOIL_MOISTURE_SENSOR);
  float newMoisture = mapSoilMoistureToPercentage(rawValue);
  float moisturePercentage = smoothMoisture(newMoisture);  // Apply smoothing

  // Print only the moisture percentage for Python parsing
  Serial.println(moisturePercentage);

  // Check for manual control input from Flask backend
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  
    command.trim();  // Remove extra spaces

    if (command == "PUMP_ON") {
      digitalWrite(MOTOR_RELAY_PIN, HIGH);
      motorState = true;
      manualOverride = true;
      Serial.println("Motor ON - Manual Override");
    } 
    else if (command == "PUMP_OFF") {
      digitalWrite(MOTOR_RELAY_PIN, LOW);
      motorState = false;
      manualOverride = true;
      Serial.println("Motor OFF - Manual Override");
    } 
    else if (command == "AUTO_MODE") {
      manualOverride = false;
      Serial.println("Auto Mode Enabled");
    }
  }

  // Auto-control system based on moisture level (only if manual mode is OFF)
  if (!manualOverride) {
    if (moisturePercentage > 70 && !motorState) {
      digitalWrite(MOTOR_RELAY_PIN, HIGH);
      motorState = true;
      Serial.println("Motor ON - Low Moisture");
    } 
    else if (moisturePercentage <= 70 && motorState) {
      digitalWrite(MOTOR_RELAY_PIN, LOW);
      motorState = false;
      Serial.println("Motor OFF - Sufficient Moisture");
    }
  }

  delay(1000);  // Delay for stability
}  