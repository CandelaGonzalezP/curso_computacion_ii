from multiprocessing import Pool
import time

def tarea(n):
    print(f"Procesando {n}...")
    time.sleep(1)
    return n * 2

if __name__ == '__main__':
    with Pool(processes=3) as pool:
        resultados = pool.map(tarea, [1, 2, 3, 4, 5, 6])
        print("Resultados:", resultados)
