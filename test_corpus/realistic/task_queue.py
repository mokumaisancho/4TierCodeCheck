
from queue import Queue
from threading import Thread, Lock

class TaskQueue:
    def __init__(self, num_workers=4):
        self.queue = Queue()
        self.workers = []
        self.lock = Lock()
        self.results = {}
        
        for i in range(num_workers):
            t = Thread(target=self._worker)
            t.daemon = True
            t.start()
            self.workers.append(t)
    
    def submit(self, task_id, func, *args):
        self.queue.put((task_id, func, args))
    
    def _worker(self):
        while True:
            task_id, func, args = self.queue.get()
            try:
                result = func(*args)
                with self.lock:
                    self.results[task_id] = ('success', result)
            except Exception as e:
                with self.lock:
                    self.results[task_id] = ('error', str(e))
            finally:
                self.queue.task_done()
