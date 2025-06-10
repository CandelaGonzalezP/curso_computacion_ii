# ejecicion encadenada con argparse y pipes

import argparse
import random

def main():
    # Configurar argparse
    parser = argparse.ArgumentParser(description="Genera números aleatorios.")
    parser.add_argument("--n", type=int, required=True, help="Cantidad de números aleatorios a generar.")
    args = parser.parse_args()

    # Generar números aleatorios
    for _ in range(args.n):
        print(random.randint(0, 100))  # Genera números entre 0 y 100

if __name__ == "__main__":
    main()