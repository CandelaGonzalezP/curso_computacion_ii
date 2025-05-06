#Modificá este código para que, en lugar de duplicar los números, calcule el factorial de cada número entre 1 y 6 usando Pool.map().
#Pista: usá la función math.factorial.

from multiprocessing import Pool
import math

def calcular_factorial(n):
    print(f"Calculando factorial de {n}...")
    return math.factorial(n)

if __name__ == '__main__':
    numeros = [1, 2, 3, 4, 5, 6]

    with Pool(processes=3) as pool:
        resultados = pool.map(calcular_factorial, numeros)

    print("Resultados:", resultados)
