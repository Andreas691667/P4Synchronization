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
                time_delta = self.get_time_in_ms() - self.start_time
                (
                    event_time,
                    from_process,
                    to_process,
                    event_payload,
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

    def get_time_in_ms(self):
        return time.time_ns() / 10**6

    def receive_message(self, payload, timestamp):
        """Called upon recieving a message"""
        # update timestamp
        old_ts = self.clock
        time_delta = round(self.get_time_in_ms() - self.start_time)
        self.clock = max(timestamp, self.clock) + 1
        print(
            f"{time_delta}: Process {self._id} recieved msg: {payload} \n Timestamp update: {old_ts} -> {self.clock} \n"
        )

    def enqueue_message(self, payload, clock):
        self.message_queue.put((payload, clock))

    def send_message(self, to_process, payload):
        # Send to the other process
        self.processes[to_process].enqueue_message(payload, self.clock)

    def handle_event(self, payload, out_id) -> None:
        """Handle event"""
        # STOP event, last event
        if payload == "STOP":
            self.stop_worker.set()
            return
        
        # Local event
        elif out_id == self._id:
            self.increment_clock()
            print(
                f"""LOCAL [T: {time.time()-self.start_time}], [ID: {self._id}], [C: {self.clock}]\n"""
            )
            return
        # Send
        else:
            self.increment_clock()
            self.send_message(payload, out_id)
    
    def increment_clock(self):
        self.clock += 1