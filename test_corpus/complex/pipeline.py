
class Pipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, func):
        self.steps.append(func)
        return self
    
    def execute(self, data):
        result = data
        for step in self.steps:
            result = step(result)
        return result
    
    def compose(self, other):
        new_pipe = Pipeline()
        new_pipe.steps = self.steps + other.steps
        return new_pipe
