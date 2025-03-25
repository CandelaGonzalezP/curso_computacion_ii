
#EJERCICIO 1-  Crear un proceso con fork()
import os

pid = os.fork()

if pid == 0:
    print(f"Soy el hijo, mi PID es {os.getpid()}, mi padre es {os.getppid()}")
else:
    print(f"Soy el padre, mi PID es {os.getpid()}, mi hijo es {pid}")



#EJERCICIO 2- Crear un proceso hijo que ejecute otro programa con exec()
pid = os.fork()

if pid == 0:
    print("Soy el hijo, ahora voy a ejecutar 'ls'")
    os.execvp("ls", ["ls", "-l"])  # Esto reemplaza el código del proceso hijo
else:
    print("Soy el padre, esperando que el hijo termine.")
    os.wait()  # El padre espera a que el hijo termine


#EJERCICIO 3- Simular un proceso zombi
import time

pid = os.fork()

if pid == 0:
    print("Soy el hijo, terminando mi ejecución...")
    time.sleep(5)  # Simula trabajo
    print("El hijo ha terminado.")
else:
    print("Soy el padre, no voy a esperar al hijo.")
    time.sleep(10)  # El padre no llama a wait(), el hijo se convierte en zombi
    print("El padre ha terminado.")


#EJERCICIO 4-  Simular un proceso huérfano
pid = os.fork()

if pid == 0:
    print("Soy el hijo, esperemos que el padre termine...")
    time.sleep(10)  # Simula trabajo
    print("El hijo ha terminado.")
else:
    print("Soy el padre, voy a terminar primero.")
    time.sleep(2)  # El padre termina antes que el hijo
    print("El padre ha terminado.")
