# Firmware MQTT con ESP32 en Wokwi

Este firmware simula una cerradura con ESP32 usando MQTT en Wokwi.  
La ESP32 se conecta a la red simulada `Wokwi-GUEST`, publica el estado de la cerradura y recibe comandos MQTT para abrir o cerrar.

## Objetivo

Este proyecto permite probar la lógica de comunicación MQTT sin hardware físico, usando:

- ESP32 DevKit C V4.
- Wokwi como simulador.
- MQTT Explorer como cliente para ver y enviar mensajes MQTT.

## Requisitos

- Cuenta o acceso a Wokwi.
- Proyecto configurado con `board-esp32-devkit-c-v4`.
- Librería `PubSubClient`.
- MQTT Explorer instalado en tu PC.
- Conexión a internet para acceder al broker público `broker.emqx.io`.

## Estructura esperada

En la carpeta `firmware/` deberías tener al menos:

- `diagram.json`
- `sketch.ino` o `main.ino`
- `README.md`

## Hardware simulado

El hardware mínimo para esta versión es:

- `board-esp32-devkit-c-v4`.
- 1 LED rojo.
- 1 resistencia de 220Ω o 330Ω.

Conexión recomendada:

- GPIO2 -> resistencia -> ánodo del LED.
- cátodo del LED -> GND.

## Configuración MQTT

El firmware usa estos parámetros:

- SSID: `Wokwi-GUEST`
- Password: vacío
- Broker: `broker.emqx.io`
- Puerto: `1883`

Topics:

- Comando: `locks/1/command`
- Estado: `locks/1/state`

Mensajes esperados:

- `OPEN` para desbloquear.
- `CLOSE` para bloquear.
- `LOCKED` como estado publicado.
- `UNLOCKED` como estado publicado.

## Puesta en marcha en Wokwi

1. Abrir el proyecto en Wokwi.
2. Verificar que el archivo `diagram.json` use `board-esp32-devkit-c-v4`.
3. Confirmar que el LED esté conectado al GPIO2 con su resistencia en serie.
4. Abrir el archivo del firmware y pegar o compilar el código.
5. Ejecutar la simulación.
6. Abrir el monitor serial para ver el estado de conexión WiFi y MQTT.

## Uso con MQTT Explorer

1. Abrir MQTT Explorer.
2. Crear una conexión nueva al broker `broker.emqx.io`.
3. Usar el puerto `1883`.
4. Conectarse sin usuario ni contraseña.
5. Suscribirse o navegar al topic `locks/1/state` para ver el estado.
6. Publicar mensajes en `locks/1/command` para controlar la cerradura.

Ejemplos:

- Publicar `OPEN` en `locks/1/command`.
- Publicar `CLOSE` en `locks/1/command`.

## Comportamiento del firmware

- Al iniciar, la ESP32 se conecta a WiFi.
- Luego intenta conectarse al broker MQTT.
- Publica el estado inicial de la cerradura.
- Escucha mensajes en el topic de comando.
- Cada cambio de estado actualiza `locks/1/state`.

## Verificación rápida

Si todo está bien configurado, deberías ver:

- En el Serial Monitor: mensajes de conexión WiFi y MQTT.
- En MQTT Explorer: el estado actual en `locks/1/state`.
- En la simulación: el LED encendido o apagado según el estado.

## Notas

- Este proyecto usa un broker público, por lo que no requiere credenciales.
- Si el estado no aparece en MQTT Explorer, revisa que estés conectado al mismo broker y que los topics estén escritos exactamente igual.
- Si el LED no responde, revisa la conexión en `GPIO2` y la resistencia en serie.

## Archivos relevantes

- `diagram.json`: define el hardware simulado.
- `sketch.ino`: contiene la lógica MQTT.
- `README.md`: explica cómo ejecutar la simulación.