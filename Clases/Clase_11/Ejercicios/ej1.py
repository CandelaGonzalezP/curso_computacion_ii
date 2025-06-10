# creacion de procesos con argumentos

import argparse
import os
import random
import time
from multiprocessing import Process
import subprocess

def child_process(verbose):
    sleep_time = random.randint(1, 5)
    if verbose:
        print(f"Child process {os.getpid()} sleeping for {sleep_time} seconds.")
    time.sleep(sleep_time)
    if verbose:
        print(f"Child process {os.getpid()} finished.")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process creation script.")
    parser.add_argument("--num", type=int, required=True, help="Number of child processes to create.")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed messages.")
    args = parser.parse_args()

    # Create child processes
    processes = []
    for _ in range(args.num):
        p = Process(target=child_process, args=(args.verbose,))
        p.start()
        processes.append(p)
        if args.verbose:
            print(f"Started child process with PID {p.pid}.")

    # Print parent PID and process hierarchy
    print(f"Parent PID: {os.getpid()}")
    print("Process hierarchy:")
    subprocess.run(["pstree", "-p", str(os.getpid())])

    # Wait for all child processes to finish
    for p in processes:
        p.join()

    if args.verbose:
        print("All child processes have finished.")

if __name__ == "__main__":
    main()