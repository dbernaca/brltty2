from .blocker import Blocker
from .asyncore import poll
from . import do
from threading import  Thread
from collections import deque
from time import sleep, monotonic as time

class Looper:
    def __init__ (self, timeout=30.0, task_done_callback=None):
        self._timeout    = timeout
        self.connections = {}
        self.tasks       = deque()
        self.processed   = deque()
        self.timediff    = 0.0
        self.running     = False
        self.callback    = (lambda task: None) if task_done_callback is None else task_done_callback

    def get_timeout (self):
        return self._timeout

    def set_timeout (self, timeout):
        self._timeout = timeout

    timeout = property(get_timeout, set_timeout)

    def run (self):
        connections = self.connections
        self.running = True
        while connections and self.running:
            try:
                t1 = time()
                poll(self._timeout, connections)
                self.timediff = time()-t1
            except OSError:
                break
            try:
                task = self.tasks.pop()
                if not task.autoconsume:
                    self.processed.append(task)
                task.start()
            except:
                pass
        print("ConnectionLoop ended")
        self.tasks.clear()
        self.running = False

    start = run

    def stop (self):
        self.running = False

    def __next__ (self):
        if not self.running or not self.connections:
            raise StopIteration()
        t2 = -1.0
        try:
            t1 = time()
            poll(self._timeout, self.connections)
            self.timediff = t2 = time()-t1
        except OSError:
            raise StopIteration()
        try:
            task = self.tasks.pop()
            if not task.autoconsume:
                self.processed.append(task)
            task.start()
        except:
            pass
        return t2

    def __iter__ (self):
        return self

    def enqueue (self, func, args=(), kwargs={}, threaded=False, autoconsume=False):
        if threaded:
            task = do.Task(func, args, kwargs)
        else:
            task = do.BasicTask(func, args, kwargs)
        task.autoconsume = autoconsume
        task.on_done     = self.callback
        self.tasks.append(task)
        return task

    def retrieve (self, error="raise", wait_for_task=True):
        while True:
            try:
                task = self.processed[0]
                if task.done:
                    self.processed.pop()
                    break
            except:
                if wait_for_task:
                    sleep(0.001)
                else:
                    return Ellipsis
        return task(error=error)

class BackgroundLooper (Looper, Thread):
    def __init__ (self, timeout=30.0):
        Looper.__init__(self, timeout)
        Thread.__init__(self)
        self.daemon = True

    start = Thread.start
