import numpy as np
import json
import matplotlib.pyplot as plt
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

from skill import Skill
from agent import Agent, choose_agent
from task import Task
from timeline import Timeline, Event
import PARAMETERS as P

# Useful if you need to print JSON:
# from pprint import pprint

class Workplace:
    # ---------- INITIALISATION  ----------

    def __init__(self, file=None):
        # Create an empty workplace
        self.agents = []
        self.completed_tasks = []
        self.current_task = None
        self.tasks_todo = []
        self.time = 0
        self.timeline = Timeline() # list of TimePoints
        self.coordination_times = {}
        self.Tperf = {}

        if file:
            print("Reading from input file " + file + "...\n")
            self.parse_json(file)

    def parse_json(self, filename):
        with open(filename) as f:
            data = json.load(f)
        for idx, agent in enumerate(data['agents']):
            self.add_agent(idx, agent)
        for idx, task in enumerate(data['tasks']):
            self.add_task(idx, task)
        
        self.import_parameters(data['parameters'])

    def add_agent(self, idx, agent):
        skills = [Skill(_id = skill['id'],
                        exp = skill['exp'],
                        mot = skill['mot'])
                  for skill in agent['skillset']]
        self.agents.append(Agent(_id = idx, skillset = skills))

    def add_task(self, idx, task):
        self.tasks_todo.append(Task(_id = idx, json_task = task))
    
    def import_parameters(self, params):
        if 'task_unit_duration' in params:
            P.TASK_UNIT_DURATION = params['task_unit_duration']
        if 'alpha_e' in params:
            P.ALPHA_E = params['alpha_e']
        if 'alpha_m' in params:
            P.ALPHA_M = params['alpha_m']
        if 'alpha_h' in params:
            P.ALPHA_H = params['alpha_h']
        if 'lam_learn' in params:
            P.LAM_LEARN = params['lam_learn']
        if 'lam_motiv' in params:
            P.LAM_MOTIV = params['lam_motiv']
        if 'mu_learn' in params:
            P.MU_LEARN = params['mu_learn']
        if 'mu_motiv' in params:
            P.MU_MOTIV = params['mu_motiv']
        if 'th_e' in params:
            P.TH_E = params['th_e']
        if 'th_m' in params:
            P.TH_M = params['th_m']
        if 'max_e' in params:
            P.MAX_E = params['max_e']
        if 'max_m' in params:
            P.MAX_M = params['max_m']
        if 'excite' in params:
            P.EXCITE = params['excite']
        if 'inhibit' in params:
            P.INHIBIT = params['inhibit']

    # ---------- TASK PROCESSING ----------

    # !TODO - Can we make this smarter?
    def process_tasks(self):
        # While there is work to do...
        while len(self.tasks_todo) > 0:
            # Tasks are handled one at a time
            self.current_task = self.tasks_todo.pop(0)

            self.process_current_task()
            
            print('Processed task:\n' + str(self.current_task) + ':\n')

            self.completed_tasks.append(self.current_task)
            self.current_task = None

    def process_current_task(self):
        while True:
            # Assign agents to each of the actions
            actions_to_process = [choose_agent(self, action) for action in self.current_task.actions \
                                  if action.completion < action.duration]
            
            if len(actions_to_process) == 0:
                break

            assignments, allocation_times, skill_ids, action_ids = zip(*actions_to_process)
            self.coordination_times[self.time] = sum(allocation_times)

            t_perfs = [agent.calculate_performance_time(self, skill_ids, assignments, self.time)
                        for agent in self.agents]
            self.Tperf[self.time] = max(t_perfs) + self.coordination_times[self.time]
            
            # ~ HOUSEKEEPING ~
            for agent in self.agents:
                agent.flush_prev_act(assignments, skill_ids)    # Clear internal variables relating to previous task                
                agent.update_memory(self)                       # Update expertise and motivation

            # Update current actions for all agents
            for i, assignment in enumerate(assignments):
                self.agents[assignment].current_action.append(
                    {
                        'task': self.current_task._id,
                        'action': action_ids[i],
                        'start_time': self.time
                    }
                )

                self.timeline.add_event(Event(start_time = self.time, \
                                                duration = 1,                           # Constant, for now
                                                task_id = self.current_task._id, \
                                                action_id = action_ids[i], \
                                                agent_id = assignment, \
                                                ))
            
            # ~ END HOUSEKEEPING ~

            self.time += 1
    
    # ---------- PRINTING ----------
    
    def plot_skills(self, agent):
        y1 = np.round(np.array(agent.skillset[0].expertise))
        y2 = np.round(np.array(agent.skillset[1].expertise))
        x = np.round(np.array(list(range(len(y1)))))

        trace1 = go.Scatter(
            x = x,
            y = y1,
            mode = 'markers'
        )

        trace2 = go.Scatter(
            x = x,
            y = y2,
            mode = 'markers'
        )

        data = [trace1, trace2]
        iplot(data)

    def plot_performance(self):
        y = []
        y.append(np.round(np.array(list(self.Tperf.values()))))
        y.append(np.round(np.array(list(self.coordination_times.values()))))
        y.append(np.round(np.array(list(self.agents[0].performance_times.values()))))
        y.append(np.round(np.array(list(self.agents[1].performance_times.values()))))

        x = np.array(list(range(len(y[0]))))

        data = [
                go.Scatter(
                    x = x,
                    y = _y,
                    mode = 'markers'
                ) for _y in y
               ]

        iplot(data)

    def print_params(self):
        print('task_unit_duration: ' + str(P.TASK_UNIT_DURATION))
        print('alpha_e: ' + str(P.ALPHA_E))
        print('alpha_m: ' + str(P.ALPHA_M))
        print('alpha_h: ' + str(P.ALPHA_H))
        print('lam_learn: ' + str(P.LAM_LEARN))
        print('lam_motiv: ' + str(P.LAM_MOTIV))
        print('mu_learn: ' + str(P.MU_LEARN))
        print('mu_motiv: ' + str(P.MU_MOTIV))
        print('th_e: ' + str(P.TH_E))
        print('th_m: ' + str(P.TH_M))
        print('max_e: ' + str(P.MAX_E))
        print('max_m: ' + str(P.MAX_M))
        print('excite: ' + str(P.EXCITE))
        print('inhibit: ' + str(P.INHIBIT))

    def print_history(self):
        for i in range(len(self.timeline)):
            print('--- Time Point ' + str(i) + ' ---')
            print(self.timeline.events[i])

    def agents_string(self):
        return 'Agents:\n' + '\n'.join(list(map(str, self.agents)))
    
    def tasks_string(self):
        return 'TASKS:\n\n' + '\n'.join(list(map(str, self.tasks_todo)))

    def print_current_state(self):
        # Print time stamp
        print("Time elapsed:")
        print(self.time, end='')
        print(" time units.\n")
        
        # Print Tasks: Completed, Current, To-Do
        print("Completed tasks:")
        for task in self.completed_tasks:
            print(task)        

        print("Current task:")
        print(self.current_task)

        print("Future tasks:")
        for task in self.tasks_todo:
            print(task)

        # Print Agents: List, Current Engagement...
        print("Currently employed agents:")
        for agent in self.agents:
            print(agent)

        # Print history of completed actions
        print("History:")
        self.timeline.plot_gantt()
