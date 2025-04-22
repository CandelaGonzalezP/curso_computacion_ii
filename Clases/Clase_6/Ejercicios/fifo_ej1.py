import os

fifo_path = "/tmp/chat_fifo"

if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)
    print(f"FIFO creado en {fifo_path}")
else:
    print(f"FIFO ya existe en {fifo_path}")

