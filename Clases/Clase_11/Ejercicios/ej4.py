# reemplazo con exec

import os

# Crear un proceso hijo usando fork()
pid = os.fork()

if pid == 0:
    # Código del proceso hijo
    print(f"Child PID: {os.getpid()} replacing its image with 'ls -l'")
    os.execlp("ls", "ls", "-l")  # Reemplaza la imagen del proceso hijo con el comando 'ls -l'
else:
    # Código del proceso padre
    print(f"Parent PID: {os.getpid()} created child PID: {pid}")