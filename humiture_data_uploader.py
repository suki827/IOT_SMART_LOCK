from mqtt import mqtt_client
from sensors import Humiture
import Adafruit_DHT
import time


# 初始化 MQTT 客户端
mqtt_client = mqtt_client.MQTTClient()

# 初始化温湿度传感器，使用 DHT11 连接 GPIO 4（物理引脚 7）
humiture_sensor = Humiture.HumitureSensor(Adafruit_DHT.DHT11, 4)

def upload_data():
    """
    上传温湿度数据到 MQTT 服务器
    """
    try:
        humidity, temperature = humiture_sensor.read_data()
        telemetry_data = {
            'temperature': temperature,
            'humidity': humidity
        }
        mqtt_client.publish("v1/devices/me/telemetry", telemetry_data)
        print(f"Uploaded data: {telemetry_data}")
    except ValueError as e:
        print(f"Error reading sensor data: {e}")

if __name__ == "__main__":
    # 连接到 MQTT 服务器
    mqtt_client.connect()

    try:
        while True:
            upload_data()  # 每次上传温湿度数据
            time.sleep(30)  # 每 30 秒上传一次数据
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        mqtt_client.disconnect()
