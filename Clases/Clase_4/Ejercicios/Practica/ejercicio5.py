# EJERCICIO 5 - CHAT BIDIRECCIONAL

import os
import sys
import select

def chat_bidireccional():
    padre_a_hijo_r, padre_a_hijo_w = os.pipe()
    hijo_a_padre_r, hijo_a_padre_w = os.pipe()

    pid = os.fork()

    if pid == 0:
        # === Proceso Hijo ===
        os.close(padre_a_hijo_w)
        os.close(hijo_a_padre_r)

        leer = os.fdopen(padre_a_hijo_r, 'r')
        escribir = os.fdopen(hijo_a_padre_w, 'w')

        print("👶 Hijo iniciado. Escribí algo para responder al padre.")
        while True:
            inputs = select.select([leer], [], [], 0.1)[0]
            if leer in inputs:
                mensaje = leer.readline().strip()
                if mensaje == "salir":
                    print("👶 El padre cerró el chat.")
                    break
                print(f"👶 Padre dijo: {mensaje}")
            
            mensaje_hijo = input("👶 Tú: ")
            escribir.write(mensaje_hijo + '\n')
            escribir.flush()
            if mensaje_hijo == "salir":
                break

        leer.close()
        escribir.close()
        sys.exit(0)

    else:
        # === Proceso Padre ===
        os.close(padre_a_hijo_r)
        os.close(hijo_a_padre_w)

        escribir = os.fdopen(padre_a_hijo_w, 'w')
        leer = os.fdopen(hijo_a_padre_r, 'r')

        print("👨 Padre iniciado. Escribí algo para hablar con el hijo.")
        while True:
            inputs = select.select([leer], [], [], 0.1)[0]
            if leer in inputs:
                mensaje = leer.readline().strip()
                if mensaje == "salir":
                    print("👨 El hijo cerró el chat.")
                    break
                print(f"👨 Hijo dijo: {mensaje}")

            mensaje_padre = input("👨 Tú: ")
            escribir.write(mensaje_padre + '\n')
            escribir.flush()
            if mensaje_padre == "salir":
                break

        escribir.close()
        leer.close()
        os.waitpid(pid, 0)

if __name__ == "__main__":
    chat_bidireccional()
