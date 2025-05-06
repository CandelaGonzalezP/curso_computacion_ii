#Escribí un programa que:

    #Use un Array compartido con los números del 1 al 10.

    #Cree 2 procesos: uno que eleve al cuadrado los primeros 5 elementos y otro que eleve al cubo los últimos 5.

    #Al final, muestre el contenido final del Array.

from multiprocessing import Process, Array

def elevar_cuadrado(arr):
    for i in range(5):
        arr[i] = arr[i] ** 2

def elevar_cubo(arr):
    for i in range(5, 10):
        arr[i] = arr[i] ** 3

if __name__ == '__main__':
    datos = Array('i', range(1, 11))  # Array con los números del 1 al 10

    p1 = Process(target=elevar_cuadrado, args=(datos,))
    p2 = Process(target=elevar_cubo, args=(datos,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Array final:", list(datos))
