# EJERCICIO 2 - CONTADOR DE PALABRAS

import os
import sys

def main():
    lectura_pipe_r, lectura_pipe_w = os.pipe()  # Para enviar líneas del archivo al hijo
    respuesta_pipe_r, respuesta_pipe_w = os.pipe()  # Para devolver conteos al padre

    pid = os.fork()

    if pid > 0:  # Proceso padre
        os.close(lectura_pipe_r)
        os.close(respuesta_pipe_w)

        archivo = "ejemplo_texto.txt"

        try:
            # Creo el archivo con líneas distintas
            if not os.path.exists(archivo):
                with open(archivo, 'w') as f:
                    f.write("Python facilita la programación.\n")
                    f.write("Los procesos pueden comunicarse con pipes.\n")
                    f.write("Este ejemplo ilustra eso claramente.\n")
                    f.write("Cada línea será contada por el hijo.\n")

            with open(archivo, 'r') as f:
                print(f"Padre: Procesando el archivo '{archivo}'")

                writer = os.fdopen(lectura_pipe_w, 'w')
                num_lineas = 0

                for linea in f:
                    writer.write(linea)
                    writer.flush()
                    num_lineas += 1

                print(f"Padre: Enviadas {num_lineas} líneas al proceso hijo.")
                writer.close()

                reader = os.fdopen(respuesta_pipe_r, 'r')

                print("\nResultado del conteo por línea:")
                total = 0
                for idx, count in enumerate(reader, 1):
                    cantidad = int(count.strip())
                    total += cantidad
                    print(f"Fila {idx}: {cantidad} palabras")

                print(f"\nConteo total de palabras: {total}")
                reader.close()

        except Exception as e:
            print(f"[Padre] Se produjo un error: {e}")
            os.close(lectura_pipe_w)
            os.close(respuesta_pipe_r)

        os.waitpid(pid, 0)

    else:  # Proceso hijo
        try:
            os.close(lectura_pipe_w)
            os.close(respuesta_pipe_r)

            reader = os.fdopen(lectura_pipe_r, 'r')
            writer = os.fdopen(respuesta_pipe_w, 'w')

            print("Hijo: Iniciando conteo de palabras...")

            for linea in reader:
                cantidad = len(linea.split())
                writer.write(f"{cantidad}\n")
                writer.flush()

            reader.close()
            writer.close()

        except Exception as e:
            print(f"[Hijo] Se produjo un error: {e}")
            os.close(lectura_pipe_r)
            os.close(respuesta_pipe_w)

        sys.exit(0)

if __name__ == "__main__":
    main()


