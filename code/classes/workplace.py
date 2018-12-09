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
        
        mbti = agent['mbti'] if 'mbti' in agent else None
        initial_frustration = agent['initial_frustration'] if 'initial_frustration' in agent else None
        
        self.agents.append(Agent(_id = idx, mbti = mbti,
                                 initial_frustration = initial_frustration,
                                 skillset = skills))

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
        if 'beta' in params:
            P.BETA = params['beta']
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
        if 'max_h' in params:
            P.MAX_H = params['max_h']
        if 'excite' in params:
            P.EXCITE = params['excite']
        if 'inhibit' in params:
            P.INHIBIT = params['inhibit']

        # Normalise alphas
        if P.ALPHA_E + P.ALPHA_H + P.ALPHA_M != 1:
            factor = 1 / (P.ALPHA_E + P.ALPHA_H + P.ALPHA_M)
            P.ALPHA_E *= factor
            P.ALPHA_H *= factor
            P.ALPHA_M *= factor

    # ---------- TASK PROCESSING ----------

    # !TODO - Can we make this smarter?
    def process_tasks(self):
        # While there is work to do...
        while len(self.tasks_todo) > 0:
            # Tasks are handled one at a time
            self.current_task = self.tasks_todo.pop(0)

            self.process_current_task()
            
            print('Processed task:\n' + str(self.current_task) + '\n')

            self.completed_tasks.append(self.current_task)
            self.current_task = None

    def process_current_task(self):
        # Repeat action assignment until all actions have been completed
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
                agent.flush_prev_act(assignments, skill_ids)            # Clear internal variables related to previous task                
                agent.update_memory()                                   # Update expertise and motivation

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
                                                duration = 1,                       # Constant, for now
                                                task_id = self.current_task._id, \
                                                action_id = action_ids[i], \
                                                agent_id = assignment, \
                                                ))
            
            # ~ END HOUSEKEEPING ~

            self.time += 1
    
    # ---------- GETTERS ----------

    def get_sum_perf_time(self):
        return sum(self.Tperf.values())

    # ---------- PRINTING ----------
    
    def plot_skills(self, agent):
        y1 = np.round(np.array(agent.skillset[0].expertise))
        y2 = np.round(np.array(agent.skillset[1].expertise))
        x = np.round(np.array(list(range(len(y1)))))

        y1 = [y if y > 0 else 0 for y in y1]
        y2 = [y if y > 0 else 0 for y in y2]

        trace1 = go.Scatter(
            x = x,
            y = y1,
            mode = 'lines+markers',
            name = 'Skill 1'
        )

        trace2 = go.Scatter(
            x = x,
            y = y2,
            mode = 'lines+markers',
            name = 'Skill 2'
        )

        layout = go.Layout(
            xaxis=dict(
                title='Cycles',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=24,
                    color='black'
                )
            ),
            yaxis=dict(
                title='Expertise',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=24,
                    color='black'
                )
            )
        )

        data = [trace1, trace2]

        fig = go.Figure(data=data, layout=layout)

        iplot(fig)

    def plot_frustration(self):
        y0 = np.array(self.agents[0].frustration)
        y1 = np.array(self.agents[1].frustration)
        x = np.array(list(range(len(y1))))

        trace1 = go.Scatter(
            x = x,
            y = y0,
            mode = 'lines+markers',
            name = 'Agent 1'
        )

        trace2 = go.Scatter(
            x = x,
            y = y1,
            mode = 'lines+markers',
            name = 'Agent 2'
        )

        layout = go.Layout(
            xaxis=dict(
                title='Cycles',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=24,
                    color='black'
                )
            ),
            yaxis=dict(
                title='Frustration',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=24,
                    color='black'
                )
            ),
            showlegend=True
        )

        data = [trace1, trace2]

        fig = go.Figure(data=data, layout=layout)

        iplot(fig)

    def plot_allocations(self):
        y0 = np.array(self.agents[0].allocation_times)
        y1 = np.array(self.agents[1].allocation_times)
        x = np.array(list(range(len(y1))))

        # y1 = [y if y > 0 else 0 for y in y1]
        # y2 = [y if y > 0 else 0 for y in y2]

        trace1 = go.Scatter(
            x = x,
            y = y0,
            mode = 'lines+markers',
            name = 'Agent 1'
        )

        trace2 = go.Scatter(
            x = x,
            y = y1,
            mode = 'lines+markers',
            name = 'Agent 2'
        )

        layout = go.Layout(
            xaxis=dict(
                title='Cycles',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=24,
                    color='black'
                )
            ),
            yaxis=dict(
                title='Allocation time',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=24,
                    color='black'
                )
            )
        )

        data = [trace1, trace2]

        fig = go.Figure(data=data, layout=layout)

        iplot(fig)

    def plot_performance(self):
        y = []
        y.append(np.round(np.array(list(self.Tperf.values()))))
        y.append(np.round(np.array(list(self.coordination_times.values()))))
        y.append(np.round(np.array(list(self.agents[0].performance_times.values()))))
        y.append(np.round(np.array(list(self.agents[1].performance_times.values()))))

        for _y in y:
            _y = [y if y > 0 else 0 for y in _y]

        x = np.array(list(range(len(y[0]))))

        names = [
            'System',
            'Coordination Time',
            'Agent 1',
            'Agent 2'
        ]

        data = [
                go.Scatter(
                    x = x,
                    y = _y,
                    mode = 'lines+markers',
                    name = names[i]
                ) for i, _y in enumerate(y)
               ]

        layout = go.Layout(
            xaxis=dict(
                title='Cycles',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=24,
                    color='black'
                )
            ),
            yaxis=dict(
                title='Performance Time',
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=24,
                    color='black'
                )
            )
        )

        fig = go.Figure(data=data, layout=layout)
        iplot(fig)

    def print_parameters(self):
        print('task_unit_duration: ' + str(P.TASK_UNIT_DURATION))
        print('alpha_e: ' + str(P.ALPHA_E))
        print('alpha_m: ' + str(P.ALPHA_M))
        print('alpha_h: ' + str(P.ALPHA_H))
        print('beta: ' + str(P.BETA))
        print('lam_learn: ' + str(P.LAM_LEARN))
        print('lam_motiv: ' + str(P.LAM_MOTIV))
        print('mu_learn: ' + str(P.MU_LEARN))
        print('mu_motiv: ' + str(P.MU_MOTIV))
        print('th_e: ' + str(P.TH_E))
        print('th_m: ' + str(P.TH_M))
        print('max_e: ' + str(P.MAX_E))
        print('max_m: ' + str(P.MAX_M))
        print('max_h: ' + str(P.MAX_H))
        print('excite: ' + str(P.EXCITE))
        print('inhibit: ' + str(P.INHIBIT))

        print('\n')

        print('Maximum number of steps in coordination:' + str(P.MAX_COORD_STEPS))
        
        print('\n')
        
        # TODO - This can be made prettier
        mbti_types = ['ESTJ', 'ESTP', 'ESFJ', 'ESFP', 'ENTJ', 'ENTP', 'ENFJ', 'ENFP', 'ISTJ', 'ISTP', 'ISFJ', 'ISFP', 'INTJ', 'INTP', 'INFJ', 'INFP']

        print('MBTI Matrix:')
        print('\t'.join(mbti_types))
        for i in range(len(mbti_types)):
            print(mbti_types[i] + '\t')
            for j in range(len(mbti_types)):
                print(P.MBTI[i][j], end='\t')

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
