# Nombre de la etapa: Resistencias para controlar temperatura de la pintura

## Integrantes
Michael Yesid Velasquez V.- Cod: 94882 Yeison Gabriel Niño J. - Cod: 61096 Carlos Eduardo Puentes L. - Cod: 89466

## Arquitectura propuesta
<img width="724" height="485" alt="image" src="https://github.com/user-attachments/assets/f6a70a1b-818a-462a-9783-3bb44cf8ccfe" />

## Periférico a trabajar
Resistencia, Para calentar pintura.
## Importar configuración desde config.py
try: from config import WIFI_SSID, WIFI_PASS, MQTT_BROKER, MQTT_TOPIC except ImportError: raise Exception("⚠️ Debes crear un archivo config.py con tus credenciales (ver config.py.sample)")

## Configuración I2C y LED
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000) led = Pin(13, Pin.OUT) led.off()

## Umbrales de temperatura
TEMPERATURA_ENCENDER = 20.0 # Encender LED cuando supere 20°C TEMPERATURA_APAGAR = 25.0 # Apagar LED cuando baje de 25°C

## Conectar WiFi
def conectar_wifi(): wlan = network.WLAN(network.STA_IF) wlan.active(True) wlan.connect(WIFI_SSID, WIFI_PASS) print("Conectando a WiFi...", end="") while not wlan.isconnected(): print(".", end="") time.sleep(1) print("\n✅ WiFi conectado:", wlan.ifconfig())

## Conectar MQTT
MQTT_BROKER = "10.171.40.138"  # Broker público para pruebas
# MQTT_BROKER = "192.168.1.100"   # O usa tu broker local
MQTT_PORT = 1883
MQTT_TOPIC_SUB = "esp32/leds/control"
MQTT_TOPIC_PUB = "esp32/leds/status"
CLIENT_ID = "esp32_led_controller_" + str(time.ticks_ms())

## Simulación lectura temperatura
(En práctica puedes leer desde un sensor real como LM75, DHT, etc.)

def leer_temperatura(): # Aquí puedes poner lectura real del sensor return 25 + (time.time() % 10) # Simulación 25°C a 35°C

## Programa principal
def main(): conectar_wifi() client = conectar_mqtt()

# PROGRAMA PRINCIPAL

# Conectar a WiFi
conectar_wifi()

# Buscar dispositivos I2C
dispositivos = buscar_dispositivos_i2c()

if not dispositivos:
    print("ERROR: No hay dispositivos I2C conectados.")
    # Aún así conectar MQTT para control manual del LED
    client = conectar_mqtt()
    lm75_addr = None
else:
    lm75_addr = dispositivos[0]
    print(f"Usando dispositivo I2C en 0x{lm75_addr:02X}")
    client = conectar_mqtt()

# Publicar estado inicial
def mqtt_callback(topic, msg):
    try:
        topic = topic.decode('utf-8')
        msg = msg.decode('utf-8')
        print(f"Mensaje recibido: {topic} -> {msg}")
        
        if topic == MQTT_TOPIC_SUB:
            data = json.loads(msg)
            led_id = data.get("led")
            action = data.get("action")
            interval = data.get("interval")
            
            if led_id in leds:
                if action == "on":
                    leds[led_id].on()
                    led_timers[led_id]["state"] = True
                    led_timers[led_id]["blink_enabled"] = False
                    print(f"LED {led_id} ENCENDIDO")
                    
                elif action == "off":
                    leds[led_id].off()
                    led_timers[led_id]["state"] = False
                    led_timers[led_id]["blink_enabled"] = False
                    print(f"LED {led_id} APAGADO")
                    
              
##  Evidencias de montaje final de resistencias 
![WhatsApp Image 2025-11-10 at 9 34 14 PM (3)](https://github.com/user-attachments/assets/cb6f9c5f-3729-4e82-b8b0-f65a2762e5e6)

![WhatsApp Image 2025-11-10 at 9 34 14 PM](https://github.com/user-attachments/assets/c0af4b7f-a312-4745-95d1-6b771a16ac88)

![WhatsApp Image 2025-11-10 at 9 34 14 PM (1)](https://github.com/user-attachments/assets/f1d1fcd8-23f5-4390-bf6b-52a08768e5b8)

##  visualizacion en node red  resistencias
![WhatsApp Image 2025-11-10 at 9 34 13 PM](https://github.com/user-attachments/assets/1f2a1b64-a84b-4f1a-bfab-782fddbbbdf9)

![WhatsApp Image 2025-11-10 at 9 34 13 PM (1)](https://github.com/user-attachments/assets/0ad2d6ac-25af-4b74-9516-74d182a68031)

## visualizacion de node red on/off resistencias
En este flujo podemos evidenciar el encendido y apagado de cada resistencia por independiente desde node red.

![WhatsApp Image 2025-11-12 at 10 21 04 PM](https://github.com/user-attachments/assets/c4ce088b-5276-4317-a2d0-7da578798aaa)
![WhatsApp Image 2025-11-12 at 10 20 44 PM](https://github.com/user-attachments/assets/82193182-bfaa-4ab0-8d21-4adcf6e19358)
![WhatsApp Image 2025-11-12 at 10 20 28 PM](https://github.com/user-attachments/assets/925b9b61-8021-4c1c-b2c7-5eafb3533a9d)
![WhatsApp Image 2025-11-12 at 10 20 05 PM](https://github.com/user-attachments/assets/71d14297-176f-4494-96df-386e04ff88f5)


### 1. [Flujos](/G05/flujos/flows.json)

### 2. [Programación micropython](/G05/micropython/test.py)


