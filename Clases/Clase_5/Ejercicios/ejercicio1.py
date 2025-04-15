#Ejemplo 1 – Comunicación entre procesos

import os
import time
from multiprocessing import Queue

def productor(q):
    for i in range(5):
        mensaje = f"Dato {i}"
        q.put(mensaje)
        print(f"[Productor] Enviado: {mensaje}")
        time.sleep(0.5)

def consumidor(q):
    for i in range(5):
        dato = q.get(timeout=5)  # Lanza excepción si pasan 5 segundos para evitar deadlock
        print(f"[Consumidor] Recibido: {dato}")
        time.sleep(0.5)

if __name__ == "__main__":
    q = Queue()
    pid = os.fork()
    
    if pid == 0:
        # Proceso hijo: consumidor
        consumidor(q)
        os._exit(0)
    else:
        # Proceso padre: productor
        productor(q)
        os.wait()
        print("[Main] Comunicación finalizada.")

