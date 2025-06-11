# Verificación y Construcción de Bloques 


import multiprocessing
import hashlib
import json
import os
import time
import datetime
import random
import numpy as np

# =============================
# Función para generar datos biométricos
# =============================
def generar_dato():
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "frecuencia": random.randint(60, 180),
        "presion": [random.randint(110, 180), random.randint(70, 110)],
        "oxigeno": random.randint(90, 100)
    }

# =============================
# Analizador
# =============================
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

# =============================
# Proceso Verificador y Cadena de Bloques
# =============================
def proceso_verificador(queue_a, queue_b, queue_c):
    blockchain = []
    prev_hash = "0"

    for i in range(60):
        # Esperar los tres resultados
        resultado_a = queue_a.get()
        resultado_b = queue_b.get()
        resultado_c = queue_c.get()

        # Asegurarse de que sean del mismo timestamp (simplificado)
        timestamp = resultado_a["timestamp"]

        # Reorganizar por tipo
        resultados = {
            resultado_a["tipo"]: resultado_a,
            resultado_b["tipo"]: resultado_b,
            resultado_c["tipo"]: resultado_c
        }

        # Verificación
        alerta = (
            resultados["frecuencia"]["media"] >= 200 or
            resultados["oxigeno"]["media"] < 90 or
            resultados["oxigeno"]["media"] > 100 or
            resultados["presion"]["media"] >= 200
        )

        # Crear bloque
        bloque = {
            "timestamp": timestamp,
            "datos": resultados,
            "alerta": alerta,
            "prev_hash": prev_hash
        }

        bloque_str = f'{prev_hash}{json.dumps(resultados, sort_keys=True)}{timestamp}'
        bloque["hash"] = hashlib.sha256(bloque_str.encode()).hexdigest()

        # Guardar en memoria
        blockchain.append(bloque)
        prev_hash = bloque["hash"]

        # Mostrar
        print(f"[Bloque #{i+1}] Hash: {bloque['hash']} | ALERTA: {alerta}")

    # Guardar en archivo
    with open("blockchain.json", "w") as f:
        json.dump(blockchain, f, indent=4)

# =============================
# Generador
# =============================
def proceso_principal(pipes_salida):
    for _ in range(60):
        dato = generar_dato()
        for pipe in pipes_salida:
            pipe.send(dato)
        time.sleep(1)

    for pipe in pipes_salida:
        pipe.close()

# =============================
# Main
# =============================
if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

    # Pipes
    principal_a, a_entrada = multiprocessing.Pipe()
    principal_b, b_entrada = multiprocessing.Pipe()
    principal_c, c_entrada = multiprocessing.Pipe()

    # Queues
    queue_a = multiprocessing.Queue()
    queue_b = multiprocessing.Queue()
    queue_c = multiprocessing.Queue()

    # Procesos
    analizador_a = multiprocessing.Process(target=proceso_analizador, args=("frecuencia", a_entrada, queue_a))
    analizador_b = multiprocessing.Process(target=proceso_analizador, args=("presion", b_entrada, queue_b))
    analizador_c = multiprocessing.Process(target=proceso_analizador, args=("oxigeno", c_entrada, queue_c))
    verificador = multiprocessing.Process(target=proceso_verificador, args=(queue_a, queue_b, queue_c))

    # Iniciar procesos
    analizador_a.start()
    analizador_b.start()
    analizador_c.start()
    verificador.start()

    # Ejecutar generador
    proceso_principal([principal_a, principal_b, principal_c])

    # Esperar a que terminen
    analizador_a.join()
    analizador_b.join()
    analizador_c.join()
    verificador.join()

    print("[Main] Ejecución completada.")
