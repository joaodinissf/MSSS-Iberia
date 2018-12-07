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
    lam_learn = 0.5
    lam_motiv = 0.5
    mu_learn = 0.5
    mu_motiv = 0.5
    th_e = 0.6
    th_m = 0.6
    # !TODO Are these max values right?
    max_e = 1
    max_m = 1
    excite = .1
    inhibit = .1

    time = 0

    # ---------- INITIALISATION  ----------

    def __init__(self, file=None):
        # Create an empty workplace
        self.agents = []
        self.completed_tasks = []
        self.current_task = None
        self.tasks = []
        self.time = 0
        self.timeline = Timeline() # list of TimePoints
        self.allocation_times = {}

        if file:
            print("Reading from input file " + file + "...\n")
            self.parse_json(file)

    # !TODO
    # Validate...
    # def __eq__(self, other):
    #     return self.agents == other.agents and \
    #             self.tasks == other.tasks

    def parse_json(self, filename):
        with open(filename) as f:
            data = json.load(f)
        for idx, agent in enumerate(data['agents']):
            self.add_agent(idx, agent)
        for idx, task in enumerate(data['tasks']):
            self.add_task(idx, task)

    def add_agent(self, idx, agent):
        skills = [Skill(_id = skill['id'],
                        exp = skill['exp'],
                        mot = skill['mot'])
                  for skill in agent['skillset']]
        self.agents.append(Agent(_id = idx, skillset = skills))

    def add_task(self, idx, task):
        self.tasks.append(Task(_id = idx, json_task_precedence = task))
    
    # ---------- TASK PROCESSING ----------

    # !TODO - Can we make this smarter?
    def process_tasks(self):
        # While there is work to do...
        while len(self.tasks) > 0:
            # Tasks are handled one at a time
            self.current_task = self.tasks.pop(0)

            self.process_current_task()
            
            print('Processed task:\n' + str(self.current_task) + ':\n')

            self.completed_tasks.append(self.current_task)
            self.current_task = None

    def process_current_task(self):
        for prec in self.current_task.precedence:
            # ~ HOUSEKEEPING ~
            for agent in self.agents:
                # Clear current_action, update action_history
                agent.action_history.extend(agent.current_action)
                agent.current_action = []
                # Clear short-term memory, restore these skills to long-term memory
                agent.ltm = agent.skillset
                agent.stm = []
            # ~ END HOUSEKEEPING ~

            # Assign agents to each of the channels in this layer of precedence
            assignments, allocation_times, \
            skill_ids, channel_ids, action_ids = zip(*[self.choose_agent(channel) for channel in prec['channels'] \
                                                     if channel['actions'][0]['completion'] < channel['actions'][0]['duration']])
            self.allocation_times[self.time] = sum(allocation_times)
            
            # ~ HOUSEKEEPING ~
            # Update short/long-term memories
            for agent in self.agents:
                promote_to_stm = sorted(set([skill_ids[i] for i, a in enumerate(assignments) if a == agent._id]), \
                                        reverse=True)
                
                agent.stm.append = [agent.ltm.pop(s_id) for s_id in promote_to_stm]
            
            # Update expertise and motivation
            for agent in self.agents:
                # Learn
                for skill in agent.stm:
                    skill.expertise = skill.expertise + lam_learn * ( (max_e - skill.expertise) / max_e)
                    skill.motivation = skill.motivation + lam_motiv * ( (max_m - skill.motivation) / max_m)
                # Forget
                for skill in agent.ltm:
                    skill.expertise = ((skill.expertise - mu_learn) * max_e) / (max_e - mu_learn)
                    skill.motivation = ((skill.motivation - mu_learn) * max_m) / (max_m - mu_motiv)

            # Update current actions for all agents
            for i, assignment in enumerate(assignments):
                self.agents[assignment].current_action.append(
                    {
                        'task': self.current_task._id,
                        'precedence': prec._id,
                        'channel': channel_ids[i],
                        'action': action_ids[i],
                        'start_time': self.time
                    }
                )
            
            # Update timeline
            for agent in agents:
                for action in agent.current_action:
                    self.timeline.add_event(Event(start_time = action['start_time'], \
                                                  duration = 1, # Fixed, for now
                                                  task = self.current_task._id, \
                                                  action = action._id, \
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

    # !TODO Update expertise, motivation
    # Returns tuple containing (agent, allocation_time)
    def choose_agent(self, channel):
        # We are working with only two agents for now
        # We also assume that there is only one action per channel

        action = [action_list[0] for action_list in channel]
        
        # Get manageable names for agents' expertises
        e1 = self.agents[0].skillset[action['action_id']].expertise
        m1 = self.agents[0].skillset[action['action_id']].motivation

        e2 = self.agents[1].skillset[action['action_id']].expertise
        m2 = self.agents[1].skillset[action['action_id']].motivation

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

        # BEGIN NEGOTIATION PROCESS
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
        
        # The agent that will perform this action has been determined
        agent = 0 if i1 > you1 else 1

        # Update progress of one time unit
        action['completion'] += 1
        
        return (agent, allocation_time, action['skill']), channel['channel_id'], action['action_id']

        '''
        # print('~~~ Who does? ~~~')
        # print([i1, you1, i2, you2])
        # input()

        # if i1 > you1:
        #     print('I1 does!')
        #     self.timeline.append(TimePoint(self.time, action.duration, action, self.agents[0]))
        #     self.agents[0].current_action = action
        #     self.agents[0].action_history.append(action)
        # else:
        #     print('I2 does!')
        #     self.timeline.append(TimePoint(self.time, action.duration, action, self.agents[1]))
        #     self.agents[0].current_action = action
        #     self.agents[1].action_history.append(action)
        '''

    # ---------- PRINTING ----------

    def print_history(self):
        for i in range(len(self.timeline)):
            print('--- Time Point ' + str(i) + ' ---')
            print(self.timeline.events[i])

    def agents_string(self):
        return 'Agents:\n' + '\n'.join(list(map(str, self.agents)))
    
    def tasks_string(self):
        return 'TASKS:\n\n' + '\n'.join(list(map(str, self.tasks)))

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
        for task in self.tasks:
            print(task)

        # Print Agents: List, Current Engagement...
        print("Currently employed agents:")
        for agent in self.agents:
            print(agent)

        # Print history of completed actions
        print("History:")
        self.timeline.plot_gantt()
