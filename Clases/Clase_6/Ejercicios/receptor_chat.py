import os
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
print("Esperando mensajes... (escribe 'salir' para terminar)")
with open(fifo_emisor_path, "r") as fifo_emisor, open(fifo_receptor_path, "w") as fifo_receptor:
    while True:
        # Verificamos si el emisor tiene algo para leer
        readable, _, _ = select.select([fifo_emisor], [], [], 0.1)  # Timeout de 0.1 segundos
        if readable:
            mensaje = fifo_emisor.readline().strip()
            if mensaje.lower() == "salir":
                print("El emisor cerró el canal de chat.")
                break
            elif mensaje:
                print(f"Emisor: {mensaje}")

        # Responder
        respuesta = input("Tú: ")
        if respuesta.lower() == "salir":
            fifo_receptor.write("salir\n")
            fifo_receptor.flush()
            print("Cerrando canal de chat.")
            break
        fifo_receptor.write(respuesta + "\n")
        fifo_receptor.flush()



