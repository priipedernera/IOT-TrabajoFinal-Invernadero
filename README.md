# Trabajo Final IoT – Monitoreo y riego automático de invernadero

## 1. Problema a resolver

**¿Quién lo tiene?** Pequeños productores que cultivan en invernaderos (hortalizas, plantas ornamentales).

**¿Cuál es el problema?** El suelo debe mantenerse con una humedad adecuada (por encima del 30 %) y la temperatura no debe pasar los 35 °C. Si nadie lo controla, un olvido de riego o un día de mucho calor puede arruinar el cultivo antes de que el productor lo note. Además, no queda registro histórico para entender qué pasó.

**¿Por qué IoT lo resuelve?** Un sensor mide de forma continua, el sistema detecta el problema en segundos, avisa en un dashboard, **ordena el riego automáticamente** y guarda el historial en una base de datos para consultarlo desde cualquier lugar.

## 2. Arquitectura

```
 Simulador (Python)  --MQTT invernadero/sensor-->  Broker Aedes (en Node-RED)
        ^                                                   |
        |                                                   v
        +------MQTT invernadero/comando (REGAR)------  Flujo Node-RED
                                                    |       |        |
                                                    v       v        v
                                               SQLite   Dashboard   API HTTP
```

## 3. Herramientas usadas

| Herramienta | Uso |
|---|---|
| Node-RED | Automatización: reglas, alertas y flujo principal |
| node-red-contrib-aedes | Broker MQTT dentro de Node-RED |
| node-red-node-sqlite | Base de datos |
| @flowfuse/node-red-dashboard | Visualización (Dashboard 2.0) |
| Python 3 + paho-mqtt | Dispositivo simulado |

## 4. Dispositivos y datos (simulado)

`simulador_invernadero.py` publica cada 5 segundos un JSON:

```json
{"temperatura": 24.6, "humedad_suelo": 51.2, "riego": 0, "fecha": "2026-11-02T10:00:00"}
```

Cuando recibe el comando `REGAR`, simula el riego y la humedad del suelo sube durante las siguientes lecturas.

## 5. Base de datos

SQLite, archivo `invernadero.db`, tabla `lecturas`:

| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER PK | Identificador |
| fecha | TEXT | Fecha y hora de la lectura |
| temperatura | REAL | °C |
| humedad_suelo | REAL | % |
| alerta | INTEGER | 1 si humedad < 30 %, 0 si es normal |

## 6. Protocolos de comunicación

- **MQTT**
  - `invernadero/sensor`: el sensor publica temperatura y humedad.
  - `invernadero/comando`: Node-RED publica `REGAR` cuando el suelo está seco.
- **HTTP (API REST)**
  - `GET /api/lecturas` → últimas 20 lecturas.
  - `GET /api/alertas` → últimas 50 lecturas con alerta.

## 7. Regla de automatización

```
SI humedad_suelo < 30 %
   -> mostrar ALERTA en el dashboard
   -> publicar REGAR en invernadero/comando
   -> guardar la lectura con alerta = 1
SINO
   -> guardar la lectura con alerta = 0
```

## 8. Visualización

Dashboard de Node-RED en `http://localhost:1880/dashboard` con:
- Medidor de temperatura
- Medidor de humedad del suelo
- Gráficos históricos de ambas variables
- Texto de estado (normal / alerta)

## 9. Cómo ejecutarlo

1. Instalar [Node.js](https://nodejs.org) y Node-RED:
   ```bash
   npm install -g --unsafe-perm node-red
   node-red
   ```
2. Abrir `http://localhost:1880` → menú → *Manage palette* → *Install* e instalar:
   - `node-red-contrib-aedes`
   - `node-red-node-sqlite`
   - `@flowfuse/node-red-dashboard`
3. Menú → *Import* → seleccionar `flujo_invernadero.json` → *Deploy*.
4. Instalar y correr el simulador:
   ```bash
   pip install -r requirements.txt
   python simulador_invernadero.py
   ```
5. Abrir el dashboard en `http://localhost:1880/dashboard` y probar la API:
   ```bash
   curl http://localhost:1880/api/lecturas
   curl http://localhost:1880/api/alertas
   ```

## 10. Estado del proyecto

- [x] Definición del problema
- [x] Arquitectura
- [x] Simulador MQTT en Python
- [x] Flujo Node-RED (broker, base de datos, alertas, API HTTP)
- [x] Dashboard
- [ ] Capturas de pantalla de pruebas
- [ ] Presentación final

## 11. Mejoras futuras

- Reemplazar el simulador por un ESP32 con sensor DHT22 y sensor de humedad de suelo (o simularlo en Wokwi).
- Enviar alertas por Telegram.
- Conectar Grafana para gráficos avanzados.

## Autor

Trabajo final de la materia IoT.
