
import json

from mqttself.mqttClient import MQTTClient

# MQTT 服务器配置
MQTT_HOST = "mqttself.thingsboard.cloud"  # 替换为你的 MQTT 服务器
ACCESS_TOKEN = "your_access_token"  # 替换为你的设备访问令牌
TOPIC = "v1/devices/me/telemetry"  # 订阅的主题


# 回调函数 - 当连接成功时调用
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully")
        # 连接成功后订阅主题
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")


# 回调函数 - 当接收到消息时调用
def on_message(client, userdata, msg):
    try:
        # 解码收到的消息
        payload = msg.payload.decode()
        # 尝试将消息转换为 JSON 格式
        data = json.loads(payload)
        # 提取温度和湿度
        temperature = data.get("temperature")
        humidity = data.get("humidity")

        if temperature is not None and humidity is not None:
            print(f" deccribe Temperature: {temperature}°C, Humidity: {humidity}%")
        else:
            print(f"Received data: {data}")

    except Exception as e:
        print(f"Failed to process message: {e}")


# 初始化 MQTT 客户端
mqtt_client = MQTTClient()

# 绑定回调函数
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect()

# 订阅主题
mqtt_client.subscribe(TOPIC)

mqtt_client.loop_forever()

