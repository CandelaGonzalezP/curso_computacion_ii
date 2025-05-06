#Modificá el siguiente código para lanzar 3 procesos que saluden con diferentes nombres:

from multiprocessing import Process

def saludar(nombre):
    print(f"Hola {nombre}")

if __name__ == '__main__':
    # Crear los procesos
    p1 = Process(target=saludar, args=("Candela",))
    p2 = Process(target=saludar, args=("Juan",))
    p3 = Process(target=saludar, args=("Lucía",))

    # Iniciar los procesos
    p1.start()
    p2.start()
    p3.start()
    
    # Esperar que terminen
    p1.join()
    p2.join()
    p3.join()

    print("Todos los saludos han terminado.")
