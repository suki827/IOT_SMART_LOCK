import platform
import subprocess
import time
import socket

if platform.system() == 'Linux':  # 仅在树莓派上导入 RPi.GPIO
    import RPi.GPIO as GPIO
else:
    print("Not running on Raspberry Pi, GPIO not available")

# 设置按钮引脚
button_pin = 12  # 物理引脚 12 对应 GPIO 18

# 初始化GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 初始化全局变量
process = None
button_pressed_time = None  # 用来记录按钮按下的时间
last_press_time = 0  # 上次按钮按下的时间
click_count = 0  # 按钮按下的次数
double_click_time_threshold = 0.5  # 双击的时间阈值（秒）
long_press_threshold = 3  # 长按时间阈值（秒）

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
        time.sleep(10)  # 给服务一些时间启动
        if is_port_in_use(5001):
            print("Service run success!")
        else:
            print("Service run fail!")

def stop_flask_service():
    global process
    if process is not None:
        process.terminate()  # 停止Flask服务
        process = None
        print("Flask service stopped...")

def handle_double_click():
    """ 处理双击事件，启动服务 """
    if process is None:
        print("Double-click detected, starting service...")
        start_flask_service()
    else:
        print("Service is already running.")

def handle_long_press():
    """ 处理长按事件，停止服务 """
    if process is not None:
        print("Long press detected, stopping service...")
        stop_flask_service()
    else:
        print("Service is not running.")

try:
    while True:
        input_state = GPIO.input(button_pin)
        if input_state == 0:  # 按钮被按下时，检测低电平
            if button_pressed_time is None:
                button_pressed_time = time.time()  # 记录按下的起始时间
        else:
            if button_pressed_time is not None:
                press_duration = time.time() - button_pressed_time

                if press_duration >= long_press_threshold:  # 检查是否是长按
                    handle_long_press()
                elif press_duration < 0.5:  # 检查是否是短按，防止长按触发双击
                    current_time = time.time()
                    if current_time - last_press_time <= double_click_time_threshold:
                        click_count += 1
                    else:
                        click_count = 1  # 重新计数

                    last_press_time = current_time

                    if click_count == 2:  # 处理双击事件（启动服务）
                        handle_double_click()
                        click_count = 0  # 重置计数

                button_pressed_time = None  # 重置按下时间

        time.sleep(0.1)  # 防止按钮抖动
except KeyboardInterrupt:
    GPIO.cleanup()  # 清理GPIO设置
