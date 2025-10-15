import RPi.GPIO as GPIO
import time

SERVO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_servo_angle(angle):
    # angle can be from -90° to 90°
    pulse_ms = 1.5 - (angle / 180)
    duty_cycle = (pulse_ms / 20) * 100
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.3)

try:
    while True:
        set_servo_angle(-90)
        time.sleep(3)

        set_servo_angle(90)
        time.sleep(3)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
    print("Se ha interumpido el programa")