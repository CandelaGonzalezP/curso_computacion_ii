# Ejercicio 6: Señales + FIFO
import os
import signal
import time

FIFO_PATH = "/tmp/mi_fifo"

def hijo_fifo():
    def handler(signum, frame):
        print("[Hijo] Señal recibida, leyendo FIFO...")
        with open(FIFO_PATH, 'r') as fifo:
            mensaje = fifo.read()
            print(f"[Hijo] Mensaje desde FIFO: {mensaje}")

    signal.signal(signal.SIGUSR1, handler)
    print(f"[Hijo] Esperando señal SIGUSR1...")
    signal.pause()

def padre_fifo(pid_hijo):
    if not os.path.exists(FIFO_PATH):
        os.mkfifo(FIFO_PATH)
    time.sleep(1)
    print("[Padre] Escribiendo en FIFO...")
    with open(FIFO_PATH, 'w') as fifo:
        fifo.write("Hola desde el padre!")
    print("[Padre] Enviando señal al hijo...")
    os.kill(pid_hijo, signal.SIGUSR1)

pid = os.fork()
if pid == 0:
    hijo_fifo()
else:
    padre_fifo(pid)