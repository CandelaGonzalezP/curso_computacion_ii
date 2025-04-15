# Ejemplo 5: Proceso que genera datos y otro que los guarda

import os
import time

def generador(write_fd):
    for i in range(3):
        nombre = f"Archivo_{i}.txt"
        os.write(write_fd, (nombre + '\n').encode())
        time.sleep(0.2)
    os.write(write_fd, b'Fin\n')
    os.close(write_fd)

def guardador(read_fd):
    while True:
        buffer = os.read(read_fd, 1024).decode()
        for linea in buffer.strip().split('\n'):
            if linea == 'Fin':
                print("[Guardador] Finalizando proceso.")
                return
            print(f"[Guardador] Guardando {linea} en disco...")
    os.close(read_fd)

if __name__ == '__main__':
    read_fd, write_fd = os.pipe()
    pid = os.fork()

    if pid == 0:
        os.close(read_fd)
        generador(write_fd)
        os._exit(0)
    else:
        os.close(write_fd)
        guardador(read_fd)
        os.wait()
