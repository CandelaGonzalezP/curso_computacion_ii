# fifo entre 2 scripts

import os

fifo_path = "/tmp/mi_fifo"

# Abrir el FIFO en modo escritura
with open(fifo_path, "w") as fifo:
    while True:
        message = input("Escribe un mensaje para enviar: ")
        fifo.write(message + "\n")  # Escribir el mensaje en el FIFO
        fifo.flush()  # Asegurar que el mensaje se envíe inmediatamente