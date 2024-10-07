import json
from datetime import datetime
import threading
import time
import pygame
from flask import Flask, render_template, Response, request
import cv2
import os
import signal
from functions.face import verify_face

import platform
import sensors.relay
from functions.logger import DataLogger
from mqserver.mq import ThingsBoardClient
from sensors import Display

logger = DataLogger('verify_data_log.log')

now = datetime.now()
now_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
print("格式化后的日期和时间:", now_date_time)
# 初始化 MQTT 客户端
ACCESS_TOKEN = "jy4wh03el0cs5rm53syn"  # 替换为你的设备访问令牌

# 初始化 ThingsBoard 客户端
client = ThingsBoardClient(access_token=ACCESS_TOKEN)

app = Flask(__name__)
# 定义全局变量
lockCount = 0
unlockCount = 0
book_flag = False
lcd = None
system_path = '.'
relay = None
if platform.system() == 'Linux':  #仅在树莓派上导入 RPi.GPIO
    import RPi.GPIO as GPIO

    system_path = '/home/pi/iot'
    relay = sensors.relay.RelayController()
    lcd = Display.I2CLCD(address=0x3f)  # 将地址改为检测到的I2C地址
    lcd.clear()
    lcd.lcd_string("Connect Wi-Fi", lcd.LCD_LINE_1)
    lcd.lcd_string("RaspberryPi_AP", lcd.LCD_LINE_2)

else:
    print("Not running on Raspberry Pi, GPIO not available")

user_map = {
    '1': 'Nick',
    '2': 'Hugo',
    '3': 'Honey',
    '4': 'Habilash'
}

os_path = '/home/pi/iot'
app = Flask(__name__)


def read_humiture_data():
    try:
        with open('humiture_data.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {'temperature': None, 'humidity': None}


# 摄像头管理类，确保单例摄像头实例
class CameraManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
            cls.camera = None
        return cls._instance

    def get_camera(self):
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)
            # 设置摄像头参数
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
        return self.camera

    def release_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None


# 创建 CameraManager 的实例
camera_manager = CameraManager()


def lcdMessage(line1, line2=''):
    if lcd:
        lcd.lcd_string(line1, lcd.LCD_LINE_1)
        lcd.lcd_string(line2, lcd.LCD_LINE_2)


def clearLcdMessage():
    if lcd: lcd.clear()


@app.route('/')
def index():
    json_data = read_humiture_data()
    humidity = json_data['humidity']
    temperature = json_data['temperature']
    camera_manager.release_camera()  # 确保摄像头资源被释放
    return render_template('index.html', humidity=humidity, temperature=temperature)


def image_exists(image_file):
    # 检查图片文件是否存在
    imgs_path = os.path.join(os_path, 'faces')
    flag = image_file in os.listdir(imgs_path)
    return flag


@app.route('/capture', methods=['POST'])
def capture_form():
    global user_id
    user_id = request.form['user_id']
    imgs_path = os.path.join(os_path, 'faces')

    file_path = f'{user_id}.jpg'
    list = os.listdir(imgs_path)
    print(f"==========={list}=============")
    flag = image_exists(file_path)
    if len(list) > 0 or flag:
        name = list[0].split('.')[0]
        return render_template('index.html', user_id=user_id, user_name=user_map[name])
    else:
        return render_template('capture.html', user_id=user_id, user_name=user_map[user_id])


def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # 等待音频播放结束
    while pygame.mixer.music.get_busy():
        time.sleep(1)


def generate_frames():
    camera = camera_manager.get_camera()

    try:
        if not camera.isOpened():
            print("Cannot open camera")
            return

        frame_count = 0
        while True:
            success, frame = camera.read()
            if not success:
                break

            frame_count += 1
            if frame_count % 2 == 0:
                continue
            # 调整图像尺寸（例如 640x480）
            resized_frame = cv2.resize(frame, (640, 480))

            ret, buffer = cv2.imencode('.jpg', resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    finally:
        camera_manager.release_camera()  # 确保摄像头资源被释放


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def save_face_image(user_id, frame, folder='faces'):
    """根据人脸位置保存人脸图像"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    # 调整图像尺寸
    resized_frame = cv2.resize(frame, (320, 240))
    # 保存时设置 JPEG 压缩质量
    file_path = f'{os_path}/{folder}/{user_id}.jpg'
    cv2.imwrite(file_path, resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
    print(f"Image saved: {file_path}")
    return file_path


@app.route('/save_face', methods=['POST'])
def save_face():
    global user_id, book_flag, lockCount, relay
    camera = camera_manager.get_camera()

    if not camera.isOpened():
        return "Cannot open camera"
    print(f'--save-check---- book_flag---{book_flag}------')
    success, frame = camera.read()
    if book_flag:
        message = f"The box is booked"
        clearLcdMessage()
        lcdMessage(f'The box  booked')
        return render_template('capture.html', message=message)
    if success and user_id:

        save_face_image(user_id, frame)
        message = f"User {user_map[user_id]} face Image Saved  Successfully."
        # 播放音频
        play_audio(system_path + '/static/audio/save_success.mp3')
        clearLcdMessage()
        lcdMessage(f'{user_map[user_id]} save  success')
        # 表示已经上锁了。
        book_flag = True
        lockCount += 1
        relay.relay_off()

        print(f'--save success-----lockCount------{lockCount}----- book_flag---{book_flag}------')
        return render_template('capture.html', message=message)
    else:
        clearLcdMessage()
        lcdMessage(f'{user_map[user_id]} save  fail')
        message = f"User {user_map[user_id]} face Image Saved  fail."
        return render_template('capture.html', message=message)


@app.route('/unlock', methods=['POST'])
def unlock_form():
    global user_id
    camera_manager.release_camera()  # 确保摄像头资源被释放
    user_id = request.form['user_id']
    return render_template('unlock.html', user_id=user_id, user_name=user_map[user_id])


@app.route('/validate_face', methods=['POST'])
def validate_face():
    global user_id, book_flag, unlockCount
    camera = camera_manager.get_camera()

    if not camera.isOpened():
        return "Cannot open camera"

    success, frame = camera.read()
    if success and user_id:
        stored_image_path = f'faces/{user_id}.jpg'
        if os.path.exists(stored_image_path):
            verify_path = save_face_image(user_id, frame, folder='verify')
            result = verify_face(user_id, stored_image_path, verify_path)
            if result:
                if relay:
                    relay.relay_on()
                    clearLcdMessage()
                    lcdMessage(f'{user_map[user_id]}', 'Verify Successfully')

                    # 播放音频
                    play_audio(system_path + '/static/audio/verify_success.mp3')
                    # time.sleep(10)
                    # relay.relay_on()
                    book_flag = False

                logger.log_info(f'{now_date_time} - User {user_map[user_id]} verified Successfully')
                # 删除图片 只保证里面有一张图片
                os.remove(stored_image_path)
                unlockCount += 1
                message = f"User {user_map[user_id]} verified Successfully, unlocking locker!"
                print(f'--verify success-----unlockCount------{unlockCount}----- book_flag---{book_flag}------')
                return render_template('unlock.html', message=message)
            else:
                clearLcdMessage()
                lcdMessage(f'{user_map[user_id]}', 'Verify Fail')
                message = f"User {user_map[user_id]} Face Does Not match, access denied. Try again."
                play_audio(system_path + '/static/audio/verify_fail.mp3')
                logger.log_info(f'{now_date_time} - User {user_map[user_id]} verified Fail')
                return render_template('unlock.html', message=message)
        else:
            message = "No face image found for this user."
            return render_template('unlock.html', message=message)
    else:
        message = "Failed to validate face."
        return render_template('unlock.html', message=message)


button_pin = 12  # 物理引脚 12 对应 GPIO 18

# 初始化GPIO
if platform.system() == 'Linux':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 初始化全局变量
app_process = None
stop_thread = False
button_pressed_time = None  # 用来记录按钮按下的时间
last_press_time = 0  # 上次按钮按下的时间
click_count = 0  # 按钮按下的次数
double_click_time_threshold = 0.5  # 双击的时间阈值（秒）
long_press_threshold = 3  # 长按时间阈值（秒）


def start_flask_service():
    """ 启动 Flask 服务 """
    global app_process
    if app_process is None:
        print("Starting Flask service...")
        # 使用多进程启动 Flask 服务
        app_process = threading.Thread(target=run_flask)
        app_process.start()
        time.sleep(10)  # 等待服务启动
        if is_port_in_use(5001):
            print("Service is running!")
        else:
            print("Service failed to start.")


def run_flask():
    """ 运行 Flask 服务 """
    app.run(host='0.0.0.0', port=5001, debug=False)


def stop_flask_service():
    """ 停止 Flask 服务 """
    global app_process, stop_thread
    if app_process is not None:
        print("Stopping Flask service...")
        # 通过信号停止 Flask 的线程
        # pid = app_process.pid
        os.kill(os.getpid(), signal.SIGINT)  # 发送 SIGINT 信号
        stop_thread = True
        app_process.join()
        app_process = None
        print(f"Flask service stopped.=========={app_process}=======")


def handle_double_click():
    """ 处理双击事件，启动服务 """
    if app_process is None:
        start_flask_service()

    else:
        print("Service is already running.")


def handle_long_press():
    """ 处理长按事件，停止服务 """
    if app_process is not None:
        print("button keep press")
        lc = lockCount
        ulc = unlockCount
        print(f"LockCount============={lc}")
        print(f"UnlockCount============={ulc}")
        countData = {
            'LockCount': lc,
            'UnlockCount': ulc
        }
        if lc == 0 and ulc == 0:
            print("No lock data to upload")
        else:
            client.push_telemetry(countData)
            print("lock data pushed successfully.")

        time.sleep(2)
        print('显示屏关闭')
        lcd.lcd_off()
        stop_flask_service()
    else:
        print("Service is not running.")


def is_port_in_use(port=5001):
    """ 检查指定端口是否正在监听 """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0  # 返回 True 表示端口被占用，False 表示未占用


def button_event_loop():
    """ 按钮事件循环，处理双击和长按 """
    global button_pressed_time, last_press_time, click_count, stop_thread
    print(f'============{stop_thread}================')
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
                    elif press_duration < 0.5:  # 检查是否是短按
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


if __name__ == '__main__':
    # 在一个单独的线程中运行按钮事件循环
    if platform.system() == 'Linux':
        button_thread = threading.Thread(target=button_event_loop)
        button_thread.daemon = True  # 按钮线程不作为守护线程，以确保它持续运行
        button_thread.start()
        print("Button thread started successfully. Double-click can start web service")

    try:
        # print("Attempting to start Flask application...")
        # # 启动 Flask 应用程序
        # app.run(host='0.0.0.0', port=5001, debug=True)
        # print("Flask application started successfully.")

        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Main thread error: {e}")
    except KeyboardInterrupt:
        print("Main loop interrupted.")
        lc = lockCount
        ulc = unlockCount
        print(f"LockCount============={lc}")
        print(f"UnlockCount============={ulc}")
        countData = {
            'LockCount': lc,
            'UnlockCount': ulc
        }
        if lc == 0 and ulc == 0:
            print("No lock data to upload")
        else:
            client.push_telemetry(countData)
            print("lock data pushed successfully.")
    finally:
        stop_thread = True
        if lcd:
            print('显示屏关闭')
            lcd.lcd_off()  # 确保 LCD 关闭
        if platform.system() == 'Linux':
            GPIO.cleanup()
