# Nombre de la etapa
<div align="justify">
## Integrantes  
- Heidy Nicol Sánchez Peña  
- David Mora  
- Federico Díaz Novoa  

---

## Documentación  

El objetivo de este avance es implementar un sistema de reconocimiento de colores usando el sensor TCS34725 y el módulo ESP32. El sistema detecta los colores dentro de la cabina de pintura y envía los valores RGB a la Raspberry Pi mediante comunicación MQTT.  
Toda la información se procesa y se muestra en Node-RED, lo que permite ver en tiempo real los colores captados por el sensor.  

Este avance busca lograr una lectura rápida y precisa de los colores, garantizando que la integración con el resto del sistema funcione correctamente y cumpla con el propósito general del proyecto.  

---

## Herramientas utilizadas  

- **Sensor TCS34725:** detecta los componentes de color rojo, verde y azul (RGB) con alta precisión usando comunicación I2C.  
- **ESP32:** se encarga de leer los datos del sensor y enviarlos por WiFi.  
- **Raspberry Pi:** recibe los datos enviados por el ESP32 a través de MQTT y los muestra en Node-RED.  
- **Node-RED:** permite visualizar los valores RGB de forma ordenada y monitorear los resultados en tiempo real.  

---

## Configuración del sensor TCS34725  

Antes de usarlo, fue necesario entender cómo trabaja este sensor y cómo se comunica con el ESP32.  


---
LECTURA SENSOR COLOR


---

## 1. Conexión del Sensor y pruebas
![Conexión LM75A](https://github.com/user-attachments/assets/881b1ee8-1954-4908-a165-ceaeaa151fcb)

---

##  Resultados de Lectura
![Diagrama de cableado](https://github.com/user-attachments/assets/ff6f7077-b274-4fcf-8e62-255b2a87ab65)

En esta imagen se aprecia el entorno **Thonny** durante la ejecución del script principal.  
El código realiza las siguientes tareas:

- Inicializa la interfaz I2C del ESP32 y verifica la conexión con el sensor TCS34725.  
- Configura la ganancia y el tiempo de integración del sensor para obtener lecturas precisas.  
- Inicia el bucle principal de adquisición de datos.  

El porcentaje mostrado en la parte inferior de Thonny indica el avance de la transferencia del script hacia el ESP32.  
Este indicador confirma que el microcontrolador está recibiendo correctamente el programa y comenzando la lectura de colores.


---

##  Resultados de Lectura
![Montaje del sistema](https://github.com/user-attachments/assets/25b38edc-eac0-4150-b84c-cf4a1eba454c)

En esta segunda imagen se visualizan los valores de color capturados por el sensor TCS34725.  
En la consola de Thonny aparecen los datos en formato JSON o texto, mostrando las intensidades de los canales R (rojo), G (verde) y B (azul).

- Cada lectura corresponde al color detectado en ese instante por el sensor.  
- El porcentaje de ejecución indica que el código sigue corriendo correctamente en el ESP32.  
- Los valores cambian según la luz o el color del objeto que se coloca frente al sensor.  


---


La última imagen muestra la lectura de colores de forma estable y continua, evidenciando que el sistema ha alcanzado su funcionamiento óptimo.  
Los valores RGB se mantienen dentro de un rango coherente, lo que indica:

- Buena calibración del sensor TCS34725.  
- Comunicación I2C estable con el ESP32.  
- Ejecución fluida del código sin errores en Thonny.  

El porcentaje en la parte inferior señala el estado de ejecución activo del programa, asegurando que el ESP32 continúa procesando y enviando las lecturas sin interrupciones.



## Avances  

### 1. [Flujos](/G03/flujos/flows.json)  

![Image](https://github.com/user-attachments/assets/d588804c-b1ca-42e3-9cb4-e6f7abfe8364)

### 2. [Programación Micropython](/G03/micropython/test.py)  

### Funcionamiento del sensor TCS34725  

El TCS34725 detecta el color de la luz que refleja un objeto. Mide la intensidad del rojo, verde y azul (RGB) y también calcula un valor adicional llamado Clear, que representa la cantidad total de luz.  
Tiene un filtro infrarrojo que bloquea la luz no visible para hacer las mediciones más precisas, y un conversor interno que convierte esas señales de luz en datos digitales que el ESP32 puede leer fácilmente mediante I2C, usando los pines SDA y SCL.  

Cuenta con cuatro LEDs blancos que iluminan el objeto mientras se mide, lo que evita depender de la luz ambiental y mejora la estabilidad de las lecturas.  
Además, permite ajustar la ganancia y el tiempo de integración desde el software, lo que ayuda a adaptarse a diferentes niveles de iluminación.  

También dispone de un pin de interrupción que puede configurarse para ejecutar acciones automáticas si se detecta un color fuera de un rango específico.  
En general, es un sensor muy versátil y confiable, ampliamente usado en robótica, control de iluminación y sistemas IoT que requieren un reconocimiento de color rápido y preciso.  

El sensor se conectó al ESP32 mediante el protocolo I2C con la siguiente distribución de pines:

- **VDD → 3.3V:** alimentación del sensor  
- **SCL → GPIO 22:** línea de reloj  
- **GND → GND:** referencia de tierra  
- **NC:** sin conexión  
- **INT:** no se utilizó  
- **SDA → GPIO 21:** línea de datos  

---

### Proceso de calibración del sensor  

Para calibrar el sensor se realizaron tres pasos sencillos:  

1. Se colocó una superficie **blanca** frente al sensor para registrar los valores RGB más altos.  
2. Luego, se midió una superficie **negra** para obtener los valores más bajos.  
3. Con esos límites, se ajustaron las lecturas para lograr una medición más precisa de cualquier color intermedio.  

---

### Características técnicas  

- Voltaje de entrada: 3.0 V a 5.0 V  
- Corriente de entrada: hasta 20 mA  
- Chip base: TCS3472  
- Interfaz de comunicación: I2C (SDA y SCL)  
- Filtro IR integrado para mejorar la precisión  

---

### Aplicaciones  

- Detección y reconocimiento de color  
- Control automático de iluminación RGB  
- Clasificación de objetos por color  
- Sensado ambiental o ajuste de balance de blancos en cámaras  

---

#### Figura 1. Distribución de pines del sensor TCS34725  

<img width="600" alt="Distribución de pines del sensor TCS34725" src="https://github.com/user-attachments/assets/99e27d8b-741d-4262-a29c-fb898426a1cf" />  

**Fuente:** [TCS34725 Datasheet – ams OSRAM](https://electronilab.co/wp-content/uploads/2021/06/TCS34725.pdf)  

---
 
# Explicación del código del sistema de reconocimiento de color

Este programa permite que el **ESP32** lea los valores de color detectados por el **sensor TCS34725**, los convierta a una escala RGB de 0 a 255 y los envíe mediante **MQTT** hacia una **Raspberry Pi** para su visualización en **Node-RED**.  
A continuación se explica paso a paso cómo funciona.

---

## 1. Conexión WiFi

**WIFI_SSID = "TU_SSID"**
**WIFI_PASS = "TU_PASSWORD"**

El ESP32 se conecta a una red WiFi usando el nombre y la contraseña definidos aquí.  
Esto permite que más adelante pueda enviar los datos del sensor a través del protocolo MQTT hacia la Raspberry Pi.

---

## 2. Configuración MQTT

**BROKER = "192.168.153.216"**
**PORT = 1883**
**TOPIC = b"in/micro/sensor/color"**

- **BROKER:** es la dirección IP de la Raspberry Pi, donde está instalado Node-RED y el servidor MQTT.  
- **PORT:** es el puerto de comunicación (1883 es el estándar de MQTT).  
- **TOPIC:** es el canal por el cual el ESP32 envía los valores RGB que detecta el sensor.

En resumen, esta parte configura el medio de comunicación entre el ESP32 y Node-RED.

---

## 3. Configuración del sensor TCS34725

**i2c = I2C(1, scl=Pin(22), sda=Pin(21))**
**ADDR = 0x29**

El sensor TCS34725 se comunica mediante el bus **I2C**, usando los pines GPIO 21 (SDA) y GPIO 22 (SCL) del ESP32.  
La dirección **0x29** identifica al sensor dentro del bus I2C.

### Funciones principales:
- **write_reg():** escribe datos en un registro del sensor.  
- **read_reg16():** lee un valor de 16 bits desde un registro.  
- **init_tcs34725():** inicializa el sensor, lo enciende y configura el tiempo de integración y la ganancia.  
- **leer_rgbc():** obtiene los valores crudos de los cuatro canales del sensor: rojo, verde, azul y claro (intensidad de luz).

Esta parte prepara al sensor para empezar a tomar lecturas precisas de color.

---

## 4. Conversión a escala RGB (0–255)

**def convertir_255(r, g, b, coef):**

El sensor entrega valores altos (por ejemplo, entre 0 y 30000).  
Esta función los convierte al formato RGB estándar (de 0 a 255), usando los **valores máximos y mínimos obtenidos durante la calibración**.  
Así, el color detectado es más real y proporcional a la luz del entorno.

---

## 5. Conexión a WiFi

**def conectar_wifi():**

Activa el WiFi del ESP32 y lo conecta a la red configurada.  
Muestra por consola el proceso de conexión y la dirección IP obtenida.  
Esto es esencial para que luego el ESP32 pueda comunicarse con el broker MQTT.

---

## 6. Calibración del sensor

**def calibrar():**

Este proceso se hace una vez para obtener los límites de color:

1. Se coloca una superficie **blanca**, se leen los valores RGB y se guardan como máximos.  
2. Luego una superficie **negra**, para registrar los valores mínimos.  
3. Con estos datos se crea un archivo llamado **calib_rgb.json**, que guarda los coeficientes de calibración.

Gracias a esto, el sensor puede dar lecturas más precisas sin depender de la luz ambiente.

---

## 7. Programa principal

El flujo principal del programa hace lo siguiente:

1. Inicializa el sensor con init_tcs34725().  
2. Conecta el ESP32 al WiFi con conectar_wifi().  
3. Carga la calibración guardada (o realiza una nueva si no existe).  
4. Se conecta al **broker MQTT**.  
5. Entra en un bucle infinito donde:
   - Lee los valores de color del sensor.  
   - Los convierte a escala 0–255.  
   - Crea un mensaje en formato JSON, por ejemplo:
     {"R": 120, "G": 85, "B": 60}
   - Envía ese mensaje al **topic MQTT** para que Node-RED lo reciba y visualice.

## Node RED

### Flujo general


![Image 6](https://github.com/user-attachments/assets/2fd229b1-3abf-4d01-9bae-c8ea19bddfa8)


Esta imagen muestra el diagrama completo del flujo en **Node-RED**, donde el nodo MQTT recibe los datos de color enviados desde el **ESP32**.  
Esos datos pasan a dos nodos función: uno para **dividir** el valor RGB y otro para **agruparlo** nuevamente.

Los valores separados alimentan los **indicadores de color** del dashboard.  
El objeto agrupado viaja al **nodo template**, encargado de mostrar el color detectado.

Todo el flujo está organizado para **procesar y visualizar los valores RGB** del sensor.

### Nodo MQTT IN

![Image 1](https://github.com/user-attachments/assets/b1fc2930-c9a6-4c19-82fc-e1d7a6c3c80a)


En esta imagen aparece la configuración del nodo encargado de recibir datos desde MQTT.  
Está suscrito al tópico **`in/micro/sensor/color`** usando el **broker local**.  
La opción de salida está configurada para **interpretar JSON automáticamente**.

Este nodo debe recibir el mensaje enviado por el ESP32 con los valores **RGB**.  
Si no llegan datos, todo el flujo queda sin información para procesar.


### Nodo “Dividir RGB”

![Image 4](https://github.com/user-attachments/assets/fb9d5ec8-12e4-4795-bbb1-1a463788ec2c)



Esta imagen muestra el nodo función que separa el mensaje RGB original.  
El código toma los valores de **R**, **G** y **B** y genera **tres mensajes independientes**.

Cada mensaje lleva un **topic distinto** y contiene únicamente un valor numérico en el payload.  
Estos mensajes luego se conectan a indicadores individuales para representar cada color.

Este nodo permite **visualizar los tres canales por separado** en el dashboard.


### Nodo “Agrupar RGB”

![Image 5](https://github.com/user-attachments/assets/9061c416-d160-4931-909e-ed608fc47b47)



Aquí se ve el nodo función encargado de tomar los valores **R**, **G** y **B** del mensaje recibido.  
El código extrae cada componente del payload y los coloca dentro de un **nuevo objeto JSON**.

Ese objeto se asigna al **payload final** para ser enviado a la interfaz.  
Su propósito es entregar los **tres valores juntos** al template que mostrará el color.

Es una etapa de **reconstrucción de datos** para usarlos en el dashboard.

### HTML color detectado

![Image 2](https://github.com/user-attachments/assets/0f40eb46-ca02-4c8a-86d8-b9953604d745)



Esta imagen muestra el nodo que contiene el código **HTML y JavaScript** para visualizar el color detectado.  
El HTML crea un **recuadro** y un **texto** donde se mostrará el código RGB.  
El JavaScript observa los cambios en el **payload** y actualiza dinámicamente el color y el texto.

El recuadro cambia su fondo según los valores **R**, **G** y **B** recibidos.  
Este nodo es el encargado de **mostrar el resultado final del sensor** en la pantalla.


### Dashboard con indicadores en cero

![Image 3](https://github.com/user-attachments/assets/e331b434-33a0-4f74-95c9-bb1e272b672f)



Aquí se observa la interfaz gráfica del dashboard, donde deberían aparecer los valores de **rojo**, **verde** y **azul**.  
Los tres indicadores están en **cero**, lo cual significa que **no se están recibiendo datos del sensor**.

Debajo aparece el cuadro destinado a mostrar el **color detectado**, también vacío por la falta de información.  
La interfaz está bien diseñada, pero no tiene datos para actualizarse.

Esto indica un **problema previo en la recepción MQTT**.

### COLOR AZUL

<img width="600" alt="Imagen 1" src="https://github.com/user-attachments/assets/e9d752c2-ad74-4641-a56d-c5231911fe10" />

### COLOR AMARILLO

<img width="600" alt="Imagen 2" src="https://github.com/user-attachments/assets/e6940424-997d-43fe-82e3-bb4cdfcb6de1" />

### COLOR BLANCO

<img width="600" alt="Imagen 3" src="https://github.com/user-attachments/assets/118096a3-c927-4e66-b57a-009e6b6a7304" />

---
</div>
