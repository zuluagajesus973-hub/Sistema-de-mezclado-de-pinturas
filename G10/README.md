[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21147975&assignment_repo_type=AssignmentRepo)
# Proyecto integrador avance 1/11/2025

## Integrantes

[Karen Lizeth Sosa](https://github.com/karenlsosam-hub)  -  GRUPO 10

[Michael Mendez](https://github.com/michaelsmendezm-collab)  -  GRUPO 10

[Juan Acosta](https://github.com/juanfacostap-wq)  -  GRUPO 10

[Julian Rodriguez](https://github.com/juliandrodriguezp-ops)  -  GRUPO 8

[Edwin Correa](https://github.com/ECORREA-96)  -  GRUPO 8

[Ricardo Sabogal]( https://github.com/ricardosr-82)  -  GRUPO 8

## Objetivo

Implementar un sistema de lectura de peso mediante galgas extensiométricas conectadas a sus respectivos módulos HX711, los cuales entregan los valores digitales a una ESP32. De esta manera, se integra un sistema que combina la información obtenida por la cámara —encargada de sensar el color inicial— con los valores digitales de peso, con el fin de codificar dichos valores en el modelo de color CMYK y obtener así el color deseado en el recipiente final de pintura.



## Arquitectura propuesta

En el caso del Grupo 10, corresponde el desarrollo e implementación de los periféricos asociados a los sensores de peso para cada tanque de pintura, utilizando para este propósito el módulo HX711 en conjunto con una galga extensiométrica.

El sistema permite realizar la medición de peso mediante celdas de carga, empleando el HX711 como amplificador y convertidor analógico-digital (ADC), el cual entrega la señal procesada hacia el microcontrolador ESP32 para su posterior lectura y transmisión de datos.

Se adjunta el documento en formato PDF, donde se presenta el diseño del sistema, el esquema de conexiones eléctricas y la configuración de los periféricos utilizados para la correcta integración del sensor de peso con el entorno de control.

ver pfd (PLANO_CONEXIONES.pdf)


Se implementaron los programas destinados a la adquisición y visualización de los datos generados por la galga extensiométrica, empleando el entorno de desarrollo Thonny,  el lenguaje MicroPython para la programación del microcontrolador.

![alt text](image.png)


A continuación, se diseñaron los esquemas de comunicación en Node-RED y se realizó la configuración del tópico MQTT, permitiendo la visualización en tiempo real de las lecturas de la galga extensiométrica dentro del entorno de monitoreo de Node-RED.


![alt text](image-1.png)


![alt text](image-2.png)



## Periférico a trabajar



#  Configuracion de Pines del Modulo HX711 y la esp32

VCC= FUENTE +5V
GND=GND DE LA FUENTE

## GALGA 1
DT_PIN = 12    # Pin de datos DT del HX711 pin GPIO 13 de la esp32
SCK_PIN = 13   # Pin de reloj SCK del HX711 pin GPIO 12 de la esp32

## GALGA 2
DT_PIN = 14   # Pin de datos DT del HX711 pin GPIO 16 de la esp32
SCK_PIN = 27   # Pin de reloj SCK del HX711 pin GPIO 17 de la esp32

## GALGA 3
DT_PIN = 25   # Pin de datos DT del HX711 pin GPIO 5 de la esp32
SCK_PIN = 28   # Pin de reloj SCK del HX711 pin GPIO 18 de la esp32

## GALGA 4
DT_PIN = 32   # Pin de datos DT del HX711 pin GPIO 19 de la esp32
SCK_PIN = 33   # Pin de reloj SCK del HX711 pin GPIO 3 de la esp32

## GALGA 5
DT_PIN = 4   # Pin de datos DT del HX711 pin GPIO 1 de la esp32
SCK_PIN = 16   # Pin de reloj SCK del HX711 pin GPIO 23 de la esp32



![alt text](image-4.png)







GALGA:

VCC:E+

GND:E-

SEÑAL+:A+

SEÑAL-: A-

![alt text](image-3.png)

# Avances

En este apartado se presenta la evidencia fotográfica del montaje realizado por parte de nuestro equipo, correspondiente al sistema instalado.

![alt text](image-5.png)

![alt text](image-6.png)

![alt text](image-7.png)


A continuación, se presenta el diseño preliminar propuesto para las bases de las galgas extensiométricas y sus respectivos recipientes, donde se alojará la pintura destinada al proceso de mezclado previo a la entrega final.

![alt text](DISEÑOS_1.png)

![alt text](DISEÑOS_2.png)


Se elabora el diagrama de flujo del sistema utilizando pseudocódigo, en el cual se indica la lógica prevista para la integración completa del sistema. Este diagrama representa la secuencia de operaciones que se ejecutarán durante el proceso de adquisición de datos de las galgas extensiométricas (por medio de los módulos HX711), la lectura de color mediante la cámara y la posterior codificación de los valores en el modelo CMYK, con el fin de obtener el color final en el recipiente de pintura.

# AVANCE 07-11-2025


Montaje de la estructura 


Se realizó el montaje de la estructura y la fabricación de los recipientes, los cuales estarán destinados a alojar las respectivas pinturas para el proceso de mezclado.


![alt text](Esctructura.png)


Durante la semana se realizó la integración de las cinco galgas extensiométricas con el módulo ESP32, dejando cada una debidamente calibrada para que puedan ser dispuestas en las pruebas finales.

![alt text](medida.png)


Igualmente, se realizaron los esquemas de conexión y visualización mediante Node-RED. En este caso, se dejaron configurados los bloques de medida y el histograma obtenido durante las pruebas, permitiendo una representación gráfica del comportamiento de las señales provenientes de las galgas.


![alt text](node_red.png)

igualmente, se realizaron las visualizaciones en el Dashboard, permitiendo monitorear en tiempo real las lecturas de las cinco galgas extensiométricas.

![alt text](dashboard.png)

![alt text](dashboard2.png)


## AVANCE 14-11-2025

Durante el proceso se inició la instalación de las galgas sobre la estructura de madera. Conforme al diseño establecido, se efectuó el montaje de las bases de las galgas junto con su tornillería correspondiente, garantizando la correcta fijación y alineación de los elementos.


![alt text](Montaje1.png)



![alt text](Montaje2.png)



![alt text](Montaje3.png)


Una vez finalizado el montaje de las bases y de las galgas, se procedió con la instalación de los módulos HX711, junto con su respectivo cableado, asegurando las conexiones según las especificaciones técnicas del diseño


![alt text](cableado1.png)

## Entrega a integradores 21/11/2025


Posterior a la realización del cableado y las conexiones, se efectuó nuevamente la validación del código, donde se evidenció la necesidad de reemplazar los pines 34 y 35 de la ESP32, debido a que dichos pines estaban generando fallas en la lectura de los datos.
En consecuencia, se optó por realizar el cambio de pines asignados, con el fin de garantizar la correcta adquisición de señales y proceder con las pruebas finales del sistema.


# Entrega Final 

El programa inicia importando módulos como machine, time, HX711, el cliente MQTT y la función conectar_wifi().
También se aumenta la frecuencia del procesador del ESP32 a 240 MHz para garantizar la lectura rápida y estable de los cinco sensores.
Posteriormente, se definen los parámetros principales:

![alt text](2pines.png)

- Dirección del broker MQTT
- ID del cliente MQTT
- Tópicos base para publicación y comandos de TARA
- Parámetros de suavizado del filtro EMA

## Gestión de las 5 celdas de carga (GALGAS)

El arreglo de galgas se implementa mediante una lista de diccionarios en Python, donde cada diccionario almacena:

- Nombre de la galga
- Identificador único para su tópico MQTT
- Pines DT y SCK del módulo HX711
- Factor de calibración individual

Este diseño permite añadir o modificar sensores sin alterar el resto del código.

![alt text](1pines.png)

## Ejemplo de configuración:

GALGAS_CONFIG = [
    {"nombre": "Cyan", "id": "Cyan", "pin_dt": 12, "pin_sck": 13, "calibracion": 400},
    ...]
    
Cada galga se inicializa así:

- Se configura el módulo HX711 en sus pines asignados.
- Se realiza una TARA inicial usando 200 muestras para obtener un cero estable.
- Se aplica el factor de calibración configurado.
- Se precarga el filtro EMA tomando 20 lecturas estables del sensor.

La clase HX711 realiza la lectura bit a bit controlando manualmente los pines:

- PD_SCK (salida): genera pulsos de reloj
- DOUT (entrada): recibe los 24 bits del valor medido

Además maneja:

- OFFSET: valor base después del tare
- SCALE: factor usado para convertir la lectura RAW en gramos

El sistema escucha comandos en el tópico:

- (bascula/comando/<ID>)

Cuando llega un mensaje con "TARA", Se identifica cuál galga corresponde a ese ID, se marca la solicitud de TARA mediante tara_solicitada_idx
l sistema ejecutará la TARA en la siguiente iteración del loop principal

Esto permite controlar cada báscula desde Node-RED u otro sistema externo.

* Botón físico de TARA:

El pin configurado como entrada permite realizar TARA manual presionando un botón.

Si se presiona:

- Se detecta la interrupción

- Se marca que la galga activa debe ser tarada

- La TARA se ejecuta inmediatamente en el siguiente ciclo


## Conexión a WiFi y creación del cliente MQTT:

La función conectar_wifi() activa el WiFi del ESP32, conecta usando las credenciales almacenadas y espera hasta obtener una dirección IP y luego se crea un cliente MQTT y se suscribe al tópico de comandos:

-(bascula/comando/#)

Esto permite recibir órdenes de TARA por MQTT.

![alt text](3pines.png)

## Filtro exponencial EMA para suavizar lecturas

Cada lectura cruda del HX711 tiende a ser ruidosa. El programa utiliza un filtro EMA con un factor alpha configurable:

- peso_suave = lectura_raw * α + lectura_anterior * (1 – α)

Esto reduce variaciones rápidas y produce una lectura más estable para visualizar y publicar en MQTT.

## Ciclo principal del programa (main loop)

El corazón del sistema es un bucle que corre continuamente:

## 1. Revisión de mensajes MQTT

Se verifica si llegó una solicitud de TARA remota.

## 2. Ejecución de TARA

Si una galga tiene TARA pendiente:

- Se ejecuta hx.tara()

- Se recalcula la memoria del filtro EMA con 20 muestras nuevas

- Se limpia el indicador de TARA

## 3. Lectura secuencial de cada galga

El sistema no lee todas las galgas al tiempo y va leyendo una por ciclo, en orden circular:

- Lectura del HX711

- Aplicación del filtro EMA

- Conversión a texto formateado

- Actualización en consola

Publicación en su tópico MQTT:

(in/bascula/peso/<ID>)
Esto mantiene alta velocidad y evita saturar la CPU.

## 4. Cambio a la siguiente galga

El índice avanza de esta forma:
- Cyan → Magenta → Yellow → Key → White → Cyan...

## 5. Pequeño delay

Se espera 10 ms para mejorar estabilidad.
 Reinicio por errores

Si ocurre un error fatal:

- Se imprime el mensaje

- El ESP32 espera 10 segundos

- Y luego se reinicia

Esto da robustez al sistema en ambientes reales.

Con el equipo de integración se verificó que la información generada por las galgas llega correctamente a la interfaz gráfica en Node-RED. Como se observa, se realizó la implementación y visualización individual de cada galga, incluyendo su lectura inicial antes de ejecutar la tara y comenzar las mediciones. De esta manera, el sistema de galgas realiza las pruebas funcionales finales necesarias para su correcta integración con los demás sistemas del proyecto.

![alt text](nodered.png)

### 1. [Flujos](/G10/flujos/flows.json)

![alt text](Flujo_mezclador-Galga.drawio.png)


### 2. [Programación micropython](/G10/micropython/test.py)

# CÓDIGO BÁSCULA ESP32 PARA NODE-RED CON TARA INDIVIDUAL v7 (OPTIMIZADO POR EMA)

```python
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
FACTOR_SUAVIZADO = 0.2
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
    
    conectar_wifi()
    print(f"Conectando al broker MQTT: {MQTT_BROKER}:{MQTT_PORT}...")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(sub_callback)
    client.connect()
    client.subscribe(TOPIC_SUB_COMANDO_WILDCARD)
    print(f"Conectado a MQTT y suscrito al tópico: {TOPIC_SUB_COMANDO_WILDCARD.decode()}")

    sensores_hx = []
    pesos_suavizados = []
    print("\nInicializando galgas...")
    for config in GALGAS_CONFIG:
        print(f"   -> Configurando {config['nombre']}...")
        hx = HX711(Pin(config['pin_dt']), Pin(config['pin_sck']))
        hx.wakeUp()
        hx.kanal(1)
        print(f"     Realizando TARA inicial...")
        hx.tara(GALGA_TARA_SAMPLES)
        hx.calFaktor(config['calibracion'])
        
        lectura_inicial_suave = hx.masse(20) 
        pesos_suavizados.append(lectura_inicial_suave)
        
        sensores_hx.append(hx)
    print("¡Todas las galgas listas y memoria EMA precargada!")

    boton = Pin(PIN_BOTON_TARA, Pin.IN, Pin.PULL_UP)
    boton.irq(trigger=Pin.IRQ_FALLING, handler=manejador_interrupcion_tara)
    print(f"Botón físico configurado en pin {PIN_BOTON_TARA}.")
    print("------------------------------------------")

    ultimas_lecturas = ["0,00"] * len(GALGAS_CONFIG)

    while True:
        client.check_msg()

        if tara_solicitada_idx != -1:
            config_tara = GALGAS_CONFIG[tara_solicitada_idx]
            hx_tara = sensores_hx[tara_solicitada_idx]
            
            print(f"\n[TARA] Procesando solicitud para {config_tara['nombre']}...")
            hx_tara.tara(GALGA_TARA_SAMPLES)
            pesos_suavizados[tara_solicitada_idx] = hx_tara.masse(20)
            print(f"[TARA] ¡Nueva TARA completada y memoria EMA reiniciada para {config_tara['nombre']}!")
            
            tara_solicitada_idx = -1
            continue 

        hx_activo = sensores_hx[galga_activa_idx]
        config_activa = GALGAS_CONFIG[galga_activa_idx]

        lectura_actual_raw = hx_activo.masse(1) 

        peso_anterior = pesos_suavizados[galga_activa_idx]
        nuevo_peso_suave = (lectura_actual_raw * FACTOR_SUAVIZADO) + (peso_anterior * (1.0 - FACTOR_SUAVIZADO))
        pesos_suavizados[galga_activa_idx] = nuevo_peso_suave

        m_str = "{:0.2f}".format(nuevo_peso_suave)
        
        ultimas_lecturas[galga_activa_idx] = m_str.replace('.', ',')

        linea_estado = ""
        for i, lectura in enumerate(ultimas_lecturas):
            linea_estado += f"B{i+1}: {lectura} g | "
        print(linea_estado, end='\r')

        topic_galga_actual = f"{TOPIC_PUB_PESO_BASE.decode()}/{config_activa['id']}".encode()
        client.publish(topic_galga_actual, m_str.encode())

        galga_activa_idx = (galga_activa_idx + 1) % len(GALGAS_CONFIG)

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

