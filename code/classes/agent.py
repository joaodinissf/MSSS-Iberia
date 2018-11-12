class Agent:
    def __init__(self, _id, skillset = []):
        self._id = _id
        self.skillset = skillset

        # !TODO
        # Need to update this accordingly!
        self.current_action = -1
        self.action_history = []
    
    def __str__(self):
        return 'Agent ' + str(self._id) + \
               ', Skills:' + '\n' + str(list(map(str, self.skillset)))
