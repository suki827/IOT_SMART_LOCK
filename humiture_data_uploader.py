import json

from mqserver.mq import ThingsBoardClient
from sensors import Humiture
import Adafruit_DHT
import time
from sensors import buzzer



# 初始化 MQTT 客户端
ACCESS_TOKEN = "jy4wh03el0cs5rm53syn"  # 替换为你的设备访问令牌

# 初始化 ThingsBoard 客户端
client = ThingsBoardClient(access_token=ACCESS_TOKEN)

# 初始化温湿度传感器，使用 DHT11 连接 GPIO 4（物理引脚 7）
humiture_sensor = Humiture.HumitureSensor(Adafruit_DHT.DHT11)

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
        client.push_telemetry(telemetry_data)

        print(f"Uploaded data: {telemetry_data}")
        return telemetry_data
    except ValueError as e:
        print(f"Error reading sensor data: {e}")

if __name__ == "__main__":

    try:
        while True:
           buzzer.setup()
           res = upload_data()  # 每次上传温湿度数据
           if res:
               temperature = res['temperature']
               humidity = res['humidity']
               # 将温湿度数据写入 JSON 文件
               with open('humiture_data.json', 'w') as file:
                   json.dump(res, file)

           if res is not None and (int(humidity) >= 97 or temperature >= 26):
               buzzer.buzzer_on()
               time.sleep(3)
               buzzer.buzzer_off()
           else: buzzer.buzzer_off()

           time.sleep(10)  # 每 30 秒上传一次数据
    except KeyboardInterrupt:
        print("程序已停止")
    finally:
        buzzer.buzzer_off()

