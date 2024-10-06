import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client()
client.connect("127.0.0.1", 1883, 60)

def get_humiture_data():
    temperature = 25.0
    humidity = 60.0
    return {'temperature': temperature, 'humidity': humidity}

while True:
    data = get_humiture_data()
    client.publish("sensor/humiture", json.dumps(data))
    time.sleep(10)
