# EJERCICIO 6 - SERVIDOR DE OPERACIONES MATEMATICAS

import os
import sys

def main():
    c_to_s_r, c_to_s_w = os.pipe()
    s_to_c_r, s_to_c_w = os.pipe()

    pid = os.fork()

    if pid == 0:
        # ======= PROCESO HIJO: SERVIDOR =======
        os.close(c_to_s_w) 
        os.close(s_to_c_r)  

        c_reader = os.fdopen(c_to_s_r, 'r')
        s_writer = os.fdopen(s_to_c_w, 'w')

        print("Servidor: Esperando operaciones del cliente...")

        for operacion in c_reader:
            operacion = operacion.strip()
            if not operacion:
                continue

            print(f"Servidor: Recibido '{operacion}'")
            try:
                resultado = eval(operacion, {"__builtins__": {}})
                respuesta = f"Resultado: {resultado}"
            except Exception as e:
                respuesta = f"Error: operación inválida ({str(e)})"

            s_writer.write(respuesta + "\n")
            s_writer.flush()

        c_reader.close()
        s_writer.close()
        sys.exit(0)

    else:
        # ======= PROCESO PADRE: CLIENTE =======
        os.close(c_to_s_r)  
        os.close(s_to_c_w)  

        c_writer = os.fdopen(c_to_s_w, 'w')
        s_reader = os.fdopen(s_to_c_r, 'r')

        print("\nCliente: Enviando operaciones...\n")
        while True:
            operacion = input("Cliente (escribe operación o 'salir'): ")
            if operacion.strip().lower() == 'salir':
                break

            c_writer.write(operacion + "\n")
            c_writer.flush()

            respuesta = s_reader.readline()
            print(f"Servidor responde → {respuesta.strip()}")

        c_writer.close()
        s_reader.close()
        os.waitpid(pid, 0)

if __name__ == "__main__":
    main()


