# "A task consists of actions in such a way that for every action exactly one skill is required to perform this action."

class Task:
    def __init__(self, _id = -1, skill_ids = [], channel = [], precedence = [], duration = []):
        # Ensure that the provided list is coherent
        try:
            assert(len(skill_ids) == len(channel) == len(precedence) == len(duration))
        except AssertionError:
            print("Incoherent skill_ids / channel / precedence / duration provided!")
        except:
            print("Error initialising task!")

        self._id = _id

        # Sort precedence array, get back the permutation as a list
        perm, self.precedence = map(list, zip(*sorted(enumerate(precedence), key=lambda x: x[1])))

        # Preserve sorting order, apply same permutation to skill_ids, channel and duration
        self.skill_ids = [skill_ids[i] for i in perm]
        self.channel = [channel[i] for i in perm]
        self.duration = [duration[i] for i in perm]

        # tasks -> precedence -> channels -> actions
        
        
    
    def __str__(self):
        return '--- TASK ' + str(self._id) + ' ---\n' + \
               'Actions:\n' + '\n'.join(list(map(str, self.actions))) + '\n' \
               'Duration: ' + str(self.action_duration) + '\n'


class Action:
    def __init__(self, parent, _id = -1, skill = -1, action_duration = -1, channel = -1, precedence = -1):
        self.parent = parent
        self._id = _id
        self.total_acts = total_acts
        self.skill = skill
        self.duration = action_duration
        self.channel = channel
        self.precedence = precedence
    
    def __str__(self):
        return ''.join(['< Action ', str(self._id), '/', str(self.total_acts), \
                        ', Skill: ', str(self.skill), \
                        ', Duration: ', str(self.duration), ' >'])
