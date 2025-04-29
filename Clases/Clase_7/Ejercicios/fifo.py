# Ejercicio 3: fork() y os.kill()
import os
import signal
import time

def hijo():
    print(f"[Hijo] PID: {os.getpid()} esperando SIGUSR1...")
    signal.signal(signal.SIGUSR1, lambda s, f: print("[Hijo] Señal SIGUSR1 recibida."))
    signal.pause()

def padre(pid_hijo):
    time.sleep(1)
    print(f"[Padre] Enviando SIGUSR1 al hijo PID {pid_hijo}")
    os.kill(pid_hijo, signal.SIGUSR1)

pid = os.fork()
if pid == 0:
    hijo()
else:
    padre(pid)
