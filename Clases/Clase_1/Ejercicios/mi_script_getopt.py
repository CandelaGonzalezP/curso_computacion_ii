import sys
import getopt

def main(argv):
    input_file = ""
    output_file = ""

    try:
        opts, args = getopt.getopt(argv, "i:o:", ["input=", "output="])
    except getopt.GetoptError:
        print("Uso: script.py -i <archivo_entrada> -o <archivo_salida>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg

    print(f"Archivo de entrada: {input_file}")
    print(f"Archivo de salida: {output_file}")

if __name__ == "__main__":
    main(sys.argv[1:])