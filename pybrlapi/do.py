from threading import Thread

class BasicTask:
    def __init__ (self, func, args=(), kwargs={}):
        self.func   = func
        self.args   = args
        self.kwargs = kwargs
        self.name   = func.__name__
        self.done   = False
        self.res    = Ellipsis
        self.exc    = None

    def __repr__ (self):
        r  = "<"+self.__class__.__name__+f": {self.name}("+", ".join(repr(x) for x in self.args)
        r += ", "+", ".join(k+"="+repr(v) for k, v in self.kwargs.items()) if self.kwargs else ""
        r += ")>"
        return r

    def __hash__ (self):
        return hash(repr(self)+hex(id(self)))

    on_done = lambda self, me: None

    def run (self):
        try:
            self.res = self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.exc = e
        self.done = True
        self.on_done(self)

    def start (self):
        self.run()
        return self

    def retrieve (self, error="raise"):
        if self.exc:
            if error=="raise":
                raise self.exc
            elif error=="ignore":
                return
            return self.exc
        if self.res==Ellipsis and error=="raise":
            raise RuntimeError("Task() not started yet!")
        return self.res
    __call__ = retrieve

class Task (BasicTask, Thread):
    def __init__ (self, func, args=(), kwargs={}):
        Thread.__init__(self)
        self.daemon = True
        BasicTask.__init__(self, func, args, kwargs)

    def start (self):
        Thread.start(self)
        return self

    def retrieve (self, error="raise"):
        try:
            self.join()
        except RuntimeError:
            if self.res==Ellipsis and error=="raise":
                raise RuntimeError("Task() not started yet!")
            elif self.res==Ellipsis:
                pass
            else:
                raise RuntimeError("O NO! You don't! What on Earth you think you are doing! Do you wish to intentionally cause a deadlock?!")
        if self.exc:
            if error=="raise":
                raise self.exc
            elif error=="ignore":
                return
            return self.exc
        return self.res
    __call__ = retrieve

    __hash__ = BasicTask.__hash__

class RepeatableTask (BasicTask):
    def __init__ (self, func, args=(), kwargs={}):
        self.func   = func
        self.args   = args
        self.kwargs = kwargs
        self.name   = func.__name__
        self.res    = Ellipsis
        self.exc    = None
        self.task   = None

    def start (self):
        if self.task:
            if not self.task.done:
                return self
        self.task = task = Task(self.func, self.args, self.kwargs)
        task.on_done = self.on_done
        task.start()
        return self

    def run (self):
        raise NotImplementedError("RepeatableTask() cannot be run directly!")

    def retrieve (self, error="raise"):
        if self.task:
            return self.task.retrieve(error)
        if error=="raise":
            raise RuntimeError("Task() not started yet!")
        return Ellipsis
    __call__ = retrieve

    __hash__ = BasicTask.__hash__

    @property
    def done (self):
        return self.task.done if self.task else False

def map (func, seq, error="return"):
    q = [Task(func, (arg,)).start() for arg in seq]
    for task in q:
        yield task(error=error)
