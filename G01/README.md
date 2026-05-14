# AVANCES PROYECTO INTEGRADOR

# Nombre de la etapa: Bomba

## Integrantes

- [Michael Handrety Fonseca Arana](https://github.com/MichaelJF50)
- [Laura Daniela Rincón Pinilla](https://github.com/Laura03rincon)

## Documentación

En este proyecto se desarrolló un sistema de control automático para bombas peristálticas, utilizando un ESP32 y el protocolo MQTT.

El sistema permite dosificar con precisión las pinturas base: Cian (C), Magenta (M), Amarillo (Y), Negro (K) y Blanco (W), necesarias para obtener el color final deseado en el proceso de mezcla automatizada.

Por medio de la comunicación MQTT, las bombas pueden encenderse y apagarse desde una interfaz en Node-RED, mientras que el ESP32 recibe las proporciones de cada color y controla el tiempo de activación según la cantidad que se necesita dosificar.

Además, el sistema cuenta con una galga de carga que mide el peso del recipiente y detiene automáticamente las bombas cuando se alcanza el valor esperado.

### Objetivo

Diseñar e implementar un sistema de control para las bombas peristálticas encargadas de transferir las pinturas base (C, M, Y, K, W), utilizando un ESP32 conectado a un servidor MQTT, para lograr una dosificación automática, precisa y monitoreada en tiempo real.

# Funcionamiento General

## Inicio del proceso
- El usuario selecciona el color que desea dosificar.  
- Se envía un mensaje MQTT con el tema `bomba/inicio` y el valor `ON`.  
- El ESP32 enciende la bomba (salida en el pin configurado para el actuador).  
- El líquido fluye por el sistema hasta alcanzar el sensor correspondiente al color seleccionado.  

## Lectura de sensores
- Los sensores detectan la presencia del color mediante cambios en el valor de salida (S, M, Y, K, W).  
- Cada sensor envía su señal al ESP32, donde se procesa para determinar el momento exacto en el que debe detenerse la bomba.  
- Los valores se leen constantemente para garantizar precisión en la dosificación.

## Control del sistema
- El sistema trabaja con los parámetros S, M, Y, K y W, que representan los diferentes canales de color:  
  - **S:** Sensor de inicio o sincronización.  
  - **M:** Magenta.  
  - **Y:** Amarillo.  
  - **K:** Negro.  
  - **W:** Blanco o referencia.  
- El controlador evalúa las señales recibidas y ajusta el tiempo de activación de la bomba.  
- En caso de error o lectura fuera del rango esperado, se detiene el proceso automáticamente.

## Diagrama de Flujo del Sistema

A continuación se presenta el diagrama de flujo que describe el proceso completo de dosificación automática de tintas mediante bombas peristálticas.  
El objetivo de este diagrama es representar de forma visual la **secuencia lógica de control**, desde la lectura de temperatura y peso, hasta la mezcla final de los colores base.

<p align="center">
  <img src="./Flujo_mezclador-Bombas.drawio.png" alt="Diagrama de flujo del sistema" width="800"/>
</p>

### Descripción del funcionamiento

1. **Inicio del proceso:**  
   El sistema inicia asignando el valor del color actual en 1, lo que corresponde al primer color base (por ejemplo, Cian).

2. **Lectura de temperatura de tinta:**  
   Se mide la temperatura del tanque de tinta correspondiente. Esta variable garantiza que la tinta tenga la viscosidad adecuada antes de ser bombeada.

3. **Verificación del rango de temperatura:**  
   - Si la temperatura **no está dentro del rango**, el sistema espera hasta que la tinta alcance la temperatura adecuada.  
   - Si la temperatura es correcta, continúa el proceso.

4. **Activación de la bomba:**  
   Una vez que la tinta está lista, se activa la **bomba peristáltica** asociada al color actual. El líquido comienza a fluir hacia el tanque principal.

5. **Lectura del peso del tanque principal:**  
   La galga de carga mide constantemente el peso del tanque principal para verificar el volumen transferido de tinta.

6. **Control por peso objetivo:**  
   - Si el peso **no ha alcanzado** el valor objetivo, el sistema mantiene activa la bomba.  
   - Si el peso **alcanza el valor esperado**, la bomba se detiene automáticamente.

7. **Cambio de color:**  
   El sistema incrementa el contador (`color actual = color actual + 1`) para continuar con el siguiente color base.

8. **Verificación del número total de colores:**  
   - Si aún quedan colores por dosificar (`color actual < 5`), el proceso se repite desde el paso 2.  
   - Si se han completado los cinco colores (C, M, Y, K, W), el proceso termina.

9. **Fin del proceso:**  
   El sistema detiene todas las bombas y finaliza el ciclo de mezcla.  
   En este punto, el tanque principal contiene la proporción deseada de los cinco colores base, lista para el uso o empaquetado.

---

### Funcionalidad clave representada
- **Control de temperatura:** asegura una mezcla estable y homogénea.  
- **Medición de peso en tiempo real:** permite detener el flujo con precisión.  
- **Secuencia automática:** cada bomba se activa solo cuando la anterior finaliza.  
- **Verificación cíclica:** el proceso continúa hasta completar todas las tintas configuradas.  

---

## Resumen del ciclo de control

| Etapa | Descripción | Acción del sistema |
|--------|--------------|--------------------|
| Inicialización | Se define el color inicial (C) | Color actual = 1 |
| Lectura de temperatura | Sensor lee el tanque de tinta | Verifica rango de temperatura |
| Bombeo | Bomba activa según color | Transfiere tinta al tanque principal |
| Control por peso | Galga monitorea peso objetivo | Detiene bomba al alcanzar el valor |
| Cambio de color | Incremento de variable de color | Repite proceso para siguiente tinta |
| Finalización | Último color completado | Proceso de mezcla finalizado |


## Comunicación MQTT
- El ESP32 se comunica con un servidor MQTT que recibe y envía los datos en tiempo real.  
- Los tópicos principales utilizados son:  
  - `bomba/inicio`: activa o detiene la bomba.  
  - `sensor/S`, `sensor/M`, `sensor/Y`, `sensor/K`, `sensor/W`: envían los valores de los sensores.  
  - `estado/sistema`: reporta el estado general (activo, detenido, error).  
- Esta comunicación permite visualizar el estado del proceso desde cualquier dispositivo conectado a la red.

## Visualización y monitoreo
- Los datos se pueden observar desde un panel MQTT o una interfaz desarrollada en Node-RED.  
- El sistema muestra el estado de los sensores y la bomba en tiempo real.  
- Esto permite verificar si la mezcla de colores y la cantidad dosificada son correctas.

## Variables Principales

| Variable        | Descripción                                       |
|-----------------|---------------------------------------------------|
| `sensor1`, `sensor2` | Entradas digitales conectadas al nivel del tanque |
| `bomba`         | Salida digital para el control de la bomba        |
| `led`           | LED indicador de estado de la bomba               |
| `modo_manual`   | Indica si el control es manual o automático       |
| `bomba_estado`  | Estado actual de la bomba (ON / OFF)              |

## Explicación del código
El código está dividido en bloques principales:

1. Configuración de red WiFi y MQTT
2. Definición de pines y variables
3. Funciones de conexión WiFi y MQTT
4. Funciones de control de la bomba
5. Bucle principal de ejecución

### Conexión WiFi

```python
SSID = "TIGO-E325"
PASSWORD = "7989956371"
```
Estas líneas almacenan las credenciales de la red WiFi a la que se conectará el ESP32.
La función conectar_wifi() activa el modo estación (network.STA_IF), inicia la conexión y espera hasta que el dispositivo obtenga una dirección IP válida:

```
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.5)
```
Una vez conectado, imprime la IP asignada. Esto permite la comunicación posterior con el broker MQTT.

### Configuración del broker MQTT
```
BROKER = "192.168.1.9"
CLIENT_ID = "esp32_bomba"
TOPIC_BOMBA_CONTROL = b'bomba/control'
TOPIC_BOMBA_ESTADO = b'bomba/estado'
```
El broker MQTT (en este caso la Raspberry Pi) actúa como el servidor de mensajería.
El ESP32 se conecta a él y se suscribe al tema bomba/control, donde recibe los comandos desde Node-RED.
También publica su estado (encendido o apagado) en el tema bomba/estado.

La conexión y suscripción se realizan mediante la función:

```
def conectar_mqtt():
    client = MQTTClient(CLIENT_ID, BROKER)
    client.set_callback(callback_mqtt)
    client.connect()
    client.subscribe(TOPIC_BOMBA_CONTROL)
```
## Callback MQTT

La función callback_mqtt() recibe los mensajes enviados al ESP32.
Dependiendo del comando (ON, OFF o AUTO), se activa o desactiva la bomba, o se cambia el modo de control:
```
def callback_mqtt(topic, msg):
    comando = msg.decode().strip().upper()

    if topic == TOPIC_BOMBA_CONTROL:
        if comando == "ON":
            encender_bomba()
        elif comando == "OFF":
            apagar_bomba()
        elif comando == "AUTO":
            modo_manual = False
```
Esto permite controlar el dispositivo directamente desde el dashboard en Node-RED.

## Control de la bomba

Las funciones encender_bomba() y apagar_bomba() controlan la salida GPIO25 (donde está conectada la bomba) y un LED indicador.
Además, publican el estado actual al broker para mantener sincronizado el panel de control.

```
def encender_bomba():
    bomba.value(1)
    led.value(1)
    client.publish(TOPIC_BOMBA_ESTADO, b"ON")

def apagar_bomba():
    bomba.value(0)
    led.value(0)
    client.publish(TOPIC_BOMBA_ESTADO, b"OFF")
```

## Lógica del modo automático

En el bucle principal main(), el ESP32 revisa continuamente el estado de los sensores (sensor1, sensor2).
Si ambos sensores están activos, se enciende la bomba; si alguno cambia, se apaga.

```
if not modo_manual:
    if sensor1.value() == 1 and sensor2.value() == 1:
        if not bomba_estado:
            encender_bomba()
    else:
        if bomba_estado:
            apagar_bomba()
```
Esto permite automatizar el proceso según las condiciones físicas del sistema (por ejemplo, el nivel o peso del tanque).

## Node-RED: Monitoreo y Control del Sistema

En esta etapa se integró Node-RED para visualizar las temperaturas de las cinco bombas y controlar el modo de operación mediante MQTT. El Dashboard permite observar en tiempo real el estado térmico y activar funciones manuales o automáticas según el requerimiento.

### Funcionamiento General

### Control del Modo de Operación
- El usuario modifica el estado mediante el interruptor **Cambiar Modo** en el Dashboard.
- El valor enviado se publica en un tópico MQTT que el ESP32 recibe.
- El ESP32 ajusta su comportamiento según el modo seleccionado (manual o automático).

### Recepción de Temperaturas
- Cada bomba publica su temperatura mediante un tópico MQTT independiente.
- Node-RED recibe estas temperaturas mediante nodos **MQTT In**.
- Los valores alimentan indicadores LED en el Dashboard.
- Los LED cambian según el estado térmico definido.

### Publicación del Estado Final de las Bombas
- Cada LED está conectado a un nodo **MQTT Out**.
- Se publica el estado procesado: “normal”, “advertencia” o “crítico”.
- Otros sistemas pueden suscribirse a estos tópicos.

## Arquitectura del Flujo Node-RED

### Componentes Principales
- Nodo UI **Cambiar Modo**  
- Cinco nodos **MQTT In** (temperaturas)  
- Cinco indicadores LED del Dashboard  
- Cinco nodos **MQTT Out** (estados finales)

### Flujo General de Datos
- El ESP32 envía temperatura → Node-RED la recibe.  
- Node-RED determina estado → LED indica estado.  
- LED → MQTT Out publica estado final.  
- Usuario cambia modo desde el Dashboard → valor enviado al ESP32.

## Interfaz del Dashboard

### Elementos del Dashboard
- Interruptor UI para cambiar modo.
- Cinco indicadores LED para los estados térmicos.
- Flujo visual que muestra el estado de cada bomba.

## Evidencia del Flujo y Dashboard

### Flujo en Node-RED

<p align="center">
  <img src="./Intento_ Node_red_final.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./Intento_final.jpeg" alt="Logo" width="800"/>
</p>


##  Video del funcionamiento

[Ver video en YouTube](https://youtube.com/shorts/XyB3JLqUIzM)

[Ver segundo video](https://youtube.com/shorts/PtICswtYfNs)

[Ver tercer video](https://youtube.com/shorts/ESgXuht2zm0)

[Ver cuarto video](https://youtube.com/shorts/nzPR5bZkEt8)

## Evidencias 

<p align="center">
  <img src="./Thonny.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./Node Red.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./Control bomba.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./Prueba.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./conexion.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./imagen.jpeg" alt="Logo" width="800"/>
</p>

<p align="center">
  <img src="./imagen.jpeg" alt="Logo" width="800"/>
</p>


