from multiprocessing import Process
import time

def saludar(nombre):
    print(f"Hola {nombre} desde el proceso hijo.")
    time.sleep(2)
    print(f"Chau {nombre} desde el proceso hijo.")

if __name__ == '__main__':
    p1 = Process(target=saludar, args=("Candela",))
    p2 = Process(target=saludar, args=("Juan",))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    print("Ambos procesos han terminado.")
