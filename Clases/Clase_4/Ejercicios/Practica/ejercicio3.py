# EJERCICIO 3 - PIPELINES DE FILTRADO

import os
import sys
import random

def generar_numeros(cantidad, salida):
    salida = os.fdopen(salida, 'w')
    for _ in range(cantidad):
        numero = random.randint(1, 100)
        print(f"Generado: {numero}")
        salida.write(f"{numero}\n")
        salida.flush()
    salida.close()

def filtrar_pares(entrada, salida):
    entrada = os.fdopen(entrada, 'r')
    salida = os.fdopen(salida, 'w')

    for linea in entrada:
        numero = int(linea.strip())
        if numero % 2 == 0:
            print(f"Filtrado par: {numero}")
            salida.write(f"{numero}\n")
            salida.flush()

    entrada.close()
    salida.close()

def calcular_cuadrado(entrada):
    entrada = os.fdopen(entrada, 'r')

    print("\nCuadrados de los números pares:")
    for linea in entrada:
        numero = int(linea.strip())
        cuadrado = numero ** 2
        print(f"{numero}^2 = {cuadrado}")

    entrada.close()

def main():
    gen_to_filtro_r, gen_to_filtro_w = os.pipe()
    filtro_to_cuadrado_r, filtro_to_cuadrado_w = os.pipe()

    pid1 = os.fork()
    if pid1 == 0: #primer hijo proceso
        pid2 = os.fork()
        if pid2 == 0:  #segundo hijo proceso
            os.close(gen_to_filtro_r)
            os.close(gen_to_filtro_w)
            os.close(filtro_to_cuadrado_w)
            calcular_cuadrado(filtro_to_cuadrado_r)
            sys.exit(0)
        else:
            os.close(gen_to_filtro_w)
            os.close(filtro_to_cuadrado_r)
            filtrar_pares(gen_to_filtro_r, filtro_to_cuadrado_w)
            os.waitpid(pid2, 0)
            sys.exit(0)
    else:
        # Proceso padre: genera números
        os.close(gen_to_filtro_r)
        os.close(filtro_to_cuadrado_r)
        os.close(filtro_to_cuadrado_w)
        generar_numeros(10, gen_to_filtro_w)
        os.waitpid(pid1, 0)

if __name__ == "__main__":
    main()
