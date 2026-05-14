# Control de Bombas de Diafragma con ESP32, MicroPython, Raspberry Pi y MQTT

## Integrantes

* [David Santiago Puentes Cárdenas — 99225](https://github.com/Monstertrox)
* [Juan David Arias Bojacá — 107394](https://github.com/juandariasb-ai)

---

## Introducción (Inicio del Sistema por Visión Artificial)

Todo el sistema inicia en una **Raspberry Pi**, donde una **cámara** captura la imagen del recipiente de pintura. A partir de esta imagen se realiza un **análisis de color**, obteniendo las proporciones **CMYKW (Cian, Magenta, Yellow, Black y White)**.

Una vez procesado el color:

1. La Raspberry convierte los valores de color en un **string** con formato:

   ```
   C:10 M:20 Y:5 K:3 W:2
   ```

2. Este string es enviado por **MQTT** hacia la **ESP32_2**, que es la encargada de **controlar las bombas, el agitador y la ejecución completa de la mezcla**.

Todo el código presentado en este documento corresponde exclusivamente a la **ESP32_2**, que recibe órdenes desde la Raspberry y ejecuta físicamente el proceso.

---

## Objetivo del Sistema

Controlar cinco bombas de diafragma mediante una **ESP32_2** que recibe recetas de mezcla en formato **CMYKW** por **MQTT**. El sistema convierte los porcentajes de color en **tiempos de activación**, verifica condiciones previas mediante **galgas de peso**, ejecuta las bombas de forma secuencial y finaliza con un proceso de **agitación automática**.

---

## Arquitectura del Sistema

### Componentes Principales

* Raspberry Pi con cámara para detección de color
* 2 ESP32 (control distribuido)
* 5 Bombas de diafragma controladas por PWM
* Galgas de peso para medición del nivel de pintura
* Motor agitador
* Comunicación MQTT

---

## Flujos del Sistema (Basados en Diagramas)

### 1. Flujo de Galgas (Control de Nivel de Pintura)

Este es el primer flujo que se ejecuta tras recibir el color desde la Raspberry.

<p align="center">
  <img src="./fotos_flujo/Flujo_mezclador-Galga.drawio.png" alt="Diagrama de flujo del sistema" width="800"/>
</p>


**Funcionamiento:**

1. Se activa la galga.
2. Se elimina el peso del recipiente y sensores (tara).
3. Se validan las proporciones CMYKW recibidas desde la cámara.
4. Se verifica que el nivel de pintura sea superior al mínimo.
5. Si el nivel NO es suficiente → se envía un mensaje visual y se bloquea el proceso.
6. Si el nivel SÍ es suficiente → se habilita el envío de datos hacia el módulo de bombas.

Este comportamiento se representa en el código mediante la validación indirecta antes de activar las bombas.

---

### 2. Flujo del Motor Agitador

<p align="center">
  <img src="./fotos_flujo/Flujo_motoagitador.jpg" alt="Diagrama de flujo del sistema" width="800"/>
</p>

**Funcionamiento:**

1. Desactivación inicial de válvulas.
2. Activación del motor 1 para bajar el aspa.
3. Activación del motor 2 para agitar la pintura.
4. Desactivación del motor 2.
5. Activación del motor 1 para subir el aspa.

En el código este proceso se ejecuta mediante la función:

```python
def run_agitador():
```

Que activa el pin del agitador durante **10 segundos**.

---

### 3. Flujo de Bombas de Pintura

<p align="center">
  <img src="./fotos_flujo/Flujo_mezclador-Bombas.png" alt="Diagrama de flujo del sistema" width="800"/>
</p>


**Funcionamiento:**

1. Se define el color actual.
2. Se lee la temperatura de la tinta.
3. Se verifica que esté dentro del rango permitido.
4. Se activan las bombas.
5. Se mide el peso del tanque principal.
6. Cuando se alcanza el peso objetivo, se detiene la bomba.
7. Se repite el proceso hasta completar los 5 colores.

---

## Descripción Detallada del Código (ESP32_2)

### 1. Configuración de Red WiFi

```python
WIFI_SSID = "Chucho"
WIFI_PASS = "Chucho123"
```

La función `conectar_wifi()` establece la conexión de la ESP32_2 a la red para permitir la comunicación MQTT.

---

### 2. Configuración MQTT

```python
MQTT_BROKER     = "192.168.94.216"
MQTT_PORT       = 1883
MQTT_CLIENT_ID  = b"ESP32_BOMBAS"
MQTT_TOPIC_CMYK = b"esp/out"
```

Permite recibir las recetas CMYKW provenientes desde la Raspberry.

---

### 3. Configuración de Bombas

```python
PWM_PINS   = [15, 2, 4, 16, 17]
DIR1_PINS  = [23, 19, 18, 5, 4]
DIR2_PINS  = [22, 21, 32, 33, 25]

PWM_FREQ = 1000
PWM_GLOBAL = 70

TIEMPOS_BOMBAS_MAX = [5, 5, 5, 5, 5]
MAX_TOTAL_PERCENT = 40
```

* Control PWM por bomba
* Límite de potencia al 70%
* Tiempo máximo de activación: 5 segundos por bomba
* Límite total CMYKW: 40%

---

### 4. Sistema de Agitación

```python
AGITADOR_PIN = 26
AGITATOR_TIME_S = 10
```

Encargado de homogenizar la pintura luego de terminar la succión de todos los colores.

---

### 5. Estados Globales

```python
tiempos_bombas_receta = [0.0]*5
receta_lista = False
mezcla_en_progreso = False
temp_ok = [True]*5
flags = [0]*5
```

Permiten controlar correctamente la ejecución de la receta.

---

### 6. Procesamiento de Recetas CMYKW

```python
parse_cmykw()
cmykw_to_tiempos()
```

Convierte el string recibido por MQTT en tiempos reales de activación de las bombas.

---

### 7. Control de Bombas

```python
def ejecutar_bomba_tiempo(i, t):
```

* Activa cada bomba según su tiempo
* Permite frenar la bomba con L298N
* Supervisa el sistema mientras corre

---

### 8. Callback MQTT

```python
def mqtt_callback(topic, msg):
```

Procesa automáticamente los valores recibidos desde la Raspberry para iniciar una nueva receta.

---

### 9. Flujo Principal del Programa

```python
def main():
```

1. Conecta WiFi
2. Conecta MQTT
3. Espera receta
4. Ejecuta bombas
5. Activa agitador
6. Finaliza mezcla

---

## Formato de Mensajes MQTT

### Recetas CMYKW

* **Topic**: `esp/out`
* **Formato**: `C:10 M:20 Y:5 K:3 W:2`

---

## Secuencia General de Operación

1. Raspberry detecta color
2. Envía receta por MQTT
3. Galgas validan nivel
4. ESP32_2 ejecuta bombas
5. Se activa agitador
6. Sistema queda listo para una nueva mezcla

---

## Características de Seguridad

* Límite máximo de mezcla: 40%
* Frenado activo de bombas
* Agitación sólo cuando todas las bombas terminan
* Protección por PWM

---

## Integración con Node-RED

* Dashboard para envío de recetas CMYKW
* Visualización de proceso
* Control remoto completo del sistema

---

## Conclusión

Este sistema integra visión artificial, control de motores, pesaje, automatización y comunicación IoT mediante MQTT para lograr un proceso de mezcla de pintura completamente automatizado, seguro, escalable y controlable desde red.
