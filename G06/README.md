# Nombre de la etapa:
Control de Bombas con MQTT (ESP32)
## Integrantes
Steven Herrera 
Carlos Medina
Daniel Camacho

## Documentación


# Control de Bombas CMYKW mediante MQTT y Galgas

## Resumen General

Este proyecto implementa un **sistema de control remoto para cinco bombas peristálticas** correspondientes a los colores del modelo **CMYKW (Cyan, Magenta, Yellow, Black y White)**.  
El control se realiza mediante el **protocolo MQTT**, utilizando un **ESP32 programado en MicroPython**, el cual recibe comandos remotos, **verifica el estado físico mediante galgas** y activa las bombas de forma segura.

Cada bomba está asociada a un **topic MQTT individual**, y su funcionamiento depende tanto del **comando remoto ("ON"/"OFF")** como del **estado lógico de la galga correspondiente**, que actúa como un permiso físico de habilitación.



## Objetivos del Sistema

  -Permitir el **control remoto e independiente** de las cinco bombas CMYKW mediante MQTT.  
  -Implementar una **seguridad lógica y física** con galgas que habilitan o bloquean cada bomba.  
  -Facilitar la **integración con plataformas IoT** (Node-RED, Raspberry Pi, SCADA educativos, etc.).  
  -Servir como **base didáctica** para prácticas de control y comunicaciones con MicroPython y ESP32.  

## Arquitectura del Sistema

### ESP32 con MicroPython
- Conectado por Wi-Fi mediante el módulo personalizado `wify.py`.  
- Suscrito a **cinco topics MQTT**, uno por cada bomba.  
- Controla directamente las **salidas digitales** que alimentan las bombas.  
- Lee las **entradas digitales** de las galgas (una por cada color).  

### Broker MQTT (Ngrok)
- Servidor remoto que **intermedia la comunicación** entre el cliente y el ESP32.  

###  Cliente Remoto (Node-RED / PC)
- Envía comandos `"ON"` o `"OFF"` a los topics específicos de cada color.  

## Funcionamiento Lógico

1. Al iniciar, el ESP32 se **conecta a la red Wi-Fi**.  
2. Luego se **conecta al broker MQTT** y se **suscribe a los cinco topics**:

-bombas/CYAN
-bombas/MAGENTA
-bombas/YELLOW
-bombas/BLACK
-bombas/WHITE


3. En el ciclo principal, el programa **escucha los mensajes MQTT**:

- Si el mensaje es `"ON"` **y la galga está activa (True)** → la bomba se energiza.  
- Si el mensaje es `"OFF"` **o la galga está inactiva (False)** → la bomba se apaga.  

4. Las **galgas actúan como interruptores de seguridad**, evitando la activación de una bomba sin permiso físico.  

## Variables y Componentes Principales

| Elemento | Descripción |
|-----------|-------------|
| **bombas[]** | Lista de objetos `Pin` configurados como **salidas digitales** conectadas a las bombas CMYKW. |
| **flag_*_galga** | Variables booleanas (`True/False`) que representan el **estado de cada galga**. |
| **TOPICS** | Diccionario con los **topics MQTT** para cada color. |
| **mensaje()** | Función *callback* ejecutada al recibir un mensaje MQTT. Controla las bombas según el topic, comando y galga. |
| **conectar_mqtt()** | Función que **establece la conexión** con el broker y realiza la **suscripción a los topics**. |

## Mensajes MQTT Admitidos

| Topic | Mensaje | Acción |
|-------|----------|--------|
| `bombas/CYAN` | `"ON"` / `"OFF"` | Controla la bomba **Cyan** |
| `bombas/MAGENTA` | `"ON"` / `"OFF"` | Controla la bomba **Magenta** |
| `bombas/YELLOW` | `"ON"` / `"OFF"` | Controla la bomba **Amarilla** |
| `bombas/BLACK` | `"ON"` / `"OFF"` | Controla la bomba **Negra** |
| `bombas/WHITE` | `"ON"` / `"OFF"` | Controla la bomba **Blanca** |

## Lógica de Seguridad

Cada **galga actúa como un permiso físico**.  
Si una galga está desactivada (`False`), **la bomba no podrá encenderse**, incluso si se recibe el comando `"ON"`.  
Esto evita fallos eléctricos o activaciones indebidas, garantizando **un control seguro y estable**.

## Ventajas del Diseño

-  **Control remoto seguro** con validación física mediante galgas.  
-  **Separación clara** entre control lógico (galgas) y control remoto (MQTT).  
-  **Sistema modular y escalable**, fácil de ampliar a más bombas o sensores.  
-  **Compatible** con plataformas IoT educativas o industriales.  
- **Ejecución estable** y bajo consumo en ESP32.  

## Tecnologías Utilizadas

- **MicroPython**  
- **ESP32**  
- **MQTT (umqtt.robust)**  
- **Ngrok (Broker remoto)**  
- **Wi-Fi (módulo personalizado `wify.py`)**

## Estructura del Proyecto

Control_Bombas_CMYKW_MQTT

─ main.py # Código principal de control de bombas
─ wify.py # Módulo de conexión Wi-Fi
─ README.md # Documentación del proyecto
─ requirements.txt # Dependencias (opcional)

## Ejemplo de Uso

1. Iniciar el ESP32 con los archivos cargados (`main.py`, `wify.py`).  
2. Conectarse al Wi-Fi automáticamente.  
3. Conectarse al broker MQTT mediante Ngrok.  
4. Enviar comandos desde Node-RED o un cliente MQTT:

Topic: bombas/CYAN
Mensaje: ON 

Si la galga CYAN está activa, la bomba se encenderá.  
Enviar `"OFF"` para apagarla.


### 1. [flujos](/G06/flujos/flows.json)



## Diseño en Canva
Puedes ver el diseño original en este enlace:
[Abrir en Canva](https://www.canva.com/design/DAG4QK7LDeE/3pnAjeRpyq-hxvf97iX1vA/edit?utm_content=DAG4QK7LDeE&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)


### 2. [Programación micropython](/G06/micropython/test.py)

# ============================================================
#  Proyecto: Control de Bombas CMYKW mediante MQTT y Galgas
#  Plataforma: ESP32 con MicroPython
#  Descripción: Este programa permite controlar cinco bombas peristálticas correspondientes a los colores CMYKW (Cyan, Magenta, Yellow, Black y White) mediante el protocolo MQTT. Cada bomba cuenta con una galga que actúa como interruptor de seguridad, habilitando o bloqueando su funcionamiento según condiciones físicas.
# ============================================================

# -------------------- IMPORTACIÓN DE LIBRERÍAS --------------------

import network            # Módulo para conexión Wi-Fi
import time               # Permite pausas o temporización
from machine import Pin   # Control de pines digitales del ESP32
from umqtt.robust import MQTTClient  # Cliente MQTT robusto
import ujson              # Para manejo de datos en formato JSON
import wify               # Módulo personalizado para conexión Wi-Fi

# -------------------- CONFIGURACIÓN DEL BROKER MQTT --------------------

BROKER = "6.tcp.ngrok.io"   # Dirección del broker MQTT (ngrok en este caso)
PORT = 18263                # Puerto TCP asignado al túnel MQTT

# -------------------- DEFINICIÓN DE TOPICS MQTT --------------------
# Cada bomba tiene su propio canal MQTT para recibir órdenes ON/OFF

TOPICS = {
    "CYAN": b"bombas/CYAN",
    "MAGENTA": b"bombas/MAGENTA",
    "YELLOW": b"bombas/YELLOW",
    "BLACK": b"bombas/BLACK",
    "WHITE": b"bombas/WHITE"
}

# -------------------- CONFIGURACIÓN DE PINES --------------------
# Cada bomba está conectada a un pin de salida del ESP32
# Cada galga (sensor o interruptor) está en un pin de entrada

bombas = {
    "CYAN": Pin(12, Pin.OUT),
    "MAGENTA": Pin(13, Pin.OUT),
    "YELLOW": Pin(14, Pin.OUT),
    "BLACK": Pin(27, Pin.OUT),
    "WHITE": Pin(26, Pin.OUT)
}

galgas = {
    "CYAN": Pin(32, Pin.IN),
    "MAGENTA": Pin(33, Pin.IN),
    "YELLOW": Pin(25, Pin.IN),
    "BLACK": Pin(15, Pin.IN),
    "WHITE": Pin(4, Pin.IN)
}

# -------------------- CONEXIÓN A LA RED WI-FI --------------------
# Se usa el módulo personalizado wify.py que contiene una función
# de conexión automática. Esta función se encarga de conectar el
# ESP32 a la red Wi-Fi configurada en ese archivo.

print("Conectando a Wi-Fi...")
wify.connect()             # Llama a la función de conexión del módulo externo
print("Wi-Fi conectada correctamente\n")

# -------------------- FUNCIÓN CALLBACK DE MENSAJES MQTT --------------------
# Esta función se ejecuta automáticamente cada vez que llega un mensaje MQTT.
# Recibe como parámetros el topic (canal) y el mensaje (ON/OFF).
# Su función es determinar qué bomba debe encenderse o apagarse según:
#  1. El topic del mensaje.
#  2. El estado lógico de la galga asociada.

def mensaje(topic, msg):
    try:
        # Decodifica los valores recibidos de bytes a texto
        topic_str = topic.decode()
        msg_str = msg.decode()
        print(f"Mensaje recibido -> Topic: {topic_str} | Mensaje: {msg_str}")

        # Recorre todos los colores definidos en el diccionario de TOPICS
        for color, topico in TOPICS.items():
            # Si el topic recibido corresponde a uno de los definidos
            if topic == topico:
                estado_galga = galgas[color].value()  # Lee el estado de la galga (1 o 0)
                
                # Condición lógica de seguridad:
                # Solo enciende la bomba si el comando es "ON" y la galga está activa (1)
                if msg_str == "ON" and estado_galga == 1:
                    bombas[color].on()   # Activa la bomba
                    print(f"Bomba {color} ENCENDIDA (galga activa)")
                else:
                    bombas[color].off()  # Apaga la bomba
                    print(f"Bomba {color} APAGADA (comando OFF o galga inactiva)")
                    
    except Exception as e:
        # Si ocurre un error (por ejemplo, topic no válido), se muestra en consola
        print(f"Error procesando mensaje MQTT: {e}")

# -------------------- FUNCIÓN PARA CONECTAR AL BROKER MQTT --------------------
# Esta función establece la conexión con el broker MQTT y realiza la suscripción
# a los topics definidos en el diccionario TOPICS.

def conectar_mqtt():
    try:
        print("Conectando al broker MQTT...")
        # Se crea un objeto cliente MQTT con un ID de cliente único
        cliente = MQTTClient("ESP32_CMKW", BROKER, PORT)
        cliente.set_callback(mensaje)  # Asigna la función callback a los mensajes entrantes
        cliente.connect()              # Intenta establecer conexión con el broker
        print("Conexión MQTT establecida correctamente.\n")

        # Se suscribe a todos los topics definidos
        for color, topic in TOPICS.items():
            cliente.subscribe(topic)
            print(f"Suscrito al topic: {topic.decode()}")
        
        return cliente  # Devuelve el objeto cliente para usarlo en el bucle principal

    except Exception as e:
        print(f"Error conectando al broker MQTT: {e}")
        return None  # En caso de fallo, retorna None

# -------------------- PROGRAMA PRINCIPAL --------------------

cliente = conectar_mqtt()  # Llama a la función de conexión

if cliente:
    print("Esperando mensajes MQTT...\n")
    while True:
        try:
            # Verifica si hay nuevos mensajes MQTT disponibles
            cliente.check_msg()
            # Pequeña pausa para evitar saturar el CPU
            time.sleep(0.1)

        except Exception as e:
            # Si se pierde la conexión, intenta reconectarse automáticamente
            print(f"Error en la conexión MQTT: {e}")
            time.sleep(3)
            cliente = conectar_mqtt()

           print("No fue posible establecer conexión MQTT. Reinicie el dispositivo.")


           
else:![Imagen de WhatsApp 2025-11-12 a las 21 20 54_911c1da5](https://github.com/user-attachments/assets/1d85a63e-9ea6-49bc-93d5-34f362265db9)

Esta imagen muestra un panel de control titulado "DSB Bombas" que contiene botones para gestionar cinco bombas identificadas por colores (CYAN, MAGENTA, YELLOW, BLACK, WHITE), donde cada bomba tiene dos comandos independientes: "ON" para activación y "OFF" para desactivación, lo que sugiere la implementación de un sistema de control remoto basado en MQTT donde estos botones enviarían mensajes a los tópicos correspondientes para que un ESP32 o microcontrolador similar ejecute las acciones físicas sobre los actuadores conectados a sus pines GPIO.

_________________________________________________________________________________________________________________________________________________________


   

    
![Imagen de WhatsApp 2025-11-12 a las 21 23 26_a00b6747](https://github.com/user-attachments/assets/8a6209b0-3653-4ff0-9e06-0204b86a53f7)

Esta imagen muestra la interfaz de control y la salida del sistema MQTT en funcionamiento, donde se observa el panel completo con botones ON/OFF para cinco bombas de colores (CYAN, MAGENTA, YELLOW, BLACK, WHITE) y simultáneamente la consola que indica el proceso de conexión a los tópicos MQTT específicos para cada bomba ("bombas/CYAN", "bombas/MAGENTA", etc.), demostrando que el sistema está estableciendo las suscripciones individuales para cada canal de control mientras mantiene disponible la interfaz gráfica para que el usuario envíe comandos de activación y desactivación a cada dispositivo de forma independiente.


_________________________________________________________________________________________________________________________________________________________

INFORME DE IMPLEMENTACIÓN DEL SISTEMA DE BOMBEO PARA MEZCLADOR DE PINTURAS 

1. OBJETIVO DEL PROYECTO

 El objetivo de la implementación, tiene como alcance diseñar y programar el sistema de control para cinco bombas destinadas a la dosificación de pintura en un mezclador automático. Seleccionar y validar los componentes hidráulicos adecuados que garanticen un flujo controlado. Integrar el sistema de bombeo con la plataforma de control basada en micro python, utilizando la ESP32 como microcontrolador y una rapberry Pi como procesador principal. Realizar pruebas funcionales del sistema de bombeo en diferentes condiciones de pintura. Implementar la instalación final de bombas, mangueras, tanques y sistema cisterna elevada, asregurando de esta manera el correcto funcionamiento del proceso de dosificación. 

 
![integrador 1](https://github.com/user-attachments/assets/9c9e24ba-7e81-4d7c-95b3-446d8502b861)

2. Desarrollo del proyecto

  El proyecto comenzó con la necesidad de programar e implementar el sistema de bombeo compuesto por cinco bombas para alimentar el mezclador de pintura. El primer intento de control de flujo se realizó utilizando una electroválvula; el caudal obtenido fue demasiado bajo, por lo que este componente se descartó. Luego se realizaron ensayos utilizando una bomba de diafragma, iniciando con agua para evaluar el funcionamiento general. Durante estas pruebas se identificó la presencia de un residual dentro de la manguera de salida, como alternativa, se instaló electroválvulas a la salida de la bomba, pero este residuo permaneció, después de discutirlo con el equipo y el docente Alfredo Becerra, llegamos a la conclusión de considerar este residual com parte de un porcentaje aceptable dentro del sistema. Luego se procedió a trabajar directamente con vinilo al 100% Se evidenció nuevamente un flujo lento y un alto riesgo de estancamiento debido a la viscosidad, lo cual podría generar daños en el sistema. Por esta razón, se deidió modificar la mezcla, empleando una porción de 50% pintura y 50% agua, permitiendo así un flujo más adecuado. El grupo acordó la ocmpra de vinilos necesarios y se informó a los demás equipos sobre la materia prima de la pintura a utilizar.En cuanto al control, se desarrolló una implementación en Node-RED con un servidor propio, obteniendo un funcionamiento satisfactorio. Al pasar al servidor general, se presentaron problemas de conexión que fueron solucionados con el apoyo de la docente Diana Maldonado. Superada esta etapa, se inició la instalación física de bombas y mangueras. Con apoyo del taller de mecánica de la universidad, se realizaron perforaciones en los tanques y se instalaron acoples para conectar las mangueras tanto a los tanques como a los motores de las bombas. Estos motores fueron conectados a sus respectivos puentes H, previamente programados para su control. Una vez ensamblado el mezclador por el otro equipo, se completó la instalación de las mangueras. Sin embargo, durante las primeras pruebas se identificó que las bombas no sellaban completamente, permitiendo el flujo de pintura aun cuando no estaban activas. Esto impedía un control preciso del volumen suministrado. Se probaron otros modelos de bombas, pero el problema persistía debido a la diferencia de presión generada por la gravedad desde los tanques superiores. Como solución, se instaló un sistema de cisterna elevada, eliminando el flujo continuo causado por la presión gravitacional. Tras implementar esta modificación, las pruebas con varias bombas operando simultáneamente dieron resultados satisfactorios, cumpliendo con los requerimientos iniciales. Finalmente, debido a un cambio de último momento solicitado por el equipo encargado de integrar todo el sistema, fue necesario modificar el cableado de conexión de las bombas. Este nuevo cableado no corresponde a la lógica originalmente programada, por lo que se dejó abierto a realizar adaptaciones adicionales en caso de ser requeridas.

  
![integrador 2](https://github.com/user-attachments/assets/d8f006fe-d5bd-4b31-b18d-bf64acb838d1)

3. TECNOLOGÍAS USADAS

   Lenguaje de programación: Python

  Microcontrolador: ESP32

  Procesador central / servidor: Raspberry Pi

  Interfaz de control: Node-RED

  Componentes de potencia: Puentes H para control de motores

  Componentes hidráulicos: Bombas de diafragma, mangueras, acoples, electroválvulas (en fase de   pruebas)

  4. CONCLUSIONES

  El proceso permitió validar diferentes alternativas de bombeo, descartando las electroválvulas por bajo caudal y el vinilo puro por su alta viscosidad. La mezcla de 50 % pintura y 50 % agua fue la solución más adecuada para garantizar un flujo estable sin comprometer la integridad de las bombas. La implementación del sistema de cisterna elevada resolvió el problema del flujo indeseado causado por la presión gravitacional, permitiendo un control preciso del volumen suministrado. La integración del sistema con ESP32, Raspberry Pi y Node-RED demostró ser funcional y estable, logrando comunicación y control efectivo tras resolver las dificultades de red. Se cumplió el objetivo principal: instalar, programar y validar el funcionamiento de las cinco bombas para el mezclador de pinturas, dejando solo ajustes menores derivados de cambios solicitados por el equipo integrador. El trabajo conjunto con docentes, talleres y otros equipos permitió mejorar la calidad técnica del proyecto y garantizar la operatividad del sistema dentro del prototipo final.

  _________________________________________________________________________________________________________________________________________________________

CÓDIGO FINAL 

from machine import Pin, PWM
from time import sleep, time
from umqtt.robust import MQTTClient
import Wifi

# Constantes del sistema
TIEMPO_100_PORCIENTO = 25          # Tiempo total para succión del 100%
MOTOR_PWM_FREQ = 1000              # Frecuencia PWM para los motores
SEGUNDOS_ENTRE_MOTORES = 2         # Pausa entre motores

# Variables de motores del tanque final
TIEMPO_FINAL_MOTOR = 3             # Tiempo para bajar/agitar/subir
PAUSA_FINAL = 2                    # Pausa entre secuencias

# MQTT - Configuración del broker
MQTT_BROKER = "192.168.59.216"
MQTT_PORT = 1883
MQTT_CLIENT_ID = b"ESP32_BOMBAS"
MQTT_TOPIC_IN = b"esp/out"         # Topic donde llega el setpoint de mezcla

# Topics de estado para actualizar el dashboard
TOPIC_ESTADO_BOMBAS = b"in/esp2/bombas/estado"
TOPIC_AGITADOR = b"agitador/estado"
TOPIC_ELEVADOR = b"elevador/estado"

# Configuración de motores base (bombas)
COLORES_MOTORES = [
    ("CIAN",    26, 27, 25, 'C'),
    ("MAGENTA", 32, 33, 23, 'M'),
    ("YELLOW",  13, 19, 14, 'Y'),
    ("BLACK",   21, 4, 5, 'K'),
    ("WHITE",   12, 22, 2, 'W'),
]

MOTORES = []  # Contendrá todos los motores inicializados

# Pines de motores del tanque final
ELEVADOR_IN1_PIN = 15
ELEVADOR_IN2_PIN = 16
AGITADOR_IN1_PIN = 17
AGITADOR_IN2_PIN = 18

MOTOR_ELEVADOR = {}
MOTOR_AGITADOR = {}

def inicializar_motores():
    # Inicialización de las 5 bombas dosificadoras
    for color, pin_in1, pin_in2, pin_ena, clave in COLORES_MOTORES:
        try:
            IN1 = Pin(pin_in1, Pin.OUT)
            IN2 = Pin(pin_in2, Pin.OUT)
            ENA_PWM = PWM(Pin(pin_ena), freq=MOTOR_PWM_FREQ)
            IN1.value(0)
            IN2.value(0)
            ENA_PWM.duty(0)
            MOTORES.append({'color': color, 'clave': clave, 'in1': IN1, 'in2': IN2, 'ena': ENA_PWM})
        except Exception as e:
            print(f"Error en motor {color}: {e}")

    # Motores del tanque final
    try:
        MOTOR_ELEVADOR['in1'] = Pin(ELEVADOR_IN1_PIN, Pin.OUT)
        MOTOR_ELEVADOR['in2'] = Pin(ELEVADOR_IN2_PIN, Pin.OUT)
        MOTOR_AGITADOR['in1'] = Pin(AGITADOR_IN1_PIN, Pin.OUT)
        MOTOR_AGITADOR['in2'] = Pin(AGITADOR_IN2_PIN, Pin.OUT)
        MOTOR_ELEVADOR['in1'].value(0)
        MOTOR_ELEVADOR['in2'].value(0)
        MOTOR_AGITADOR['in1'].value(0)
        MOTOR_AGITADOR['in2'].value(0)
    except Exception as e:
        print(f"Error al inicializar tanque final: {e}")

def motor_apagar_total(motor):
    # Apaga PWM si el motor lo usa
    if 'ena' in motor:
        motor['ena'].duty(0)
    motor['in1'].value(0)
    motor['in2'].value(0)

def motor_succionar(motor, tiempo_segundos):
    # Publica estado ON
    msg_on = '{"bomba":"%s", "estado":"ON", "tiempo":%.2f}' % (motor['color'], tiempo_segundos)
    client.publish(TOPIC_ESTADO_BOMBAS, msg_on)
    # Activa motor (gira en una dirección)
    motor['in1'].value(1)
    motor['in2'].value(0)
    motor['ena'].duty(800)
    # Tiempo succión
    sleep(tiempo_segundos)
    # Apaga motor y publica OFF
    motor_apagar_total(motor)
    msg_off = '{"bomba":"%s", "estado":"OFF"}' % motor['color']
    client.publish(TOPIC_ESTADO_BOMBAS, msg_off)

def Elevador_agitador():
    # 1. Bajada del elevador
    client.publish(TOPIC_ELEVADOR, b"DOWN")
    MOTOR_ELEVADOR['in1'].value(1)
    MOTOR_ELEVADOR['in2'].value(0)
    sleep(TIEMPO_FINAL_MOTOR)
    motor_apagar_total(MOTOR_ELEVADOR)
    client.publish(TOPIC_ELEVADOR, b"STOP")
    sleep(PAUSA_FINAL)

    # 2. Agitación
    client.publish(TOPIC_AGITADOR, b"ON")
    MOTOR_AGITADOR['in1'].value(1)
    MOTOR_AGITADOR['in2'].value(0)
    sleep(TIEMPO_FINAL_MOTOR)
    motor_apagar_total(MOTOR_AGITADOR)
    client.publish(TOPIC_AGITADOR, b"OFF")
    sleep(PAUSA_FINAL)

    # 3. Subida del elevador
    client.publish(TOPIC_ELEVADOR, b"UP")
    MOTOR_ELEVADOR['in1'].value(0)
    MOTOR_ELEVADOR['in2'].value(1)
    sleep(TIEMPO_FINAL_MOTOR)
    motor_apagar_total(MOTOR_ELEVADOR)
    client.publish(TOPIC_ELEVADOR, b"STOP")

def parse_mqtt_message(msg):
    # Convierte el mensaje tipo "C:20 M:30 Y:50" en tiempos de succión
    msg_str = msg.decode().strip()
    tiempos = {}
    suma = 0
    for item in msg_str.split():
        if ":" not in item:
            continue
        clave, valor = item.split(":")
        try:
            porcentaje = int(valor)
        except:
            return None
        suma += porcentaje
        tiempos[clave.upper()] = (porcentaje / 100) * TIEMPO_100_PORCIENTO
    return tiempos if suma == 100 else None

def on_message(topic, msg):
    # Procesa el setpoint recibido
    if topic != MQTT_TOPIC_IN:
        return
    tiempos = parse_mqtt_message(msg)
    if tiempos is None:
        return

    # Ejecución de succión
    for i, motor in enumerate(MOTORES):
        t = tiempos.get(motor['clave'], 0)
        if t > 0:
            motor_succionar(motor, t)
            if i < len(MOTORES) - 1:
                sleep(SEGUNDOS_ENTRE_MOTORES)

    # Secuencia final
    Elevador_agitador()

# Conexión WiFi
if not Wifi.conectar():
    while True:
        sleep(1)

# Inicialización
inicializar_motores()
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
client.set_callback(on_message)
client.connect()
client.subscribe(MQTT_TOPIC_IN)

# Loop principal
while True:
    client.check_msg()
    sleep(0.1)
