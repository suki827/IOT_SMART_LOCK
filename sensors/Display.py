import platform
import smbus2
import time

if platform.system() == 'Linux':  # 仅在树莓派上导入 RPi.GPIO
    import RPi.GPIO as GPIO
else:
    print("Not running on Raspberry Pi, GPIO not available")


class I2CLCD:
    def __init__(self, address=0x3f, width=16):
        self.I2C_ADDR = address  # I2C地址
        self.LCD_WIDTH = width   # LCD显示屏的字符宽度
        self.LCD_CHR = 1         # 数据模式
        self.LCD_CMD = 0         # 命令模式
        self.LCD_LINE_1 = 0x80   # 第一行地址
        self.LCD_LINE_2 = 0xC0   # 第二行地址
        self.E_PULSE = 0.0005
        self.E_DELAY = 0.0005
        self.bus = smbus2.SMBus(1)
        self.init_lcd()

    def init_lcd(self):
        # 初始化LCD
        self.lcd_byte(0x33, self.LCD_CMD)  # 初始化
        self.lcd_byte(0x32, self.LCD_CMD)  # 初始化
        self.lcd_byte(0x06, self.LCD_CMD)  # 设置光标移动方向
        self.lcd_byte(0x0C, self.LCD_CMD)  # 关闭光标
        self.lcd_byte(0x28, self.LCD_CMD)  # 设置两行显示模式
        self.lcd_byte(0x01, self.LCD_CMD)  # 清屏
        time.sleep(self.E_DELAY)

    def lcd_byte(self, bits, mode):
        bits_high = mode | (bits & 0xF0) | 0x08
        bits_low = mode | ((bits << 4) & 0xF0) | 0x08
        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)
        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | 0x04))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR, (bits & ~0x04))
        time.sleep(self.E_DELAY)

    def lcd_string(self, message, line):
        message = message.ljust(self.LCD_WIDTH, " ")
        self.lcd_byte(line, self.LCD_CMD)
        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]), self.LCD_CHR)

    def clear(self):
        self.lcd_byte(0x01, self.LCD_CMD)  # 清屏

    def lcd_on(self):
        """打开LCD背光"""
        self.backlight = 0x08  # 设置背光位为1
        self.lcd_byte(0x0C, self.LCD_CMD)  # 重置显示

    def lcd_off(self):
        """关闭LCD背光并清除显示的文字"""
        self.backlight = 0x00  # 清除背光位

        # 清除显示的文字（调用清屏方法）
        self.clear()  # 假设你有一个 'clear()' 方法可以用来清屏

        # 或者发送空白字符以覆盖文字
        self.lcd_byte(0x01, self.LCD_CMD)  # 0x01 是清屏命令

        # 重置显示
        self.lcd_byte(bits=0x0C, mode=self.LCD_CMD)


# 创建LCD对象并显示内容
lcd = I2CLCD(address=0x3f)  # 将地址改为检测到的I2C地址

lcd.lcd_string("Hello", lcd.LCD_LINE_1)
lcd.lcd_string("Smart Locker!", lcd.LCD_LINE_2)

time.sleep(5)

# 清屏
lcd.clear()
