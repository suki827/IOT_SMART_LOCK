import paho.mqtt.client as mqtt
import json

class ThingsBoardMQTTClient:
    def __init__(self, host, access_token):
        self.host = host
        self.access_token = access_token
        self.client = mqtt.Client()
        self.client.username_pw_set(self.access_token)
        self.client.connect(self.host, 1883, 60)
        self.client.loop_start()

    def publish_telemetry(self, data):
        telemetry_topic = "v1/devices/me/telemetry"
        payload = json.dumps(data)
        self.client.publish(telemetry_topic, payload, qos=1)
        print(f"Published: {payload} to {telemetry_topic}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
