# "A task consists of actions in such a way that for every action exactly one skill is required to perform this action."


class Task:
    def __init__(self, _id = -1, skill_order = [], act_duration = 0):
        self._id = _id
        self.action_duration = act_duration    # For now, all actions require the same duration

        self.actions = []
        for i in range(len(skill_order)):
            self.actions.append(Action(self, i, len(skill_order)-1, skill_order[i]))
        
        # !TODO
        # Does it make sense to consider different durations for each action?
        # self.actions_durations = []
    
    def __str__(self):
        return '--- TASK ' + str(self._id) + ' ---\n' + \
               'Actions:\n' + '\n'.join(list(map(str, self.actions))) + '\n' \
               'Duration: ' + str(self.action_duration) + '\n'


class Action:
    def __init__(self, parent, _id = -1, total_acts = -1, skill = -1):
        self.parent = parent
        self._id = _id
        self.total_acts = total_acts
        self.skill = skill
        self.duration = parent.action_duration
    
    def __str__(self):
        return ''.join(['< Action ', str(self._id), '/', str(self.total_acts), \
                        ', Skill: ', str(self.skill), \
                        ', Duration: ', str(self.duration), ' >'])
