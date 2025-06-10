import argparse
import sys

def main():
    # Configurar argparse
    parser = argparse.ArgumentParser(description="Filtra números mayores a un umbral.")
    parser.add_argument("--min", type=int, required=True, help="Umbral mínimo para filtrar números.")
    args = parser.parse_args()

    # Leer números desde la entrada estándar
    for line in sys.stdin:
        try:
            num = int(line.strip())
            if num > args.min:
                print(num)
        except ValueError:
            pass  # Ignorar líneas que no sean números válidos

if __name__ == "__main__":
    main()