import sys
from queue import Queue
from time import sleep, time

sys.path.insert(0, "./Vector_clocks")
sys.path.insert(0, "./Lamport_timestamps")

from VectorProcess import VectorProcess
from LamportProcess import LamportProcess

def test_lamport ():
    print("---- LAMPORT TIMESTAMPS TEST ----")
    # Initialize processes array
    processes = []
    ids = [0, 1, 2]

    # --- instantiate and pass processes ---
    # Instantiate objects
    for _, id in enumerate(ids):
        processes.append(LamportProcess(id))

    # Set processes in processes
    for index, id in enumerate(ids):
        processes[index].set_processes(processes)

    # --- Inject events ---
    e0 = Queue()
    e1 = Queue()
    e2 = Queue()
    terminate_event = (12, "STOP", -1)  # Event to stop the processes
    e0_list = [(1, "e1", 0), (6, "e6", 1), terminate_event]
    e1_list = [(2, "e2", 1), (3, "e3", 0), (8, "e8", 2), (11, "e10", 1), terminate_event]
    e2_list = [(5, "e5", 2), (9, "e11", 2), terminate_event]
    list(map(e0.put, e0_list))  # Put elements into the queue
    list(map(e1.put, e1_list))  # Put elements into the queue
    list(map(e2.put, e2_list))  # Put elements into the queue
    processes[0].inject_events(e0)
    processes[1].inject_events(e1)
    processes[2].inject_events(e2)

    # --- Start Threads ---
    start_time = time()
    for index, id in enumerate(ids):
        processes[index].start_loop(start_time)

    # run infinite loop until all processes are stopped
    while not all([p.stop_worker.is_set() for p in processes]):
        pass

def test_vector_clocks ():
    print("---- VECTOR CLOCKS TEST ----")
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


if __name__ == "__main__":
    test_lamport()
    test_vector_clocks()
