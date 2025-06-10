# proceso zombie

import os
import time

def main():
    print(f"Parent PID: {os.getpid()}")

    # Create a child process
    pid = os.fork()
    if pid == 0:
        # Child process: exit immediately
        print(f"Child PID: {os.getpid()} exiting.")
        os._exit(0)
    else:
        # Parent process: wait for 10 seconds
        print(f"Child PID: {pid} created. Waiting 10 seconds to collect its status...")
        time.sleep(10)

        # Collect child's status
        _, status = os.wait()
        print(f"Child PID: {pid} collected. Exit status: {status}")

if __name__ == "__main__":
    main()