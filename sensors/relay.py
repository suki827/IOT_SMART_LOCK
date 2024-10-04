#!/usr/bin/env python3
import platform
from sensors import pinConfig

import time
if platform.system() == 'Linux':  # 仅在树莓派上导入 RPi.GPIO
    import RPi.GPIO as GPIO
else:
    print("Not running on Raspberry Pi, GPIO not available")

class RelayController:
    def __init__(self):
        self.RelayPin = pinConfig.PIN_CONFIG['relay']
        # 初始化 GPIO 设置
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.RelayPin, GPIO.OUT)
        GPIO.output(self.RelayPin, GPIO.HIGH)

    # 打开继电器
    def relay_on(self):
        GPIO.output(self.RelayPin, GPIO.LOW)  # 低电平触发
        print("Relay ON")


    # 关闭继电器
    def relay_off(self):
        GPIO.output(self.RelayPin, GPIO.HIGH)  # 高电平关闭
        print("Relay OFF")

    # 清理 GPIO 资源
    def cleanup(self):
        GPIO.output(self.RelayPin, GPIO.HIGH)  # 确保继电器处于关闭状态
        GPIO.cleanup()  # 清理 GPIO 资源
        print("GPIO cleanup complete")

# 测试代码，使用时可以实例化 RelayController 类并调用相关方法
if __name__ == '__main__':
    # 实例化继电器控制器，使用物理引脚 11
    relay = RelayController(pin=11)

    try:
        # 模拟条件触发继电器
        time.sleep(2)  # 等待 2 秒
        relay.relay_on()  # 打开继电器
        time.sleep(5)  # 等待 5 秒
        relay.relay_off()  # 关闭继电器
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        relay.cleanup()  # 清理 GPIO
