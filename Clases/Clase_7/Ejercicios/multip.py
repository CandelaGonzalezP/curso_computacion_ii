# Ejercicio 5: multiprocessing + señales (limitado en Python)
import multiprocessing
import signal
import os
import time

def manejador(signum, frame):
    print(f"[Hijo] Señal recibida: {signum}")

def proceso_hijo():
    signal.signal(signal.SIGUSR1, manejador)
    print(f"[Hijo] Esperando señal en PID {os.getpid()}...")
    signal.pause()

def proceso_padre(pid):
    time.sleep(1)
    print(f"[Padre] Enviando SIGUSR1 a PID {pid}")
    os.kill(pid, signal.SIGUSR1)

if __name__ == '__main__':
    hijo = multiprocessing.Process(target=proceso_hijo)
    hijo.start()
    proceso_padre(hijo.pid)
    hijo.join()