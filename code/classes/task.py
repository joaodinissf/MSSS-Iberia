# "A task consists of actions in such a way that for every action \
# exactly one skill is required to perform this action."

class Action:
    def __init__(self, _id, skill_id, duration, completion):
        self._id = _id
        self.skill_id = skill_id
        self.duration = duration
        self.completion = completion

class Task:
    def __init__(self, _id = -1, json_task = None):
		# json_task is the task as loaded directly from the input json file
        self._id = _id

        self.actions = [Action(action['id'], action['skill_id'], action['duration'], 0)
                        for action in json_task['actions']] if json_task != None else []

    def __str__(self):
        actions_str = ''
        for action in self.actions:
            actions_str += '\tAction ' + str(action._id) + \
                            ' | Skill ID ' + str(action.skill_id) + \
                            ' | Duration ' + str(action.duration) + \
                            ' | Completion ' + str(action.completion) + '\n'

        return '--- TASK ' + str(self._id) + ' ---\n' + actions_str
