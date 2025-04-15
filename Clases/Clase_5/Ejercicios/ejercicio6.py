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
    q = Queue()  # Crear la cola para la comunicación
    pid = os.fork()  # Crear un proceso hijo
    
    if pid == 0:
        # Proceso hijo: consumidor
        consumidor(q)
        os._exit(0)  # Termina el proceso hijo
    else:
        # Proceso padre: productor
        productor(q)
        os.wait()  # Espera a que el proceso hijo termine
        print("[Main] Comunicación finalizada.")
