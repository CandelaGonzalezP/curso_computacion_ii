# proceso huerfano

import os
import time

def main():
    print(f"Parent PID: {os.getpid()}")

    # Create a child process
    pid = os.fork()
    if pid == 0:
        # Child process: continue running after parent exits
        print(f"Child PID: {os.getpid()} created. Parent PID: {os.getppid()}")
        time.sleep(20)  # Simulate work for 20 seconds
        print(f"Child PID: {os.getpid()} finished. Current Parent PID: {os.getppid()}")
    else:
        # Parent process: exit immediately
        print(f"Parent PID: {os.getpid()} exiting.")
        os._exit(0)

if __name__ == "__main__":
    main()