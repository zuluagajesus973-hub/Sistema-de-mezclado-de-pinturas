import network
import time

SSID = "Chucho"
PASSWORD = "Chucho123"

def conectar():

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(SSID, PASSWORD)

        t0 = time.time()
        while not wlan.isconnected():
            if time.time() - t0 > 15:
                return False
            time.sleep(1)

    print("WiFi OK:", wlan.ifconfig())
    return True
