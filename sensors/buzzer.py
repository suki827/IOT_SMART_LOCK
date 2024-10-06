#!/usr/bin/env python3
import RPi.GPIO as GPIO


# Pin settings

BUZZER_PIN = 11   #GPIO17

def setup():
    GPIO.setmode(GPIO.BOARD)
    initialize_buzzer()
    buzzer_off()


def initialize_buzzer():
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Ensure the buzzer is off at start


def buzzer_on():
    initialize_buzzer()
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def buzzer_off():
    GPIO.cleanup(BUZZER_PIN)

def check_alarm_conditions(temperature, humidity):
    if temperature > 40 or humidity > 90:
        print("ALARM: Temperature or Humidity exceeded threshold!")
        buzzer_on()
    else:
        buzzer_off()


