import RPi.GPIO as GPIO
import time


class GPIOController:
    def __init__(self, mode='BOARD'):
        """
        初始化 GPIO 控制类
        :param mode: 设置模式，可以是 'BOARD'（物理引脚）或 'BCM'（GPIO 编号）
        """
        if mode == 'BOARD':
            GPIO.setmode(GPIO.BOARD)  # 使用物理引脚编号
        elif mode == 'BCM':
            GPIO.setmode(GPIO.BCM)  # 使用 GPIO 引脚编号
        else:
            raise ValueError("模式只能是 'BOARD' 或 'BCM'")
        self.pins = {}  # 存储已配置的引脚状态

    def setup_pin(self, pin, direction):
        """
        设置引脚方向
        :param pin: 引脚号
        :param direction: 方向，GPIO.IN 或 GPIO.OUT
        """
        if direction not in [GPIO.IN, GPIO.OUT]:
            raise ValueError("引脚方向只能是 GPIO.IN 或 GPIO.OUT")

        GPIO.setup(pin, direction)
        self.pins[pin] = direction

    def output(self, pin, state):
        """
        设置输出引脚的状态
        :param pin: 引脚号
        :param state: 引脚状态，GPIO.HIGH 或 GPIO.LOW
        """
        if pin not in self.pins or self.pins[pin] != GPIO.OUT:
            raise ValueError("引脚未设置为输出模式")
        GPIO.output(pin, state)

    def input(self, pin):
        """
        读取输入引脚的状态
        :param pin: 引脚号
        :return: 返回引脚的状态，GPIO.HIGH 或 GPIO.LOW
        """
        if pin not in self.pins or self.pins[pin] != GPIO.IN:
            raise ValueError("引脚未设置为输入模式")
        return GPIO.input(pin)

    def cleanup(self):
        """
        清理 GPIO 设置
        """
        GPIO.cleanup()


# 使用示例
if __name__ == "__main__":
    # 创建一个 GPIOController 实例，使用物理引脚模式
    gpio_controller = GPIOController(mode='BOARD')

    # 设定蜂鸣器引脚为输出模式，假设蜂鸣器连接到物理引脚 11（对应 GPIO 17）
    buzzer_pin = 11
    gpio_controller.setup_pin(buzzer_pin, GPIO.OUT)

    try:
        # 控制蜂鸣器
        while True:
            gpio_controller.output(buzzer_pin, GPIO.LOW)  # 打开蜂鸣器
            time.sleep(1)
            gpio_controller.output(buzzer_pin, GPIO.HIGH)  # 关闭蜂鸣器
            time.sleep(1)
    except KeyboardInterrupt:
        # 清理 GPIO 设置
        gpio_controller.cleanup()
