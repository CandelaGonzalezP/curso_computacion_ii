from multiprocessing import Process, Value

def incrementar(valor):
    for _ in range(100000):
        valor.value += 1

if __name__ == '__main__':
    contador = Value('i', 0)  # 'i' indica un entero

    p1 = Process(target=incrementar, args=(contador,))
    p2 = Process(target=incrementar, args=(contador,))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print(f"Valor final: {contador.value}")
