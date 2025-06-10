import signal
import os

def manejar_sigusr1(signum, frame):
    print(f"Proceso {os.getpid()} recibió SIGUSR1: Acción 1 ejecutada.")

def manejar_sigusr2(signum, frame):
    print(f"Proceso {os.getpid()} recibió SIGUSR2: Acción 2 ejecutada.")

if __name__ == "__main__":
    print(f"PID del receptor: {os.getpid()}")
    signal.signal(signal.SIGUSR1, manejar_sigusr1)
    signal.signal(signal.SIGUSR2, manejar_sigusr2)
    print("Esperando señales...")
    signal.pause()  # Espera indefinida