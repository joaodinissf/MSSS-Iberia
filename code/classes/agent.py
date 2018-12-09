import math
import numpy as np
import PARAMETERS as P

# TODO
# Agents should be initialised with an MBTI and an initial_frustration

class Agent:
    def __init__(self, _id, mbti = None, initial_frustration = None, skillset = []):
        self._id = _id
        self.mbti = '' if mbti == None else mbti

        self.skillset = sorted(skillset, key=lambda s: s._id)  # Ensure skills are stored in order
        self.frustration = [] if initial_frustration == None else [initial_frustration]

        self.allocation_times = []
        self.performance_times = {}

        # Agent Memory
        self.stm = []                    # Should be updated when task is allocated
        self.ltm = self.skillset.copy()  # Initially, all skills are part of the long-term memory

        self.current_action = []
        self.action_history = []

        self.validate_internals()

    # ---------- INTERNAL VALIDATION ----------

    def validate_internals(self):
        return \
        self.validate_frustration() and \
        self.validate_skillset() and \
        self.validate_mbti()
        # ...
    
    def validate_frustration(self):
        if self.frustration == []:
            print("Warning: no initial frustration provided!")
            return False
        return True

    # Sanity check - skills should be consecutive integers starting at zero
    def validate_skillset(self):
        try:
            assert [skill._id for skill in self.skillset] == list(range(len(self.skillset)))
        except AssertionError:
            print('Invalid skillset provided! Please verify the correctness of your input.')
            exit(1)

    # Validate MBTI
    # TODO Validate this funtion...
    def validate_mbti(self):
        if self.mbti == '':
            print("Warning: empty MBTI provided!")
            return False
        
        valid = True

        if len(self.mbti) != 4 or not isinstance(self.mbti, str):
            valid = False
        
        if self.mbti[0] not in ['E', 'I']:
            valid = False
        if self.mbti[1] not in ['N', 'S']:
            valid = False
        if self.mbti[2] not in ['T', 'F']:
            valid = False
        if self.mbti[3] not in ['J', 'P']:
            valid = False
        
        try:
            assert valid == True
        except:
            print('Invalid/incomplete MBTI provided!')
            exit(1)
        
        return valid

    # ---------- INTERNAL UPDATES ----------

    def calculate_performance_time(self, wp, skill_ids, assignments, time):
        self.performance_times[time] = sum(
            [
                P.TASK_UNIT_DURATION / ((P.ALPHA_E * self.get_latest_expertise(skill_ids[ix]) / P.MAX_E) +
                                        (P.ALPHA_M * self.get_latest_motivation(skill_ids[ix]) / P.MAX_M) +
                                        (P.ALPHA_H * self.get_frustration() / P.MAX_H))
                for ix, assignment in enumerate(assignments) if assignment == self._id
            ]
        )

        return self.performance_times[time]

    def update_frustration(self, immediate_frustration):
        if self.frustration == []:
            return
        
        # !TODO Justify this
        MOV_AVG_FACTOR = 0.8
        self.frustration.append(MOV_AVG_FACTOR * self.frustration[-1] + (1-MOV_AVG_FACTOR) * immediate_frustration)

    def update_memory(self):
        # Learn
        for skill in self.stm:
            new_exp = skill.expertise[-1] + P.LAM_LEARN * ( (P.MAX_E - skill.expertise[-1]) / P.MAX_E)
            new_mot = ((skill.motivation[-1] - P.MU_MOTIV) * P.MAX_M) / (P.MAX_M - P.MU_MOTIV)
            skill.expertise.append(new_exp)
            skill.motivation.append(new_mot)

        # Forget
        for skill in self.ltm:
            new_exp = ((skill.expertise[-1] - P.MU_LEARN) * P.MAX_E) / (P.MAX_E - P.MU_LEARN)
            new_mot = skill.motivation[-1] + P.LAM_MOTIV * ( (P.MAX_M - skill.motivation[-1]) / P.MAX_M)
            skill.expertise.append(new_exp)
            skill.motivation.append(new_mot)
    
    def insert_alloc_time(self, coord_time):
        self.allocation_times.append(coord_time)

    def flush_prev_act(self, assignments, skill_ids):
        # Clear current_action, update action_history
        self.action_history.extend(self.current_action)
        self.current_action = []
        
        # Clear short-term memory, restore these skills to long-term memory
        self.ltm = self.skillset.copy()
        
        promote_to_stm = list(set([skill_ids[i] for i, a in enumerate(assignments) if a == self._id]))
        self.stm = [self.ltm[i] for i in promote_to_stm]
        
        for i in promote_to_stm[::-1]:
            del self.ltm[i]

    # ---------- GETTERS ----------
    def get_latest_expertise(self, skill_id):
        return self.skillset[skill_id].expertise[-1]

    def get_latest_motivation(self, skill_id):
        return self.skillset[skill_id].motivation[-1]

    def get_frustration(self):
        return self.frustration[-1] if len(self.frustration) > 0 else -1
    
    def get_initial_i_you(self, wp, skill_id):
        # Determine current expertise and motivation for this skill
        exp = self.get_latest_expertise(skill_id)
        mot = self.get_latest_motivation(skill_id)

        # Should scale P.ALPHA_E, P.ALPHA_M locally
        # Normalise alphas
        factor = 1 / (P.ALPHA_E + P.ALPHA_M)    
        
        ALPHA_E = P.ALPHA_E * factor
        ALPHA_M = P.ALPHA_M * factor

        # Compute i, you
        # Situation 1 - insufficient expertise
        if exp < P.TH_E:
            i = 0
            you = 1
        # Situation 2 - Sufficient expertise, sufficient motivation
        elif mot >= P.TH_M:
            i = ALPHA_E * (exp - P.TH_E) / (P.MAX_E - P.TH_E) + \
                 ALPHA_M * (mot - P.TH_M) / (P.MAX_M - P.TH_M)
            you = 0
        # Situation 3 - Sufficient expertise, insufficient motivation
        else:
            i = ALPHA_E * (exp - P.TH_E) / (P.MAX_E - P.TH_E)
            you = ALPHA_M * (P.TH_M - mot) / P.TH_M
        
        return i, you

    def get_mbti_ix(self):
        ix = 0

        if self.mbti[0] == 'I':
            ix += 8
        
        if self.mbti[0] == 'N':
            ix += 4

        if self.mbti[0] == 'F':
            ix += 2

        if self.mbti[0] == 'P':
            ix += 1

        return ix

    # ---------- OUTPUT ----------
    # TODO - Update with MBTI / Frustration
    def __str__(self):
        stm_str = 'Short-term memory:\n' + '\n'.join(list(map(str, self.stm))) + '\n'
        ltm_str = 'Long-term memory:\n' + '\n'.join(list(map(str, self.ltm))) + '\n'

        curr_act_str = 'Current action:\n' + str(self.current_action) + '\n'
        act_hist_str = 'Action history:\n' + str(self.action_history) + '\n'
        
        return '--- AGENT ' + str(self._id) + ' ---\n' + stm_str + ltm_str + curr_act_str + act_hist_str

# Returns tuple containing:
# (assignments, allocation_times, skill_ids, action_ids)
def choose_agent(wp, action):
    # We are working with only two agents for now
    i0, you0 = wp.agents[0].get_initial_i_you(wp, action.skill_id)
    i1, you1 = wp.agents[1].get_initial_i_you(wp, action.skill_id)

    # frustration should be updated before their interaction
    f0, f1 = wp.agents[0].get_frustration(), wp.agents[1].get_frustration()
    
    # Begin negotiation process
    agent, allocation_time = negotiate(i0, you0, i1, you1,
                                       r_ij = get_relationship(wp.agents[0], wp.agents[1]),
                                       f0 = f0, f1 = f1)

    # Update each agent's internal tracking of allocation time
    wp.agents[0].insert_alloc_time(allocation_time)
    wp.agents[1].insert_alloc_time(allocation_time)

    # Calculate immediate frustration with information from latest interaction
    f0, f1 = calculate_immediate_frustration(wp.agents[0], wp.agents[1])
    wp.agents[0].update_frustration(f0)
    wp.agents[1].update_frustration(f1)
    
    # Update action progress by one cycle
    action.completion += 1
    
    return (agent, allocation_time, action.skill_id, action._id)

def negotiate(i0, you0, i1, you1, inhibit = P.INHIBIT, excite = P.EXCITE, r_ij = -1, f0 = -1, f1 = -1):
    # If parameters are not specified, they also hold no effect over the system
    if r_ij == -1 or f0 == -1 or f1 == -1:
        r_ij = 0.5
        f0 = 1
        f1 = 1

    allocation_time = 0

    # DEBUG
    # print([i0, you0, i1, you1])

    while (i0 > you0 and i1 > you1) or \
          (you0 > i0 and you1 > i1):

        diff_i = abs(i0 - i1)
        diff_you = abs(you0 - you1)

        prev_i0, prev_i1, prev_you0, prev_you1 = i0, i1, you0, you1

        # Update agent 0
        i0 -= inhibit * prev_i0 * prev_i1 * diff_i
        you0 -= inhibit * prev_you0 * prev_you1 * diff_you
        you0 += excite * (1 - prev_you0) * prev_i1 * diff_i
        i0 += excite * prev_you1 * (1 - prev_i0) * diff_you

        # Update agent 1
        i1 -= inhibit * prev_i0 * prev_i1 * diff_i
        you1 -= inhibit * prev_you0 * prev_you1 * diff_you
        you1 += excite * (1 - prev_you1) * prev_i0 * diff_i
        i1 += excite * prev_you0 * (1 - prev_i1) * diff_you

        allocation_time += 1

        # DEBUG
        # print([i0, you0, i1, you1])

        if allocation_time >= P.MAX_COORD_STEPS:
            if np.random.randint(0, 2):
                i0, you0, i1, you1 = 1, 0, 0, 1
            else:
                i0, you0, i1, you1 = 0, 1, 1, 0
            break
    
    # The agent that will perform this action has been determined
    agent = 0 if i0 > you0 else 1
    
    # DEBUG
    # print([agent, allocation_time])

    # Adjust allocation_time with a factor based on r_ij, f0, f1
    MAX_DELTA = 0.5
    allocation_time *= (1 + MAX_DELTA * -(r_ij - 0.5)/0.5 * (f0 - P.MAX_H/2)/(P.MAX_H/2) * (f1 - P.MAX_H/2)/(P.MAX_H/2))
    
    return agent, allocation_time

def get_relationship(agent0, agent1):
    r_ij = P.MBTI[agent0.get_mbti_ix()][agent1.get_mbti_ix()] \
           if agent0.validate_mbti() and agent1.validate_mbti() \
           else -1
    return r_ij if r_ij != 0 else np.finfo(float).eps

def calculate_immediate_frustration(agent0, agent1):
    immediate_frustrations = []

    r_ij = get_relationship(agent0, agent1)
    personality = (1 - r_ij) / r_ij
    
    for agent in [agent0, agent1]:
        # coord_penalty = (agent.allocation_times[-1] / (P.MAX_COORD_STEPS+1)) / \
        #            (1 - (agent.allocation_times[-1] / (P.MAX_COORD_STEPS+1)))

        # coord_penalty = 1 - math.exp(-coord_penalty)

        # !TODO Justify this
        HARD_LIMITER = 0.1
        alloc_time = agent.allocation_times[-1] if agent.allocation_times[-1] < round(P.MAX_COORD_STEPS * HARD_LIMITER) else (round(P.MAX_COORD_STEPS * HARD_LIMITER) - 1)
        coord_penalty = (alloc_time / (P.MAX_COORD_STEPS / 10)) / \
                        (1 - (alloc_time / (P.MAX_COORD_STEPS / 10)))

        immediate_frustrations.append(P.MAX_H * (1 - math.exp(-P.BETA * personality * coord_penalty)))

    return immediate_frustrations[0], immediate_frustrations[1]
