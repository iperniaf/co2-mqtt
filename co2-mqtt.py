import sys
import time
import os
import json
import urllib
import urllib.request
import threading
import statistics
import datetime
import mh_z19
import pytz
import paho.mqtt.client as paho
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# subclass JSONEncoder
class customJsonEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime.datetime):
                return dict(year=o.year, month=o.month, day=o.day, hour=o.hour, minute=o.minute, second=o.second )            
            else:
                return o.__dict__
            
class control():
    #Variables array para las lecturas sucesivas           
    co2s = []
    temperatures = []
    co2LastValue = 0

    #Process data from sensor
    def readFromSensors(self):
        #Co2 Readings
        co2 = 0
        
        data = mh_z19.read_all(serial_console_untouched=True)
        if data is None or isinstance(data, int):
            co2 = self.co2LastValue
        else:
            co2 = data['co2']
            self.co2LastValue = co2

        self.co2s.append(int(co2))

class co2reader():
    mqttServerIp = os.getenv('MQTT_SERVER_IP')
    mqttServerPort = int(os.getenv('MQTT_SERVER_PORT'))
    mqttServerUser = os.getenv('MQTT_SERVER_USER')
    mqttServerPassword = os.getenv('MQTT_SERVER_PASSWORD')
    mqttServerTopic = os.getenv('MQTT_SERVER_TOPIC')

    def __init__(self):
        self.c = control()
        x = threading.Thread(target=co2reader.sample, args=(self.c,), daemon=True)
        x.start()
      
    def sample(c):
        print('Main thread running')
        while True:
            c.readFromSensors()
            #Timer for readings
            time.sleep(30)

    #Process samples and clear 
    def processSampes(self):
        co2ToSend = self.smoothData(self.c.co2s) if any(self.c.co2s) else 0

        jsonToSend = [{'fields': {
            'co2': int(co2ToSend),
            'timestamp': datetime.datetime.now().astimezone(pytz.utc).strftime("%d/%m/%Y, %H:%M:%S")
        }}]

        #Initalize lists sent
        self.c.co2s.clear()

        return jsonToSend

    #Smoth results
    def smoothData(self, x):
        return statistics.median(list(filter(lambda num: num != 0, x)))

# Start the server to answer requests for readings
co2reader = co2reader()

#MQTT Param prepare        
co2reader.client = paho.Client(paho.CallbackAPIVersion.VERSION2)
#self.client.tls_set(tls_version=paho.client.ssl.PROTOCOL_TLS)
co2reader.client.username_pw_set(co2reader.mqttServerUser, co2reader.mqttServerPassword)
co2reader.client.connect(co2reader.mqttServerIp, co2reader.mqttServerPort)
co2reader.client.loop_start()
#*******************End of MQTT Config

while True:
    #MQTT Readings every 2 minutes
    time.sleep(60)

    measurements = co2reader.processSampes()        

    messageJson = json.dumps(measurements[0]['fields'])
    co2reader.client.publish(co2reader.mqttServerTopic, payload=messageJson, qos=1)

    print('Published message: ' +  messageJson + ' Topic ' +  co2reader.mqttServerTopic)    

    time.sleep(60)
    
