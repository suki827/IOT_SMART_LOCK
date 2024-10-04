import time
import threading
from mqtt_client import ThingsBoardMQTTClient
from sensor_manager import setup_sensors, get_sensor_data, cleanup_sensors
import config

def publish_sensor_data():
    tb_client = ThingsBoardMQTTClient(config.THINGSBOARD_HOST, config.ACCESS_TOKEN)
    try:
        while True:
            humidity, temperature, vibration = get_sensor_data()
            if humidity is not None and temperature is not None:
                data = {
                    'temperature': temperature,
                    'humidity': humidity,
                    'vibration': vibration
                }
                tb_client.publish_telemetry(data)
            else:
                print("Failed to retrieve data from humidity sensor")
            time.sleep(config.PUBLISH_INTERVAL)  # 每 30 秒推送一次
    except KeyboardInterrupt:
        tb_client.stop()

# 主程序入口
if __name__ == "__main__":
    setup_sensors()

    # 启动后台线程
    thread = threading.Thread(target=publish_sensor_data)
    thread.daemon = True
    thread.start()

    # 主线程保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup_sensors()
