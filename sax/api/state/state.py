# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from threading import Lock

class State:
    state_lock = Lock()

    def __init__(self):
       self.data= None

    def get_state_copy(self):
        # Acquire the lock before reading app.state
        self.state_lock.acquire()
        try:
            state_copy = self.data.copy() if self.data else None
        finally:
            # Release the lock after reading app.state
            self.state_lock.release()
        return state_copy

    def update_state(self,data):
        self.state_lock.acquire()
        try:
            self.data=data
        finally:
            self.state_lock.release()        

    def clear_state(self):
        self.state_lock.acquire()
        try:
            self.data=None
        finally:
            self.state_lock.release() 
