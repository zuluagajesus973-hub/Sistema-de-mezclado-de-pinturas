# Nombre de la etapa:

## Integrantes
Maria Paula Fierro Barrios (https://github.com/fierrobarriosmariapaula-blip)

Astrid Catalina Ortiz Lopez (https://github.com/astridcortizl-del)

Camilo Suarez Camacho (https://github.com/Camilosc13)

## Documentación

## Objetivo General

Diseñar e implementar un sistema distribuido de monitoreo y control de temperatura basado en ESP32, con comunicación MQTT y visualización en Node-RED que permita activar válvulas y resistencias automáticamente al superar un umbral térmico definido.


### Funcionamiento del Sistema

**Capa 1: Lectura de Sensores (ESP32)**

El ESP32 recibe señales de cinco sensores DS18B20 conectados en diferentes pines (33, 25, 26, 27, 14).
Cada sensor mide la temperatura y publica los valores por MQTT en los siguientes tópic:

- micro/temperatura/sensor1
- micro/temperatura/sensor2
- micro/temperatura/sensor3
- micro/temperatura/sensor4
- micro/temperatura/sensor5

**Capa 2: Control Local**

El ESP32 compara cada lectura con un umbral de 30°C (TEMP_UMBRAL).

- Si la temperatura ≥ 30°C → activa la válvula correspondiente enviando ON al tópico MQTT.
- Si la temperatura < 30°C → envía OFF para desactivar la válvula.

Tópic de control:

- micro/pintura/valvula1
- micro/pintura/valvula2
- micro/pintura/valvula3
- micro/pintura/valvula4
- micro/pintura/valvula5

<p align="center">
  <img src="flujos/NodeRed_SensorTemperatura.png" alt="Flujo en Node-RED" width="500">
  <br>
  <b>Figura 1.</b> Flujo de monitoreo de temperatura en Node-RED.
</p>


**Capa 3: Visualización en Node-RED**

En Node-RED se visualizan las temperaturas y estados:

- Indicadores tipo termómetro muestran la temperatura en tiempo real.
- LEDs representan el estado de cada válvula (encendida o apagada).

El flujo incluye:

- Nodos MQTT IN para recibir datos de temperatura.
- Nodos Function que procesan las condiciones de temperatura.
- Nodos MQTT OUT para enviar comandos de activación/desactivación.
- Dashboard con widgets de temperatura y estado de válvulas.

<p align="center">
  <img src="flujos/Dashboard.png" alt="Dashboard Node-RED" width="500">
  <br>
  <b>Figura 2.</b> Panel de control (Dashboard) en Node-RED para visualizar las temperaturas y estados de válvulas.
</p>


## Variables y Parámetros Principales

| **Variable**          | **Descripción**                                   | **Tipo**          |
|------------------------|--------------------------------------------------|-------------------|
| **TEMP_UMBRAL**        | Umbral de activación de válvulas (30°C)          | Float             |
| **datos**              | Diccionario con las lecturas actuales            | Dict              |
| **estado_valvulas**    | Lista con el estado ON/OFF de cada válvula       | Boolean list      |
| **json_filename**      | Archivo donde se guardan los registros           | String            |
| **MQTT_TOPICS_TEMP**   | Lista de tópicos de publicación de temperatura   | List              |
| **MQTT_TOPICS_VALVULAS** | Lista de tópicos de control de válvulas        | List              |


**Registro de Datos**

Cada ciclo de lectura guarda las temperaturas en un archivo local temperaturasSensores.json, que actúa como un histórico de las mediciones.

El formato JSON permite analizar tendencias o generar reportes posteriores.

## Pruebas ESP32 y Node Red

<p align="center">
  <img src="flujos/PruebasDashboard.png" alt="Prueba de funcionamiento MQTT" width="450">
  <br>
  <b>Figura 3.</b> Prueba de funcionamiento del sistema MQTT en Node-RED.
</p>

### Funcionamiento MQTT

En esta etapa se verifica la comunicación entre el **ESP32** y **Node-RED** mediante **MQTT**.  
Cada sensor **DS18B20** envía su temperatura a un tópico específico, y el **ESP32** publica el estado **ON/OFF** de las válvulas según el umbral configurado.

En el panel se muestran cinco termómetros con sus indicadores de **LED** y **válvula**.  
Solo el **Sensor 5**, con **32 °C**, supera el umbral de **30 °C**, activando su válvula correspondiente, mientras las demás permanecen apagadas.


<p align="center">
  <img src="flujos/PruebasMycroPython.png" alt="Prueba de funcionamiento del script en Thonny" width="450">
  <br>
  <b>Figura 4.</b> Prueba de funcionamiento del sistema en Thonny con ESP32 y sensores DS18B20.
</p>

### Funcionamiento en Thonny (ESP32 - MicroPython)

En esta etapa se programa y prueba el **ESP32** en **Thonny** usando **MicroPython**.  
Durante las pruebas, las lecturas se muestran en tiempo real entre **21.0 °C y 21.5 °C**, confirmando el correcto funcionamiento de los sensores **DS18B20** y el guardado de datos.  
Esta verificación garantiza la comunicación estable del hardware antes de integrar el envío de datos por **MQTT** hacia **Node-RED**.



 ## [Funciones Especiales del Código SensoresValvulas.py](/G09/micropython/SensoresValvulas.py)

- **KeyboardInterrupt:**
Permite detener manualmente el programa (con Ctrl + C) sin perder control.
Cuando se interrumpe, el script automáticamente ejecuta otro archivo (MqttValvula.py), garantizando que el sistema no quede inactivo.

- **try/except:**
Evita que errores en sensores o la conexión WiFi detengan el sistema.
En caso de falla, reinicia o ejecuta un script alterno.

- **os.system("MqttValvula.py"):**
Sirve para lanzar otro proceso cuando ocurre una interrupción o error, útil como mecanismo de respaldo o failover.



 ## [Funcionamiento y funciones Especiales del Código MqttValvula.py](/G09/micropython/MqttValvula.py)

Este código **“ MQTT VALVULAS”** hace que la ESP32 funcione como un dispositivo inteligente que controla 5 válvulas usando el protocolo MQTT.

Explicación código 
1.	Configuración MQTT
Se define el broker MQTT (es el servidor que reparte los mensajes) y se indican los nombres de los topics donde el ESP32 va a recibir las órdenes para las válvulas.
En este caso son:
micro/pintura/valvula1
micro/pintura/valvula2 , etc… 
2.	Definición de pines
Difinimos los pines digitales para activar o desactivar las valvulas.
Aquí se asocia cada válvula a un pin físico (por ejemplo, el pin 15 controla la válvula 1, el 16 la válvula 2, etc.).
Así cuando llegue un mensaje para “valvula3”, el programa sabrá que debe encender o apagar el pin 17.
3.	Recepción de mensajes
Tenemos la función llamada on_message() que se ejecuta automáticamente cada vez que llega un mensaje nuevo desde el servidor MQTT.
Si el mensaje dice "ON", el pin correspondiente se activa (enciende la válvula).
Si dice "OFF", se apaga.
4.	Bucle principal
El programa entra en un ciclo infinito donde constantemente revisa si hay mensajes nuevos.
Si los hay, llama a la función on_message() y ejecuta la acción correspondiente.

Términos nuevos o importantes
 

- **Callback:** "Una función que se ejecuta automáticamente cuando ocurre un evento (por ejemplo, cuando llega un mensaje)."

- **check_msg():** "Método que revisa si hay nuevos mensajes MQTT."

- **subscribe():** "Indica al broker que quieres recibir los mensajes de un topic."

- **decode():** "Convierte un dato en bytes a texto normal."

- **value(1) / value(0):** "Enciende (1) o apaga (0) el pin del ESP32."


<p align="center">
  <img src="flujos/NodeRed_Valvula.png" alt="Visualización de válvulas en Node-RED" width="450">
  <br>
  <b>Figura 5.</b> Visualización del control de válvulas en Node-RED.
</p>

 ## Funcionamiento y funciones Especiales del Código FuncionSensores

El código “Función sensor” funciona para tomar la lectura de temperatura de un sensor y dependiendo del valor, decide si una válvula debe encenderse o apagarse.
Además envía tres tipos de información hacia distintos destinos de Node-RED.
 Funciones principales
1.	**Lee la temperatura**
-	El código recibe la temperatura desde el sensor (en msg.payload).
-	La convierte en número para poder compararla.
2.	**Compara con un valor límite (umbral)**
-	Tiene un valor de referencia (por ejemplo, 30 °C).
-   Si la temperatura es mayor o igual a ese límite → el estado es "ON".
-	Si es menor → el estado es "OFF".
3.	**Define los destinos (topics)**
-	Un topic es como la dirección del mensaje dentro del sistema MQTT.
-	En este caso se usan dos:
-   esp1/temperatura/sensor1 → donde se envía el valor de la temperatura.
-	esp2/pintura/valvula1 → donde se envía la orden para encender o apagar la válvula.
4.	**Crea los mensajes**
-	Uno con el valor de temperatura (para visualizarlo).
-	Otro con el estado "ON" o "OFF" (para activar la válvula).
-	Y un tercero para un LED o indicador visual en el panel (Dashboard).
5.	**Envía los mensajes**
-	El return [msgValve, msgSensor, msgLed] manda los tres mensajes, cada uno por una salida        diferente del nodo Function.
Así, Node-RED puede enviar cada dato al destino que corresponde.

**Terminos Nuevos**

 - **payload**: Es el “contenido” del mensaje que viaja entre los nodos.
 - **parseFloat():** Convierte un texto en número decimal.
 - **isNaN():**	Revisa si un valor no es un número.
 - **const / let:**	Formas de crear variables en JavaScript.


 ## [Funcionamiento y funciones Especiales del Código SVR.py](/G09/micropython/SVR.py)


El código SVR se encarga de leer la temperatura desde varios sensores DS18B20 y dependiendo del valor que obtenga, decide si debe activar una válvula (cuando la temperatura sube) o activar una resistencia (cuando la temperatura baja).

1. Lee la temperatura

El ESP32 toma la lectura directamente desde cada sensor DS18B20 conectado.
Cada lectura queda guardada dentro de la variable temp.

2. Compara la temperatura con los valores de control

Se definieron dos umbrales:

<table style="width: 70%; border-collapse: collapse; font-family: Arial, sans-serif; background-color: #000; color: #fff;">

  <tr style="border-bottom: 1px solid #555;">
    <th style="text-align: left; padding: 10px;">Temperatura</th>
    <th style="text-align: left; padding: 10px;">Acción del Sistema</th>
  </tr>

  <tr style="border-bottom: 1px solid #333;">
    <td style="padding: 8px; text-align: center;">≤ 25°C</td>
    <td style="padding: 8px;">Se enciende la resistencia → aumenta la temperatura</td>
  </tr>

  <tr style="border-bottom: 1px solid #333;">
    <td style="padding: 8px; text-align: center;">≥ 27°C</td>
    <td style="padding: 8px;">Se activa la válvula → disminuye la temperatura</td>
  </tr>

  <tr>
    <td style="padding: 8px; text-align: center;">25°C a 27°C</td>
    <td style="padding: 8px;">Se mantiene el estado → evita cambios bruscos</td>
  </tr>

</table>

Esto permite mantener la temperatura estable sin que el sistema esté encendiendo y apagando continuamente.

3. Define los tópicos MQTT

Se modifico los Topic Utilizados anteriormente por los siguientes:

<table style="width: 75%; border-collapse: collapse; font-family: Arial, sans-serif; background-color: #000; color: #fff;">

  <tr style="border-bottom: 1px solid #555;">
    <th style="text-align: left; padding: 10px;">Tipo de Dato</th>
    <th style="text-align: left; padding: 10px;">Ejemplo de Tópico</th>
    <th style="text-align: left; padding: 10px;">Función</th>
  </tr>

  <tr style="border-bottom: 1px solid #333;">
    <td style="padding: 8px;">Temperatura</td>
    <td style="padding: 8px; font-family: monospace;">esp1/temperatura/sensor1</td>
    <td style="padding: 8px;">Se envía el valor de la temperatura medida</td>
  </tr>

  <tr>
    <td style="padding: 8px;">Control de Válvulas</td>
    <td style="padding: 8px; font-family: monospace;">esp2/pintura/valvula1</td>
    <td style="padding: 8px;">Se envía la orden <strong>ON</strong> o <strong>OFF</strong> para activar o desactivar la válvula</td>
  </tr>

</table>

Las resistencias no usan MQTT, ya que se controlan directamente desde el ESP32 mediante pines digitales.

4. Acciona los dispositivos

Según la temperatura medida:

<table style="width: 75%; border-collapse: collapse; font-family: Arial, sans-serif; background-color: #000; color: #fff;">

  <tr style="border-bottom: 1px solid #555;">
    <th style="text-align: left; padding: 10px;">Comando</th>
    <th style="text-align: left; padding: 10px;">Dispositivo</th>
    <th style="text-align: left; padding: 10px;">Acción</th>
  </tr>

  <tr style="border-bottom: 1px solid #333;">
    <td style="padding: 8px; font-family: monospace;">client.publish(..., "ON")</td>
    <td style="padding: 8px;">Válvula</td>
    <td style="padding: 8px;">Se abre para bajar la temperatura</td>
  </tr>

  <tr style="border-bottom: 1px solid #333;">
    <td style="padding: 8px; font-family: monospace;">client.publish(..., "OFF")</td>
    <td style="padding: 8px;">Válvula</td>
    <td style="padding: 8px;">Se cierra cuando ya no es necesario enfriar</td>
  </tr>

  <tr style="border-bottom: 1px solid #333;">
    <td style="padding: 8px; font-family: monospace;">resistencia_pin.value(1)</td>
    <td style="padding: 8px;">Resistencia</td>
    <td style="padding: 8px;">Se enciende para aumentar la temperatura</td>
  </tr>

  <tr>
    <td style="padding: 8px; font-family: monospace;">resistencia_pin.value(0)</td>
    <td style="padding: 8px;">Resistencia</td>
    <td style="padding: 8px;">Se apaga cuando se alcanza la temperatura deseada</td>
  </tr>

</table>


## Retos Encontrados

1.	Sincronización de sensores:
Los DS18B20 requieren un tiempo de conversión (750 ms); si no se respeta, las lecturas pueden ser erróneas.
2.	Gestión de tópicos MQTT:
Mantener nombres consistentes en Node-RED y el código es vital para evitar desconexiones o mensajes perdidos.
3.	Actualización visual en Node-RED:
Requiere configurar correctamente los widgets y funciones para reflejar el estado real en tiempo real.


