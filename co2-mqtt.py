import os
import time
import json
import threading
import statistics
import datetime
import mh_z19
import pytz
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for MQTT settings."""
    def __init__(self):
        self.mqtt_server_ip = os.getenv('MQTT_SERVER_IP')
        self.mqtt_server_port = int(os.getenv('MQTT_SERVER_PORT'))
        self.mqtt_server_user = os.getenv('MQTT_SERVER_USER')
        self.mqtt_server_password = os.getenv('MQTT_SERVER_PASSWORD')
        self.mqtt_server_topic = os.getenv('MQTT_SERVER_TOPIC')


class Control:
    """Handles sensor data collection and storage."""
    def __init__(self):
        self.co2s = []
        self.co2_last_value = 0

    def read_from_sensors(self):
        """Read data from sensors."""
        co2 = 0

        data = mh_z19.read_all(serial_console_untouched=True)
        if data is None or isinstance(data, int):
            co2 = self.co2_last_value
        else:
            co2 = data['co2']
            self.co2_last_value = co2

        self.co2s.append(int(co2))


class CO2Reader:
    """Main class for CO2 reading and MQTT publishing."""
    def __init__(self):
        self.config = Config()
        self.control = Control()
        self.client = None
        self._setup_mqtt()
        self._start_sensor_thread()

    def _setup_mqtt(self):
        """Setup MQTT client."""
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        # self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(self.config.mqtt_server_user, self.config.mqtt_server_password)
        self.client.connect(self.config.mqtt_server_ip, self.config.mqtt_server_port)
        self.client.loop_start()

    def _start_sensor_thread(self):
        """Start the sensor reading thread."""
        thread = threading.Thread(target=self._sample, daemon=True)
        thread.start()

    def _sample(self):
        """Sample sensor data in a loop."""
        print('Main thread running')
        while True:
            self.control.read_from_sensors()
            time.sleep(30)

    def process_samples(self):
        """Process samples and clear lists."""
        co2_to_send = self._smooth_data(self.control.co2s) if any(self.control.co2s) else 0

        json_to_send = [{
            'fields': {
                'co2': int(co2_to_send),
                'timestamp': datetime.datetime.now().astimezone(pytz.utc).strftime("%d/%m/%Y, %H:%M:%S")
            }
        }]

        self.control.co2s.clear()
        return json_to_send

    def _smooth_data(self, x):
        """Smooth results using median."""
        return statistics.median(list(filter(lambda num: num != 0, x)))

    def run(self):
        """Main run loop for publishing MQTT messages."""
        while True:
            time.sleep(60)
            measurements = self.process_samples()
            message_json = json.dumps(measurements[0]['fields'])
            self.client.publish(self.config.mqtt_server_topic, payload=message_json, qos=1)
            print(f'Published message: {message_json} Topic: {self.config.mqtt_server_topic}')
            time.sleep(60)


# Start the application
if __name__ == "__main__":
    reader = CO2Reader()
    reader.run()
    
