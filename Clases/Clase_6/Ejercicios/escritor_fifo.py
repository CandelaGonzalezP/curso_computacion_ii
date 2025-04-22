import os

fifo_path = "/tmp/chat_fifo"

with open(fifo_path, "w") as fifo:
    fifo.write("Hola desde el proceso escritor\n")
    print("Mensaje enviado.")

