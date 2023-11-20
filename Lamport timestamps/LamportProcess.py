from queue import Queue, Empty
from threading import Event, Thread
from time import time

class LamportProcess:
    def __init__(self, _id):
        self._id = _id
        self.main_thread = Thread(target=self.main_loop, daemon=True)
        self.stop_worker = Event()
        self.message_queue = Queue()    #queue of incoming message (timestamp, payload)
        self.events_queue = Queue()     #queue of tuples: (time, payload)
        self.current_time = 0
        self.clock = None
        self.processes = []
        
    def start_loop(self):
        self.current_time = time.time()
        self.main_thread.start()

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
        

            # Check for incomming messages
            try:
                payload, clock_in = self.message_queue.get(timeout=0.1)
            
            # Empty
            except Empty:
                pass
            
            # Not empy
            else:
                self.receive_message(payload, clock_in) 

            self.current_time = time.time()


    def receive_message(self, payload, timestamp):
        pass
    
    def send_message(self, payload, timestamp):
        pass

    