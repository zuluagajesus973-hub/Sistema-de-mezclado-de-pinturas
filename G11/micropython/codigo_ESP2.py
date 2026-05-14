
from machine import Pin, PWM
from umqtt.simple import MQTTClient
import time
import network

WIFI_SSID = "Chucho"
WIFI_PASS = "Chucho123"

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    print("Conectando a WiFi...", end="")
    while not wlan.isconnected():
        time.sleep(0.3)
        print(".", end="")

    print("\nWiFi conectado:", wlan.ifconfig())

# CONFIG MQTT 
MQTT_BROKER     = "192.168.94.216"
MQTT_PORT       = 1883
MQTT_CLIENT_ID  = b"ESP32_BOMBAS"
MQTT_TOPIC_CMYK = b"esp/out"

# CONFIG BOMBAS
PWM_PINS   = [15, 2, 4, 16, 17]     # Pines de PWM
DIR1_PINS  = [23, 19, 18, 5, 4]     # Pines IN1
DIR2_PINS  = [22, 21, 32, 33, 25]   # Pines IN2

PWM_FREQ = 1000
PWM_GLOBAL = 70   # % duty general

TIEMPOS_BOMBAS_MAX = [5, 5, 5, 5, 5]   # segundos para 100%
MAX_TOTAL_PERCENT = 40

# AGITADOR
AGITADOR_PIN = 26
AGITATOR_TIME_S = 10

# ESTADOS
client = None
pwms = [] 
IN1 = []
IN2 = []

tiempos_bombas_receta = [0.0]*5
receta_lista = False
mezcla_en_progreso = False

temp_ok = [True]*5   # por ahora siempre TRUE (luego lo integramos)
flags = [0]*5

# TOOLS
def _duty_from_percent(p):
    if p < 0:  p = 0
    if p > 100: p = 100
    return int(1023 * (p/100))

# Inicializar PWM + dirección
def init_bombas():
    global pwms, IN1, IN2

    pwms = []
    IN1 = []
    IN2 = []

    for i in range(5):
        pwm = PWM(Pin(PWM_PINS[i]), freq=PWM_FREQ)
        pwm.duty(0)

        pin1 = Pin(DIR1_PINS[i], Pin.OUT)
        pin2 = Pin(DIR2_PINS[i], Pin.OUT)

        pin1.value(0)
        pin2.value(0)

        pwms.append(pwm)
        IN1.append(pin1)
        IN2.append(pin2)

# Modo frenado activo L298N
def frenar_bomba(i):
    IN1[i].value(0)
    IN2[i].value(0)
    pwms[i].duty(1023)  # BRAKE
    time.sleep_ms(300)
    pwms[i].duty(0)

# Encender bomba → succión
def encender_bomba(i):
    IN1[i].value(1)
    IN2[i].value(0)
    pwms[i].duty(_duty_from_percent(PWM_GLOBAL))
    print("Bomba", i+1, "ENCENDIDA")

# Ejecutar por tiempo
def ejecutar_bomba_tiempo(i, t):
    if t <= 0:
        print("Bomba", i+1, "→ tiempo 0, se omite")
        flags[i] = 1
        return

    print("Bomba", i+1, "→", t, "segundos")
    encender_bomba(i)

    start = time.ticks_ms()
    dur = int(t*1000)

    while time.ticks_diff(time.ticks_ms(), start) < dur:
        client.check_msg()
        time.sleep_ms(20)

    print("Frenando bomba", i+1)
    frenar_bomba(i)

    flags[i] = 1

# AGITADOR
agitador = Pin(AGITADOR_PIN, Pin.OUT)
agitador.value(0)

def run_agitador():
    print("Agitando", AGITATOR_TIME_S, "segundos...")
    agitador.value(1)
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < AGITATOR_TIME_S*1000:
        client.check_msg()
        time.sleep_ms(50)
    agitador.value(0)
    print("Agitación terminada")

# PARSEO CMYKW
def parse_cmykw(txt):
    vals = {"C":0,"M":0,"Y":0,"K":0,"W":0}
    for p in txt.split():
        if ":" in p:
            k,v = p.split(":")
            k=k.upper()
            try: vals[k] = int(v)
            except: pass
    return vals

def cmykw_to_tiempos(v):
    total = v["C"]+v["M"]+v["Y"]+v["K"]+v["W"]
    
    if total > MAX_TOTAL_PERCENT and total>0:
        factor = MAX_TOTAL_PERCENT/total
        for k in v:
            v[k] = int(v[k]*factor)

    keys = ["C","M","Y","K","W"]
    tiempos = []
    for i,k in enumerate(keys):
        t = TIEMPOS_BOMBAS_MAX[i]*(v[k]/100)
        tiempos.append(t)
    return tiempos

# MQTT CALLBACK
def mqtt_callback(topic, msg):
    global receta_lista, mezcla_en_progreso, tiempos_bombas_receta

    t = topic.decode()
    s = msg.decode()

    print("\nMQTT:", t, "->", s)

    if t == MQTT_TOPIC_CMYK.decode():
        vals = parse_cmykw(s)
        tiempos = cmykw_to_tiempos(vals)
        tiempos_bombas_receta = tiempos
        receta_lista = True
        mezcla_en_progreso = False
        for i in range(5): flags[i]=0
        print("Receta lista:", tiempos)
        return

# MQTT CONNECT
def connect_mqtt():
    global client
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC_CMYK)
    print("MQTT conectado y suscrito")

# MAIN
def main():
    global receta_lista, mezcla_en_progreso
    connect_mqtt()
    init_bombas()

    print("Sistema listo. Esperando receta...")

    while True:
        client.check_msg()

        if receta_lista and not mezcla_en_progreso:
            mezcla_en_progreso = True
            print("\n INICIANDO MEZCLA ")

            for i in range(5):
                ejecutar_bomba_tiempo(i, tiempos_bombas_receta[i])

            if all(flags):
                print("Todas las bombas terminaron.")
                run_agitador()

            print(" MEZCLA COMPLETA \n")
            receta_lista = False

        time.sleep_ms(50)

# EJECUCIÓN 
conectar_wifi()
main()
