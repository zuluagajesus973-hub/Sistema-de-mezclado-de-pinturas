import network
import time

SSID = "moto 32_3496"          # Nombre de la red WiFi
PASSWORD = "serviciotop2024"      # Contraseña de la red WiFi

def conectar():
    wifi = network.WLAN(network.STA_IF)  
    wifi.active(True)                     

    if not wifi.isconnected():
        print('Conectando a la red WiFi...')
        wifi.connect(SSID, PASSWORD)

        timeout = 15  
        start = time.time()
        while not wifi.isconnected():
            if time.time() - start > timeout:
                print("No se pudo conectar al WiFi.")
                return False
            time.sleep(1)

    if wifi.isconnected():
        print("Conectado a WiFi")
        print("Dirección IP:", wifi.ifconfig()[0])
        return True
    else:
        print("Fallo al conectar.")
        return False