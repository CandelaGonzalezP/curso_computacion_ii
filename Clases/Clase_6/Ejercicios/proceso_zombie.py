import os
import time
import multiprocessing

# Función del proceso hijo
def proceso_hijo():
    print(f"Proceso hijo (PID: {os.getpid()}) iniciado.")
    time.sleep(3)
    print(f"Proceso hijo (PID: {os.getpid()}) terminado.")
    
# Función del proceso padre
def proceso_padre():
    print(f"Proceso padre (PID: {os.getpid()}) iniciado.")
    p_hijo = multiprocessing.Process(target=proceso_hijo)
    p_hijo.start()
    p_hijo.join()  # El proceso padre espera que el hijo termine
    print(f"Proceso padre (PID: {os.getpid()}) ha terminado.")

if __name__ == "__main__":
    proceso_padre()
