class Agent:
    def __init__(self, _id, skillset = []):
        self._id = _id
        self.skillset = skillset

        # Agent Memory
        self.stm = []               # Should be updated when task is allocated
        self.ltm = skillset

        # !TODO
        # Need to update this accordingly!
        self.current_action = -1
        self.action_history = []

    def __str__(self):
        stm_str = 'Short-term memory:\n' + str(list(map(str, self.skillset)))
        ltm_str = 'Long-term memory:\n'

        curr_act_str = 'Current action:\n'
        act_hist_str = 'Action history:\n'
        
        return '--- AGENT ' + str(self._id) + ' ---\n' + actions_str
