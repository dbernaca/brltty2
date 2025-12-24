from threading   import Lock
from .exceptions import *

class Blocker:
    def __init__ (self, source="<generic>", timeout=-1, wait_at_exit=False):
        self.lock     = l = Lock()
        self.source       = source
        self.timeout      = timeout
        self.wait_at_exit = wait_at_exit
        self.exception    = None
        self.isWaiting    = l.locked

    def wait (self):
        """
        Blocks until done() or throw() are called.
        If timeout occurs, raises the TimedOut() exception.
        If an exception was enqueued, raises it, regardless of interruption method.
        """
        self.lock.acquire(False)
        timedout = not self.lock.acquire(True, self.timeout)
        try:
            self.lock.release()
        except:
            pass
        e = self.exception
        if e:
            self.exception = None
            raise e
        if timedout:
            raise TimedOut(self.source, self.timeout)

    def block (self):
        """
        Blocks until done() or throw() are called.
        No timeout included in this one.
        If an exception occurs during the block, raises it when interrupted.
        """
        self.lock.acquire(False)
        self.lock.acquire()
        self.lock.release()
        e = self.exception
        if e:
            self.exception = None
            raise e

    def done (self):
        """
        Interrupts a wait or block.
        """
        try:
            self.lock.release()
        except:
            pass

    end = finish = finished = stop = stopped = exit = done

    def throw (self, e):
        """
        Enqueues an exception to be raised and interrupts the waiting or a block.
        The waiting method then raises the exception.
        """
        if self.exception:
            self.exception = MultipleExceptions(self.exception, e)
        else:
            self.exception = e
        try:
            self.lock.release()
        except:
            pass

    def __enter__ (self):
        """
        Context manager method making this Blocker() behave as a regular Lock(),
        with support for the set timeout.
        """
        if not self.lock.acquire(True, self.timeout):
            raise TimedOut(self.source, self.timeout)
        return self

    begin = prepare = start = started = enter = __enter__

    def __exit__ (self, et=None, ev=None, tb=None):
        """
        Context manager method for classic Lock() behaviour,
        but it cleans up the enqueued exceptions and raises those which occurred.
        An extra feature is wait_at_exit given in the constructor or by the attribute
        that can be set within the context body.
        If True, the exiting from the context will wait for done() or throw().
        The wait will use a timeout and if it occurs without an exception the
        TimedOut() will be raised instead.
        """
        timeout = False
        if self.wait_at_exit:
            timeout = not self.lock.acquire(True, self.timeout)
        e = self.exception
        self.exception = None
        try:
            self.lock.release()
        except:
            pass
        if et or ev or tb:
            return False
        if e:
            raise e
        if timeout:
            raise TimedOut(self.source, self.timeout)
