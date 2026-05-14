import network
from time import sleep

# === PARÁMETROS WIFI ===
WIFI_SSID = "Chucho" # Android124
WIFI_PASSWORD = "Chucho123"

def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f"Conectando a la red {WIFI_SSID}...")
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            sleep(1)
    print("Conexión WiFi exitosa:", sta_if.ifconfig())
