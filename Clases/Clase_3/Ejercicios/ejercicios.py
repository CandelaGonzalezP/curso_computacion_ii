#Ejercicio 1: Identificación de procesos padre e hijo
import os
import time

def main():
    pid = os.fork()
    if pid == 0:
        # Proceso hijo
        print(f"[Hijo] PID: {os.getpid()} | PPID (padre): {os.getppid()}")
    else:
        # Proceso padre
        print(f"[Padre] PID: {os.getpid()} | PID del hijo: {pid}")

if __name__ == "__main__":
    main()


#Ejercicio 2: Doble bifurcación (dos hijos)
for i in range(2):
    pid = os.fork()
    if pid == 0:
        print(f"[Hijo {i+1}] PID: {os.getpid()}")
        os._exit(0)
for _ in range(2):
    os.wait()
print("[Padre] Hijos finalizados.")


#Ejercicio 3: Reemplazo con exec()
pid = os.fork()
if pid == 0:
    os.execlp("ls", "ls", "-l")
else:
    os.wait()
    print("[Padre] El hijo terminó.")


#Ejercicio 4: Secuencia controlada de procesos
pid1 = os.fork()
if pid1 == 0:
    print("[Hijo 1] Ejecutando tarea...")
    time.sleep(1)
    print("[Hijo 1] Terminando.")
    os._exit(0)
os.wait()
pid2 = os.fork()
if pid2 == 0:
    print("[Hijo 2] Ejecutando tarea...")
    time.sleep(1)
    print("[Hijo 2] Terminando.")
    os._exit(0)
os.wait()
print("[Padre] Ambos hijos han terminado.")


#Ejercicio 5: Proceso zombi temporal
pid = os.fork()
if pid == 0:
    print(f"[Hijo] PID: {os.getpid()} finalizando de inmediato.")
    os._exit(0)
print(f"[Padre] PID: {os.getpid()} — esperando 10 segundos sin hacer wait().")
time.sleep(10)
os.wait()
print("[Padre] Estado del hijo recogido.")


#Ejercicio 6: Proceso huérfano adoptado por init/systemd
pid = os.fork()
if pid == 0:
    time.sleep(5)
    print(f"[Hijo] Sigo vivo. PID: {os.getpid()} | Nuevo PPID: {os.getppid()}")
else:
    print(f"[Padre] Terminando. PID: {os.getpid()}")
    os._exit(0)


#Ejercicio 7: Multiproceso paralelo (3 hijos)
for i in range(3):
    if os.fork() == 0:
        print(f"[Hijo {i+1}] PID: {os.getpid()}")
        time.sleep(1)
        os._exit(0)
for _ in range(3):
    os.wait()
print("[Padre] Todos los hijos finalizaron.")


#Ejercicio 8: Simulación de servidor multiproceso
clientes = 5 
for i in range(clientes):
    pid = os.fork()
    if pid == 0:
        print(f"[Hijo {i+1}] Atendiendo al cliente {i+1} (PID: {os.getpid()})")
        time.sleep(2)  
        print(f"[Hijo {i+1}] Cliente {i+1} atendido.")
        os._exit(0)
for _ in range(clientes):
    os.wait()
print("[Servidor] Todos los clientes fueron atendidos.")


#Ejercicio 9: Detección de procesos zombis sin ps
def detectar_zombis():
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f"/proc/{pid}/status") as f:
                    lines = f.readlines()
                    estado = next((l for l in lines if l.startswith("State:")), "")
                    if "Z" in estado:
                        nombre = next((l for l in lines if l.startswith("Name:")), "").split()[1]
                        ppid = next((l for l in lines if l.startswith("PPid:")), "").split()[1]
                        print(f"Zombi detectado → PID: {pid}, PPID: {ppid}, Nombre: {nombre}")
            except IOError:
                continue
detectar_zombis()


#Ejercicio 10: Proceso huérfano que ejecuta comando externo
pid = os.fork()
if pid == 0:
    time.sleep(3) 
    print(f"[Hijo huérfano] PPID: {os.getppid()} ejecutando comando externo...")
    os.system("echo '[*] Acción fuera de control del padre'")
    os._exit(0)
else:
    print(f"[Padre] PID: {os.getpid()} — finalizando.")
    os._exit(0)
