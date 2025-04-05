import serial
import time
import threading


SERIAL_PORT = "COM3" 
BAUD_RATE = 115200
SOIL_MOISTURE_FILE = "soil_moisture.txt"
MAX_RETRIES = 3  # Maximum retries before fallback
DEFAULT_SOIL_MOISTURE = 100.0  # Default value if sensor read fails
RECONNECT_ATTEMPTS = 5  # Attempts to reconnect if Arduino disconnects
READ_INTERVAL = 2  # Interval (seconds) between readings

# Function to Connect to Arduino
def connect_arduino():
    """Attempt to establish a connection with the Arduino."""
    for attempt in range(1, RECONNECT_ATTEMPTS + 1):
        try:
            print(f"🔄 Attempting to connect to Arduino (Try {attempt}/{RECONNECT_ATTEMPTS})...")
            arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
            time.sleep(2)  # Allow time for connection
            print(f"Connected to Arduino on {SERIAL_PORT}")
            return arduino
        except Exception as e:
            print(f"Connection attempt {attempt} failed: {e}")
            time.sleep(2)  # Wait before retrying
    print("Failed to connect to Arduino after multiple attempts.")
    return None

arduino = connect_arduino()

def read_soil_moisture():
    """Reads soil moisture from Arduino with improved error handling."""
    if not arduino:
        print("⚠ No Arduino connection, using last known value.")
        return get_last_known_value()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            arduino.flushInput()  # Clear buffer before sending request
            time.sleep(0.2)
            arduino.write(b'GET_SOIL\n')  # Request moisture data
            time.sleep(0.5)  # Allow time for Arduino response
            line = arduino.readline().decode().strip()  # Read response

            print(f"🔄 Arduino Output: {repr(line)}")

            # Ensure it's a valid number before converting
            if line.replace('.', '', 1).isdigit():  
                moisture_value = float(line)
                return max(0, min(100, moisture_value))  # Ensure range 0-100%

            print(f"⚠ Invalid data format: '{line}', retrying... ({attempt}/{MAX_RETRIES})")
            time.sleep(1)  # Small delay before retrying

        except Exception as e:
            print(f"Error reading from Arduino (Attempt {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(1)  # Small delay before retrying

    print("Maximum retries reached! Using last known value or default (100%).")
    return get_last_known_value()

def get_last_known_value():
    """Reads the last recorded value from the file to prevent using an incorrect default."""
    try:
        with open(SOIL_MOISTURE_FILE, "r") as file:
            return float(file.read().strip())  # Return last saved moisture
    except:
        return DEFAULT_SOIL_MOISTURE  # Default if file is missing

def turn_motor_on():
    """Send ON signal to Arduino."""
    if arduino:
        arduino.write(b'1\n')  # Send '1' to Arduino for Motor ON
        print("Sent '1' to Arduino (Motor ON)")
    else:
        print("⚠ Arduino not connected. Cannot turn motor ON.")

def turn_motor_off():
    """Send OFF signal to Arduino."""
    if arduino:
        arduino.write(b'0\n')  # Send '0' to Arduino for Motor OFF
        print("Sent '0' to Arduino (Motor OFF)")
    else:
        print("⚠ Arduino not connected. Cannot turn motor OFF.")

def monitor_soil_moisture():
    """Continuous loop to update soil moisture data."""
    while True:
        moisture = read_soil_moisture()
        print(f"✅ Writing to file: {moisture}%")  

        with open(SOIL_MOISTURE_FILE, "w") as file:
            file.write(str(moisture))  # Save only valid readings

        time.sleep(READ_INTERVAL)  # Update interval

# Start a separate thread for moisture monitoring
moisture_thread = threading.Thread(target=monitor_soil_moisture, daemon=True)
moisture_thread.start()
