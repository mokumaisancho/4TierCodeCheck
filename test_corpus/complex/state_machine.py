
class StateMachine:
    def __init__(self):
        self.state = 'idle'
        self.transitions = {
            'idle': {'start': 'running'},
            'running': {'pause': 'paused', 'stop': 'idle'},
            'paused': {'resume': 'running', 'stop': 'idle'}
        }
    
    def trigger(self, event):
        if event in self.transitions.get(self.state, {}):
            self.state = self.transitions[self.state][event]
            return True
        return False
