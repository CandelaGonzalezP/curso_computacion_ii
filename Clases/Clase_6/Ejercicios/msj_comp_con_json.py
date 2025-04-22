import os
import time
import json
import multiprocessing

# Rutas de los FIFOs
fifo_emisor_path = "/tmp/chat_fifo_emisor"
fifo_receptor_path = "/tmp/chat_fifo_receptor"

# Crear los FIFOs si no existen
if not os.path.exists(fifo_emisor_path):
    os.mkfifo(fifo_emisor_path)
    print(f"FIFO {fifo_emisor_path} creado.")

if not os.path.exists(fifo_receptor_path):
    os.mkfifo(fifo_receptor_path)
    print(f"FIFO {fifo_receptor_path} creado.")

def emisor(id):
    """Función del emisor que escribe un mensaje complejo (JSON) en el FIFO"""
    with open(fifo_emisor_path, "w") as fifo_emisor:
        for i in range(5):
            mensaje = {"emisor": id, "mensaje": f"Mensaje {i}", "timestamp": time.time()}
            mensaje_json = json.dumps(mensaje)  # Convertir a JSON
            print(f"Emisor {id}: Enviando mensaje JSON: {mensaje_json}")
            fifo_emisor.write(mensaje_json + "\n")
            fifo_emisor.flush()
            time.sleep(1)

def receptor(id):
    """Función del receptor que lee desde el FIFO y deserializa el mensaje JSON"""
    with open(fifo_receptor_path, "r") as fifo_receptor:
        while True:
            mensaje_json = fifo_receptor.readline().strip()
            if mensaje_json:
                try:
                    mensaje = json.loads(mensaje_json)  # Convertir de JSON a diccionario
                    print(f"Receptor {id} recibió: {mensaje}")
                except json.JSONDecodeError:
                    print(f"Receptor {id} error al decodificar mensaje.")
            time.sleep(0.1)

def iniciar_comunicacion():
    """Inicia la comunicación entre múltiples emisores y receptores"""
    emisores = [multiprocessing.Process(target=emisor, args=(i,)) for i in range(1, 3)]
    receptores = [multiprocessing.Process(target=receptor, args=(i,)) for i in range(1, 3)]

    # Iniciar los procesos
    for e in emisores:
        e.start()

    for r in receptores:
        r.start()

    # Esperar a que todos los procesos terminen
    for e in emisores:
        e.join()

    for r in receptores:
        r.join()

if __name__ == "__main__":
    iniciar_comunicacion()
