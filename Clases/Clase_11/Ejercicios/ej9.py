# semaphore

import multiprocessing
import time

def zona_critica(semaforo, proceso_id):
    """Función que simula el acceso a una zona crítica."""
    print(f"Proceso {proceso_id} intentando acceder a la zona crítica...")
    with semaforo:  # Adquirir el semáforo
        print(f"Proceso {proceso_id} accedió a la zona crítica.")
        time.sleep(2)  # Simular trabajo en la zona crítica
        print(f"Proceso {proceso_id} salió de la zona crítica.")

def main():
    semaforo = multiprocessing.Semaphore(3)  # Permitir hasta 3 accesos simultáneos
    procesos = []

    # Crear 10 procesos
    for i in range(10):
        proceso = multiprocessing.Process(target=zona_critica, args=(semaforo, i + 1))
        procesos.append(proceso)
        proceso.start()

    # Esperar a que todos los procesos terminen
    for proceso in procesos:
        proceso.join()

    print("Todos los procesos han terminado.")

if __name__ == "__main__":
    main()