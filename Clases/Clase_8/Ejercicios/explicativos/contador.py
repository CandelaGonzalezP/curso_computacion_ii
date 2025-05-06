from multiprocessing import Process

contador = 0

def incrementar():
    global contador
    for _ in range(100000):
        contador += 1

if __name__ == '__main__':
    p1 = Process(target=incrementar)
    p2 = Process(target=incrementar)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    print(f"Valor final del contador: {contador}")
