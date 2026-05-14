from machine import Pin, I2C
import time, json
from umqtt.simple import MQTTClient
import network

# ==========================================================
# === CONFIGURACIÓN WiFi ===
# ==========================================================
WIFI_SSID = "Chucho"          
WIFI_PASS = "Chucho123"

# ==========================================================
# === CONFIGURACIÓN MQTT ===
# ==========================================================
BROKER =  "192.168.176.216"     
PORT = 1883                   
TOPIC = b"in/micro/sensor/color"   

# ==========================================================
# === CONFIGURACIÓN SENSOR TCS34725 ===
# ==========================================================
i2c = I2C(1, scl=Pin(22), sda=Pin(21))
ADDR = 0x29  # Dirección I2C del TCS34725

def write_reg(reg, val):
    i2c.writeto_mem(ADDR, 0x80 | reg, bytes([val]))

def read_reg16(reg):
    data = i2c.readfrom_mem(ADDR, 0x80 | reg, 2)
    return data[1] << 8 | data[0]

def init_tcs34725():
    write_reg(0x00, 0x01)   # Power ON
    time.sleep(0.01)
    write_reg(0x00, 0x03)   # Enable RGBC
    write_reg(0x01, 0xD5)   # Integration time 101 ms
    write_reg(0x0F, 0x00)   # Gain 1x

def leer_rgbc():
    clear = read_reg16(0x14)
    red   = read_reg16(0x16)
    green = read_reg16(0x18)
    blue  = read_reg16(0x1A)
    return red, green, blue, clear

# ==========================================================
# === CONVERSIÓN A ESCALA 0–255 ===
# ==========================================================
def convertir_255(r, g, b, coef):
    R = (r - coef["Rmin"]) / (coef["Rmax"] - coef["Rmin"]) * 255
    G = (g - coef["Gmin"]) / (coef["Gmax"] - coef["Gmin"]) * 255
    B = (b - coef["Bmin"]) / (coef["Bmax"] - coef["Bmin"]) * 255
    R = int(max(0, min(255, R)))
    G = int(max(0, min(255, G)))
    B = int(max(0, min(255, B)))
    return R, G, B

# ==========================================================
# === CONEXIÓN WiFi ===
# ==========================================================
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("Conectando a WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\n WiFi conectado:", wlan.ifconfig())
    return wlan

# ==========================================================
# === CALIBRACIÓN ===
# ==========================================================
def calibrar():
    print("\n** Calibración RGB (0–255) **")
    print("1️⃣ Coloca una muestra BLANCA y presiona Enter.")
    input()
    time.sleep(1)
    rb, gb, bb, cb = leer_rgbc()
    print("Blanco:", rb, gb, bb, cb)

    print("2️⃣ Coloca una muestra NEGRA y presiona Enter.")
    input()
    time.sleep(1)
    rn, gn, bn, cn = leer_rgbc()
    print("Negro:", rn, gn, bn, cn)

    coef = {
        "Rmin": rn, "Rmax": rb,
        "Gmin": gn, "Gmax": gb,
        "Bmin": bn, "Bmax": bb
    }

    with open("calib_rgb.json", "w") as f:
        json.dump(coef, f)
    print("✅ Calibración guardada en calib_rgb.json")
    return coef

# ==========================================================
# === PROGRAMA PRINCIPAL ===
# ==========================================================
init_tcs34725()
conectar_wifi()

# Cargar o crear calibración
try:
    with open("calib_rgb.json", "r") as f:
        coef = json.load(f)
        print("✅ Calibración cargada.")
except:
    coef = calibrar()

# Conectar al broker MQTT
client = MQTTClient("esp32_color", BROKER, PORT)
client.connect()
print(f"✅ Conectado al broker MQTT en {BROKER}")

# Bucle principal
while True:
    r, g, b, c = leer_rgbc()
    R255, G255, B255 = convertir_255(r, g, b, coef)

    # Crear JSON forzado en orden R, G, B
    msg = '{"R": %d, "G": %d, "B": %d}' % (R255, G255, B255)

    # Publicar por MQTT
    client.publish(TOPIC, msg)
    print("Enviado:", msg)

    time.sleep(0.5)