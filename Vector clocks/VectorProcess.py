from queue import Queue, Empty
from threading import Event, Thread
from time import time

class VectorProcess:
    def __init__(self, _id, n):
        self._id = _id
        self.no_processes = n
        self.processes = []
        self.main_thread = Thread(target=self.main_loop, daemon=True)
        self.stop_worker = Event()
        self.message_queue = Queue()    #queue of incoming message (payload, timestamp)
        self.events_queue = Queue()     #queue of tuples: (payload, time)
        self.current_time = 0
        self.clock = [0] * n            #vector clock initialized to 0
        
    def start_loop(self):
        self.current_time = time.time()
        self.main_thread.start()

    def get_process(self, _id):
        """Get process object by id"""
        return self.processes[_id]
    
    def enqueue_message(self, payload, timestamp):
        """Enqueue message to be processed by the state machine"""
        self.message_queue.put((payload, timestamp))

    def main_loop(self):
        while not self.stop_worker.is_set():
            # Check event queue for events
            if not self.events_queue.empty():
                event_time, event_payload = self.events_queue.queue[0]
                if (self.current_time >= event_time):
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

            self.current_time = time.time()


    def receive_message(self, payload, timestamp):
        pass
    
    def send_message(self, payload, timestamp):
        self.clock[self._id] += 1

    