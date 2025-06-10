#!/bin/bash

# Diccionario para contar los estados
declare -A estados

# Recorrer los directorios en /proc
for pid in /proc/[0-9]*; do
    # Verificar si el archivo status existe
    if [[ -f "$pid/status" ]]; then
        # Extraer información del archivo status
        PID=$(grep -m 1 "^Pid:" "$pid/status" | awk '{print $2}')
        PARENT_PID=$(grep -m 1 "^PPid:" "$pid/status" | awk '{print $2}')
        NAME=$(grep -m 1 "^Name:" "$pid/status" | awk '{print $2}')
        STATE=$(grep -m 1 "^State:" "$pid/status" | awk '{print $2}')

        # Mostrar información del proceso
        echo "PID: $PID, PARENT_PID: $PARENT_PID, Name: $NAME, State: $STATE"

        # Contar el estado
        estados["$STATE"]=$((estados["$STATE"] + 1))
    fi
done

# Mostrar resumen de estados
echo -e "\nResumen de estados:"
for estado in "${!estados[@]}"; do
    echo "Estado $estado: ${estados[$estado]} procesos"
done
