import os
import signal
import time

# Variable global segura
terminar = False

def handler(signum, frame):
    global terminar
    terminar = True

signal.signal(signal.SIGINT, handler)

print("Presioná Ctrl+C para salir.")
while not terminar:
    print(".", end="", flush=True)
    time.sleep(1)

print("\nFin seguro del programa.")


#Aquí el handler solo cambia un flag. El trabajo pesado se hace fuera del handler.