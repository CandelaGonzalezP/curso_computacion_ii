import os

fifo_path = "/tmp/chat_fifo"

print("Esperando mensaje...")
with open(fifo_path, "r") as fifo:
    mensaje = fifo.read()
    print(f"Mensaje recibido: {mensaje}")
