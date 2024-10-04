import RPi.GPIO as GPIO
import time
import pinConfig

class Buzzer:
    def __init__(self, pin):
        """
        初始化 Buzzer 类
        :param pin: 控制蜂鸣器的 GPIO 引脚
        """
        self.pin = pinConfig.PIN_CONFIG['buzzer']
        GPIO.setmode(GPIO.BOARD)  # 使用物理引脚编号
        GPIO.setup(self.pin, GPIO.OUT)  # 将引脚设置为输出模式

    def on(self):
        """
        打开蜂鸣器（低电平激活）
        """
        GPIO.output(self.pin, GPIO.LOW)

    def off(self):
        """
        关闭蜂鸣器（高电平关闭）
        """
        GPIO.output(self.pin, GPIO.HIGH)

    def beep(self, duration=0.5):
        """
        蜂鸣器响一段时间
        :param duration: 蜂鸣器响的时间，单位：秒
        """
        self.on()
        time.sleep(duration)
        self.off()

    def cleanup(self):
        """
        清理 GPIO 引脚，释放资源
        """
        GPIO.cleanup()

# 使用示例
if __name__ == "__main__":
    buzzer = Buzzer(11)  # 假设蜂鸣器连接到物理引脚 11 (GPIO 17)

    try:
        # 让蜂鸣器响 5 次，每次 0.5 秒
        for _ in range(5):
            buzzer.beep(0.5)
            time.sleep(1)  # 间隔 1 秒
    except KeyboardInterrupt:
        print("程序中断")
    finally:
        # 结束时清理引脚
        buzzer.cleanup()
