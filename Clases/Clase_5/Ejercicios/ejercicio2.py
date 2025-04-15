# Ejemplo 2 -Proceso que envía mensajes

import os

def enviar_mensajes(write_fd):
    mensajes = ['Hola', '¿Cómo estás?', 'Esto es una queue', 'Fin']
    for msg in mensajes:
        os.write(write_fd, (msg + '\n').encode())
    os.close(write_fd)  # Cerrar escritura

def recibir_mensajes(read_fd):
    while True:
        buffer = os.read(read_fd, 1024).decode()
        for linea in buffer.strip().split('\n'):
            if linea == 'Fin':
                print("[Receptor] Mensaje de finalización recibido.")
                os.close(read_fd)
                return
            print(f"[Receptor] Recibido: {linea}")

if __name__ == '__main__':
    read_fd, write_fd = os.pipe()
    pid = os.fork()

    if pid == 0:
        # Proceso hijo → Emisor
        os.close(read_fd)
        enviar_mensajes(write_fd)
        os._exit(0)
    else:
        # Proceso padre → Receptor
        os.close(write_fd)
        recibir_mensajes(read_fd)
        os.wait()
