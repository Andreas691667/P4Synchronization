import sys
sys.path.insert(0, "./Vector_clocks")
from VectorProcess import VectorProcess

if __name__ == "__main__":
    N = 2
    processes = [VectorProcess(i, N) for i in range(N)]

    events = [(5, "event1"), (10, "event2")]
    
    for e in events:
        processes[0].events_queue.put(e)

    for process in processes:
        process.processes = processes

    for process in processes:
        process.start_loop()

    while True:
        pass