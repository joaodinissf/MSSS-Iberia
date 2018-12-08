import numpy as np
import PARAMETERS as P

class Agent:
    def __init__(self, _id, skillset = []):
        self._id = _id
        #self.mood = []
        self.performance_times = {}

        self.skillset = sorted(skillset, key=lambda s: s._id)  # Ensure skills are stored in order
        
        # Sanity check - skills should be consecutive integers starting at zero
        try:
            assert [skill._id for skill in self.skillset] == list(range(len(self.skillset)))
        except AssertionError:
            print('Invalid skillset provided! Please verify the correctness of your input.')

        # Agent Memory
        self.stm = []                    # Should be updated when task is allocated
        self.ltm = self.skillset.copy()  # Initially, all skills are part of the long-term memory

        # Need to update this accordingly
        self.current_action = []
        self.action_history = []

    # ---------- INTERNAL UPDATES ----------

    def calculate_performance_time(self, wp, skill_ids, assignments, time):
        self.performance_times[time] = sum(
            [
                P.TASK_UNIT_DURATION / ((P.ALPHA_E * self.skillset[skill_ids[ix]].expertise[-1] / P.MAX_E) +
                                         (P.ALPHA_M * self.skillset[skill_ids[ix]].motivation[-1] / P.MAX_M))
                for ix, assignment in enumerate(assignments) if assignment == self._id
            ]
        )

        return self.performance_times[time]

    def update_memory(self, wp):
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
    
    def get_initial_i_you(self, wp, skill_id):
        # Determine current expertise and motivation for this skill
        exp = self.get_latest_expertise(skill_id)
        mot = self.get_latest_motivation(skill_id)

        # Compute i, you
        # Situation 1 - insufficient expertise
        if exp < P.TH_E:
            i = 0
            you = 1
        # Situation 2 - Sufficient expertise, sufficient motivation
        elif mot >= P.TH_M:
            i = P.ALPHA_E * (exp - P.TH_E) / (P.MAX_E - P.TH_E) + \
                 P.ALPHA_M * (mot - P.TH_M) / (P.MAX_M - P.TH_M)
            you = 0
        # Situation 3 - Sufficient expertise, insufficient motivation
        else:
            i = P.ALPHA_E * (exp - P.TH_E) / (P.MAX_E - P.TH_E)
            you = P.ALPHA_M * (P.TH_M - mot) / P.TH_M
        
        return i, you

    # ---------- OUTPUT ----------
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

    # TODO
    # Mood should be updated before their interaction
    
    i0, you0 = wp.agents[0].get_initial_i_you(wp, action.skill_id)
    i1, you1 = wp.agents[1].get_initial_i_you(wp, action.skill_id)

    # BEGIN NEGOTIATION PROCESS
    agent, allocation_time = negotiate(i0, you0, i1, you1)
    
    # Update progress of one time unit
    action.completion += 1
    
    return (agent, allocation_time, action.skill_id, action._id)

def negotiate(i0, you0, i1, you1, inhibit = P.INHIBIT, excite = P.EXCITE):
    allocation_time = 0

    print([i0, you0, i1, you1])

    diff_i = abs(i0 - i1)
    diff_you = abs(you0 - you1)

    while (i0 > you0 and i1 > you1) or \
          (you0 > i0 and you1 > i1):

        # diff_i = abs(i0 - i1)
        # diff_you = abs(you0 - you1)

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

        print([i0, you0, i1, you1])

        if allocation_time >= 1000:
            if np.random.randint(0, 2):
                i0, you0, i1, you1 = 1, 0, 0, 1
            else:
                i0, you0, i1, you1 = 0, 1, 1, 0
            break
    
    # The agent that will perform this action has been determined
    agent = 0 if i0 > you0 else 1
    
    print([agent, allocation_time])
    return agent, allocation_time