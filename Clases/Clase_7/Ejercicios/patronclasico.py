import os
import signal
import time

def handler(signum, frame):
    print("✅ Señal recibida del hijo. Continuando ejecución...")

# Registrar handler
signal.signal(signal.SIGUSR1, handler)

pid = os.fork()

if pid == 0:
    # Proceso hijo
    print(f"Hijo ({os.getpid()}): ejecutando tarea...")
    time.sleep(2)
    print("Hijo: enviando señal al padre...")
    os.kill(os.getppid(), signal.SIGUSR1)
    os._exit(0)
else:
    # Proceso padre
    print(f"Padre ({os.getpid()}): esperando señal...")
    signal.pause()  # Espera hasta recibir una señal
    print("Padre: fin del programa.")
