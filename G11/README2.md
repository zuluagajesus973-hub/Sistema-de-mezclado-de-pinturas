# Control de Bombas de Diafragma con ESP32, MicroPython y MQTT

## Integrantes
- [David Santiago Puentes Cárdenas — 99225](https://github.com/Monstertrox)  
- [Juan David Arias Bojacá — 107394](https://github.com/juandariasb-ai)

## Objetivo del Sistema
Controlar cinco bombas de diafragma mediante una ESP32 que recibe recetas de mezcla en formato CMYKW (Cian, Magenta, Yellow, Black, White) por MQTT. El sistema convierte los porcentajes de color en tiempos de activación para cada bomba, considerando restricciones de temperatura y límites de capacidad total.

## Arquitectura del Sistema

### Componentes Principales
- 5 Bombas de diafragma controladas por PWM
- 1 Motor agitador para mezclar la pintura
- Sistema de validación de temperatura por bomba
- Comunicación MQTT para recibir recetas y estados

## Descripción Detallada del Código

### 1. Configuración de Hardware y Comunicaciones

```python
# Configuración WiFi
WIFI_SSID = ""
WIFI_PASSWORD = ""

# Configuración MQTT
MQTT_BROKER = ""
MQTT_PORT = 1883
MQTT_CLIENT_ID = b""

# Topics de estado de temperatura / válvulas (1..5)
VALVE_TOPICS = [
    b"",  # bomba 1 -> C
    b"",  # bomba 2 -> M
    b"",  # bomba 3 -> Y
    b"",  # bomba 4 -> K
    b"",  # bomba 5 -> W
]

```
Propósito: Establece las credenciales de red y la conexión al broker MQTT.

2. Configuración de Bombas y PWM

```python

PWM_PINS = []   # Pines para 5 bombas
PWM_FREQ = 1000                 # Frecuencia PWM en Hz
PWM_GLOBAL = 70                 # Duty cycle global en %
TIEMPOS_BOMBAS_MAX = []  # Tiempos máximos por bomba
MAX_TOTAL_PERCENT = 40          # Límite total de porcentaje CMYKW

Funcionalidad:

Control individual de cada bomba mediante PWM

Limitación del duty cycle al 70% para protección

Restricción del total CMYKW al 40% para evitar sobrecargas

```

3. Sistema de Agitador

```python

AGITATOR_PIN_NUM = 
AGITATOR_TIME_S = 
Propósito: Mezcla la pintura después de completar la secuencia de bombas durante 10 segundos.

```

4. Estados y Variables Globales

```python
# Estados del sistema
tiempos_bombas_receta = [0.0] * 5  # Tiempos calculados para cada bomba
flags = [0] * 5                    # Bandera de finalización por bomba
receta_lista = False               # Indica si hay receta pendiente
mezcla_en_progreso = False         # Indica si hay mezcla en curso
temp_ok = [False] * 5              # Estados de temperatura por bomba
```

Funciones Principales de Control
Inicialización de PWM
```python
def init_pwms():
    global pwms
    pwms = []
    for n in PWM_PINS:
        p = PWM(Pin(n), freq=PWM_FREQ)
        p.duty(0)
        pwms.append(p)
    aplicar_pwm_global()
```
Propósito: Configura todos los pines PWM y establece el duty cycle inicial.

Procesamiento de Recetas CMYKW
```python
def parse_cmykw(text):
    """
    Convierte texto 'C:10 M:0 Y:0 K:90 W:0' a diccionario
    """
    values = {'C':0, 'M':0, 'Y':0, 'K':0, 'W':0}
    parts = text.replace(',', ' ').split()
    for p in parts:
        if ':' in p:
            k, v = p.split(':', 1)
            k = k.strip().upper()
            v = v.strip()
            if k in values:
                try:
                    values[k] = int(v)
                except:
                    pass
    return values
```
Conversión a Tiempos
```python
def cmykw_to_tiempos(values):
    # Aplica límite del 40% y escala si es necesario
    total = values['C'] + values['M'] + values['Y'] + values['K'] + values['W']
    if total > MAX_TOTAL_PERCENT and total > 0:
        factor = MAX_TOTAL_PERCENT / float(total)
        for k in values:
            values[k] = int(round(values[k] * factor))
    
    # Convierte porcentajes a tiempos
    keys = ['C', 'M', 'Y', 'K', 'W']
    tiempos = []
    for i, k in enumerate(keys):
        pct = values[k]
        tmax = TIEMPOS_BOMBAS_MAX[i]
        t = tmax * (pct / 100.0)
        tiempos.append(t)
    return tiempos
```

Control de Ejecución de Bombas

```python
def ejecutar_bomba_tiempo(i, t_seg):
    """
    Ejecuta bomba i por t_seg segundos si:
    - t_seg > 0
    - temp_ok[i] == True
    """
    global flags

    if t_seg <= 0:
        flags[i] = 1
        return

    if not temp_ok[i]:
        print("Bomba {}: temperatura NO OK, se omite".format(i+1))
        flags[i] = 1
        return

    encender_bomba(i)
    start = time.ticks_ms()
    dur_ms = int(t_seg * 1000)
    while time.ticks_diff(time.ticks_ms(), start) < dur_ms:
        if client is not None:
            try:
                client.check_msg()
            except:
                pass
        time.sleep_ms(50)
    apagar_bomba(i)
    flags[i] = 1
```

Características:

Verificación de temperatura antes de activar

Control de tiempo preciso con time.ticks_ms()

Monitoreo continuo de MQTT durante la ejecución

Manejo de MQTT

```python

def mqtt_callback(topic, msg):
    global tiempos_bombas_receta, receta_lista, mezcla_en_progreso, temp_ok

    t = topic.decode() if isinstance(topic, bytes) else str(topic)
    s = msg.decode() if isinstance(msg, bytes) else str(msg)

    # Procesar receta CMYKW
    if t == MQTT_TOPIC_CMYK.decode():
        vals = parse_cmykw(s)
        tiempos = cmykw_to_tiempos(vals)
        tiempos_bombas_receta = tiempos
        receta_lista = True
        mezcla_en_progreso = False
        reset_flags_all()
        return

    # Procesar estados de temperatura/válvulas
    for i in range(5):
        if t == VALVE_TOPICS[i].decode():
            val = s.strip().upper()
            temp_ok[i] = (val in ("ON", "1", "TRUE"))
            return
```
Flujo Principal del Programa
```python
def main():
    global receta_lista, mezcla_en_progreso

    connect_wifi()
    init_pwms()
    connect_mqtt()

    while True:
        # Escuchar MQTT continuamente
        if client is not None:
            try:
                client.check_msg()
            except:
                pass

        # Ejecutar receta cuando esté lista
        if receta_lista and not mezcla_en_progreso:
            mezcla_en_progreso = True
            print("\n*** Iniciando secuencia de bombas ***")

            for i in range(5):
                ejecutar_bomba_tiempo(i, tiempos_bombas_receta[i])

            if all(flags):
                print("Activando agitador...")
                run_agitador()

            mezcla_en_progreso = False
            receta_lista = False

        time.sleep_ms(100)
```
## Formato de Mensajes MQTT

### Recetas CMYKW
- **Topic**: `""`
- **Formato**: `C:10 M:20 Y:5 K:15 W:0`
- **Descripción**: Porcentajes de cada color (0-100%)

### Estados de Temperatura
- **Topics**: `""` a `""`
- **Valores**: `ON`, `1`, `TRUE` (temperatura OK) u otros (temperatura no OK)

## Secuencia de Operación

1. **Recepción de Receta**: El sistema recibe una receta CMYKW por MQTT
2. **Validación de Temperatura**: Verifica que cada bomba tenga temperatura OK
3. **Ejecución Secuencial**: Activa cada bomba en orden por su tiempo calculado
4. **Agitación Final**: Mezcla la pintura por 10 segundos
5. **Reset**: Prepara el sistema para la siguiente receta

## Características de Seguridad

- **Límite de Capacidad**: Máximo 40% total en recetas CMYKW
- **Verificación de Temperatura**: Cada bomba requiere temperatura OK
- **Control de PWM**: Duty cycle limitado al 70%
- **Manejo de Errores**: Try-catch en puntos críticos

## Integración con Node-RED

### Flujo Recomendado:
- **Nodo de Entrada**: Para enviar recetas CMYKW al topic `""`
- **Nodos de Temperatura**: Publicar estados de válvulas en topics `""`
- **Dashboard**: Monitoreo visual del estado del sistema

Conclusión
Este sistema proporciona un control preciso de mezclas de pintura con validaciones de seguridad y comunicación bidireccional mediante MQTT.


Este formato README.md está bien estructurado para GitHub con:
- Encabezados jerárquicos claros
- Código formateado en bloques
- Listas organizadas
- Secciones lógicas
- Énfasis en elementos importantes
- Fácil lectura y navegación

