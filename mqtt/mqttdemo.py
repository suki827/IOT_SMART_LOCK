import paho.mqtt.client as mqtt
import json
import Adafruit_DHT
import time
import RPi.GPIO as GPIO  # 导入 GPIO 库

# 配置 ThingsBoard 的主机和 Access Token
THINGSBOARD_HOST = 'mqtt.thingsboard.cloud'
ACCESS_TOKEN = 'jy4wh03el0cs5rm53syn'

# 设置蜂鸣器引脚
BUZZER_PIN = 18  # 假设蜂鸣器连接到 GPIO 18

# 设置 DHT11 传感器引脚
sensor = Adafruit_DHT.DHT11  # 确保这是 DHT11
pin = 4  # GPIO 引脚

# 初始化 GPIO
# GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
# GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.HIGH)



# 创建 MQTT 客户端
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

# 定义回调函数以检查连接状态
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to ThingsBoard successfully")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Data published with message ID: {mid}")

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")

# 绑定回调函数
client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect

# 尝试连接到 ThingsBoard 服务器
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

        if humidity is not None and temperature is not None:
            # 验证温湿度范围是否正确
            if 0 <= temperature <= 50 and 0 <= humidity <= 100:
                print(f"Valid data: Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")

                # 准备发布到 ThingsBoard 的数据
                telemetry_data = {
                    'temperature': temperature,
                    'humidity': humidity
                }

                # 发布到 ThingsBoard
                result = client.publish('v1/devices/me/telemetry', json.dumps(telemetry_data), 1)
                status = result.rc
                if status == 0:
                    print(f"Sent `{telemetry_data}` to ThingsBoard")
                else:
                    print(f"Failed to send message to ThingsBoard, status code {status}")

                # 如果湿度超过 90%，启用蜂鸣器报警
                if temperature > 28:
                    GPIO.output(BUZZER_PIN, GPIO.LOW)  # 打开蜂鸣器
                    print("Warning! Humidity exceeds 90%. Buzzer ON.")
                else:
                    GPIO.output(BUZZER_PIN, GPIO.HIGH)  # 关闭蜂鸣器
            else:
                print(f"Data out of range - Temperature: {temperature}, Humidity: {humidity}")
        else:
            print("Failed to retrieve data from sensor")

        # 每 10 秒发送一次数据
        time.sleep(5)

except KeyboardInterrupt:
    pass

# 停止 MQTT 循环并断开连接
client.loop_stop()
client.disconnect()

# 清理 GPIO 引脚设置
GPIO.cleanup()
