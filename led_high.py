import RPi.GPIO as GPIO
import time

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(4, GPIO.OUT)

def loop():
    GPIO.output(4, GPIO.HIGH)
    time.sleep(0.5)  
    GPIO.output(4, GPIO.LOW)
    time.sleep(0.5)

if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        print("Programa terminado")
        GPIO.cleanup()
