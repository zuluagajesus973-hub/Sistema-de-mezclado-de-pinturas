import time
import machine
from umqtt.robust import MQTTClient
import wifi  # Tu módulo wifi.py 

# === 1. Conexión WiFi ===
if not wifi.conectar():
    print(" Error: no se puede continuar sin conexión WiFi")
    while True:
        time.sleep(1)

# === 2. Configuración MQTT ===
MQTT_BROKER = "test.mosquitto.org"   # Cambia si usas un broker local
CLIENT_ID = "ESP32_PINTURA"
MQTT_TOPICS_VALVULAS = [
    b"micro/pintura/valvula1",
    b"micro/pintura/valvula2",
    b"micro/pintura/valvula3",
    b"micro/pintura/valvula4",
    b"micro/pintura/valvula5"
]
 
# === 3. Configuración de pines para las 5 válvulas ===
# Puedes usar los GPIO que prefieras, excepto los reservados (0, 2, 6–11, 12, 34–39)
VALVULA_PINS = [15, 16, 17, 18, 19]  # ejemplo
valvulas = {}

for i in range(5):
    valvulas[MQTT_TOPICS_VALVULAS[i]] = machine.Pin(VALVULA_PINS[i], machine.Pin.OUT)
    valvulas[MQTT_TOPICS_VALVULAS[i]].value(0)  # Todas apagadas inicialmente

# === 4. Callback al recibir mensajes ===
def on_message(topic, msg):
    topic_str = topic.decode()
    msg_str = msg.decode().upper()
    print(f"📩 {topic_str}: {msg_str}")

    if topic in valvulas:
        if msg_str == "ON":
            valvulas[topic].value(1)
            print(f"✅ {topic_str} activada")
        elif msg_str == "OFF":
            valvulas[topic].value(0)
            print(f"🟢 {topic_str} desactivada")
        else:
            print("⚠️ Comando no reconocido. Usa 'ON' o 'OFF'")
    else:
        print("⚠️ Topic no asociado a ninguna válvula")

# === 5. Conectar al broker ===
client = MQTTClient(CLIENT_ID, MQTT_BROKER)
client.set_callback(on_message)
client.connect()
print("🔗 Conectado al broker MQTT")

# === 6. Suscribirse a los 5 topics ===
for t in MQTT_TOPICS_VALVULAS:
    client.subscribe(t)
    print(f"📡 Suscrito a {t.decode()}")

# === 7. Bucle principal ===
try:
    while True:
        client.check_msg()  # Revisa si hay mensajes nuevos
        time.sleep(0.1)
except KeyboardInterrupt:
    client.disconnect()
    print("🔌 Desconectado de MQTT")
