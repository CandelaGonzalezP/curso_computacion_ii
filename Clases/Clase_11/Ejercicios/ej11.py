# manejo de señales

import os
import signal
import time

def manejador_sigusr1(signum, frame):
    """Manejador para la señal SIGUSR1."""
    print(f"Señal SIGUSR1 recibida en el proceso con PID {os.getpid()}.")

def main():
    # Instalar el manejador para SIGUSR1
    signal.signal(signal.SIGUSR1, manejador_sigusr1)

    print(f"Proceso en espera. PID: {os.getpid()}")
    print("Envía la señal con: kill -SIGUSR1 [pid]")

    # Mantener el proceso en espera pasiva
    try:
        while True:
            signal.pause()  # Esperar señales
    except KeyboardInterrupt:
        print("\nProceso terminado por el usuario.")

if __name__ == "__main__":
    main()