# procesos concurrentes con multiprocessing

import multiprocessing
import time
from datetime import datetime

def write_log(lock, log_file, process_id):
    """Función que escribe en el archivo de log."""
    with lock:  # Adquirir el bloqueo
        with open(log_file, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Proceso {process_id} - PID: {multiprocessing.current_process().pid} - Timestamp: {timestamp}\n")
        time.sleep(1)  # Simular trabajo

def main():
    log_file = "procesos.log"
    lock = multiprocessing.Lock()  # Crear el bloqueo
    processes = []

    # Crear 4 procesos
    for i in range(4):
        process = multiprocessing.Process(target=write_log, args=(lock, log_file, i + 1))
        processes.append(process)
        process.start()

    # Esperar a que todos los procesos terminen
    for process in processes:
        process.join()

    print("Todos los procesos han terminado. Revisa el archivo de log.")

if __name__ == "__main__":
    main()