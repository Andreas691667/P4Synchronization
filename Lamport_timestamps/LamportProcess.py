from queue import Queue, Empty
from threading import Event, Thread
import time


class LamportProcess:
    def __init__(self, _id):
        self._id = _id
        self.main_thread = Thread(target=self.main_loop, daemon=True)
        self.stop_worker = Event()
        self.message_queue = Queue()  # queue of incoming message (timestamp, payload)
        self.events_queue = Queue()  # queue of tuples: (time, payload)
        self.clock: int = 0
        self.processes: list[LamportProcess] = []
        self.log = []  # (time, from, to, timestamp_in, timestamp_updated)

    def set_processes(self, processes) -> None:
        """set processes"""
        self.processes = processes

    def inject_events(self, events: Queue) -> None:
        """Injects events"""
        self.events_queue = events

    def start_loop(self, start_time):
        self.start_time = start_time
        self.main_thread.start()

    def main_loop(self):
        while not self.stop_worker.is_set():
            # Check event queue for events
            if not self.events_queue.empty():
                time_delta = self.get_time()
                (
                    event_time,
                    event_payload,
                    to_process
                ) = self.events_queue.queue[0]
                if time_delta >= event_time:
                    # Remove element
                    self.events_queue.get()

                    # Call send message with event and timestamp
                    self.handle_event(event_payload, to_process)

            # Check for incomming messages
            try:
                payload, clock_in = self.message_queue.get(timeout=0.1)

            # Empty
            except Empty:
                pass

            # Not empy
            else:
                self.receive_message(payload, clock_in)

    def get_time(self):
        return time.time() - self.start_time

    def receive_message(self, payload, timestamp):
        """Called upon recieving a message"""
        # update timestamp
        self.clock = max(timestamp + 1 , self.clock + 1)
        self.print_event("RECEIVE", payload, self.get_time())

    def enqueue_message(self, payload, clock):
        self.message_queue.put((payload, clock))

    def send_message(self, to_process, payload):
        # Send to the other process
        self.processes[to_process].enqueue_message(payload, self.clock)
        self.print_event("SEND", payload, self.get_time())

    def handle_event(self, payload, out_id) -> None:
        """Handle event"""
        # STOP event, last event
        if payload == "STOP":
            self.stop_worker.set()
            return
        
        # Local event
        elif out_id == self._id:
            self.increment_clock()
            self.print_event("LOCAL", payload, self.get_time())
            return
        
        # Send event
        else:
            self.increment_clock()
            self.send_message(out_id, payload)
    
    def increment_clock(self):
        self.clock += 1

    def print_event(
        self, event_type: str, event_payload: str, event_time: float
    ) -> None:
        """Print event"""
        print(
            f"""{event_type} event [T: {time.time()-self.start_time}], [PROCESS_ID: {self._id}], [CLOCK: {self.clock}], [PAYLOAD: {event_payload}], [TIME: {event_time}] \n"""
        )