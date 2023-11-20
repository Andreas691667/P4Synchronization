from queue import Queue, Empty
from threading import Event, Thread
import time
import random

class VectorProcess:
    def __init__(self, _id, n):
        self._id = _id
        self.processes = []
        self.main_thread = Thread(target=self.main_loop, daemon=True)
        self.stop_worker = Event()
        self.message_queue = Queue()    #queue of incoming message (payload, timestamp)
        self.events_queue = Queue()     #queue of tuples: (payload, time)
        self.start_time = 0
        self.clock = [0] * n            #vector clock initialized to 0

    def start_loop(self):
        """Start the process loop"""
        self.start_time = time.time()
        print(f"Process {self._id} started")
        self.main_thread.start()

    def get_process(self, _id):
        """Get process object by id"""
        return self.processes[_id]
    
    def enqueue_message(self, payload, timestamp):
        """Enqueue message to be processed by the state machine"""
        self.message_queue.put((payload, timestamp))

    def main_loop(self):
        """Main loop for the process"""
        while not self.stop_worker.is_set():
            time_delta = time.time() - self.start_time
            # Check event queue for events
            if not self.events_queue.empty():
                event_time, event_payload = self.events_queue.queue[0]
                if (time_delta >= event_time):
                    # Remove element
                    self.events_queue.get()
                    # Call send message with event and timestamp
                    self.send_message(event_payload, self.clock)
        

            # Check for incoming messages
            try:
                payload, clock_in = self.message_queue.get(timeout=0.1)
            
            # Empty
            except Empty:
                pass
            
            # Not empty
            else:
                self.receive_message(payload, clock_in) 

    def receive_message(self, payload, timestamp):
        """Receive message from another process"""
        self.clock[self._id] += 1
        # update clock by taking elementwise max
        for i, clock_old in enumerate(self.clock):
            self.clock[i] = max(clock_old, timestamp[i])

        print(f"Process {self._id} received message {payload} with timestamp {timestamp}")
    
    def send_message(self, payload, timestamp):
        """Send message to another process"""
        self.clock[self._id] += 1
        # send message to random process
        process : VectorProcess = random.choice(self.processes)
        process.enqueue_message(payload, timestamp)
        print(f"Process {self._id} sent message {payload} with timestamp {timestamp} to process {process._id}")

    