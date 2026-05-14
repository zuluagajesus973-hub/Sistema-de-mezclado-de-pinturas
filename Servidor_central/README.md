# Servidor Central - Sistema de Captura y Comunicación MQTT con Raspberry Pi

### Indice


1. [**Resumen**](#resumen)  
2. [**Introducción**](#introduccion)  
3. [**Metodología del Servidor Central**](#metodologia-del-servidor-central)  
   - [3.1 Instalación del entorno base](#31-instalacion-del-entorno-base)  
   - [3.2 Configuración del Broker MQTT (Mosquitto)](#32-configuracion-del-broker-mqtt-mosquitto)  
   - [3.3 Instalación y configuración de Node-RED](#33-instalacion-y-configuracion-de-node-red)  
   - [3.4 Instalación y configuración de Ngrok](#34-instalacion-y-configuracion-de-ngrok)  
4. [**Integración completa del sistema**](#integracion-completa-del-sistema)  
5. [**Pruebas y Validación del Sistema**](#pruebas-y-validacion-del-sistema)  
6. [**Conclusión**](#conclusion) 


## 1. RESUMEN

Este documento explica cómo se implementó el servidor central del sistema de monitoreo basado en Raspberry Pi, MQTT, Node-RED y Ngrok.

El servidor es el "cerebro" del proyecto: recibe datos, publica imágenes y coordina la comunicación con otros dispositivos como ESP32 u otros nodos IoT. Aquí encontrarás todos los pasos necesarios para configurarlo: instalación de servicios, activación del broker MQTT, habilitación de accesos externos con Ngrok, solución de errores comunes y pruebas básicas para validar el funcionamiento.	

## 2. INTRODUCCIÓN
El servidor central es la pieza fundamental del sistema de monitoreo desarrollado. Su función principal es actuar como punto de encuentro para todos los dispositivos que participan en el proyecto: cámaras, sensores, microcontroladores ESP32, dashboards de supervisión y cualquier otro nodo IoT que necesite enviar o recibir información.

Este enfoque se logra gracias a una arquitectura basada en Raspberry Pi, Node-RED, MQTT y Ngrok, tecnologías que permiten construir una plataforma sólida, modular y accesible.

### ¿Por qué se necesita un servidor central?

En sistemas de monitoreo y control distribuidos, cada dispositivo genera datos de manera independiente. Sin un servidor central, estos datos quedarían aislados, serían difíciles de coordinar y no habría una forma eficiente de integrarlos. El servidor central cumple funciones clave como:

* Recolectar datos provenientes de distintos dispositivos.

* Procesar información, como imágenes u otros eventos capturados.

* Distribuir mensajes MQTT, garantizando que cada nodo reciba la información correcta.

* Conectar la red local con Internet, permitiendo supervisión remota en tiempo real.

* Ejecutar automatizaciones mediante Node-RED.
### Componentes utilizados
•	Hardware: Raspberry Pi 3 B+ (o superior), microSD ≥ 16GB, cámara CSI.

• Software: Raspberry Pi OS, Mosquitto, Node-RED, Python3, Ngrok.

## ¿Cómo opera dentro del sistema?

La Raspberry Pi se ejecuta como un mini-servidor completamente autónomo. Administra:
* El broker Mosquitto MQTT, que gestiona tópicos, conexiones, publicaciones y suscripciones.

* El servidor Node-RED, encargado de flujos lógicos, interfaces visuales y automatizaciones.

* La pasarela remota Ngrok, que permite acceder desde cualquier lugar sin necesidad de modificar el router o abrir puertos.

Dado que la Raspberry Pi consume poca energía, puede mantenerse encendida de manera continua, convirtiéndose en un servidor estable, seguro y confiable para un sistema IoT. Esta configuración está pensada para que incluso personas sin experiencia puedan entender las funciones del servidor y replicarlo paso a paso.


### 3. METODOLOGÍA
### 3.1 Preparación del entorno
1.	Actualizar el sistema operativo:

 	```sudo apt update && sudo apt upgrade -y```
2.	Instalar Mosquitto y sus clientes: [Instalacion de mosquito](https://github.com/DianaNatali/ECCI-Sistemas-Digitales-3-2025-II/blob/main/labs/05_lab05/README.md)

 	    sudo apt install mosquitto mosquitto-clients -y
        sudo systemctl enable mosquitto
        sudo systemctl start mosquitto

 	Verificación:

 	```sudo systemctl status mosquitto```
 	El servicio debe mostrarse como active (running).
3.	Instalar Node-RED: 	[Instalacion Node_RED](https://github.com/DianaNatali/ECCI-Sistemas-Digitales-3-2025-II/blob/main/labs/04_lab04/README.md)

 	```bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)```

 	Luego:

 	```node-red-start```

 	Acceso desde navegador local:

 	```http://localhost:1880```

 	Para que Node-RED arranque automáticamente con el sistema:

 	```sudo systemctl enable nodered.service```

4.	Instalar Python y dependencias:

 	```sudo apt install python3-pip imagemagick -y```

    ```pip install paho-mqtt --break-system-packages```

Una vez instaladas las dependencias necesarias para el procesamiento de imágenes y la comunicación MQTT en Python, se valida también la correcta integración del sistema visual mediante Node-RED. En la siguiente figura se presenta el dashboard completo del proyecto, donde se centraliza la visualización de los diferentes sensores y módulos conectados.

Este panel operativo permite monitorear, en tiempo real, los valores reportados por los sensores de temperatura, las galgas de fuerza, el módulo de detección de color y el estado de las válvulas. Además, incluye el componente de cámara, desde el cual se pueden capturar imágenes y realizar análisis directamente desde la interfaz. Esta integración facilita la supervisión global del sistema y confirma que todos los módulos de software y hardware se encuentran correctamente vinculados.

![Arquitectura de servidor](/Servidor_central/img/Interfaz.JPG)

### 3.2 Configuración del broker MQTT

El broker Mosquitto es el núcleo de la infraestructura MQTT: gestiona conexiones, tópicos, publicaciones y suscripciones. Aquí tienes una guía paso a paso —más clara, segura y orientada a resolución de problemas— para dejar el broker operativo en la Raspberry Pi y exponerlo (si es necesario) a clientes externos.

Con el broker MQTT funcionando localmente y protegido mediante autenticación, el siguiente paso es habilitar acceso remoto seguro utilizando Ngrok, lo cual se explica en la siguiente sección.

#### 1) Prueba rápida local (verifica que Mosquitto funciona)

Terminal A (suscriptor):

	mosquitto_sub -t prueba

Terminal B (publicador):

	mosquitto_pub -t prueba -m "Hola MQTT"

Si en la Terminal A aparece Hola MQTT, el broker funciona localmente.

#### 2) Configuración básica y control de acceso (¡no uses allow_anonymous true en producción!)

Por defecto permitir acceso anónimo es cómodo pero inseguro. Te muestro dos opciones según tu objetivo:

### A) Para pruebas rápidas en red local (solo temporal)

Editar archivo:

	sudo nano /etc/mosquitto/mosquitto.conf

Agregar al final:

	listener 1883
	allow_anonymous true

Guardar y reiniciar:

	sudo systemctl restart mosquitto
	sudo systemctl status mosquitto --no-pager

Aviso: esto permite que cualquiera en tu red local se conecte sin autenticación. Úsalo solo en entornos controlados.


### B) Recomendado: acceso con usuario/contraseña (seguro)

1) Crear archivo de contraseñas y añadir un usuario:
	sudo mosquitto_passwd -c /etc/mosquitto/passwd tu_usuario
	nota: te pedirá la contraseña
2) Configurar Mosquitto para usar el archivo y denegar anónimo:

	sudo nano /etc/mosquitto/mosquitto.conf

Agregar:

	listener 1883
	allow_anonymous false
	password_file /etc/mosquitto/passwd

3) Reiniciar y verificar:

	sudo systemctl restart mosquitto
	sudo systemctl status mosquitto

4) Probar la conexión autenticada (desde cliente):

		mosquitto_pub -h localhost -t prueba -m "test" -u tu_usuario -P 'tu_contraseña'
		mosquitto_sub -h localhost -t prueba -u tu_usuario -P 'tu_contraseña'


### 3.3 Instalación y configuración de Ngrok
Ngrok permite acceder al servidor desde Internet sin necesidad de modificar el router, abrir puertos o gestionar IP pública dinámica. Esto hace que el sistema sea fácil de implementar incluso en redes restringidas, como universidades, oficinas o redes domésticas sin acceso al módem.

Nota: La versión gratuita solo permite un túnel activo. Para este proyecto se crearon dos cuentas (una para Node-RED y otra para MQTT).

* Para este proyecto fue necesario crear dos cuentas distintas ya que para la vercion gratuita solo se puede crear un tunel a la vez.

1.	Crear cuenta y obtener token:
	* ir a [Ngrok](https://ngrok.com)
	* Registrarse gratis y copiar el AuthToken (en el panel principal)

 2.	Agregar tokens de autenticación (cuentas separadas):
	* Para esto se creaaron dos carpetas para correr y almacenar los tokens de forma separa y asi evitar conplictos

		```mkdir ~/ngrok_nodered```

		```mkdir ~/ngrok_mqtt```

	* Token Node-RED (puerto 1880): Se ingresa a la carpeta ```~/ngrok_nodered``` o donde este guardodo el token para ser utilizado en el puerto 1880 y luego ejecutar:

 	```ngrok config add-authtoken Aca va el token que se copio```

	* Token MQTT (puerto 1883):Se ingresa a la carpeta ```~/ngrok_mqtt```o donde este guardodo el token para ser utilizado en el puerto 1883 y luego ejecutar:

 	```ngrok config add-authtoken <Aca va el token que se copio>```

3.	Lanzar túneles:
* Para Node-RED:

 	```cd ~/ngrok_nodered```
	
	```ngrok http 1880```

 	→ Copiar la URL HTTPS pública y compartirla con los demas integrantes.
* Para MQTT (tras verificar la cuenta):
 	
	```cd ~/ngrok_mqtt```

	```ngrok tcp 1883```

 	Esto generará una dirección tipo tcp://0.tcp.ngrok.io:xxxxx.
 	
Para permitir que el servidor MQTT sea accesible de forma segura desde ubicaciones externas, se utilizó Ngrok, una herramienta que crea túneles cifrados hacia servicios locales.
En la prueba realizada, Ngrok generó un túnel TCP que redirige las conexiones públicas hacia el puerto local 1883, donde se ejecuta el broker MQTT.


![Arquitectura de servidor](/Servidor_central/img/1..JPG)

* El túnel activo en la región Estados Unidos (US)
* La latencia promedio del enlace
* El endpoint público generado:
tcp://8.tcp.ngrok.io:12777 → localhost:1883
* El panel de control local disponible en http://127.0.0.1:4041
* El registro de conexiones realizadas en tiempo real

### Conclusion

El servidor central construido sobre Raspberry Pi integra de forma eficiente las tecnologías Node-RED, Mosquitto MQTT y Ngrok, permitiendo un entorno IoT robusto, modular y accesible. Su arquitectura garantiza comunicación en tiempo real, fácil escalabilidad y acceso remoto seguro. La metodología presentada permite que cualquier usuario pueda replicar la instalación, extenderla con nuevos sensores y depurar problemas comunes sin dificultades, consolidando así un sistema confiable para monitoreo distribuido.

 	



 	