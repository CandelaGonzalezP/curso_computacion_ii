from multiprocessing import Process, Array

def cuadrado(valores):
    for i in range(len(valores)):
        valores[i] = valores[i] * valores[i]

if __name__ == '__main__':
    datos = Array('i', [1, 2, 3, 4, 5])  # Array de enteros

    p = Process(target=cuadrado, args=(datos,))
    p.start()
    p.join()
    
    print("Datos al cuadrado:", list(datos))
