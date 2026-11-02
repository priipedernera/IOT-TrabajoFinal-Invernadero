"""Simulador de sensores de un invernadero.

Publica temperatura y humedad del suelo por MQTT cada 5 segundos y
escucha el topic de comandos: cuando recibe REGAR, activa el riego y
la humedad del suelo sube.
"""
import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883
TOPIC_SENSOR = "invernadero/sensor"
TOPIC_COMANDO = "invernadero/comando"
INTERVALO = 5

estado = {"temperatura": 24.0, "humedad_suelo": 55.0, "riego": 0}


def on_connect(client, userdata, flags, rc, *args):
    print(f"Conectado al broker (rc={rc})")
    client.subscribe(TOPIC_COMANDO)


def on_message(client, userdata, msg):
    comando = msg.payload.decode().strip()
    print(f"<- Comando recibido: {comando}")
    if comando == "REGAR":
        estado["riego"] = 3  # el riego dura 3 lecturas


def siguiente_lectura():
    estado["temperatura"] += random.uniform(-0.8, 0.9)
    estado["temperatura"] = max(15.0, min(38.0, estado["temperatura"]))
    if estado["riego"] > 0:
        estado["humedad_suelo"] += random.uniform(10, 15)
        estado["riego"] -= 1
    else:
        estado["humedad_suelo"] -= random.uniform(1, 4)
    estado["humedad_suelo"] = max(5.0, min(95.0, estado["humedad_suelo"]))
    return {
        "temperatura": round(estado["temperatura"], 1),
        "humedad_suelo": round(estado["humedad_suelo"], 1),
        "riego": 1 if estado["riego"] > 0 else 0,
        "fecha": datetime.now().isoformat(timespec="seconds"),
    }


def main():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # paho 2.x
    except AttributeError:
        client = mqtt.Client()  # paho 1.x
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PUERTO, 60)
    client.loop_start()
    try:
        while True:
            lectura = siguiente_lectura()
            client.publish(TOPIC_SENSOR, json.dumps(lectura))
            print(f"-> {lectura}")
            time.sleep(INTERVALO)
    except KeyboardInterrupt:
        print("Simulador detenido")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
