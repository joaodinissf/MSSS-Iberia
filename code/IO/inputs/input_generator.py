import json

def generator_exp2():
    data = {}

    ### PARAMETERS ###

    data['parameters'] = {
        'task_unit_duration': 10,
        'alpha_e': 0.5,
        'alpha_m': 0.5,
        'alpha_h': 0,
        'lam_learn': 1,
        'lam_motiv': 0,
        'mu_learn': 0.05,
        'mu_motiv': 0,
        'th_e': 10,
        'th_m': 10,
        'max_e': 25,
        'max_m': 25,
        'excite': 0.1,
        'inhibit': 0.1
    }
    
    ### AGENTS ###

    n_skills = 40

    exp_a0 = [18, 15, 14, 11, 12, 13, 16, 7]
    exp_a1 = [17, 16, 13, 12, 11, 14, 15, 18]

    agents = []
    agents.append(
        {
            'skillset':
            [
                {
                    'id': i,
                    'exp': exp_a0[i % 8],
                    'mot': exp_a0[i % 8]
                }
                for i in range(n_skills)
            ]
        }
    )
    agents.append(
        {
            'skillset':
            [
                {
                    'id': i,
                    'exp': exp_a1[i % 8],
                    'mot': exp_a1[i % 8]
                }
                for i in range(n_skills)
            ]
        }
    )

    data['agents'] = agents

    ### TASKS ###

    n_tasks = 10
    n_actions = 4
    n_cycles = 5

    data['tasks'] = []

    for i in range(n_tasks):
        ids = list(range(4))
        skill_ids = list(range(i*n_actions, (i+1)*n_actions))
        duration = [n_cycles] * n_actions
        
        actions = [
                {
                    'id': ids[i],
                    'skill_id': skill_ids[i],
                    'duration': duration[i]
                }
                for i in range(4) ]

        data['tasks'].append(
            {
                'actions': actions
            }
        )

    json_data = json.dumps(data)

    with open('Exp2_Zoethout_auto.json', 'w') as outfile:
        json.dump(json_data, outfile)

generator_exp2()