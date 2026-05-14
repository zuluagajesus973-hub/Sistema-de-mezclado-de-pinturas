import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

# ======== CONFIGURACIÓN WiFi ========
SSID = "TIGO-E325"           # Cambia por tu red
PASSWORD = "7989956371"     # Cambia por tu contraseña

# ======== CONFIGURACIÓN MQTT ========
BROKER = "192.168.1.9"         # IP del broker MQTT (Raspberry Pi)
CLIENT_ID = "esp32_bomba"
TOPIC_SENSOR1 = b'sensores/sensor1'
TOPIC_SENSOR2 = b'sensores/sensor2'
TOPIC_BOMBA_CONTROL = b'bomba/control'
TOPIC_BOMBA_ESTADO = b'bomba/estado'

# ======== CONFIGURACIÓN DE PINES ========
sensor1 = Pin(32, Pin.IN)      # Sensor 1
sensor2 = Pin(33, Pin.IN)      # Sensor 2
bomba = Pin(25, Pin.OUT)       # Salida de la bomba (GPIO25)
led = Pin(2, Pin.OUT)          # LED indicador

# ======== VARIABLES ========
modo_manual = False
bomba_estado = False

# ======== CONEXIÓN WiFi ========
def conectar_wifi():
    print("Conectando a WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\nConectado a WiFi:", wlan.ifconfig())

# ======== CALLBACK MQTT ========
def callback_mqtt(topic, msg):
    global modo_manual
    comando = msg.decode().strip().upper()
    print("Mensaje recibido:", topic, comando)

    if topic == TOPIC_BOMBA_CONTROL:
        if comando == "ON":
            modo_manual = True
            encender_bomba()
        elif comando == "OFF":
            modo_manual = True
            apagar_bomba()
        elif comando == "AUTO":
            modo_manual = False
            print("Modo automático activado")

# ======== CONTROL DE BOMBA ========
def encender_bomba():
    global bomba_estado
    bomba.value(1)
    led.value(1)
    bomba_estado = True
    client.publish(TOPIC_BOMBA_ESTADO, b"ON")
    print("Bomba encendida")

def apagar_bomba():
    global bomba_estado
    bomba.value(0)
    led.value(0)
    bomba_estado = False
    client.publish(TOPIC_BOMBA_ESTADO, b"OFF")
    print("Bomba apagada")

# ======== CONEXIÓN AL BROKER MQTT ========
def conectar_mqtt():
    global client
    client = MQTTClient(CLIENT_ID, BROKER)
    client.set_callback(callback_mqtt)
    client.connect()
    client.subscribe(TOPIC_BOMBA_CONTROL)
    print("Conectado al broker MQTT:", BROKER)
    print("Suscrito al tema:", TOPIC_BOMBA_CONTROL)

# ======== PROGRAMA PRINCIPAL ========
def main():
    conectar_wifi()
    conectar_mqtt()

    while True:
        client.check_msg()  # Escucha mensajes MQTT

        if not modo_manual:  # Modo automático
            if sensor1.value() == 1 and sensor2.value() == 1:
                if not bomba_estado:
                    encender_bomba()
            else:
                if bomba_estado:
                    apagar_bomba()

        time.sleep(0.2)

# ======== EJECUCIÓN ========
try:
    main()
except KeyboardInterrupt:
    print("Programa detenido")
    client.disconnect()
