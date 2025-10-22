import RPi.GPIO as GPIO
import time
from flask import Flask, jsonify
from datetime import datetime
import threading # <-- 1. Importamos threading

# --- Configuración de Hardware ---
POT_PIN = 4
GPIO.setmode(GPIO.BCM)

# --- Variables Globales y Candado (Lock) ---
app = Flask(__name__)

# Diccionario para compartir datos entre el hilo del sensor y el hilo de la API
datos_sensor = {
    "Valor crudo": 0,
    "porcentaje": '0%',
    "resistencia aproximada": "0Ω",
    "ultima_actualizacion": None # El hilo lo llenará
}
# Usamos un "candado" para evitar que la API lea
# mientras el hilo del sensor está escribiendo (y viceversa)
datos_sensor_lock = threading.Lock()

# Variables de calibración (se llenarán al inicio)
min_value = 0
max_value = 100

# --- Endpoints de la API ---

@app.route('/')
def home():
    return jsonify({"mensaje": "API del Sensor", "endpoints": ["/api/sensor", "/api/estado"]})

@app.route('/api/sensor')
def get_sensor_data():
    global datos_sensor
    
    # Adquirimos el candado para leer los datos de forma segura
    with datos_sensor_lock:
        # Devolvemos una *copia* de los datos
        # para liberar el candado rápidamente
        return jsonify(datos_sensor.copy())

@app.route('/api/estado')
def get_status():
    return jsonify({"estado": "sistema funcionando", "timestamp": datetime.now().isoformat()})

# --- Funciones del Sensor (GPIO) ---

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
        if count > 100000:  # Timeout
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

    # Evitar división por cero si min y max son iguales
    if max_val <= min_val:
        print("¡Advertencia! Mínimo y máximo son iguales. Ajustando...")
        max_val = min_val + 100 # Valor por defecto para evitar errores
    
    print(f"Calibración: Mínimo={min_val}, Máximo={max_val}")
    return min_val, max_val

# --- Hilo de Background (El "Loop") ---

def sensor_update_loop():
    """
    Esta función se ejecuta en un hilo separado
    para actualizar los datos del sensor constantemente.
    """
    global datos_sensor, min_value, max_value

    print("Iniciando hilo de actualización del sensor...")
    
    while True:
        try:
            value = read_potentiometer()
                
            # Normalizar el valor
            normalized = 0.0
            if (max_value - min_value) > 0:
                normalized = (value - min_value) / (max_value - min_value) * 100.0
                normalized = max(0, min(100, normalized))
            
            # Calcular resistencia (aproximación basada en el %)
            resistance_approx = (normalized / 100) * 10000 # 10k es el max
            
            # Imprimir en consola para depuración
            print(f"Valor crudo: {value:4d} -> {normalized:5.1f}% -> ~{resistance_approx:4.0f}Ω")

            # --- Sección Crítica: Actualizar datos globales ---
            # Adquirimos el candado ANTES de modificar el diccionario
            with datos_sensor_lock:
                datos_sensor["Valor crudo"] = value
                datos_sensor["porcentaje"] = f"{normalized:5.1f}%"
                datos_sensor["resistencia aproximada"] = f"~{resistance_approx:4.0f}Ω"
                datos_sensor["ultima_actualizacion"] = datetime.now().isoformat()
            # --- Fin de la Sección Crítica (el candado se libera) ---
            
            time.sleep(0.3) # Esperar para la próxima lectura
        
        except Exception as e:
            print(f"Error en el hilo del sensor: {e}")
            time.sleep(2) # Esperar antes de reintentar

# --- Arranque Principal ---

if __name__ == "__main__":
    try:
        # 1. Calibrar primero
        min_value, max_value = calibrate()
        
        # 2. Iniciar el hilo de actualización del sensor
        # daemon=True significa que el hilo se cerrará
        # automáticamente cuando el programa principal (Flask) termine.
        sensor_thread = threading.Thread(target=sensor_update_loop, daemon=True)
        sensor_thread.start()
        
        # 3. Iniciar la aplicación Flask (en el hilo principal)
        # IMPORTANTE: debug=False
        # Si usas debug=True, Flask reinicia el script y puede
        # causar conflictos con GPIO y threads.
        print("\nIniciando servidor Flask en http://0.0.0.0:5000")
        print("Visita http://<IP_DE_TU_RASPBERRY>:5000/api/sensor en tu navegador")
        app.run(host='0.0.0.0', port=5000, debug=False)

    except KeyboardInterrupt:
        print("\nDetenido por el usuario")
    finally:
        # Limpiar GPIO al salir
        GPIO.cleanup()
        print("GPIO limpiado. Adiós.")
