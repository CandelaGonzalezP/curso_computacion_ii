import argparse

def main():
    parser = argparse.ArgumentParser(description="Script para procesar archivos de entrada y salida")
    
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada")
    parser.add_argument("-o", "--output", required=True, help="Archivo de salida")

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    print(f"Archivo de entrada: {input_file}")
    print(f"Archivo de salida: {output_file}")

if __name__ == "__main__":
    main()
