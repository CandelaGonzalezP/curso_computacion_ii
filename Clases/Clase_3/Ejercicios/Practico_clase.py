#EJERCICIO CLASES

import os
import time

pid1 = os.fork()  # Crear el primer hijo

if pid1 == 0:  # Código del primer hijo
    time.sleep(2)
    print(f"Soy el uno, mi PID es {os.getpid()}")
    os._exit(0)  # Terminar el proceso hijo

pid2 = os.fork()  # Crear el segundo hijo

if pid2 == 0:  # Código del segundo hijo
    time.sleep(3)
    print(f"Soy el dos, mi PID es {os.getpid()}")
    os._exit(0)  # Terminar el proceso hijo

# Código del padre (no espera a los hijos)
print(f"Soy el padre, termino, mi PID es {os.getpid()}")

"""
import os
import time

def create_child(wait_time, message):
    pid = os.fork()
    if pid == 0:  # Código del hijo
        time.sleep(wait_time)
        print(f"{message}, mi PID es {os.getpid()}, el PID de mi padre es {os.getppid()}")
        os._exit(0)

if __name__ == "__main__":
    create_child(2, "Soy el hijo 1")
    create_child(3, "Soy el hijo 2")

    # time.sleep(2)
    print(f"Soy el padre, mi PID es {os.getpid()}")
"""

#EJERCICIO 2

def create_child(level):
    if level > 0:
        pid = os.fork()
        if pid == 0:  # Código del hijo
            print(f"Soy el proceso en nivel {level}, mi PID es {os.getpid()}, mi padre es {os.getppid()}")
            time.sleep(1)  # Simula trabajo del proceso
            create_child(level - 1)  # Crea el siguiente hijo en cascada
            os._exit(0)  # Termina el hijo
        else:
            os.waitpid(pid, 0)  # El padre espera a su hijo
            print(f"Soy el padre en nivel {level}, mi PID es {os.getpid()}, terminé de esperar a mi hijo {pid}")

if __name__ == "__main__":
    print(f"Soy el proceso raíz, mi PID es {os.getpid()}")
    create_child(5)  # Inicia la cascada con 5 procesos

"""
import os
import time

def create_child(child_number):
    child_number += 1 
    pid = os.fork()
    
    if pid == 0:  
        print(f"Soy el hijo {child_number}, mi PID es {os.getpid()}, el PID de mi padre es: {os.getppid()}")
        if child_number < 5:
            create_child(child_number)
        os._exit(0)

if __name__ == "__main__":
    os.system('clear')
    create_child(0)
    print(f"Soy el padre, mi PID es {os.getpid()}")
"""
