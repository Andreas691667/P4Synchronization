import sys
sys.path.insert(0, "./Vector_clocks")
from VectorProcess import VectorProcess

if __name__ == "__main__":
    N = 2   # Number of processes
    # Create processes
    processes = [VectorProcess(i, N) for i in range(N)]

    # create events for processes
    terminate_event = (15, "STOP", -1)  # Event to stop the processes
    events0 = [(5, "event1", 1), (10, "event2", 1)]
    events1 = [(6, "event3", 0), (11, "event4", 0)]
    E = [events0, events1]


    for i, e in enumerate(E):
        for ei in e:
            processes[i].events_queue.put(ei)
        processes[i].events_queue.put(terminate_event)

    for process in processes:
        process.processes = processes

    for process in processes:
        process.start_loop()

    # run infinite loop until all processes are stopped
    while not all([p.stop_worker.is_set() for p in processes]):
        pass
