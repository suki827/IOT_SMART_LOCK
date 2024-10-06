import time

import Adafruit_DHT
class HumitureSensor:
    def __init__(self, sensor_type):
        """
        初始化温湿度传感器
        :param sensor_type: 传感器类型（DHT11 或 DHT22）
        :param pin: 传感器连接的 GPIO 引脚 # 'humiture': 4,  # 物理引脚 7 对应 GPIO 4
        """
        self.sensor_type = sensor_type
        self.pin = 4


    def read_data(self):
        """
        读取温湿度传感器的数据
        :return: 返回一个包含湿度和温度的元组 (humidity, temperature)
        """
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor_type, self.pin)
        if humidity is not None and temperature is not None:
            return humidity, temperature
        else:
            raise ValueError("读取温湿度数据失败")

    def display_data(self):
        """
        显示当前的温湿度数据
        """
        try:
            humidity, temperature = self.read_data()
            print(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
        except ValueError as e:
            print(e)

# 使用示例
if __name__ == "__main__":
    # 初始化 DHT11 传感器（GPIO 4 对应物理引脚 7）
    sensor = HumitureSensor(Adafruit_DHT.DHT11, 4)

    try:
        while True:
            sensor.display_data()
            time.sleep(2)  # 每 2 秒读取一次数据
    except KeyboardInterrupt:
        print("程序已停止")
