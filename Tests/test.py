import sys

sys.path.insert(0, "./Vector_clocks")
from VectorProcess import VectorProcess

if __name__ == "__main__":
    N = 3  # Number of processes
    # Create processes
    processes = [VectorProcess(i, N) for i in range(N)]

    # create events for processes
    terminate_event = (12, "STOP", -1)  # Event to stop the processes
    events0 = [(1, "e1", 0), (6, "e6", 1)]
    events1 = [(2, "e2", 1), (3, "e3", 0), (8, "e8", 2), (11, "e10", 1)]
    events2 = [(5, "e5", 2), (9, "e11", 2)]
    E = [events0, events1, events2]

    for i, e in enumerate(E):
        for ei in e:
            processes[i].events_queue.put(ei)
        processes[i].events_queue.put(terminate_event)

    for process in processes:
        process.set_processes(processes)

    for process in processes:
        process.start_loop()

    # run infinite loop until all processes are stopped
    while not all([p.stop_worker.is_set() for p in processes]):
        pass
