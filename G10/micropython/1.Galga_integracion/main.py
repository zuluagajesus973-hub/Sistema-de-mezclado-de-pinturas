# CÓDIGO BÁSCULA ESP32 PARA NODE-RED CON TARA INDIVIDUAL v7 (OPTIMIZADO POR EMA)

from machine import Pin, freq, reset
from time import sleep, time
import sys
from hx711 import HX711
from umqtt.simple import MQTTClient

# Importar WiFi desde archivo externo
from wafi import conectar_wifi

# --- Configuración del Sistema ---
freq(240000000)

# =========================================================================
# === PARÁMETROS DE RED Y MQTT ===
# =========================================================================
MQTT_BROKER = "192.168.94.216" 
MQTT_PORT = 1883 
MQTT_CLIENT_ID = "esp32_bascula_casa_01"

# Tópicos Base
TOPIC_PUB_PESO_BASE = b"in/bascula/peso"
TOPIC_SUB_COMANDO_WILDCARD = b"bascula/comando/"

# =========================================================================
# === CONFIGURACIÓN DE LAS 5 GALGAS ===
# =========================================================================
GALGAS_CONFIG = [
    {"nombre": "Cyan", "id": "Cyan", "pin_dt": 12, "pin_sck": 13, "calibracion":400},
    {"nombre": "Magenta", "id": "Magenta", "pin_dt": 14, "pin_sck": 27, "calibracion": 587},
    {"nombre": "Yellow", "id": "Yellow", "pin_dt": 25, "pin_sck": 26, "calibracion": 587},
    {"nombre": "key", "id": "key", "pin_dt": 32, "pin_sck": 33, "calibracion": 587},
    {"nombre": "White", "id": "White", "pin_dt": 4, "pin_sck": 16, "calibracion": 587},
]

# Parámetros generales
GALGA_TARA_SAMPLES = 200 # Se mantiene alto para la TARA (proceso lento y único)
PIN_BOTON_TARA = 0

# =========================================================================
# === NUEVAS VARIABLES PARA EL FILTRO EXPONENCIAL (EMA) ===
# =========================================================================
# FACTOR_SUAVIZADO (Alpha): 0.3 es un buen punto de partida. AJUSTAR según pruebas.
FACTOR_SUAVIZADO = 0.2
# Lista global que almacena el ÚLTIMO valor suave de cada báscula (la 'memoria' del filtro)
# Se inicializa correctamente dentro de bascula_principal_loop
pesos_suavizados = [] 


# --- Banderas y Variables Globales ---
tara_solicitada_idx = -1
galga_activa_idx = 0

# =========================================================================
# === FUNCIONES DE CALLBACK Y CONEXIÓN ===
# =========================================================================

def sub_callback(topic, msg):
    global tara_solicitada_idx
    
    topic_str = topic.decode()
    msg_str = msg.decode()
    print(f"\n[MQTT] Mensaje recibido -> Tópico: {topic_str}, Mensaje: {msg_str}")

    if msg_str == "TARA" and topic_str.startswith("bascula/comando/"):
        id_bascula = topic_str.split('/')[-1]
        
        for i, config in enumerate(GALGAS_CONFIG):
            if config["id"] == id_bascula:
                print(f"[MQTT] ¡Solicitud de TARA recibida para {config['nombre']} (ID: {id_bascula})!")
                tara_solicitada_idx = i 
                return 

def manejador_interrupcion_tara(pin):
    global tara_solicitada_idx, galga_activa_idx
    if tara_solicitada_idx == -1:
        print(f"\n[BOTÓN] ¡Botón físico presionado! Solicitando TARA para la galga activa: {GALGAS_CONFIG[galga_activa_idx]['nombre']}")
        tara_solicitada_idx = galga_activa_idx

# =========================================================================
# === FUNCIÓN PRINCIPAL ===
# =========================================================================
def bascula_principal_loop():
    global tara_solicitada_idx, galga_activa_idx, pesos_suavizados
    
    # --- Conexiones Iniciales ---
    conectar_wifi()
    print(f"Conectando al broker MQTT: {MQTT_BROKER}:{MQTT_PORT}...")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(sub_callback)
    client.connect()
    client.subscribe(TOPIC_SUB_COMANDO_WILDCARD)
    print(f"Conectado a MQTT y suscrito al tópico: {TOPIC_SUB_COMANDO_WILDCARD.decode()}")

    # --- Inicialización de las 5 Galgas ---
    sensores_hx = []
    pesos_suavizados = [] # Reinicia la memoria
    print("\nInicializando galgas...")
    for config in GALGAS_CONFIG:
        print(f"   -> Configurando {config['nombre']}...")
        hx = HX711(Pin(config['pin_dt']), Pin(config['pin_sck']))
        hx.wakeUp()
        hx.kanal(1)
        print(f"     Realizando TARA inicial...")
        hx.tara(GALGA_TARA_SAMPLES)
        hx.calFaktor(config['calibracion'])
        
        # PRE-CARGA DE LA MEMORIA DEL FILTRO
        # Leemos 20 muestras estables para iniciar la memoria EMA sin un valor de 0
        lectura_inicial_suave = hx.masse(20) 
        pesos_suavizados.append(lectura_inicial_suave)
        
        sensores_hx.append(hx)
    print("¡Todas las galgas listas y memoria EMA precargada!")

    # --- Configuración del Botón ---
    boton = Pin(PIN_BOTON_TARA, Pin.IN, Pin.PULL_UP)
    boton.irq(trigger=Pin.IRQ_FALLING, handler=manejador_interrupcion_tara)
    print(f"Botón físico configurado en pin {PIN_BOTON_TARA}.")
    print("------------------------------------------")

    # --- Bucle Principal de Medición ---
    ultimas_lecturas = ["0,00"] * len(GALGAS_CONFIG)

    while True:
        # 1. Revisa mensajes MQTT (actualizará tara_solicitada_idx si llega un comando)
        client.check_msg()

        # 2. PROCESO DE TARA PRIORITARIO: 
        if tara_solicitada_idx != -1:
            config_tara = GALGAS_CONFIG[tara_solicitada_idx]
            hx_tara = sensores_hx[tara_solicitada_idx]
            
            print(f"\n[TARA] Procesando solicitud para {config_tara['nombre']}...")
            hx_tara.tara(GALGA_TARA_SAMPLES)
            
            # **IMPORTANTE: Actualizar la memoria EMA después de la tara**
            pesos_suavizados[tara_solicitada_idx] = hx_tara.masse(20)
            print(f"[TARA] ¡Nueva TARA completada y memoria EMA reiniciada para {config_tara['nombre']}!")
            
            tara_solicitada_idx = -1
            #sleep(0.05) 
            continue # Volver al inicio del bucle para la lectura normal

        # 3. PROCESO DE LECTURA SECUENCIAL: Rápido y con filtro EMA
        hx_activo = sensores_hx[galga_activa_idx]
        config_activa = GALGAS_CONFIG[galga_activa_idx]

        # Tomamos SOLO 1 muestra: Máxima velocidad.
        lectura_actual_raw = hx_activo.masse(1) 

        # Aplicamos el FILTRO EXPONENCIAL (EMA)
        peso_anterior = pesos_suavizados[galga_activa_idx]
        
        nuevo_peso_suave = (lectura_actual_raw * FACTOR_SUAVIZADO) + (peso_anterior * (1.0 - FACTOR_SUAVIZADO))
        
        # Actualizamos la memoria del filtro
        pesos_suavizados[galga_activa_idx] = nuevo_peso_suave

        # Usamos el valor suavizado para el resto del proceso
        m_str = "{:0.2f}".format(nuevo_peso_suave)
        
        # *** CAMBIO: Actualiza la lista con la nueva lectura ***
        ultimas_lecturas[galga_activa_idx] = m_str.replace('.', ',')

        # Imprime estado (igual que antes)
        linea_estado = ""
        for i, lectura in enumerate(ultimas_lecturas):
            linea_estado += f"B{i+1}: {lectura} g | "
        print(linea_estado, end='\r')

        # 4. Publica el valor en su tópico MQTT específico
        topic_galga_actual = f"{TOPIC_PUB_PESO_BASE.decode()}/{config_activa['id']}".encode()
        client.publish(topic_galga_actual, m_str.encode())

        # 5. Avanza a la siguiente galga para la próxima iteración
        galga_activa_idx = (galga_activa_idx + 1) % len(GALGAS_CONFIG)

        # 6. Mínima pausa para evitar saturación de CPU, puede probarse en 0.0
        sleep(0.01)

# =========================================================================
# === PUNTO DE ENTRADA ===
# =========================================================================
if __name__ == "__main__":
    try:
        bascula_principal_loop()
    except Exception as e:
        print(f"\nError fatal en el bucle principal: {e}")
        print("Reiniciando el dispositivo en 10 segundos...")
        sleep(10)
        reset()