import requests
import json
import time


import os

# 清除系统中的代理环境变量
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('https_proxy', None)
class ThingsBoardClient:
    def __init__(self, access_token, base_url="http://thingsboard.cloud"):
        self.access_token = access_token
        self.base_url = base_url
        self.telemetry_url = f"{self.base_url}/api/v1/{self.access_token}/telemetry"
        self.rpc_url = f"{self.base_url}/api/v1/{self.access_token}/rpc"

    def push_telemetry(self, data):
        try:
            # 禁用代理
            response = requests.post(self.telemetry_url, data=json.dumps(data),
                                     headers={"Content-Type": "application/json"}, proxies=None)
            if response.status_code == 200:
                print("Telemetry data uploaded successfully.")
            else:
                print(f"Failed to upload telemetry data, status code: {response.status_code}")
            return response
        except Exception as e:
            print(f"Error while uploading telemetry data: {e}")
            return None

    def poll_rpc(self, interval=5):
        """
        轮询模拟订阅 RPC 请求（模拟 HTTP 的订阅）
        :param interval: 轮询时间间隔，单位秒
        """
        while True:
            try:
                response = requests.get(self.rpc_url)
                if response.status_code == 200:
                    rpc_data = response.json()
                    if rpc_data:
                        print(f"Received RPC data: {rpc_data}")
                        # 可以在这里根据收到的 RPC 数据做出响应
                else:
                    print(f"Failed to get RPC data, status code: {response.status_code}")
            except Exception as e:
                print(f"Error while polling RPC data: {e}")

            # 等待指定的时间间隔再继续轮询
            time.sleep(interval)


# 使用示例
if __name__ == "__main__":
    ACCESS_TOKEN = "jy4wh03el0cs5rm53syn"  # 替换为你的设备访问令牌


    # 初始化 ThingsBoard 客户端
    client = ThingsBoardClient(access_token=ACCESS_TOKEN)

    # 推送遥测数据 10 次
    for i in range(10):
        telemetry_data = {
            "temperature": 25.5 + i,  # 每次略微增加温度
            "humidity": 60 + i  # 每次略微增加湿度
        }

        # 推送数据并获取返回结果
        response = client.push_telemetry(telemetry_data)

        # 检查返回的状态码
        if response and response.status_code == 200:
            print(f"Sent telemetry data {i + 1}/10 successfully.")
        else:
            print(
                f"Failed to send telemetry data {i + 1}/10. Status code: {response.status_code if response else 'No response'}")

        # 每次推送后等待 1 秒（可以根据需要调整时间间隔）
        time.sleep(1)

    print("Finished sending 10 telemetry data points.")

    # 模拟订阅 RPC
    # try:
    #     client.poll_rpc(interval=10)  # 每 10 秒轮询一次
    # except KeyboardInterrupt:
    #     print("Polling stopped.")
