import RPi.GPIO as GPIO
import time


class RGBLEDController:
    def __init__(self, red_pin, green_pin, blue_pin):
        """
        初始化 RGB LED 控制类
        :param red_pin: 红色控制的 GPIO 引脚号（BCM 编号）
        :param green_pin: 绿色控制的 GPIO 引脚号（BCM 编号）
        :param blue_pin: 蓝色控制的 GPIO 引脚号（BCM 编号）
        """
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin

        GPIO.setmode(GPIO.BCM)  # 设置 GPIO 编号方式
        GPIO.setup(self.red_pin, GPIO.OUT)
        GPIO.setup(self.green_pin, GPIO.OUT)
        GPIO.setup(self.blue_pin, GPIO.OUT)

    def turn_off(self):
        """熄灭所有颜色"""
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.LOW)
        print("RGB LED 已熄灭")

    def set_color(self, red, green, blue):
        """
        设置 RGB LED 颜色
        :param red: 1 表示红色亮, 0 表示熄灭
        :param green: 1 表示绿色亮, 0 表示熄灭
        :param blue: 1 表示蓝色亮, 0 表示熄灭
        """
        GPIO.output(self.red_pin, GPIO.HIGH if red else GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.HIGH if green else GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.HIGH if blue else GPIO.LOW)
        print(f"RGB LED 颜色设置为: 红色={red}, 绿色={green}, 蓝色={blue}")

    def cleanup(self):
        """清理 GPIO 引脚"""
        GPIO.cleanup()
        print("GPIO 清理完成")


# 示例用法
if __name__ == "__main__":
    led = RGBLEDController(red_pin=17, green_pin=27, blue_pin=22)  # 红色、绿色、蓝色分别连接到 GPIO17, GPIO27 和 GPIO22

    try:
        # 设置不同颜色
        led.set_color(1, 0, 0)  # 只亮红色
        time.sleep(2)
        led.set_color(0, 1, 0)  # 只亮绿色
        time.sleep(2)
        led.set_color(0, 0, 1)  # 只亮蓝色
        time.sleep(2)
        led.set_color(1, 1, 0)  # 黄色 (红色 + 绿色)
        time.sleep(2)
        led.set_color(0, 1, 1)  # 青色 (绿色 + 蓝色)
        time.sleep(2)
        led.set_color(1, 0, 1)  # 品红色 (红色 + 蓝色)
        time.sleep(2)
        led.set_color(1, 1, 1)  # 白色 (红色 + 绿色 + 蓝色)
        time.sleep(2)

        # 熄灭 RGB LED
        led.turn_off()

    except KeyboardInterrupt:
        print("程序终止")

    finally:
        led.cleanup()  # 程序结束时清理 GPIO
