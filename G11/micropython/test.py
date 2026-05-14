## Código MicroPython 


# main.py – Control secuencial de 5 bombas de diafragma vía MQTT
# ESP32 + MicroPython

from umqtt.simple import MQTTClient
from machine import Pin, reset
import network
import time
import ujson

# =========================
# 1. CONFIGURACIÓN WiFi
# =========================
SSID = "TuSSID"          # reemplaza con el nombre de tu red
PASSWORD = "TuPassword"  # reemplaza con la contraseña

# =========================
# 2. CONFIGURACIÓN MQTT
# =========================
MQTT_BROKER = "192.168.1.100"  # IP del broker MQTT (por ejemplo, la Raspberry Pi)
MQTT_TOPIC_CMD = b"linea/pintura/cmd"     # topic de entrada de comandos
MQTT_TOPIC_STATUS = b"linea/pintura/status"  # topic de salida para reportar estados
CLIENT_ID = b"ESP32_LINEA_PINTURA"         # identificador único del cliente

# =========================
# 3. CONFIGURACIÓN DE SALIDAS
# =========================
# definimos 5 pines para las bombas (conecta cada uno a un relé o transistor adecuado)
PUMP_PINS = [5, 18, 19, 21, 22]
pumps = [Pin(p, Pin.OUT) for p in PUMP_PINS]
for p in pumps:
    p.value(0)  # inicializa todas las bombas apagadas

# LED indicador (puede ser el integrado de la placa o uno externo)
LED_PIN = 2
led = Pin(LED_PIN, Pin.OUT)
led.value(0)

# =========================
# 4. ESTRUCTURA DE ESTADO DE LOS SENSORES
# =========================
# sensor_data es una lista de 5 diccionarios (uno por bomba) que almacena
# las señales lógicas de la galga y la temperatura
sensor_data = [
    {"galga": 0, "temp_ok": 0},  # bomba 1
    {"galga": 0, "temp_ok": 0},  # bomba 2
    {"galga": 0, "temp_ok": 0},  # bomba 3
    {"galga": 0, "temp_ok": 0},  # bomba 4
    {"galga": 0, "temp_ok": 0},  # bomba 5
]

# tiempo de funcionamiento de cada bomba (en segundos)
PUMP_RUNTIME_SEC = 2.0
# tiempo máximo sin recibir mensajes antes de reiniciar (seguridad)
MQTT_TIMEOUT_SEC = 60
# marca de tiempo del último mensaje recibido
last_msg_ts = time.time()


def conectar_wifi():
    """Conecta la ESP32 a la red Wi‑Fi."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi…")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Conectado a WiFi:", wlan.ifconfig())


def mqtt_callback(topic, msg):
    """
    Función que se ejecuta cuando llega un mensaje al topic suscrito.
    Se espera un JSON con claves pX_galga y pX_temp (donde X es 1…5).
    Actualiza la estructura sensor_data con 0 o 1.
    """
    global sensor_data, last_msg_ts
    last_msg_ts = time.time()
    print("Mensaje MQTT recibido:", msg)
    try:
        data = ujson.loads(msg)
        # actualiza las señales para cada bomba
        for i in range(5):
            g_key = "p{}_galga".format(i + 1)
            t_key = "p{}_temp".format(i + 1)
            if g_key in data:
                sensor_data[i]["galga"] = 1 if int(data[g_key]) == 1 else 0
            if t_key in data:
                sensor_data[i]["temp_ok"] = 1 if int(data[t_key]) == 1 else 0
    except Exception as e:
        print("Error parseando JSON:", e)


def conectar_mqtt():
    """Configura el cliente MQTT, asigna la callback, se conecta y se suscribe."""
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(mqtt_callback)
    client.connect()
    print("Conectado al broker MQTT")
    client.subscribe(MQTT_TOPIC_CMD)
    print("Suscrito al topic:", MQTT_TOPIC_CMD)
    return client


def activar_bomba(idx, client):
    """
    Enciende la bomba indicada por idx (0…4) durante un tiempo fijado,
    enciende el LED, y publica mensajes de inicio y fin.
    """
    print("Activando bomba", idx + 1)
    pumps[idx].value(1)
    led.value(1)
    try:
        client.publish(MQTT_TOPIC_STATUS, b"BOMBA_%d_ON" % (idx + 1))
    except:
        pass
    time.sleep(PUMP_RUNTIME_SEC)
    pumps[idx].value(0)
    led.value(0)
    print("Bomba", idx + 1, "apagada")
    try:
        client.publish(MQTT_TOPIC_STATUS, b"BOMBA_%d_OFF" % (idx + 1))
    except:
        pass


def loop_principal():
    """Bucle principal: recibe mensajes y activa bombas secuencialmente."""
    conectar_wifi()
    client = conectar_mqtt()
    while True:
        # comprueba si hay mensajes nuevos
        client.check_msg()
        # recorre las 5 bombas en orden
        for i in range(5):
            if sensor_data[i]["galga"] == 1 and sensor_data[i]["temp_ok"] == 1:
                activar_bomba(i, client)
                # pequeña pausa entre bombas para no saturar el micro
                time.sleep(0.3)
        # reinicia si no llega MQTT en el tiempo establecido
        if (time.time() - last_msg_ts) > MQTT_TIMEOUT_SEC:
            print("No llegan comandos MQTT desde hace tiempo, reiniciando…")
            for p in pumps:
                p.value(0)
            led.value(0)
            time.sleep(1)
            reset()
        # breve espera para reducir uso de CPU
        time.sleep(0.1)


try:
    loop_principal()
except Exception as e:
    print("Error en ejecución:", e)
    for p in pumps:
        p.value(0)
    led.value(0)
    time.sleep(5)
    reset()
```

