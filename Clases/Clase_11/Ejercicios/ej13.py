# jerarquia de procesos

import os
import time

def main():
    print(f"Proceso principal (PID: {os.getpid()})")

    # Crear el primer proceso hijo
    pid1 = os.fork()
    if pid1 == 0:
        # Código del primer hijo
        print(f"Primer proceso hijo creado (PID: {os.getpid()}, Padre: {os.getppid()})")
        time.sleep(30)  # Mantener el proceso activo
        exit(0)

    # Crear el segundo proceso hijo
    pid2 = os.fork()
    if pid2 == 0:
        # Código del segundo hijo
        print(f"Segundo proceso hijo creado (PID: {os.getpid()}, Padre: {os.getppid()})")
        time.sleep(30)  # Mantener el proceso activo
        exit(0)

    # Proceso principal espera
    time.sleep(30)
    print("Proceso principal terminado.")

if __name__ == "__main__":
    main()