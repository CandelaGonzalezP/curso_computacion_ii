# lsof


import os
import time

def proceso_hijo(pipe_escritura):
    os.close(pipe_lectura)  # Cerrar el extremo de lectura en el hijo
    for i in range(5):
        mensaje = f"Mensaje {i} desde el hijo\n"
        os.write(pipe_escritura, mensaje.encode())
        time.sleep(1)
    os.close(pipe_escritura)  # Cerrar el extremo de escritura al terminar

def proceso_padre(pipe_lectura):
    os.close(pipe_escritura)  # Cerrar el extremo de escritura en el padre
    while True:
        mensaje = os.read(pipe_lectura, 1024)
        if not mensaje:
            break
        print(f"Padre recibió: {mensaje.decode()}")
    os.close(pipe_lectura)  # Cerrar el extremo de lectura al terminar

if __name__ == "__main__":
    pipe_lectura, pipe_escritura = os.pipe()  # Crear el pipe

    pid = os.fork()  # Crear un proceso hijo

    if pid == 0:  # Código del hijo
        proceso_hijo(pipe_escritura)
    else:  # Código del padre
        print(f"PID del proceso padre: {os.getpid()}")
        proceso_padre(pipe_lectura)