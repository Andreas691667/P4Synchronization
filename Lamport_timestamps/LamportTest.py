from LamportProcess import LamportProcess
from queue import Queue, Empty
from time import sleep, time_ns


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
    e0_list = [(500, 0, 1, "0->1"), (1500, 0, 2, "0->2")]  # (time, from, to, payload)
    e1_list = [(1000, 1, 2, "1->2"), (3000, 1, 0, "1->0")]
    e2_list = [(2000, 2, 0, "2->0"), (2500, 2, 1, "2->1")]
    list(map(e0.put, e0_list))  # Put elements into the queue
    list(map(e1.put, e1_list))  # Put elements into the queue
    list(map(e2.put, e2_list))  # Put elements into the queue
    processes[0].inject_events(e0)
    processes[1].inject_events(e1)
    processes[2].inject_events(e2)

    # --- Start Threads ---
    start_time = time_ns() / 10**6
    for index, id in enumerate(ids):
        processes[index].start_loop(start_time)

    # Run threads for 1 second
    sleep(5)

    # --- Print results ---


if __name__ == "__main__":
    main()
