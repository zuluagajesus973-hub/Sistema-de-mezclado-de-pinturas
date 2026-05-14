# Tomar foto mediante NODE-red
import paho.mqtt.client as mqtt
import subprocess
import time
import os

BROKER = "localhost"
TOPIC_TRIGGER = "camara/captura"
TOPIC_PUBLISH = "camara/pi"
TMP_JPG = "/tmp/foto_node_red.jpg"

def tomar_y_publicar():
    # 1) tomar foto
    cmd_capture = f"libcamera-jpeg -o {TMP_JPG} --width 640 --height 480"
    p = subprocess.run(cmd_capture, shell=True)
    if p.returncode != 0:
        print("ERROR: libcamera-jpeg falló", p.returncode)
        return

    # 2) codificar y publicar por mosquitto_pub
    cmd_pub = f'base64 {TMP_JPG} | bash -c \'echo -n "data:image/jpeg;base64,"; cat\' | mosquitto_pub -h {BROKER} -t {TOPIC_PUBLISH} -s'
    p2 = subprocess.run(cmd_pub, shell=True)
    if p2.returncode == 0:
        print("Foto tomada y publicada en", TOPIC_PUBLISH)
    else:
        print("ERROR publicando imagen", p2.returncode)

def on_connect(client, userdata, flags, rc):
    print("Conectado al broker, rc=", rc)
    client.subscribe(TOPIC_TRIGGER)

def on_message(client, userdata, msg):
    payload = msg.payload.decode() if isinstance(msg.payload, bytes) else msg.payload
    print("Mensaje recibido en", msg.topic, ":", payload)
    if payload.lower().strip() in ("capturar", "1", "take"):
        tomar_y_publicar()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Detenido por teclado")
