import os
import time
import select

# Rutas de los FIFOs
fifo_emisor_path = "/tmp/chat_fifo_emisor"
fifo_receptor_path = "/tmp/chat_fifo_receptor"

# Crear los FIFOs si no existen
if not os.path.exists(fifo_emisor_path):
    os.mkfifo(fifo_emisor_path)

if not os.path.exists(fifo_receptor_path):
    os.mkfifo(fifo_receptor_path)

# Iniciar el chat
print("Canal de chat iniciado. Escribe 'salir' para terminar.")
with open(fifo_emisor_path, "w") as fifo_emisor, open(fifo_receptor_path, "r") as fifo_receptor:
    while True:
        # Verificamos si el receptor tiene algo para leer
        readable, _, _ = select.select([fifo_receptor], [], [], 0.1)  # Timeout de 0.1 segundos
        if readable:
            respuesta = fifo_receptor.readline().strip()
            if respuesta.lower() == "salir":
                print("El receptor cerró el canal de chat.")
                break
            elif respuesta:
                print(f"Receptor: {respuesta}")

        # Enviar mensaje
        mensaje = input("Tú: ")
        if mensaje.lower() == "salir":
            fifo_emisor.write("salir\n")
            fifo_emisor.flush()
            print("Cerrando canal de chat.")
            break
        fifo_emisor.write(mensaje + "\n")
        fifo_emisor.flush()
