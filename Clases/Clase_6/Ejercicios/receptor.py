import os

fifo_path = "/tmp/log_fifo"

# Crear FIFO si no existe
if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)

# Abrimos el FIFO para leer los eventos
with open(fifo_path, "r") as fifo, open("log.txt", "a") as log_file:
    while True:
        evento = fifo.readline()
        if evento:
            print(f"Recibido: {evento.strip()}")
            log_file.write(evento)
        else:
            break  # Si no hay más eventos, salimos del bucle

