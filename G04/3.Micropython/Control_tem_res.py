import time
import machine
import onewire
import ds18x20
from umqtt.robust import MQTTClient
import Wifi
from machine import Pin, I2C
import json

#   WIFI
if not Wifi.conectar():
    print("Error WiFi")
    while True:
        time.sleep(1)

print("WiFi conectado\n")

#   MQTT
MQTT_BROKER = "192.168.59.216"
MQTT_PORT   = 1883
MQTT_ID     = "esp1_temperaturas"

TOPICS_TEMP = [
    b"in/esp1/temperatura/azul",
    b"in/esp1/temperatura/rojo",
    b"in/esp1/temperatura/amarillo",
    b"in/esp1/temperatura/negro",
    b"in/esp1/temperatura/blanco"
]

TOPIC_COLOR = b"in/micro/sensor/color"
TOPIC_OUT   = b"esp/out"

def on_message(topic, msg):
    print("\nMensaje recibido")
    print("Topic:", topic)
    print("Msg:", msg)

client = MQTTClient(MQTT_ID, MQTT_BROKER, port=MQTT_PORT)
client.set_callback(on_message)
client.connect()
client.subscribe(TOPIC_OUT)
print("MQTT conectado\n")

#   PINES
PINES_SENSORES = [15, 2, 4, 5, 32]
PINES_RESISTENCIAS = [33, 25, 26, 27, 14]

#   SENSORES DS18B20
sensores = []
estado_sensores = []

for pin in PINES_SENSORES:
    ow = onewire.OneWire(machine.Pin(pin))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()

    sensores.append(ds)
    estado_sensores.append({
        "roms": roms,
        "fallos": 0,
        "estado": "OK" if roms else "SIN_ROM"
    })

    print(f"Sensor en pin {pin}: {roms}")

#   RESISTENCIAS
resistencias = []
for pin in PINES_RESISTENCIAS:
    r = machine.Pin(pin, machine.Pin.OUT)
    r.value(0)
    resistencias.append(r)

TEMP_MIN = 22.0
TEMP_MAX = 27.0
TIEMPO_MAX_RESISTENCIA = 60
INTERVALO_LECTURA = 5

resistencia_activa = None
tiempo_inicio_resistencia = None


def apagar_todas():
    global resistencia_activa, tiempo_inicio_resistencia
    for r in resistencias:
        r.value(0)
    resistencia_activa = None
    tiempo_inicio_resistencia = None
    print("Todas las resistencias apagadas\n")

#   SENSOR TCS34725
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
ADDR = 0x29

# Detección del sensor
dispositivos = i2c.scan()
print("I2C detectados:", dispositivos)

sensor_color_presente = (ADDR in dispositivos)

def write_reg(reg, val):
    try:
        i2c.writeto_mem(ADDR, 0x80 | reg, bytes([val]))
        return True
    except:
        return False

def read_reg16(reg):
    try:
        data = i2c.readfrom_mem(ADDR, 0x80 | reg, 2)
        return (data[1] << 8) | data[0]
    except:
        return None

def init_tcs34725():
    if not write_reg(0x00, 0x01):
        return False

    time.sleep(0.01)
    if not write_reg(0x00, 0x03):
        return False

    write_reg(0x01, 0xD5)
    write_reg(0x0F, 0x00)

    return True

if sensor_color_presente:
    if init_tcs34725():
        print("Sensor de color inicializado")
    else:
        print("Error inicializando sensor → desactivado")
        sensor_color_presente = False
else:
    print("Sensor de color NO detectado → desactivado")

# Cargar calibración
try:
    with open("calib_rgb.json", "r") as f:
        coef = json.load(f)
        print("Calibración cargada.")
except:
    coef = {"Rmin":0,"Rmax":4095,"Gmin":0,"Gmax":4095,"Bmin":0,"Bmax":4095}
    print("Sin calibración, usando valores por defecto")

def leer_rgb():
    r = read_reg16(0x16)
    g = read_reg16(0x18)
    b = read_reg16(0x1A)
    c = read_reg16(0x14)

    if None in [r, g, b, c]:
        return None

    return r, g, b, c

def convertir_255(r, g, b):
    R = (r - coef["Rmin"]) / (coef["Rmax"] - coef["Rmin"]) * 255
    G = (g - coef["Gmin"]) / (coef["Gmax"] - coef["Gmin"]) * 255
    B = (b - coef["Bmin"]) / (coef["Bmax"] - coef["Bmin"]) * 255
    return max(0,int(R)), max(0,int(G)), max(0,int(B))

#   BUCLE PRINCIPAL
print("ESP1 listo!\n")

while True:
    print("\033[2J\033[H")
    client.check_msg()

    temperaturas = []

    #   LECTURA TEMPERATURAS
    for i, ds in enumerate(sensores):
        registro = estado_sensores[i]
        roms = registro["roms"]

        if not roms:
            registro["fallos"] += 1
            registro["estado"] = "SIN_ROM"
            temperaturas.append(None)
            print(f"Sensor {i+1}: SIN_ROM")
            continue

        try:
            ds.convert_temp()
            time.sleep_ms(750)

            temp = ds.read_temp(roms[0])
            registro["fallos"] = 0
            registro["estado"] = "OK"
            temperaturas.append(temp)

            print(f"Sensor {i+1}: {temp} °C")
            client.publish(TOPICS_TEMP[i], str(temp))

        except:
            registro["fallos"] += 1
            temperaturas.append(None)
            registro["estado"] = "ERROR"
            print(f"Sensor {i+1}: ERROR")

    #   CONTROL RESISTENCIAS
    for i, temp in enumerate(temperaturas):
        if temp is None:
            continue

        if temp < TEMP_MIN:
            if resistencia_activa not in [None, i]:
                continue
            if resistencia_activa is None:
                print(f"Encendiendo resistencia {i+1}")
                resistencias[i].value(1)
                resistencia_activa = i
                tiempo_inicio_resistencia = time.time()

        elif temp > TEMP_MAX:
            if resistencia_activa == i:
                print(f"Apagando resistencia {i+1}")
                resistencias[i].value(0)
                resistencia_activa = None

    if resistencia_activa is not None:
        if time.time() - tiempo_inicio_resistencia > TIEMPO_MAX_RESISTENCIA:
            print("Tiempo máximo alcanzado")
            apagar_todas()


    #   SENSOR DE COLOR
    if sensor_color_presente:
        lectura = leer_rgb()

        if lectura:
            r, g, b, c = lectura
            R255, G255, B255 = convertir_255(r, g, b)
            msg = '{"R":%d,"G":%d,"B":%d}' % (R255, G255, B255)
            client.publish(TOPIC_COLOR, msg)
            print("Color enviado:", msg)
        else:
            print("Error leyendo color (no se publica)")
    else:
        print("Sensor de color desactivado")

    time.sleep(INTERVALO_LECTURA)
