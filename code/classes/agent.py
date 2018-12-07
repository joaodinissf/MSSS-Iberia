class Agent:
    def __init__(self, _id, skillset = []):
        self._id = _id

        #self.mood = []

        # Ensure skills are stored in order
        self.skillset = sorted(skillset, key=lambda s: s._id)

        # Sanity check - skills should be consecutive integers starting at zero
        try:
            assert [skill._id for skill in self.skillset] == range(len(self.skillset))
        except AssertionError:
            print('Invalid skillset provided! Please verify the correctness of your input.')

        # Agent Memory
        self.stm = []                    # Should be updated when task is allocated
        self.ltm = self.skillset.copy()  # Initially, all skills are part of the long-term memory

        # TODO
        # Need to update this accordingly
        self.current_action = []
        self.action_history = []

    def __str__(self):
        stm_str = 'Short-term memory:\n' + '\n'.join(list(map(str, self.stm))) + '\n'
        ltm_str = 'Long-term memory:\n' + '\n'.join(list(map(str, self.ltm))) + '\n'

        curr_act_str = 'Current action:\n' + str(self.current_action) + '\n'
        act_hist_str = 'Action history:\n' + str(self.action_history) + '\n'
        
        return '--- AGENT ' + str(self._id) + ' ---\n' + stm_str + ltm_str + curr_act_str + act_hist_str
