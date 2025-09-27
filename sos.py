import RPi.GPIO as GPIO
import time

PIN = 17

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(PIN, GPIO.OUT)

def punto():
    GPIO.output(PIN, GPIO.HIGH)
    time.sleep(1/6)
    GPIO.output(PIN, GPIO.LOW)
    time.sleep(1/6)

def raya():
    GPIO.output(PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(PIN, GPIO.LOW)
    time.sleep(0.5)

def pausa_letra():
    time.sleep(0.5)

def pausa_palabra():
    time.sleep(1.2)

def sos():
    # S = ...
    punto(); punto(); punto()
    pausa_letra()

    # O = ---
    raya(); raya(); raya()
    pausa_letra()

    # S = ...
    punto(); punto(); punto()

    # pausa y repetir
    pausa_palabra()

if __name__ == "__main__":
    try:
        setup()
        while True:
            sos()
    except KeyboardInterrupt:
        print("Programa terminado")
    finally:
        GPIO.cleanup()
