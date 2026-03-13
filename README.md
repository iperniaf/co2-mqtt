# CO2 MQTT Publisher

Este proyecto es un script en Python que lee datos de concentración de CO2 de un sensor MH-Z19 y los publica en un broker MQTT. Está diseñado para integrarse con sistemas de domótica como Home Assistant.

## Características

- Lectura continua de CO2 desde el sensor MH-Z19.
- Publicación de datos promediados en MQTT cada 2 minutos.
- Configuración segura mediante variables de entorno (.env).
- Manejo de errores básicos para lecturas fallidas.

## Requisitos

- **Python**: Versión 3.6 o superior.
- **Hardware**: Sensor MH-Z19 conectado al sistema (generalmente via USB/serial).
- **Broker MQTT**: Un servidor MQTT accesible (ej. Mosquitto).
- **Dependencias**: Ver `requirements.txt` para la lista completa.

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/co2-mqtt.git
   cd co2-mqtt
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura el entorno:
   - Copia el archivo de ejemplo: `cp .env.example .env`
   - Edita `.env` con tus valores reales (ver sección de Configuración).

## Configuración

El script utiliza un archivo `.env` para las configuraciones sensibles. Las variables requeridas son:

- `MQTT_SERVER_IP`: Dirección IP del broker MQTT.
- `MQTT_SERVER_PORT`: Puerto del broker MQTT (por defecto 1883).
- `MQTT_SERVER_USER`: Usuario para autenticación MQTT.
- `MQTT_SERVER_PASSWORD`: Contraseña para autenticación MQTT.
- `MQTT_SERVER_TOPIC`: Tópico MQTT donde publicar los datos (ej. `homeassistant/co2`).

Ejemplo de `.env`:
```
MQTT_SERVER_IP=192.168.1.100
MQTT_SERVER_PORT=1883
MQTT_SERVER_USER=tu_usuario
MQTT_SERVER_PASSWORD=tu_contraseña
MQTT_SERVER_TOPIC=homeassistant/sensor/co2
```

**Nota de seguridad**: Nunca subas el archivo `.env` real al repositorio. Usa `.env.example` como plantilla.

## Uso

Ejecuta el script principal:
```bash
python co2-mqtt.py
```

El script iniciará un hilo para leer el sensor cada 30 segundos y publicará un mensaje MQTT cada 2 minutos con el valor mediano de CO2 y una marca de tiempo.

### Salida de ejemplo
```
Main thread running
Published message: {"co2": 450, "timestamp": "13/03/2026, 12:00:00"} Topic homeassistant/co2
```

## Estructura del proyecto

- `co2-mqtt.py`: Script principal.
- `mh_z19.py`: Módulo para interactuar con el sensor MH-Z19.
- `requirements.txt`: Dependencias de Python.
- `.env.example`: Plantilla de configuración.
- `.gitignore`: Archivos ignorados por Git.

## Notas adicionales

- **Sensor**: Asegúrate de que el sensor MH-Z19 esté correctamente conectado y no sea accedido por otros procesos (usa `serial_console_untouched=True`).
- **MQTT**: Si usas TLS, descomenta la línea correspondiente en el código.
- **Errores**: Si el sensor falla, el script usa el último valor válido.
- **Licencia**: [MIT](LICENSE) (agrega un archivo LICENSE si no lo tienes).

## Contribución

Si encuentras problemas o quieres mejorar el código, abre un issue o envía un pull request.