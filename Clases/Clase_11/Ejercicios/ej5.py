# pipes anonimos entre padres e hijos

import os

# Crear un pipe anónimo
read_fd, write_fd = os.pipe()

# Crear un proceso hijo usando fork()
pid = os.fork()

if pid == 0:
    # Código del proceso hijo
    os.close(read_fd)  # Cerrar el descriptor de lectura en el hijo
    message = b"Hola, soy el proceso hijo!"  # Mensaje en formato binario
    os.write(write_fd, message)  # Escribir el mensaje en el pipe
    os.close(write_fd)  # Cerrar el descriptor de escritura después de enviar el mensaje
else:
    # Código del proceso padre
    os.close(write_fd)  # Cerrar el descriptor de escritura en el padre
    message = os.read(read_fd, 1024)  # Leer el mensaje del pipe (máximo 1024 bytes)
    os.close(read_fd)  # Cerrar el descriptor de lectura después de recibir el mensaje
    print(f"Padre recibió: {message.decode('utf-8')}")  # Decodificar y mostrar el mensaje