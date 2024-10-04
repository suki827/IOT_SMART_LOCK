import Adafruit_DHT
import RPi.GPIO as GPIO
import time

# 设置 GPIO 引脚
DHT_SENSOR = Adafruit_DHT.DHT22  # 或 DHT11
DHT_PIN = 4  # DHT 数据引脚连接到 GPIO 4
VIBRATION_PIN = 17  # 震动传感器连接到 GPIO 17

def setup_sensors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(VIBRATION_PIN, GPIO.IN)

def get_sensor_data():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    vibration = GPIO.input(VIBRATION_PIN)
    return humidity, temperature, vibration

def cleanup_sensors():
    GPIO.cleanup()
