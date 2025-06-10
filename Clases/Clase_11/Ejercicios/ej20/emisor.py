import os
import time

if __name__ == "__main__":
    receptor_pid = int(input("Ingrese el PID del receptor: "))
    while True:
        print(f"Enviando SIGUSR1 al proceso {receptor_pid}...")
        os.kill(receptor_pid, signal.SIGUSR1)
        time.sleep(2)
        print(f"Enviando SIGUSR2 al proceso {receptor_pid}...")
        os.kill(receptor_pid, signal.SIGUSR2)
        time.sleep(2)