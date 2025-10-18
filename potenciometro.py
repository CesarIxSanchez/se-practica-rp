import RPi.GPIO as GPIO
import time
import math

# --- Configuración ---
POT_PIN = 4          # GPIO4 (pin físico 7)
C_FARADS = 22e-9     # 22 nF;
ALPHA = 0.5          # fracción del umbral Vih ~ 50% de 3.3V (aprox.)
TIMEOUT = 0.2        # 200 ms de tope

GPIO.setmode(GPIO.BCM)

def read_potentiometer():
    # Descargar el capacitor
    GPIO.setup(POT_PIN, GPIO.OUT)
    GPIO.output(POT_PIN, False)
    time.sleep(0.01)  # 10 ms para asegurar descarga

    # Cambiar a entrada y medir tiempo hasta HIGH
    GPIO.setup(POT_PIN, GPIO.IN)
    t0 = time.perf_counter()
    while GPIO.input(POT_PIN) == GPIO.LOW:
        if (time.perf_counter() - t0) > TIMEOUT:
            return TIMEOUT  # llegó a tope
    return time.perf_counter() - t0  # segundos

def rc_to_resistance(t_s):
    # Estima R a partir del tiempo t = -R*C*ln(1-α)
    if t_s >= TIMEOUT:
        return float('inf')  # saturó
    denom = -math.log(1.0 - ALPHA)  # ~0.693 si ALPHA=0.5
    return t_s / (C_FARADS * denom)

def calibrate():
    print("Calibrando para potenciómetro 10K...")
    print("Gira completamente a la izquierda (mínimo)")
    time.sleep(2)
    t_min = read_potentiometer()

    print("Gira completamente a la derecha (máximo)")
    time.sleep(2)
    t_max = read_potentiometer()

    print(f"Calibración: t_min={t_min:.6f}s, t_max={t_max:.6f}s")
    return t_min, t_max

try:
    t_min, t_max = calibrate()

    print("Leyendo potenciómetro... (Ctrl+C para detener)")
    while True:
        t = read_potentiometer()  # segundos
        # Normalización segura
        if t_max > t_min:
            normalized = (t - t_min) / (t_max - t_min) * 100.0
            normalized = max(0.0, min(100.0, normalized))
        else:
            normalized = 0.0  # evita división por cero si calibración falló

        R_est = rc_to_resistance(t)
        if R_est == float('inf'):
            r_txt = "∞ (timeout)"
        else:
            r_txt = f"{R_est:,.0f}Ω"

        print(f"t={t*1e3:7.2f} ms  -> {normalized:6.1f}%  -> R≈ {r_txt}")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nDetenido por el usuario")
finally:
    GPIO.cleanup()
