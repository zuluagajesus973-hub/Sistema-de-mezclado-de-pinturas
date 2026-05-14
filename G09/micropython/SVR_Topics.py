import time
import machine
import onewire
import ds18x20
import json
from machine import Pin
from umqtt.robust import MQTTClient
import wifi
import os

#=== Conexión WiFi ===
if not wifi.conectar():
    print("Error: no se puede continuar sin conexión WiFi")
    while True:
        time.sleep(1)

# === Configuración de sensores DS18B20 ===
pines_sensores = [33]  # Pines de los 5 sensores
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
MQTT_BROKER = "8.tcp.ngrok.io"
MQTT_PORT = 12777
MQTT_CLIENT_ID = "esp32_valvulas_resistencias"

# Tópicos MQTT para temperaturas
MQTT_TOPICS_TEMP = [
    b"in/esp1/temperatura/azul",
    b"in/esp1/temperatura/rojo",
    b"in/esp1/temperatura/amarillo",
    b"in/esp1/temperatura/negro",
    b"esp1/temperatura/blanco",
]

# Tópicos MQTT para válvulas
MQTT_TOPICS_VALVULAS = [
    b"out/esp2/pintura_azul",
    b"out/esp2/pintura_rojo",
    b"out/esp2/pintura_amarillo",
    b"out/esp2/pintura_negro",
    b"out/esp2/pintura_blanco",
]

# === Conectar al broker MQTT ===
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
client.connect()
print("Conectado al broker MQTT")

# === Archivo JSON ===
json_filename = "temperaturasSensores.json"

# === Configuración de pines para resistencias ===
# Mapeo directo: sensor1→15, sensor2→2, sensor3→4, sensor4→35, sensor5→32
pines_resistencias = [15, 2, 4, 5, 32]
resistencias = []

for i, pin in enumerate(pines_resistencias):
    try:
        p = Pin(pin, Pin.OUT)
        p.value(0)
        resistencias.append(p)
        print(f"Resistencia {i+1} asignada al pin {pin}")
    except Exception as e:
        print(f"Error inicializando resistencia {i+1} en pin {pin}: {e}")
        resistencias.append(None)

# === Parámetros de control ===
TEMP_UMBRAL_VALVULA = 27.0  # Temperatura para activar válvula
TEMP_ON_RESIST = 25.0       # Encender resistencia
TEMP_OFF_RESIST = 27.0      # Apagar resistencia

estado_valvulas = [False] * 5
estado_resistencias = [False] * 5

# === Bucle principal ===
try:
    while True:
        datos = {}

        for i, (sensor, roms, pin_sensor) in enumerate(sensores):
            if not roms:
                print(f"No hay sensor en pin {pin_sensor}")
                continue

            try:
                sensor.convert_temp()
                time.sleep_ms(750)

                for rom in roms:
                    temp = sensor.read_temp(rom)
                    print(f"Sensor {i+1} (pin {pin_sensor}): {temp:.2f} °C")

                    # Publicar temperatura
                    client.publish(MQTT_TOPICS_TEMP[i], "{:.2f}".format(temp))
                    datos[f"sensor{i+1}"] = temp

                    # === Lógica de válvulas ===
                    if temp >= TEMP_UMBRAL_VALVULA and not estado_valvulas[i]:
                        client.publish(MQTT_TOPICS_VALVULAS[i], b"ON")
                        estado_valvulas[i] = True
                        print(f"Sensor {i+1} ≥ 27°C → Válvula {i+1} ACTIVADA")

                    elif temp < TEMP_UMBRAL_VALVULA and estado_valvulas[i]:
                        client.publish(MQTT_TOPICS_VALVULAS[i], b"OFF")
                        estado_valvulas[i] = False
                        print(f"Sensor {i+1} < 27°C → Válvula {i+1} DESACTIVADA")

                    # === Lógica de resistencias (asociadas 1 a 1 con sensores) ===
                    if resistencias[i] is not None:
                        if temp <= TEMP_ON_RESIST and not estado_resistencias[i]:
                            resistencias[i].value(1)
                            estado_resistencias[i] = True
                            print(f"Sensor {i+1} ≤ 25°C → Resistencia {i+1} ENCENDIDA")

                        elif temp >= TEMP_OFF_RESIST and estado_resistencias[i]:
                            resistencias[i].value(0)
                            estado_resistencias[i] = False
                            print(f"Sensor {i+1} ≥ 27°C → Resistencia {i+1} APAGADA")

            except Exception as e:
                print(f"Error leyendo sensor en pin {pin_sensor}: {e}")

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
                for j, d in enumerate(historial):
                    linea = json.dumps(d)
                    if j < len(historial) - 1:
                        f.write("  " + linea + ",\n")
                    else:
                        f.write("  " + linea + "\n")
                f.write("]")

            print("Lectura guardada correctamente en", json_filename)

        except Exception as e:
            print("Error al guardar JSON:", e)

        time.sleep(5)

# === Interrupción manual (Ctrl+C) ===
except KeyboardInterrupt:
    print("\nLectura interrumpida por el usuario.")
    print("Iniciando MqttValvula.py...")
    time.sleep(2)
    os.system("MqttValvula.py")

# === Errores inesperados ===
except Exception as e:
    print("Error inesperado:", e)
    print("Iniciando MqttValvula.py...")
    time.sleep(2)
    os.system("MqttValvula.py")


