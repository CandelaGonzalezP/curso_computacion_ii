from multiprocessing import Process, Queue

def producir(queue):
    for i in range(5):
        queue.put(f"Mensaje {i}")

if __name__ == '__main__':
    q = Queue()
    p = Process(target=producir, args=(q,))
    p.start()
    p.join()

    while not q.empty():
        print(q.get())
