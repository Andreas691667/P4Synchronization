from queue import Queue, Empty
from threading import Event, Thread
import time


class VectorProcess:
    """Process class that uses vector clocks"""

    def __init__(self, _id, n):
        self._id: int = _id
        self.processes = []
        self.main_thread = Thread(target=self.main_loop, daemon=True)
        self.stop_worker = Event()
        self.message_queue = Queue()  # queue of incoming message (payload, timestamp)
        self.events_queue = Queue()  # queue of tuples: (payload, receiver_id, time)
        self.start_time: float = 0
        self.clock: list = [0] * n  # vector clock initialized to 0

    def set_processes(self, processes) -> None:
        """Set processes"""
        self.processes = processes

    def start_loop(self) -> None:
        """Start the process loop"""
        self.start_time = time.time()
        self.print_event("INIT", "INIT", self.get_time())
        # print(
        #     f"INIT [T: {time.time()-self.start_time}], [ID: {self._id}], [C: {self.clock}]"
        # )
        self.main_thread.start()

    def get_process(self, _id) -> "VectorProcess":
        """Get process object by id"""
        return self.processes[_id]

    def enqueue_message(self, payload, timestamp) -> None:
        """Enqueue message to be processed by the state machine"""
        self.message_queue.put((payload, timestamp))

    def main_loop(self) -> None:
        """Main loop for the process"""
        while not self.stop_worker.is_set():
            time_delta = time.time() - self.start_time
            # Check event queue for events
            if not self.events_queue.empty():
                event_time, event_payload, out_id = self.events_queue.queue[0]
                if time_delta >= event_time:
                    # Remove element
                    self.events_queue.get()
                    # Call send message with event and timestamp
                    self.handle_event(event_payload, out_id)

            # Check for incoming messages
            try:
                payload, clock_in = self.message_queue.get(timeout=0.1)

            # Empty
            except Empty:
                pass

            # Not empty
            else:
                self.receive_message(payload, clock_in)

        print(f"Process {self._id} stopped \n")

    def receive_message(self, payload, timestamp) -> None:
        """Receive message from another process"""
        self.clock[self._id] += 1
        # update clock by taking elementwise max
        for i, clock_old in enumerate(self.clock):
            self.clock[i] = max(clock_old, timestamp[i])

        self.print_event("RECEIVE", payload, self.get_time())
        # print(
        #     f"""RECEIVE [T: {time.time()-self.start_time}], [ID: {self._id}], [C: {self.clock}] \n"""
        # )

    def handle_event(self, payload, out_id) -> None:
        """Handle event"""
        if payload == "STOP":
            self.stop_worker.set()
            return
        elif out_id == self._id:
            self.clock[self._id] += 1
            self.print_event("LOCAL", payload, self.get_time())
            # print(
            #     f"""LOCAL [T: {time.time()-self.start_time}], [ID: {self._id}], [C: {self.clock}]\n"""
            # )
            return
        else:
            self.clock[self._id] += 1
            self.send_message(payload, out_id)

    def send_message(self, payload, out_id) -> None:
        """Send message to another process"""
        # send message to random process
        process: VectorProcess = self.get_process(out_id)
        process.enqueue_message(payload, self.clock)
        self.print_event("SEND", payload, self.get_time())
        # print(
        #     f"""SEND [T: {time.time()-self.start_time}], [ID: {self._id}], [C: {self.clock}] \n"""
        # )

    def get_time(self) -> float:
        """Get time in ms"""
        return time.time() - self.start_time

    def print_event(
        self, event_type: str, event_payload: str, event_time: float
    ) -> None:
        """Print event"""
        print(
            f"""{event_type} event [T: {time.time()-self.start_time}], [PROCESS_ID: {self._id}], [CLOCK: {self.clock}], [PAYLOAD: {event_payload}], [TIME: {event_time}] \n"""
        )
