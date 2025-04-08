#EJERCICIOS PROMPT

import os

def main():
    # Crear el pipe: devuelve dos file descriptors (lectura y escritura)
    r, w = os.pipe()

    # Crear un nuevo proceso (hijo)
    pid = os.fork()

    if pid > 0:
        # 🔵 Proceso padre
        os.close(r)  # Cierra el extremo de lectura (solo escribirá)
        mensaje = "Hola desde el padre\n"
        os.write(w, mensaje.encode())  # Escribir al pipe
        os.close(w)  # Cierra el extremo de escritura
        os.wait()  # Espera que el hijo termine

    else:
        # 🟢 Proceso hijo
        os.close(w)  # Cierra el extremo de escritura (solo leerá)
        mensaje_recibido = os.read(r, 1024)  # Lee hasta 1024 bytes
        print("Hijo recibió:", mensaje_recibido.decode())
        os.close(r)  # Cierra el extremo de lectura

if __name__ == "__main__":
    main()

#########################################################################################


def main():
    r, w = os.pipe()
    pid = os.fork()

    if pid > 0:
        # 🔵 Padre
        os.close(r)  # No lee
        numero = "21"
        os.write(w, numero.encode())
        os.close(w)
        os.wait()
    else:
        # 🟢 Hijo
        os.close(w)  # No escribe
        datos = os.read(r, 32).decode()
        resultado = int(datos) * 2
        print(f"Hijo recibió {datos}, y el resultado es: {resultado}")
        os.close(r)

if __name__ == "__main__":
    main()





def main():
    # Creamos dos pipes: uno para enviar, otro para recibir
    r1, w1 = os.pipe()  # Padre → Hijo
    r2, w2 = os.pipe()  # Hijo → Padre

    pid = os.fork()

    if pid > 0:
        # 🔵 Padre
        os.close(r1)  # No lee del primero
        os.close(w2)  # No escribe en el segundo

        numero = "10"
        os.write(w1, numero.encode())
        os.close(w1)

        resultado = os.read(r2, 32).decode()
        print("Padre recibió:", resultado)
        os.close(r2)

        os.wait()

    else:
        # 🟢 Hijo
        os.close(w1)  # No escribe en el primero
        os.close(r2)  # No lee del segundo

        datos = os.read(r1, 32).decode()
        resultado = int(datos) * 2
        os.write(w2, str(resultado).encode())

        os.close(r1)
        os.close(w2)

if __name__ == "__main__":
    main()
