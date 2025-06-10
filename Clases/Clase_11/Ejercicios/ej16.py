# recoleccion de estados de hijos


import os
import time

def main():
    # Lista para almacenar los PIDs de los hijos
    child_pids = []
    # Lista para registrar el orden de finalización
    termination_order = []

    # Crear 3 procesos hijos
    for i in range(3):
        pid = os.fork()
        if pid == 0:
            # Código del hijo
            print(f"Hijo {i + 1} iniciado con PID {os.getpid()}")
            time.sleep(3 - i)  # Simular que cada hijo termina en distinto orden
            print(f"Hijo {i + 1} con PID {os.getpid()} finalizando")
            os._exit(0)  # Finalizar el proceso hijo
        else:
            # Código del padre
            child_pids.append(pid)

    # El padre espera a que los hijos terminen
    for _ in range(3):
        pid, status = os.waitpid(-1, 0)  # Recolectar el estado de un hijo
        termination_order.append(pid)
        print(f"Padre: hijo con PID {pid} terminó con estado {status}")

    # Imprimir el orden de finalización
    print("\nOrden de finalización de los hijos:")
    for i, pid in enumerate(termination_order, start=1):
        print(f"{i}. PID {pid}")

if __name__ == "__main__":
    main()