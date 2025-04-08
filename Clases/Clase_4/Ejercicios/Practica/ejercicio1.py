#EJERCICIO1 - ECO SIMPLE

import os

def eco_simple():
    padre_a_hijo_r, padre_a_hijo_w = os.pipe()
    hijo_a_padre_r, hijo_a_padre_w = os.pipe()

    pid = os.fork()

    if pid == 0:
        # Proceso hijo
        os.close(padre_a_hijo_w)  
        os.close(hijo_a_padre_r)  
        mensaje = os.read(padre_a_hijo_r, 1024).decode()
        print(f"[Hijo] Recibido del padre: {mensaje}")

        # Responder (eco)
        respuesta = f"Eco: {mensaje}"
        os.write(hijo_a_padre_w, respuesta.encode())

        os.close(padre_a_hijo_r)
        os.close(hijo_a_padre_w)

    else:
        # Proceso padre
        os.close(padre_a_hijo_r)  
        os.close(hijo_a_padre_w)  

        mensaje = "Hola hijo, ¿me escuchás?"
        os.write(padre_a_hijo_w, mensaje.encode())
        print(f"[Padre] Enviado al hijo: {mensaje}")

        # Leer eco del hijo
        respuesta = os.read(hijo_a_padre_r, 1024).decode()
        print(f"[Padre] Recibido del hijo: {respuesta}")

        os.close(padre_a_hijo_w)
        os.close(hijo_a_padre_r)

if __name__ == "__main__":
    eco_simple()
