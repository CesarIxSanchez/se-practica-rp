import serial, time
import RPi.GPIO as GPIO

LED_PIN = 18  # GPIO18
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

pwm = None
ser = None

def map01(x, in_min=0, in_max=1023, out_min=0.0, out_max=100.0):
    x = max(in_min, min(in_max, x))
    return (x - in_min) * (out_max - out_min) / float(in_max - in_min) + out_min

def setup():
    global pwm, ser
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN, GPIO.OUT)

    pwm = GPIO.PWM(LED_PIN, 1000)
    pwm.start(0)

    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    
    ser.reset_input_buffer() # Limpia cualquier basura del buffer

def loop():
    line = ser.readline().decode(errors="ignore").strip()
    if line.isdigit():
        val = int(line) # 0..1023 desde el ESP
        duty = map01(val) # 0..100 %
        pwm.ChangeDutyCycle(duty) # brillo LED

if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        print("Programa terminado")
    finally:
        if pwm is not None:
            pwm.stop()
        if ser is not None and ser.is_open:
            ser.close()
        GPIO.cleanup()
