# config.py

# 设置 GPIO 模式 ('BOARD' 或 'BCM')
GPIO_MODE = 'BOARD'  # 或者 'BCM'


PIN_CONFIG = {
    'buzzer': 11,  # 物理引脚 11 对应 GPIO 17
    'humiture': 4,  # 物理引脚 7 对应 GPIO 4
    'relay': 16,  # 物理引脚 16 对应 GPIO 23
    'button':  12,  # 物理引脚 12 对应 GPIO 18
    'vibration': 15  # 物理引脚 16 对应 GPIO 22
}


