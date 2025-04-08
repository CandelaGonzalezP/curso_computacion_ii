# EJERCICIO 4 - SIMULADOR DE SHELL

import os
import sys

def ejecutar_pipeline(cmd1, cmd2):
    r, w = os.pipe()

    pid1 = os.fork()
    if pid1 == 0:
        os.dup2(w, sys.stdout.fileno())  # Redirige stdout al pipe
        os.close(r)
        os.close(w)
        os.execvp(cmd1[0], cmd1)
    else:
        pid2 = os.fork()
        if pid2 == 0:
            os.dup2(r, sys.stdin.fileno())  
            os.close(w)
            os.close(r)
            os.execvp(cmd2[0], cmd2)
        else:
            os.close(r)
            os.close(w)
            os.waitpid(pid1, 0)
            os.waitpid(pid2, 0)

def main():
    entrada = input("Ingresá dos comandos separados por '|':\n> ")

    try:
        parte1, parte2 = entrada.split('|')
        cmd1 = parte1.strip().split()
        cmd2 = parte2.strip().split()

        ejecutar_pipeline(cmd1, cmd2)

    except ValueError:
        print("Error: asegurate de ingresar dos comandos separados por el símbolo '|'.")
    except FileNotFoundError as e:
        print(f"Error de comando: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
