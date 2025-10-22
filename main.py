import RPi.GPIO as GPIO
import time
from flask import Flask, jsonify
import json
import time
from datetime import datetime

# Configuración
POT_PIN = 4
GPIO.setmode(GPIO.BCM)
min_value, max_value = calibrate()

def setup():
    GPIO.setup(POT_PIN, GPIO.OUT)
    app.run(host='0.0.0.0', port=5000, debug=True)


def loop():
    value = read_potentiometer()
        
    # Normalizar el valor para potenciómetro de 10K
    if max_value - min_value > 0:
        normalized = (value - min_value) / (max_value - min_value) * 100.0
        normalized = max(0, min(100, normalized))  # Limitar entre 0-100%
    else:
        normalized = 50  # Valor por defecto
        
    # También calcular resistencia aproximada
    resistance_approx = (value / max_value) * 10000  # Aproximación para 10K
    
    print(f"Valor crudo: {value:4d} -> {normalized:5.1f}% -> ~{resistance_approx:4.0f}Ω")
    time.sleep(0.3)


if __name__ == "__main__":
    setup()

    try:
        while True:
            loop()
    except KeyboardInterrupt:
        print("Detenido por el usuario")

# Calibrar para potenciómetro de 5K
def calibrate():
    print("Calibrando para potenciómetro 10K...")
    print("Gira completamente a la izquierda (mínimo)")
    time.sleep(3)
    min_val = read_potentiometer()
    
    print("Gira completamente a la derecha (máximo)")
    time.sleep(3)
    max_val = read_potentiometer()
    
    print(f"Calibración: Mínimo={min_val}, Máximo={max_val}")
    return min_val, max_val


def read_potentiometer():
    # Medir tiempo de carga del capacitor
    count = 0
    
    # Descargar capacitor
    GPIO.setup(POT_PIN, GPIO.OUT)
    GPIO.output(POT_PIN, False)
    time.sleep(0.1)  # Reducido para potenciómetro de 10K
    
    # Cambiar a entrada y medir tiempo hasta que se cargue
    GPIO.setup(POT_PIN, GPIO.IN)
    
    # Contar hasta que el pin sea HIGH
    while GPIO.input(POT_PIN) == GPIO.LOW:
        count += 1
        if count > 100000:  # Timeout reducido para 10K
            break
    
    return count

# Api
app = Flask(__name__)
# Datos de ejemplo (pueden venir de tu sensor)
datos_sensor = {
    "Valor crudo": 1000,
    "porcentaje": '20%',
    "resistencia aproximada": "10kO",
    "ultima_actualizacion": datetime.now().isoformat()
}

@app.route('/')
def home():
    return jsonify({"mensaje": "API del Sensor", "endpoints": ["/api/sensor", "/api/estado"]})

@app.route('/api/sensor')
def get_sensor_data():
    # Actualizar timestamp
    datos_sensor["ultima_actualizacion"] = datetime.now().isoformat()
    return jsonify(datos_sensor)

@app.route('/api/estado')
def get_status():
    return jsonify({"estado": "sistema funcionando", "timestamp": datetime.now().isoformat()})
