from multiprocessing import Pool

def tarea(x):
    return x * x

if __name__ == '__main__':
    with Pool(processes=4) as pool:
        resultados = pool.map(tarea, [1, 2, 3, 4, 5])
        print(resultados)
