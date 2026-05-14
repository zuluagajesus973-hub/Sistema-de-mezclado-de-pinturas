from machine import Pin, PWM
from umqtt.simple import MQTTClient
import network
import time

# =======================
# CONFIGURACIÓN WiFi y MQTT
# =======================
WIFI_SSID     = "Chucho"
WIFI_PASSWORD = "Chucho123"

MQTT_BROKER     = "192.168.149.216"
MQTT_PORT       = 1883
MQTT_CLIENT_ID  = b"ESP32_BOMBAS"

MQTT_TOPIC_CMYK = b"esp/out"

# Topics de estado de temperatura / válvulas (1..5)
VALVE_TOPICS = [
    b"esp2/pintura/valvula1",  # bomba 1 -> C
    b"esp2/pintura/valvula2",  # bomba 2 -> M
    b"esp2/pintura/valvula3",  # bomba 3 -> Y
    b"esp2/pintura/valvula4",  # bomba 4 -> K
    b"esp2/pintura/valvula5",  # bomba 5 -> W
]

# =======================
# CONFIGURACIÓN BOMBAS
# =======================

PWM_PINS   = [15, 2, 0, 16, 17]   # 5 bombas
PWM_FREQ   = 1000                 # Hz
PWM_GLOBAL = 70                   # % duty global

# Tiempo MAX para 100% de cada bomba (en segundos)
TIEMPOS_BOMBAS_MAX = [5, 5, 5, 5, 5]


MAX_TOTAL_PERCENT = 40    # suma(C+M+Y+K+W) <= 40

# =======================
# CONFIGURACIÓN AGITADOR
# =======================
AGITATOR_PIN_NUM = 18   # pin del motor agitador
AGITATOR_TIME_S  = 10   # segundos de agitación

# =======================
# ESTADO GLOBAL
# =======================

client = None

pwms = []

# tiempos de esta receta (segundos por bomba)
tiempos_bombas_receta = [0.0] * 5

# flags de que cada bomba ya terminó
flags = [0] * 5

# receta lista para ejecutar
receta_lista = False

# mezcla en curso
mezcla_en_progreso = False

temp_ok = [False] * 5

# =======================
# UTILIDADES HARDWARE
# =======================

def _duty_from_percent(pct):
    if pct < 0:
        pct = 0
    if pct > 100:
        pct = 100
    return int(1023 * (pct / 100.0))

def init_pwms():
    global pwms
    pwms = []
    for n in PWM_PINS:
        p = PWM(Pin(n), freq=PWM_FREQ)
        p.duty(0)
        pwms.append(p)
    aplicar_pwm_global()

def aplicar_pwm_global():
    duty = _duty_from_percent(PWM_GLOBAL)
    for p in pwms:
        p.duty(duty)

def reset_flags_all():
    global flags
    flags = [0]*5
    print("Flags reseteadas:", flags)

# agitador
agitador = Pin(AGITATOR_PIN_NUM, Pin.OUT)
agitador.value(0)

def run_agitador():
    print("Iniciando agitador por {} s".format(AGITATOR_TIME_S))
    agitador.value(1)
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < AGITATOR_TIME_S * 1000:
        if client is not None:
            try:
                client.check_msg()
            except:
                pass
        time.sleep_ms(50)
    agitador.value(0)
    print("Agitador apagado")
    reset_flags_all()

# =======================
# WIFI
# =======================

def connect_wifi():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        print("Conectando a WiFi...")
        sta.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta.isconnected():
            time.sleep(0.5)
    print("WiFi conectado:", sta.ifconfig())

# =======================
# PARSEO CMYKW
# =======================

def parse_cmykw(text):
    """
    text: 'C:10 M:0 Y:0 K:90 W:0'
    -> {'C':10,'M':0,'Y':0,'K':90,'W':0}
    """
    values = {'C':0, 'M':0, 'Y':0, 'K':0, 'W':0}
    parts = text.replace(',', ' ').split()
    for p in parts:
        if ':' in p:
            k, v = p.split(':', 1)
            k = k.strip().upper()
            v = v.strip()
            if k in values:
                try:
                    values[k] = int(v)
                except:
                    pass
    return values

def cmykw_to_tiempos(values):
    """
    Aplica límite MAX_TOTAL_PERCENT y convierte % a tiempo por bomba.
    Orden bombas: 1->C, 2->M, 3->Y, 4->K, 5->W
    """
    total = values['C'] + values['M'] + values['Y'] + values['K'] + values['W']
    if total > MAX_TOTAL_PERCENT and total > 0:
        factor = MAX_TOTAL_PERCENT / float(total)
        print("Suma CMYKW={} > {}, escalando por factor {:.3f}".format(
            total, MAX_TOTAL_PERCENT, factor))
        for k in values:
            values[k] = int(round(values[k] * factor))

    keys = ['C', 'M', 'Y', 'K', 'W']
    tiempos = []
    for i, k in enumerate(keys):
        pct = values[k]
        tmax = TIEMPOS_BOMBAS_MAX[i]
        t = tmax * (pct / 100.0)
        tiempos.append(t)

    print("CMYKW ajustado:", values)
    print("Tiempos calculados (s):", tiempos)
    return tiempos

# =======================
# CONTROL DE BOMBAS (modo tiempo)
# =======================

def encender_bomba(i):
    pwms[i].duty(_duty_from_percent(PWM_GLOBAL))
    print("Bomba {} ENCENDIDA".format(i+1))

def apagar_bomba(i):
    pwms[i].duty(0)
    print("Bomba {} APAGADA".format(i+1))

def ejecutar_bomba_tiempo(i, t_seg):
    """
    Ejecuta bomba i por t_seg segundos si:
    - t_seg > 0
    - temp_ok[i] == True
    """
    global flags

    if t_seg <= 0:
        print("Bomba {} -> tiempo 0s, se omite".format(i+1))
        flags[i] = 1
        return

    if not temp_ok[i]:
        print("Bomba {}: temperatura NO OK (valvula{} != ON), se omite".format(i+1, i+1))
        flags[i] = 1
        return

    print("Bomba {} -> tiempo programado: {:.2f} s".format(i+1, t_seg))
    encender_bomba(i)
    start = time.ticks_ms()
    dur_ms = int(t_seg * 1000)
    while time.ticks_diff(time.ticks_ms(), start) < dur_ms:
        if client is not None:
            try:
                client.check_msg()
            except:
                pass
        time.sleep_ms(50)
    apagar_bomba(i)
    flags[i] = 1
    print("Bomba {} completó turno.".format(i+1))

# =======================
# MQTT
# =======================

def mqtt_callback(topic, msg):
    global tiempos_bombas_receta, receta_lista, mezcla_en_progreso, temp_ok

    t = topic.decode() if isinstance(topic, bytes) else str(topic)
    s = msg.decode() if isinstance(msg, bytes) else str(msg)

    print("\n=== MENSAJE MQTT RECIBIDO ===")
    print("Topic :", t)
    print("Texto :", s)

    # 1) Receta CMYKW
    if t == MQTT_TOPIC_CMYK.decode():
        vals = parse_cmykw(s)
        tiempos = cmykw_to_tiempos(vals)
        tiempos_bombas_receta = tiempos
        receta_lista = True
        mezcla_en_progreso = False
        reset_flags_all()
        print("Receta actualizada desde MQTT.\n")
        return

    # 2) Estados de válvulas 1..5 (temperatura OK por bomba)
    for i in range(5):
        if t == VALVE_TOPICS[i].decode():
            val = s.strip().upper()
            temp_ok[i] = (val in ("ON", "1", "TRUE"))
            print("Temp OK bomba {} ({}): {}".format(i+1, VALVE_TOPICS[i], temp_ok[i]))
            return

def connect_mqtt():
    global client
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    print("MQTT conectado a {}:{}".format(MQTT_BROKER, MQTT_PORT))
    client.subscribe(MQTT_TOPIC_CMYK)
    for t in VALVE_TOPICS:
        client.subscribe(t)
    print("Suscrito a:", MQTT_TOPIC_CMYK, "y", VALVE_TOPICS)

# =======================
# PROGRAMA PRINCIPAL
# =======================

def main():
    global receta_lista, mezcla_en_progreso

    connect_wifi()
    init_pwms()
    connect_mqtt()

    print("\nSistema 5 bombas en modo TIEMPO por CMYKW preparado.")
    print("Esperando receta en", MQTT_TOPIC_CMYK,
          "y estados de válvulas en", VALVE_TOPICS)

    while True:
        # Escuchar MQTT
        if client is not None:
            try:
                client.check_msg()
            except:
                pass

        # Si hay receta y no hay mezcla en progreso, iniciar secuencia
        if receta_lista and not mezcla_en_progreso:
            mezcla_en_progreso = True
            print("\n*** Iniciando secuencia de bombas ***")

            for i in range(5):
                ejecutar_bomba_tiempo(i, tiempos_bombas_receta[i])

            if all(flags):
                print("\nTodas las bombas terminaron (trabajaron o fueron omitidas).")
                print("Activando agitador...")
                run_agitador()

            print("*** Fin de secuencia de bombas ***\n")
            mezcla_en_progreso = False
            receta_lista = False

        time.sleep_ms(100)

# Ejecutar
main()
