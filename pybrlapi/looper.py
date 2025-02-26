from .blocker import Blocker
from .asyncore import poll
from threading import  Thread
from collections import deque
from time import monotonic as time

class Looper:
    def __init__ (self, timeout=30.0):
        self._timeout    = timeout
        self.connections = {}
        self.tasks       = deque()
        self.task        = Blocker("MainLoop", timeout)
        self.taskresults = deque()
        self.timediff    = 0.0
        self.running     = False

    def get_timeout (self):
        return self._timeout

    def set_timeout (self, timeout):
        self._timeout = timeout
        self.task.timeout = timeout

    timeout = property(get_timeout, set_timeout)

    def run (self):
        connections = self.connections
        self.running = True
        while self.running:
            try:
                t1 = time()
                poll(self._timeout, connections)
                self.timediff = time()-t1
            except OSError:
                break
            try:
                func, args, kwargs = self.tasks.pop()
            except:
                continue
            with self.task:
                self.taskresults.append(func(*args, **kwargs))
        print("ConnectionLoop ended")
        self.running = False

    start = run

    def stop (self):
        self.running = False

    def enqueue (self, func, args=(), kwargs={}):
        self.tasks.append((func, args, kwargs))

    def retrieve (self):
        self.task.wait()
        return self.taskresults.pop()

class BackgroundLooper (Looper, Thread):
    def __init__ (self, timeout=30.0):
        Looper.__init__(self, timeout)
        Thread.__init__(self)
        self.daemon = True

    start = Thread.start
