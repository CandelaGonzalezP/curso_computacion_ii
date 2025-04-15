# Ejemplo 3: Proceso que genera datos y otro que los guarda

import os
import time

def generador(write_fd):
    for i in range(3):
        nombre = f"Archivo_{i}.txt"
        os.write(write_fd, (nombre + '\n').encode())
        time.sleep(0.2)
    os.write(write_fd, b'Fin\n')
    os.close(write_fd)  # Cerrar escritura

def guardador(read_fd):
    while True:
        buffer = os.read(read_fd, 1024).decode()
        for linea in buffer.strip().split('\n'):
            if linea == 'Fin':
                print("[Guardador] Finalizando proceso.")
                os.close(read_fd)
                return
            print(f"[Guardador] Guardando {linea} en disco...")

if __name__ == '__main__':
    read_fd, write_fd = os.pipe()
    pid = os.fork()

    if pid == 0:
        # Proceso hijo → Generador de nombres
        os.close(read_fd)
        generador(write_fd)
        os._exit(0)
    else:
        # Proceso padre → Guardador
        os.close(write_fd)
        guardador(read_fd)
        os.wait()
