# Ejercicio 1: Manejador de SIGINT (Ctrl+C)
import signal
import time

def manejador_sigint(signum, frame):
    print("\n[INFO] Señal SIGINT recibida. Interrupción ignorada.")

signal.signal(signal.SIGINT, manejador_sigint)

print("Presioná Ctrl+C para probar. Ejecutando...")
while True:
    time.sleep(1)
