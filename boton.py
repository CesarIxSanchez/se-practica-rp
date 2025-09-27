import RPi.GPIO as GPIO
import time

LED_PIN = 17 
BTN_PIN = 24

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def loop():
    if GPIO.input(BTN_PIN) == GPIO.LOW:
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.5)
    else:                     
        GPIO.output(LED_PIN, GPIO.LOW)

if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        print("Programa terminado")
    finally:
        GPIO.cleanup()
