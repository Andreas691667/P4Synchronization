from LamportProcess import LamportProcess
from queue import Queue, Empty
from time import sleep, time


def main():
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

    # Run threads for 1 second
    sleep(15)


if __name__ == "__main__":
    main()
