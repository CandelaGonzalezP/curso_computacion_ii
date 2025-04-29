# Ejercicio 2: Esperar una señal personalizada SIGUSR1
import signal
import os
import time

def manejador_usr1(signum, frame):
    print(f"[PID {os.getpid()}] Señal SIGUSR1 recibida.")

signal.signal(signal.SIGUSR1, manejador_usr1)
print(f"[PID {os.getpid()}] Esperando SIGUSR1...")
signal.pause()