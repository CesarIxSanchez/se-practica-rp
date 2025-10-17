import RPi.GPIO as GPIO
import time

POT_PIN = 4
SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_servo_angle(angle):
    duty_cycle = 2 + (angle / 18)
    duty_cycle = max(2, min(12, duty_cycle))
    pwm.ChangeDutyCycle(duty_cycle)

def read_potentiometer():
    count = 0
    GPIO.setup(POT_PIN, GPIO.OUT)
    GPIO.output(POT_PIN, False)
    time.sleep(0.05)
    
    GPIO.setup(POT_PIN, GPIO.IN)
    
    while GPIO.input(POT_PIN) == GPIO.LOW:
        count += 1
        if count > 50000:
            break
    return count

def calibrate():
    print("Iniciando calibración...")
    input("Gira el potenciómetro completamente a la izquierda (0 grados) ")
    min_val = read_potentiometer()
    
    input("Ahora, gíralo completamente a la derecha (180 grados) ")
    max_val = read_potentiometer()
    
    print(f"Calibración completada: Mínimo={min_val}, Máximo={max_val}")
    time.sleep(1)
    return min_val, max_val

try:
    min_value, max_value = calibrate()
    
    print("\nControl del servo iniciado. Gira el potenciómetro. ")
    while True:
        value = read_potentiometer()
        
        if max_value - min_value > 0:
            normalized = (value - min_value) / (max_value - min_value) * 100.0
            normalized = max(0, min(100, normalized))
        else:
            normalized = 50
        
        servo_angle = (normalized / 100.0) * 180.0
        
        set_servo_angle(servo_angle)
        
        print(f"Valor crudo: {value:4d} -> {normalized:5.1f}% -> Ángulo: {servo_angle:5.1f}°", end="\r")
        
        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nDetenido por el usuario")

finally:
    print("\nDeteniendo PWM y limpiando los pines GPIO.")
    pwm.stop()
    GPIO.cleanup()