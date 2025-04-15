import os
import time
from multiprocessing import Process, Queue

def productor(q, id_prod):
    for i in range(5):
        mensaje = f"Producto {id_prod}-{i}"
        q.put(mensaje)
        print(f"[Productor {id_prod}] Enviado: {mensaje}")
        time.sleep(0.5)

def consumidor(q, id_cons):
    while True:
        try:
            dato = q.get(timeout=5)  # Lanza excepción si pasan 5 segundos
            print(f"[Consumidor {id_cons}] Recibido: {dato}")
            time.sleep(1)
        except:
            break  # Termina cuando no hay más datos

if __name__ == "__main__":
    q = Queue()
    productores = []
    consumidores = []
    
    # Crear varios productores
    for i in range(2):
        p = Process(target=productor, args=(q, i))
        productores.append(p)
        p.start()
    
    # Crear varios consumidores
    for i in range(3):
        c = Process(target=consumidor, args=(q, i))
        consumidores.append(c)
        c.start()
    
    # Esperar a que todos los productores terminen
    for p in productores:
        p.join()
    
    # Esperar a que todos los consumidores terminen
    for c in consumidores:
        c.join()

    print("[Main] Comunicación finalizada.")
