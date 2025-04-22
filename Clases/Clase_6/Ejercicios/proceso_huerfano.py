import os
import time
import multiprocessing

# Función del proceso hijo
def proceso_hijo():
    print(f"Proceso hijo (PID: {os.getpid()}) iniciado.")
    time.sleep(5)
    print(f"Proceso hijo (PID: {os.getpid()}) terminado.")

# Función del proceso padre
def proceso_padre():
    print(f"Proceso padre (PID: {os.getpid()}) iniciado.")
    p_hijo = multiprocessing.Process(target=proceso_hijo)
    p_hijo.start()
    print("El proceso padre ha terminado.")
    time.sleep(2)  # Simula el tiempo para que el hijo se vuelva huérfano
    print(f"Proceso padre (PID: {os.getpid()}) ha terminado.")
    
if __name__ == "__main__":
    proceso_padre()
