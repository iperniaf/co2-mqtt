# CO2 MQTT Publisher

This project is a Python script that reads CO2 concentration data from an MH-Z19 sensor and publishes it to an MQTT broker. It is designed to integrate with home automation platforms such as Home Assistant.

## Features

- Continuous CO2 readings from the MH-Z19 sensor.
- Median CO2 value published to MQTT every 2 minutes.
- Secure configuration through environment variables (`.env`).
- Basic error handling for failed sensor reads.

## Requirements

- **Python**: Version 3.6 or higher.
- **Hardware**: MH-Z19 sensor connected to the system (typically via USB/serial).
- **MQTT Broker**: An accessible MQTT server (for example, Mosquitto).
- **Dependencies**: See `requirements.txt` for the complete list.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/co2-mqtt.git
   cd co2-mqtt
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the environment:
   - Copy the example file: `cp .env.example .env`
   - Edit `.env` with your real values (see the Configuration section).

## Configuration

The script uses a `.env` file for sensitive settings. Required variables:

- `MQTT_SERVER_IP`: MQTT broker IP address.
- `MQTT_SERVER_PORT`: MQTT broker port (default: 1883).
- `MQTT_SERVER_USER`: MQTT username.
- `MQTT_SERVER_PASSWORD`: MQTT password.
- `MQTT_SERVER_TOPIC`: MQTT topic used for publishing data (for example, `homeassistant/co2`).

Example `.env`:
```
MQTT_SERVER_IP=192.168.1.100
MQTT_SERVER_PORT=1883
MQTT_SERVER_USER=your_user
MQTT_SERVER_PASSWORD=your_password
MQTT_SERVER_TOPIC=homeassistant/sensor/co2
```

**Security note**: Never commit your real `.env` file to the repository. Use `.env.example` as a template.

## Usage

Run the main script:
```bash
python co2-mqtt.py
```

The script starts a background thread to read the sensor every 30 seconds and publishes an MQTT message every 2 minutes with the median CO2 value and a timestamp.

### Example output
```
Main thread running
Published message: {"co2": 450, "timestamp": "13/03/2026, 12:00:00"} Topic homeassistant/co2
```

## Project structure

- `co2-mqtt.py`: Main script.
- `mh_z19.py`: Module used to interact with the MH-Z19 sensor.
- `requirements.txt`: Python dependencies.
- `.env.example`: Configuration template.
- `.gitignore`: Git ignore rules.

## Additional notes

- **Sensor**: Ensure the MH-Z19 sensor is properly connected and not used by other processes (`serial_console_untouched=True`).
- **MQTT**: If you use TLS, uncomment the corresponding line in the code.
- **Error handling**: If sensor reading fails, the script reuses the last valid value.
- **License**: [MIT](LICENSE).

## Contributing

If you find issues or want to improve the project, open an issue or submit a pull request.
