import RPi.GPIO as GPIO
import time
from flask import Flask, jsonify
from datetime import datetime
import threading 

POT_PIN = 4
GPIO.setmode(GPIO.BCM)

app = Flask(__name__)

datos_sensor = {
    "Valor crudo": 0,
    "porcentaje": '0%',
    "resistencia aproximada": "0Ω",
    "ultima_actualizacion": None
}

datos_sensor_lock = threading.Lock()

min_value = 0
max_value = 100

@app.route('/')
def home():
    return jsonify({"mensaje": "API del Sensor", "endpoints": ["/api/sensor", "/api/estado"]})

@app.route('/api/sensor')
def get_sensor_data():
    global datos_sensor
    
    with datos_sensor_lock:

        return jsonify(datos_sensor.copy())

@app.route('/api/estado')
def get_status():
    return jsonify({"estado": "sistema funcionando", "timestamp": datetime.now().isoformat()})

def read_potentiometer():
    count = 0
    
    GPIO.setup(POT_PIN, GPIO.OUT)
    GPIO.output(POT_PIN, False)
    time.sleep(0.1)
    
    GPIO.setup(POT_PIN, GPIO.IN)
    
    while GPIO.input(POT_PIN) == GPIO.LOW:
        count += 1
        if count > 100000:
            break
    
    return count

def calibrate():
    print("Calibrando para potenciómetro 10K...")
    print("Gira completamente a la izquierda (mínimo)")
    time.sleep(3)
    min_val = read_potentiometer()
    
    print("Gira completamente a la derecha (máximo)")
    time.sleep(3)
    max_val = read_potentiometer()

    if max_val <= min_val:
        print("¡Advertencia! Mínimo y máximo son iguales. Ajustando...")
        max_val = min_val + 100 
    
    print(f"Calibración: Mínimo={min_val}, Máximo={max_val}")
    return min_val, max_val

def sensor_update_loop():
    global datos_sensor, min_value, max_value

    print("Iniciando hilo de actualización del sensor...")
    
    while True:
        try:
            value = read_potentiometer()
                
            normalized = 0.0
            if (max_value - min_value) > 0:
                normalized = (value - min_value) / (max_value - min_value) * 100.0
                normalized = max(0, min(100, normalized))
            
            resistance_approx = (normalized / 100) * 10000 
            
            print(f"Valor crudo: {value:4d} -> {normalized:5.1f}% -> ~{resistance_approx:4.0f}Ω")

            with datos_sensor_lock:
                datos_sensor["Valor crudo"] = value
                datos_sensor["porcentaje"] = f"{normalized:5.1f}%"
                datos_sensor["resistencia aproximada"] = f"~{resistance_approx:4.0f}Ω"
                datos_sensor["ultima_actualizacion"] = datetime.now().isoformat()
            
            time.sleep(0.3)
        
        except Exception as e:
            print(f"Error en el hilo del sensor: {e}")
            time.sleep(2)

if __name__ == "__main__":
    try:
        min_value, max_value = calibrate()
        
        sensor_thread = threading.Thread(target=sensor_update_loop, daemon=True)
        sensor_thread.start()

        print("\nIniciando servidor Flask en http://0.0.0.0:5000")
        print("Visita http://<IP_DE_TU_RASPBERRY>:5000/api/sensor en tu navegador")
        app.run(host='0.0.0.0', port=5000, debug=False)

    except KeyboardInterrupt:
        print("\nDetenido por el usuario")
    finally:
        GPIO.cleanup()
        print("GPIO limpiado. Adiós.")
