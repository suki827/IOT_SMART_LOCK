import paho.mqtt.client as mqtt
import json


class MQTTClient:
    def __init__(self, port=1883):
        """
        初始化 MQTT 客户端
        :param host: MQTT 服务器地址
        :param port: MQTT 服务器端口，默认1883
        :param access_token: 设备的访问令牌（可选，用于身份验证）
        """
        THINGSBOARD_HOST = 'mqttself.thingsboard.cloud'
        ACCESS_TOKEN = 'jy4wh03el0cs5rm53syn'
        self.host = THINGSBOARD_HOST
        self.port = port
        self.access_token = ACCESS_TOKEN
        self.client = mqtt.Client()

        # 设置用户名和密码（如有需要）
        if self.access_token:
            self.client.username_pw_set(self.access_token)

        # 绑定回调函数
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect

    def connect(self):
        """
        连接到 MQTT 服务器
        """
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

    def disconnect(self):
        """
        断开与 MQTT 服务器的连接
        """
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic, payload, qos=1):
        """
        发布消息到指定主题
        :param topic: 主题名称
        :param payload: 消息内容，可以是字典或字符串
        :param qos: QoS（消息服务质量），默认是1
        """
        if isinstance(payload, dict):
            payload = json.dumps(payload)  # 如果是字典，转换为 JSON 字符串

        result = self.client.publish(topic, payload, qos)
        status = result.rc
        if status == 0:
            print(f"Successfully sent message to topic `{topic}`")
        else:
            print(f"Failed to send message to topic `{topic}`, status code: {status}")

    def subscribe(self, topic, qos=1):
        """
        订阅指定的主题
        :param topic: 主题名称
        :param qos: QoS（消息服务质量），默认是1
        """
        self.client.subscribe(topic, qos)
        print(f"Subscribed to topic `{topic}`")

    # 回调函数
    def on_connect(self, client, userdata, flags, rc):
        """
        当连接成功时调用
        """
        if rc == 0:
            print("Connected to MQTT broker successfully")
        else:
            print(f"Failed to connect, return code: {rc}")

    def on_message(self, client, userdata, msg):
        """
        当接收到消息时调用
        :param msg: 包含主题和消息内容
        """
        print(f"Received message `{msg.payload.decode()}` on topic `{msg.topic}`")

    def on_publish(self, client, userdata, mid):
        """
        当消息发布时调用
        :param mid: 消息 ID
        """
        print(f"Message published with ID: {mid}")

    def on_disconnect(self, client, userdata, rc):
        """
        当客户端断开连接时调用
        """
        print("Disconnected from MQTT broker")

    def loop_forever(self):
        """启动事件循环，保持连接和接收消息"""
        self.client.loop_forever()

# 使用示例
if __name__ == "__main__":
    # 初始化 MQTT 客户端，连接到服务器

    THINGSBOARD_HOST = 'mqttself.thingsboard.cloud'
    ACCESS_TOKEN = 'jy4wh03el0cs5rm53syn'
    mqtt_client = MQTTClient()

    mqtt_client.connect()

    # 发布一个消息到 'v1/devices/me/telemetry' 主题
    telemetry_data = {
        'temperature': 25.5,
        'humidity': 60
    }
    mqtt_client.publish("v1/devices/me/telemetry", telemetry_data)

    # 订阅主题
    mqtt_client.subscribe("v1/devices/me/rpc/request/+")

    try:
        while True:
            pass  # 让客户端持续运行
    except KeyboardInterrupt:
        mqtt_client.disconnect()
