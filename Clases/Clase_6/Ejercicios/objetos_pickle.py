import os
import time
import pickle
import multiprocessing

# Rutas de los FIFOs
fifo_emisor_path = "/tmp/chat_fifo_emisor"
fifo_receptor_path = "/tmp/chat_fifo_receptor"

# Crear los FIFOs si no existen
if not os.path.exists(fifo_emisor_path):
    os.mkfifo(fifo_emisor_path)

if not os.path.exists(fifo_receptor_path):
    os.mkfifo(fifo_receptor_path)

class Mensaje:
    def __init__(self, emisor, contenido):
        self.emisor = emisor
        self.contenido = contenido
        self.timestamp = time.time()

    def __repr__(self):
        return f"Mensaje({self.emisor}, {self.contenido}, {self.timestamp})"

def emisor(id):
    """Función del emisor que usa Pickle para enviar un objeto"""
    with open(fifo_emisor_path, "w") as fifo_emisor:
        for i in range(5):
            mensaje = Mensaje(id, f"Mensaje {i}")
            mensaje_pickled = pickle.dumps(mensaje)  # Convertir a Pickle
            print(f"Emisor {id}: Enviando mensaje Pickle: {mensaje}")
            fifo_emisor.write(mensaje_pickled + b"\n")  # Escribir como bytes
            fifo_emisor.flush()
            time.sleep(1)

def receptor(id):
    """Función del receptor que lee desde el FIFO y deserializa el mensaje Pickle"""
    with open(fifo_receptor_path, "r") as fifo_receptor:
        while True:
            mensaje_pickled = fifo_receptor.readline().strip()
            if mensaje_pickled:
                mensaje = pickle.loads(mensaje_pickled)  # Convertir de Pickle a objeto
                print(f"Receptor {id} recibió: {mensaje}")
            if mensaje_pickled.lower() == "salir":
                print(f"Receptor {id} cerró el canal.")
                break

def iniciar_comunicacion():
    """Inicia la comunicación entre múltiples emisores y receptores usando Pickle"""
    emisores = [multiprocessing.Process(target=emisor, args=(i,)) for i in range(1, 4)]
    receptores = [multiprocessing.Process(target=receptor, args=(i,)) for i in range(1, 4)]

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
