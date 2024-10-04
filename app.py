import time
import pygame
from flask import Flask, render_template, Response, request
import cv2
import os

from functions.face import verify_face
import sensors.relay
import platform

from functions.logger import DataLogger

logger = DataLogger('my_data_log.log')


app = Flask(__name__)
lcd = None
system_path = '.'
if platform.system() == 'Linux':  #仅在树莓派上导入 RPi.GPIO
    # import RPi.GPIO as GPIO
    system_path = '/home/pi/iot'
    relay = sensors.relay.RelayController(pin=11)
    lcd = Display.I2CLCD(address=0x3f)  # 将地址改为检测到的I2C地址
    lcd.clear()
    lcd.lcd_string("Please connect Wi-Fi", lcd.LCD_LINE_1)
    lcd.lcd_string("RaspberryPi_AP", lcd.LCD_LINE_2)


else:
    print("Not running on Raspberry Pi, GPIO not available")

user_map = {
    '1': 'Nick',
    '2': 'Hugo',
    '3': 'Honey',
    '4': 'Habilash'
}


app = Flask(__name__)


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
    camera_manager.release_camera()  # 确保摄像头资源被释放
    return render_template('index.html')


@app.route('/capture', methods=['POST'])
def capture_form():
    global user_id
    user_id = request.form['user_id']
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
    file_path = f'{folder}/{user_id}.jpg'
    cv2.imwrite(file_path, resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
    print(f"Image saved: {file_path}")
    return file_path


@app.route('/save_face', methods=['POST'])
def save_face():
    global user_id
    camera = camera_manager.get_camera()

    if not camera.isOpened():
        return "Cannot open camera"

    success, frame = camera.read()
    if success and user_id:
        save_face_image(user_id, frame)
        message = f"User {user_map[user_id]} face Image Saved  Successfully."
        # 播放音频
        play_audio(system_path + '/static/audio/save_success.mp3')
        clearLcdMessage()
        lcdMessage(f'{user_map[user_id]} save  success')
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
    return render_template('unlock.html', user_id=user_id,user_name=user_map[user_id])


@app.route('/validate_face', methods=['POST'])
def validate_face():
    global user_id
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
                    time.sleep(2)
                    relay.relay_off()
                clearLcdMessage()
                lcdMessage(f'{user_map[user_id]} Verify Successfully')
                message = f"User {user_map[user_id]} verified Successfully, unlocking locker!"
                # 播放音频
                play_audio(system_path + '/static/audio/verify_success.mp3')

                logger.log_info('')
                return render_template('unlock.html', message=message)
            else:
                clearLcdMessage()
                lcdMessage(f'{user_map[user_id]} Verify Fail')
                message = f"User {user_map[user_id]} Face Does Not match, access denied. Try again."
                play_audio(system_path + '/static/audio/verify_fail.mp3')
                return render_template('unlock.html', message=message)
        else:
            message = "No face image found for this user."
            return render_template('unlock.html', message=message)
    else:
        message = "Failed to validate face."
        return render_template('unlock.html', message=message)


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        if lcd: lcd.lcd_off()
