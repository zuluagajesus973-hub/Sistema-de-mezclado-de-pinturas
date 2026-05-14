import time
import machine
import onewire
import ds18x20
import json
from machine import Pin 
from umqtt.robust import MQTTClient
import wifi  # Importa tu archivo wifi.py
import os  # 👉 necesario para instanciar el otro script

# === Conexión WiFi ===
if not wifi.conectar():
    print("Error: no se puede continuar sin conexión WiFi")
    while True:
        time.sleep(1)

# === Configuración de sensores DS18B20 ===
pines_sensores = [33, 25, 26, 27, 14]  # Pines de los 5 sensores
sensores = []

print("=== Escaneo de sensores DS18B20 ===")
for pin in pines_sensores:
    try:
        ow = onewire.OneWire(machine.Pin(pin))
        ds = ds18x20.DS18X20(ow)
        roms = ds.scan()
        sensores.append((ds, roms, pin))
        print(f"Pin {pin}: {roms}")
    except Exception as e:
        print(f"Error inicializando pin {pin}: {e}")

if not any(roms for _, roms, _ in sensores):
    print("⚠️ No se detectaron sensores DS18B20")
    while True:
        time.sleep(2)

# === Configuración MQTT ===
MQTT_BROKER = "10.161.32.165"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "esp32_valvulas_individuales"

# Tópicos de temperatura 
MQTT_TOPICS_TEMP = [
    b"micro/temperatura/sensor1",
    b"micro/temperatura/sensor2",
    b"micro/temperatura/sensor3",
    b"micro/temperatura/sensor4",
    b"micro/temperatura/sensor5",
]

# Tópicos de control de válvulas (uno por sensor)
MQTT_TOPICS_VALVULAS = [
    b"micro/pintura/valvula1",
    b"micro/pintura/valvula2",
    b"micro/pintura/valvula3",
    b"micro/pintura/valvula4",
    b"micro/pintura/valvula5",
]

# === Conectar al broker MQTT ===
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
client.connect()
print("✅ Conectado al broker MQTT")

# === Archivo JSON ===
json_filename = "temperaturasSensores.json"

# === Parámetros de control ===
TEMP_UMBRAL = 30.0  # Temperatura de activación
estado_valvulas = [False, False, False, False, False]  # 5 válvulas (apagadas)

# === Bucle principal infinito ===
try:
    while True:
        datos = {}

        # === Leer cada sensor y controlar su válvula ===
        for i, (sensor, roms, pin) in enumerate(sensores):
            if not roms:
                print(f"⚠️ No hay sensor en pin {pin}")
                continue

            try:
                sensor.convert_temp()
                time.sleep_ms(750)

                for rom in roms:
                    temp = sensor.read_temp(rom)
                    print(f"Sensor {i+1} (pin {pin}): {temp:.2f} °C")

                    # Publicar temperatura
                    client.publish(MQTT_TOPICS_TEMP[i], "{:.2f}".format(temp))

                    # Guardar lectura
                    datos[f"sensor{i+1}"] = temp

                    # === Lógica de control individual ===
                    if temp >= TEMP_UMBRAL and not estado_valvulas[i]:
                        client.publish(MQTT_TOPICS_VALVULAS[i], b"ON")
                        estado_valvulas[i] = True
                        print(f"🟢 Sensor {i+1} superó 30°C → Válvula {i+1} ACTIVADA")

                    elif temp < TEMP_UMBRAL and estado_valvulas[i]:
                        client.publish(MQTT_TOPICS_VALVULAS[i], b"OFF")
                        estado_valvulas[i] = False
                        print(f"🔵 Sensor {i+1} bajó de 30°C → Válvula {i+1} DESACTIVADA")

            except Exception as e:
                print(f"Error leyendo sensor en pin {pin}: {e}")

        # === Guardar datos en JSON ===
        try:
            try:
                with open(json_filename, "r") as f:
                    historial = json.load(f)
                if not isinstance(historial, list):
                    historial = []
            except:
                historial = []

            historial.append(datos)

            with open(json_filename, "w") as f:
                f.write("[\n")
                for i, d in enumerate(historial):
                    linea = json.dumps(d)
                    if i < len(historial) - 1:
                        f.write("  " + linea + ",\n")
                    else:
                        f.write("  " + linea + "\n")
                f.write("]")

            print("💾 Lectura guardada correctamente en", json_filename)

        except Exception as e:
            print("Error al guardar JSON:", e)

        time.sleep(5)

# === Si el bucle se interrumpe manualmente (Ctrl+C), ejecutar MqttValvula ===
except KeyboardInterrupt:
    print("\nLectura interrumpida por el usuario.")
    print("Iniciando MqttValvula.py...")
    time.sleep(2)
    os.system("MqttValvula.py")

# === Si ocurre algún error inesperado, también puede ejecutar el otro script ===
except Exception as e:
    print("Error inesperado:", e)
    print("Iniciando MqttValvula.py...")
    time.sleep(2)
    os.system("MqttValvula.py")
