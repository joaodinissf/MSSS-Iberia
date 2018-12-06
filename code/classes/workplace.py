import numpy as np
import json
from skill import Skill
from agent import Agent
from task import Task
from timeline import Timeline

# Useful if you need to print JSON:
# from pprint import pprint

class Workplace:
    # CONSTANTS
    l = 0.5
    th_e = 0.6
    th_m = 0.6
    # !TODO Are these max values right?
    max_e = 1
    max_m = 1
    excite = .1
    inhibit = .1

    time = 0

    def __init__(self, file=None):
        # Create an empty workplace
        self.agents = []
        self.completed_tasks = []
        self.current_task = None
        self.tasks = []
        self.timeline = Timeline # list of TimePoints

        if file:
            print("Reading from input file " + file + "...")
            self.parse_json(file)

    # !TODO
    # Validate...
    def __eq__(self, other):
        return self.agents == other.agents and \
                self.tasks == other.tasks

    def parse_json(self, filename):
        with open(filename) as f:
            data = json.load(f)
        for idx, agent in enumerate(data['agents']):
            self.add_agent(idx, agent)
        for idx, task in enumerate(data['tasks']):
            self.add_task(idx, task)

    def add_agent(self, idx, agent):
        skills = [lambda skill : Skill(_id = agent.skillset['id'],
                                       exp = agent.skillset['exp'],
                                       mot = agent.skillset['mot'])
                  for skill in agent['skillset']]
        self.agents.append(Agent(_id = idx, skillset = skills))

    def add_task(self, idx, task):
        self.tasks.append(Task(_id = idx, json_task_precedence = task))

    # !TODO Update expertise, motivation
    def choose_agent(self, action):
        # We are working with only two agents for now
        
        # Get manageable names for agents' expertises
        e1 = self.agents[0].skillset[action._id].expertise
        m1 = self.agents[0].skillset[action._id].motivation
        e2 = self.agents[1].skillset[action._id].expertise
        m2 = self.agents[1].skillset[action._id].motivation

        # AGENT 1
        # Situation 1 - insufficient expertise
        if e1 < Workplace.th_e:
            i1 = 0
            you1 = 1
        # Situation 2 - Sufficient expertise, sufficient motivation
        elif m1 >= Workplace.th_m:
            i1 = Workplace.l * (e1 - Workplace.th_e) / (Workplace.max_e - Workplace.th_e) + \
                 (1 - Workplace.l) * (m1 - Workplace.th_m) / (Workplace.max_m - Workplace.th_m)
            you1 = 0
        # Situation 3 - Sufficient expertise, insufficient motivation
        else:
            i1 = Workplace.l * (e1 - Workplace.th_e) / (Workplace.max_e - Workplace.th_e)
            you1 = (1 - Workplace.l) * (Workplace.th_m - m1) / Workplace.th_m

        # AGENT 2
        # Situation 2 - insufficient expertise
        if e2 < Workplace.th_e:
            i2 = 0
            you2 = 1
        # Situation 2 - Sufficient expertise, sufficient motivation
        elif m2 >= Workplace.th_m:
            i2 = Workplace.l * (e2 - Workplace.th_e) / (Workplace.max_e - Workplace.th_e) + \
                 (1 - Workplace.l) * (m2 - Workplace.th_m) / (Workplace.max_m - Workplace.th_m)
            you2 = 0
        # Situation 3 - Sufficient expertise, insufficient motivation
        else:
            i2 = Workplace.l * (e2 - Workplace.th_e) / (Workplace.max_e - Workplace.th_e)
            you2 = (1 - Workplace.l) * (Workplace.th_m - m2) / Workplace.th_m

        allocation_time = 1

        while i1 > you1 and i2 > you2 or \
              you1 > i1 and you2 > i2:
            
            diff_i = abs(i1 - i2)
            diff_you = abs(you1 - you2)

            prev_i1, prev_i2, prev_you1, prev_you2 = i1, i2, you1, you2

            # Update 1
            i1 -= Workplace.inhibit * prev_i1 * prev_i2 * diff_i
            you1 -= Workplace.inhibit * prev_you1 * prev_you2 * diff_you
            you1 += Workplace.excite * (1 - prev_you2) * prev_i1 * diff_i
            i1 += Workplace.excite * prev_you1 * (1 - prev_i2) * diff_you

            # Update 2
            i2 -= Workplace.inhibit * prev_i1 * prev_i2 * diff_i
            you2 -= Workplace.inhibit * prev_you1 * prev_you2 * diff_you
            you2 += Workplace.excite * (1 - prev_you2) * prev_i1 * diff_i
            i2 += Workplace.excite * prev_you1 * (1 - prev_i2) * diff_you
            
            allocation_time += 1
            if allocation_time >= 1000:
                if np.random.randint(0, 2):
                    i1, you1, i2, you2 = 1, 0, 0, 1
                else:
                    i1, you1, i2, you2 = 0, 1, 1, 0
                break
        
        print('~~~ Who does? ~~~')
        print([i1, you1, i2, you2])
        input()

        if i1 > you1:
            print('I1 does!')
            self.timeline.append(TimePoint(self.time, action.duration, action, self.agents[0]))
            self.agents[0].current_action = action
            self.agents[0].action_history.append(action)
        else:
            print('I2 does!')
            self.timeline.append(TimePoint(self.time, action.duration, action, self.agents[1]))
            self.agents[0].current_action = action
            self.agents[1].action_history.append(action)

        self.time += action.duration
    

    # !TODO
    # Can we make this smarter?
    def process_tasks(self):
        while len(self.tasks) > 0:
            # Handle one task at a time
            self.current_task = self.tasks.pop(0)

            self.process_current_task()
            
            print('Processed task:\n' + str(self.current_task) + ':\n')
            
            # For debugging purposes:
            print('Current state:')
            print(self)

            self.completed_tasks.append(self.current_task)
            self.current_task = None

    def process_current_task(self):
        for action in self.current_task.actions:
            self.choose_agent(action)

    # ---------- PRINTING ----------

    def print_history(self):
        for i in range(len(self.timeline)):
            print('--- Time Point ' + str(i) + ' ---')
            print(self.timeline[i])

    def agents_string(self):
        return 'Agents:\n' + '\n'.join(list(map(str, self.agents)))
    
    def tasks_string(self):
        return 'TASKS:\n\n' + '\n'.join(list(map(str, self.tasks)))

    def __str__(self):
        # Print time stamp
        print("Time elapsed:")
        print(self.time, end='')
        print(" time units.")
        
        # !TODO
        # Print Tasks: Completed, Current, To-Do
        print("Completed tasks:")
        for task in self.completed_tasks:
            print(task)        

        print("Current task:")
        print(self.current_task)

        print("Future tasks:")
        for task in self.tasks:
            print(task)

        # !TODO
        # Print Agents: List, Current Engagement...
        print("Currently employed agents:")
        for agent in self.agents:
            print(agent)

        # !TODO
        # Print history of completed actions
        print(self.timeline)
