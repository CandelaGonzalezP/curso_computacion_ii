import signal
import threading
import time

def handler(signum, frame):
    print(f"[Main] Señal {signum} recibida.")

def background_task():
    print("[Hilo] Trabajando en segundo plano...")
    time.sleep(5)
    print("[Hilo] Listo.")

# Solo el hilo principal puede registrar handlers
signal.signal(signal.SIGUSR1, handler)

# Iniciamos un hilo de fondo
t = threading.Thread(target=background_task)
t.start()

# Esperar señal (desde otro terminal: kill -SIGUSR1 <PID>)
print("[Main] Esperando señal...")
signal.pause()

t.join()
print("Programa finalizado.")
