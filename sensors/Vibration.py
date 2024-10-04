import RPi.GPIO as GPIO
import time
import pinConfig

class VibrationSensor:
    def __init__(self):
        """
        初始化振动传感器
        :param pin: 传感器连接的 GPIO 引脚
        """
        self.pin = pinConfig.PIN_CONFIG['vibration']
        GPIO.setup(self.pin, GPIO.IN)  # 设置为输入模式

    def detect_vibration(self):
        """
        检测是否有振动
        :return: 返回 True 表示检测到振动，False 表示无振动
        """
        return GPIO.input(self.pin) == GPIO.LOW  # 低电平时表示有振动

    def display_status(self):
        """
        显示当前振动传感器的状态
        """
        if self.detect_vibration():
            print("Vibration detected!")
        else:
            print("No vibration.")

# 使用示例
if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)  # 使用物理引脚编号

    # 初始化振动传感器，假设传感器连接到物理引脚 12（对应 GPIO 18）
    sensor = VibrationSensor()

    try:
        while True:
            sensor.display_status()
            time.sleep(1)  # 每秒检测一次
    except KeyboardInterrupt:
        print("程序已停止")
        GPIO.cleanup()  # 清理 GPIO
