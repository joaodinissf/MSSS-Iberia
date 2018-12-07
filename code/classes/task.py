# "A task consists of actions in such a way that for every action exactly one skill is required to perform this action."

# class Task:
#     def __init__(self, _id = -1, skill_ids = [], channel = [], precedence = [], duration = []):
#         # Ensure that the provided list is coherent
#         try:
#             assert(len(skill_ids) == len(channel) == len(precedence) == len(duration))
#         except AssertionError:
#             print("Incoherent skill_ids / channel / precedence / duration provided!")
#         except:
#             print("Error initialising task!")
#         self._id = _id
#         # Sort precedence array, get back the permutation as a list
#         perm, self.precedence = map(list, zip(*sorted(enumerate(precedence), key=lambda x: x[1])))
#         # Preserve sorting order, apply same permutation to skill_ids, channel and duration
#         self.skill_ids = [skill_ids[i] for i in perm]
#         self.channel = [channel[i] for i in perm]
#         self.duration = [duration[i] for i in perm]
#         # tasks -> precedence -> channels -> actions
    
class Task:
    # Do we require some sort of task_metadata?
    def __init__(self, _id = -1, json_task_precedence = None):
        self._id = _id
        self.precedence = [] if json_task_precedence == None \
                             else json_task_precedence['precedence']

        if self.precedence != []:
            for prec in self.precedence:
                for channel in prec['channels']:
                    for action in channel['actions']:
                        action['completion'] = 0

        # TODO
        # Ensure that the provided file is valid
        #validate_precedences()

    def __str__(self):
        actions_str = ''
        for prec in self.precedence:
            actions_str += 'Precedence ' + str(prec['precedence_id']) + '\n'
            for channel in prec['channels']:
                actions_str += '\tChannel ' + str(channel['channel_id']) + '\n'
                for action in channel['actions']:
                    actions_str += '\t\tAction ' + str(action['action_id']) + \
                                   ' | Skill ' + str(action['skill']) + \
                                   ' | Duration ' + str(action['duration']) + '\n'
        
        return '--- TASK ' + str(self._id) + ' ---\n' + actions_str
