from multiprocessing import Process
import os

def funcion():
    print(f"Hola desde el proceso hijo. PID: {os.getpid()}")

if __name__ == '__main__':
    print(f"Hola desde el proceso padre. PID: {os.getpid()}")
    p = Process(target=funcion)
    p.start()
    p.join()
    print("El proceso hijo ha terminado.")
