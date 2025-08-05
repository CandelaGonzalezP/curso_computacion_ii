# sistema_biometrico.py
# Trabajo Práctico - Sistema Concurrente de Análisis Biométrico con Cadena de Bloques Local

import multiprocessing
import hashlib
import json
import os
import time
import datetime
import random
import numpy as np

# ========== TAREA 1: Generación y Análisis Concurrente ==========

def generar_dato():
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "frecuencia": random.randint(60, 180),
        "presion": [random.randint(110, 180), random.randint(70, 110)],
        "oxigeno": random.randint(90, 100)
    }

def proceso_analizador(nombre, pipe_entrada, queue_salida):
    ventana = []
    for _ in range(60):
        try:
            paquete = pipe_entrada.recv()
            timestamp = paquete["timestamp"]

            if nombre == "frecuencia":
                valor = paquete["frecuencia"]
            elif nombre == "presion":
                valor = paquete["presion"][0]  # sistólica
            elif nombre == "oxigeno":
                valor = paquete["oxigeno"]
            else:
                continue

            ventana.append(valor)
            if len(ventana) > 30:
                ventana.pop(0)

            media = float(np.mean(ventana))
            desv = float(np.std(ventana))

            resultado = {
                "tipo": nombre,
                "timestamp": timestamp,
                "media": media,
                "desv": desv
            }

            queue_salida.put(resultado)

        except EOFError:
            break

# ========== TAREA 2: Verificador y Blockchain ==========

def calcular_hash(prev_hash, datos, timestamp):
    bloque_str = f"{prev_hash}{json.dumps(datos, sort_keys=True)}{timestamp}"
    return hashlib.sha256(bloque_str.encode()).hexdigest()

def proceso_verificador(queue_a, queue_b, queue_c):
    blockchain = []
    prev_hash = "0"

    os.makedirs("output", exist_ok=True)

    for i in range(60):
        resultado_a = queue_a.get()
        resultado_b = queue_b.get()
        resultado_c = queue_c.get()

        timestamp = resultado_a["timestamp"]

        resultados = {
            resultado_a["tipo"]: resultado_a,
            resultado_b["tipo"]: resultado_b,
            resultado_c["tipo"]: resultado_c
        }

        alerta = (
            resultados["frecuencia"]["media"] >= 200 or
            resultados["oxigeno"]["media"] < 90 or resultados["oxigeno"]["media"] > 100 or
            resultados["presion"]["media"] >= 200
        )

        bloque = {
            "timestamp": timestamp,
            "datos": resultados,
            "alerta": alerta,
            "prev_hash": prev_hash
        }

        bloque["hash"] = calcular_hash(prev_hash, resultados, timestamp)
        blockchain.append(bloque)
        prev_hash = bloque["hash"]

        print(f"[Bloque #{i+1}] Hash: {bloque['hash']} | ALERTA: {alerta}")

    with open("output/blockchain.json", "w") as f:
        json.dump(blockchain, f, indent=4)

# ========== Proceso Principal ==========

def proceso_principal(pipes_salida):
    for _ in range(60):
        dato = generar_dato()
        for pipe in pipes_salida:
            pipe.send(dato)
        time.sleep(1)

    for pipe in pipes_salida:
        pipe.close()

# ========== Main ==========

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

    principal_a, a_entrada = multiprocessing.Pipe()
    principal_b, b_entrada = multiprocessing.Pipe()
    principal_c, c_entrada = multiprocessing.Pipe()

    queue_a = multiprocessing.Queue()
    queue_b = multiprocessing.Queue()
    queue_c = multiprocessing.Queue()

    analizador_a = multiprocessing.Process(target=proceso_analizador, args=("frecuencia", a_entrada, queue_a))
    analizador_b = multiprocessing.Process(target=proceso_analizador, args=("presion", b_entrada, queue_b))
    analizador_c = multiprocessing.Process(target=proceso_analizador, args=("oxigeno", c_entrada, queue_c))
    verificador = multiprocessing.Process(target=proceso_verificador, args=(queue_a, queue_b, queue_c))

    analizador_a.start()
    analizador_b.start()
    analizador_c.start()
    verificador.start()

    proceso_principal([principal_a, principal_b, principal_c])

    analizador_a.join()
    analizador_b.join()
    analizador_c.join()
    verificador.join()

    print("[Main] Ejecución completada.")