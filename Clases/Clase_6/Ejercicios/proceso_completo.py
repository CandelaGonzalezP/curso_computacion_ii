
import os
import time
import multiprocessing

# Rutas de los FIFOs
fifo_emisor_path = "/tmp/chat_fifo_emisor"
fifo_receptor_path = "/tmp/chat_fifo_receptor"

# Crear los FIFOs si no existen
if not os.path.exists(fifo_emisor_path):
    os.mkfifo(fifo_emisor_path)

if not os.path.exists(fifo_receptor_path):
    os.mkfifo(fifo_receptor_path)

def proceso_hijo():
    """Función que simula el proceso hijo"""
    with open(fifo_emisor_path, "r") as fifo_emisor, open(fifo_receptor_path, "w") as fifo_receptor:
        while True:
            mensaje = fifo_emisor.readline().strip()
            if mensaje.lower() == "salir":
                print("El proceso hijo ha recibido 'salir'.")
                fifo_receptor.write("Proceso hijo terminó\n")
                fifo_receptor.flush()
                break
            print(f"Proceso hijo recibe: {mensaje}")
            fifo_receptor.write("Mensaje recibido por el hijo\n")
            fifo_receptor.flush()

def proceso_padre():
    """Función del proceso principal"""
    with open(fifo_receptor_path, "r") as fifo_receptor, open(fifo_emisor_path, "w") as fifo_emisor:
        while True:
            mensaje = input("Padre: Escribe un mensaje (escribe 'salir' para salir): ")
            fifo_emisor.write(mensaje + "\n")
            fifo_emisor.flush()

            if mensaje.lower() == "salir":
                print("El proceso principal ha enviado 'salir'.")
                break

            respuesta = fifo_receptor.readline().strip()
            print(f"Respuesta del hijo: {respuesta}")

if __name__ == "__main__":
    # Crear el proceso hijo
    p = multiprocessing.Process(target=proceso_hijo)
    p.start()

    # Ejecutar el proceso principal
    proceso_padre()

    # Esperar a que el proceso hijo termine
    p.join()
