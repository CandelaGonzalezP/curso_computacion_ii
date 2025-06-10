#!/bin/bash

FIFO="mi_fifo"

# Crear la FIFO si no existe
if [[ ! -p $FIFO ]]; then
    mkfifo $FIFO
fi

# Leer continuamente desde la FIFO
echo "Lector iniciado. Leyendo de la FIFO..."
while true; do
    if read line < $FIFO; then
        echo "Lector recibió: $line"
    fi
done
