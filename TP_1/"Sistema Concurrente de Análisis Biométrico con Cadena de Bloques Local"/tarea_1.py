# Generación y Análisis Concurrente


import multiprocessing
import time
import datetime
import random
import numpy as np

def generar_dato():
    dato = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "frecuencia": random.randint(60, 180),
        "presion": [random.randint(110, 180), random.randint(70, 110)],
        "oxigeno": random.randint(90, 100)
    }
    print(f"[Generador] Dato generado: {dato}")
    return dato

def proceso_analizador(nombre, pipe_entrada, queue_salida):
    ventana = []

    for _ in range(60):
        try:
            paquete = pipe_entrada.recv()
            timestamp = paquete["timestamp"]

            if nombre == "frecuencia":
                valor = paquete["frecuencia"]
            elif nombre == "presion":
                valor = paquete["presion"][0]  # solo sistólica
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

            print(f"[{nombre.upper()}] Resultado: {resultado}")
            queue_salida.put(resultado)

        except EOFError:
            break

def proceso_principal(pipes_salida):
    for i in range(60):
        dato = generar_dato()
        for idx, pipe in enumerate(pipes_salida):
            pipe.send(dato)
        time.sleep(1)

    for pipe in pipes_salida:
        pipe.close()

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

    analizador_a.start()
    analizador_b.start()
    analizador_c.start()

    proceso_principal([principal_a, principal_b, principal_c])

    analizador_a.join()
    analizador_b.join()
    analizador_c.join()

    print("[Main] Ejecución completada.")
