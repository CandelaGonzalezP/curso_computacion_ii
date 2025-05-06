#Modificá este código para que use Lock correctamente:

from multiprocessing import Process, Value, Lock

def restar(contador, lock):
    for _ in range(100000):
        with lock:
            contador.value -= 1

if __name__ == '__main__':
    contador = Value('i', 100000)  # Valor inicial
    lock = Lock()

    # Crear los procesos
    p1 = Process(target=restar, args=(contador, lock))
    p2 = Process(target=restar, args=(contador, lock))

    # Iniciar los procesos
    p1.start()
    p2.start()

    # Esperar a que terminen
    p1.join()
    p2.join()

    print(f"Valor final del contador: {contador.value}")
