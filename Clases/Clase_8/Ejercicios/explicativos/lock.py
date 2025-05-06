from multiprocessing import Process, Lock, Value

def incrementar(lock, contador):
    for _ in range(100000):
        with lock:
            contador.value += 1

if __name__ == '__main__':
    lock = Lock()
    contador = Value('i', 0)  # 'i' = entero compartido
    
    p1 = Process(target=incrementar, args=(lock, contador))
    p2 = Process(target=incrementar, args=(lock, contador))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print(f"Valor final del contador: {contador.value}")
