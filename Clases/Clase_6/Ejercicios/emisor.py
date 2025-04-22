import os
import time

fifo_path = "/tmp/log_fifo"

# Crear FIFO si no existe
if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)

# Generamos algunos "eventos" para loguear
eventos = [
    "INFO: Sistema iniciado",
    "ERROR: No se pudo conectar a la base de datos",
    "INFO: Usuario autenticado",
    "WARNING: Espacio en disco bajo",
    "ERROR: Fallo en el servidor de correo"
]

with open(fifo_path, "w") as fifo:
    for evento in eventos:
        print(f"Escribiendo evento: {evento}")
        fifo.write(evento + "\n")
        fifo.flush()  # Aseguramos que se escriba inmediatamente
        time.sleep(1)  # Simulamos un evento por segundo
