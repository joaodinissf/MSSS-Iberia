import numpy as np
import json
import matplotlib.pyplot as plt
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

from skill import Skill
from agent import Agent
from task import Task
from timeline import Timeline, Event

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

        # DEFAULT PARAMETERS
        self.task_unit_duration = 10
        self.alpha_e = 0.5
        self.alpha_m = 0.5
        self.alpha_h = 0
        self.lam_learn = 1
        self.lam_motiv = 0
        self.mu_learn = .5
        self.mu_motiv = 0
        self.th_e = 10
        self.th_m = 10
        self.max_e = 25
        self.max_m = 25
        self.excite = .1
        self.inhibit = .1

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
        if len(data['parameters']) == 
        self.import_parameters(data['parameters'])

    def add_agent(self, idx, agent):
        skills = [Skill(_id = skill['id'],
                        exp = skill['exp'],
                        mot = skill['mot'])
                  for skill in agent['skillset']]
        self.agents.append(Agent(_id = idx, skillset = skills))

    def add_task(self, idx, task):
        self.tasks_todo.append(Task(_id = idx, json_task_precedence = task))
    
    def import_parameters(self, params):
        self.task_unit_duration = params['task_unit_duration']
        self.alpha_e = params['alpha_e']
        self.alpha_m = params['alpha_m']
        self.alpha_h = params['alpha_h']
        self.lam_learn = params['lam_learn']
        self.lam_motiv = params['lam_motiv']
        self.mu_learn = params['mu_learn']
        self.mu_motiv = params['mu_motiv']
        self.th_e = params['th_e']
        self.th_m = params['th_m']
        self.max_e = params['max_e']
        self.max_m = params['max_m']
        self.excite = params['excite']
        self.inhibit = params['inhibit']

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
        for prec in self.current_task.precedence:
            while True:
                # ~ HOUSEKEEPING ~
                for agent in self.agents:
                    # Clear current_action, update action_history
                    agent.action_history.extend(agent.current_action)
                    agent.current_action = []                
                # ~ END HOUSEKEEPING ~

                # Assign agents to each of the channels in this layer of precedence
                actions_to_process = [self.choose_agent(channel) for channel in prec['channels'] \
                    if channel['actions'][0]['completion'] < channel['actions'][0]['duration']]
                
                if len(actions_to_process) == 0:
                    break

                assignments, allocation_times, skill_ids, channel_ids, action_ids = zip(*actions_to_process)
                self.coordination_times[self.time] = sum(allocation_times)
                
                # DOING
                t_perfs = [agent.calculate_performance_time(self, skill_ids, assignments, self.time) for agent in self.agents]
                self.Tperf[self.time] = max(t_perfs) + self.coordination_times[self.time]
                
                # ~ HOUSEKEEPING ~
                # Update short/long-term memories
                for agent in self.agents:
                    # Clear short-term memory, restore these skills to long-term memory
                    agent.ltm = agent.skillset.copy()
                    
                    promote_to_stm = list(set([skill_ids[i] for i, a in enumerate(assignments) if a == agent._id]))
                    
                    agent.stm = [agent.ltm[i] for i in promote_to_stm]
                    
                    for i in promote_to_stm[::-1]:
                        del agent.ltm[i]
                
                # Update expertise and motivation
                for agent in self.agents:
                    # Learn
                    for skill in agent.stm:
                        new_exp = skill.expertise[-1] + self.lam_learn * ( (self.max_e - skill.expertise[-1]) / self.max_e)
                        new_mot = skill.motivation[-1] + self.lam_motiv * ( (self.max_m - skill.motivation[-1]) / self.max_m)
                        skill.expertise.append(new_exp)
                        skill.motivation.append(new_mot)

                    # Forget
                    for skill in agent.ltm:
                        new_exp = ((skill.expertise[-1] - self.mu_learn) * self.max_e) / (self.max_e - self.mu_learn)
                        new_mot = ((skill.motivation[-1] - self.mu_learn) * self.max_m) / (self.max_m - self.mu_motiv)
                        skill.expertise.append(new_exp)
                        skill.motivation.append(new_mot)

                # Update current actions for all agents
                for i, assignment in enumerate(assignments):
                    self.agents[assignment].current_action.append(
                        {
                            'task': self.current_task._id,
                            'precedence': prec['precedence_id'],
                            'channel': channel_ids[i],
                            'action': action_ids[i],
                            'start_time': self.time
                        }
                    )
                
                # Update timeline
                for agent in self.agents:
                    for action in agent.current_action:
                        self.timeline.add_event(Event(start_time = action['start_time'], \
                                                    duration = 1, # Fixed, for now
                                                    task = self.current_task._id, \
                                                    action = action['action'], \
                                                    agent = agent._id, \
                                                    ))

                # ~ END HOUSEKEEPING ~

                self.time += 1
        
        '''
        ORIGINAL (MORE VERSATILE, INCOMPLETE)
        # channels_done = 0
        # while channels_done < len(prec['channels']):
            # Allocation of channels within precedence
            # !TODO
            # This can be done better (more fairly) with a matrix...
            # Go over preferences in order of intensity

            # Execution of actions within channel
            # TODO - boost active (stm) skills in all working agents...
        '''

    # Returns tuple containing (agent, allocation_time)
    def choose_agent(self, channel):
        # We are working with only two agents for now
        # We also assume that there is only one action per channel

        action = channel['actions'][0]
        
        # Get manageable names for agents' expertises
        e1 = self.agents[0].skillset[action['skill']].expertise[-1]
        m1 = self.agents[0].skillset[action['skill']].motivation[-1]

        e2 = self.agents[1].skillset[action['skill']].expertise[-1]
        m2 = self.agents[1].skillset[action['skill']].motivation[-1]

        # AGENT 1
        # Situation 1 - insufficient expertise
        if e1 < self.th_e:
            i1 = 0
            you1 = 1
        # Situation 2 - Sufficient expertise, sufficient motivation
        elif m1 >= self.th_m:
            i1 = self.alpha_e * (e1 - self.th_e) / (self.max_e - self.th_e) + \
                 self.alpha_m * (m1 - self.th_m) / (self.max_m - self.th_m)
            you1 = 0
        # Situation 3 - Sufficient expertise, insufficient motivation
        else:
            i1 = self.alpha_e * (e1 - self.th_e) / (self.max_e - self.th_e)
            you1 = self.alpha_m * (self.th_m - m1) / self.th_m

        # AGENT 2
        # Situation 2 - insufficient expertise
        if e2 < self.th_e:
            i2 = 0
            you2 = 1
        # Situation 2 - Sufficient expertise, sufficient motivation
        elif m2 >= self.th_m:
            i2 = self.alpha_e * (e2 - self.th_e) / (self.max_e - self.th_e) + \
                 self.alpha_m * (m2 - self.th_m) / (self.max_m - self.th_m)
            you2 = 0
        # Situation 3 - Sufficient expertise, insufficient motivation
        else:
            i2 = self.alpha_e * (e2 - self.th_e) / (self.max_e - self.th_e)
            you2 = self.alpha_m * (self.th_m - m2) / self.th_m

        # BEGIN NEGOTIATION PROCESS
        allocation_time = 1
        while i1 > you1 and i2 > you2 or \
              you1 > i1 and you2 > i2:

            diff_i = abs(i1 - i2)
            diff_you = abs(you1 - you2)

            prev_i1, prev_i2, prev_you1, prev_you2 = i1, i2, you1, you2

            # Update 1
            i1 -= self.inhibit * prev_i1 * prev_i2 * diff_i
            you1 -= self.inhibit * prev_you1 * prev_you2 * diff_you
            you1 += self.excite * (1 - prev_you2) * prev_i1 * diff_i
            i1 += self.excite * prev_you1 * (1 - prev_i2) * diff_you

            # Update 2
            i2 -= self.inhibit * prev_i1 * prev_i2 * diff_i
            you2 -= self.inhibit * prev_you1 * prev_you2 * diff_you
            you2 += self.excite * (1 - prev_you2) * prev_i1 * diff_i
            i2 += self.excite * prev_you1 * (1 - prev_i2) * diff_you
            
            allocation_time += 1
            if allocation_time >= 1000:
                if np.random.randint(0, 2):
                    i1, you1, i2, you2 = 1, 0, 0, 1
                else:
                    i1, you1, i2, you2 = 0, 1, 1, 0
                break
        
        # The agent that will perform this action has been determined
        agent = 0 if i1 > you1 else 1

        # Update progress of one time unit
        action['completion'] += 1
        
        return (agent, allocation_time, action['skill'], channel['channel_id'], action['action_id'])

    # ---------- PRINTING ----------
    
    def plot_skills(self, agent):
        # y = {}

        # for i, skill in enumerate(agent.skillset):
        #     y[i] = skill.expertise
        
        # x = range(len(y[0]))
        # for i in range(len(y[0])):
        #     plt.plot(x, y(i))

        y1 = np.round(np.array(agent.skillset[0].expertise))
        y2 = np.round(np.array(agent.skillset[1].expertise))
        x = np.round(np.array(list(range(len(y1)))))

        # plt.plot(x, y1, x, y2)

        # plt.show()

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
        # y = {}

        # for i, skill in enumerate(agent.skillset):
        #     y[i] = skill.expertise
        
        # x = range(len(y[0]))
        # for i in range(len(y[0])):
        #     plt.plot(x, y(i))

        y = []
        y.append(np.round(np.array(list(self.Tperf.values()))))
        y.append(np.round(np.array(list(self.coordination_times.values()))))
        y.append(np.round(np.array(list(self.agents[0].performance_times.values()))))
        y.append(np.round(np.array(list(self.agents[1].performance_times.values()))))

        x = np.array(list(range(len(y[0]))))

        # plt.plot(x, y1, x, y2)

        # plt.show()

        data = [
                go.Scatter(
                    x = x,
                    y = _y,
                    mode = 'markers'
                ) for _y in y
               ]

        iplot(data)
        

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
