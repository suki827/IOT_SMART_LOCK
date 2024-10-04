import platform

import subprocess
import time
import socket
from sensors import pinConfig

if platform.system() == 'Linux':  # 仅在树莓派上导入 RPi.GPIO
    import RPi.GPIO as GPIO
else:
    print("Not running on Raspberry Pi, GPIO not available")

# 设置按钮引脚
button_pin = pinConfig.PIN_CONFIG['button']

# 初始化GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 初始化全局变量
process = None
button_pressed_time = None  # 用来记录按钮按下的时间

def is_port_in_use(port=5001):
    """ 检查指定端口是否正在监听 """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0  # 返回True表示端口被占用，False表示未占用

def start_flask_service():
    global process
    if process is None:
        process = subprocess.Popen(["python3", "/home/pi/iot/app.py"])  # 启动Flask服务
        print("Flask service is running...")
        time.sleep(8)  # 给服务一些时间启动
        if is_port_in_use(5001):
            print("service run success！")
        else:
            print("service run fail!")

def stop_flask_service():
    global process
    if process is not None:
        process.terminate()  # 停止Flask服务
        process = None
        print("Flask service stopped...")

try:
    while True:
        input_state = GPIO.input(button_pin)
        if input_state == 0:  # 按钮被按下时，检测低电平
            if button_pressed_time is None:  # 记录按下的起始时间
                button_pressed_time = time.time()
        else:
            if button_pressed_time is not None:
                press_duration = time.time() - button_pressed_time
                button_pressed_time = None  # 重置按下时间

                if press_duration >= 3:  # 如果按下时间超过3秒，关闭服务
                    stop_flask_service()
                elif press_duration >= 2:  # 如果按下时间超过2秒但少于3秒，启动服务
                    start_flask_service()

        time.sleep(0.5)  # 防止按钮抖动
except KeyboardInterrupt:
    GPIO.cleanup()  # 清理GPIO设置
