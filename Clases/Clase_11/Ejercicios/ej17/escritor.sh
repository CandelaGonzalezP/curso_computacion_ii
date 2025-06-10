#!/bin/bash

FIFO="mi_fifo"

# Crear la FIFO si no existe
if [[ ! -p $FIFO ]]; then
    mkfifo $FIFO
fi

# Escribir en la FIFO cada segundo
echo "Escritor iniciado. Escribiendo en la FIFO..."
while true; do
    echo "Mensaje desde el escritor: $(date)" > $FIFO
    sleep 1
done
