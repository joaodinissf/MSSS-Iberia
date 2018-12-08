from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import numpy as np

class Event:
    def __init__(self, start_time = -1, duration = -1, task_id = -1, action_id = -1, agent_id = -1):
        self.start_time = start_time
        self.duration = duration
        self.task_id = task_id
        self.action_id = action_id
        self.agent_id = agent_id
    
    def __str__(self):
        return ''.join([
             '[ Time: ', str(self.start_time), '-', str(self.start_time + self.duration), ', ', \
             'Duration: ', str(self.duration), ', ', \
             'Task (Action): ', str(self.task_id), ' (', str(self.action_id), '), ', \
             'Agent: ', str(self.agent_id), ' ]'])

class Timeline:
    def __init__(self):
        self.events = []             # Array of Events
        self.end = None
    
    def compute_end(self):
        self.end = max(map(lambda e: e.start_time + e.duration, self.events)) \
                    if len(self.events) > 0 else 1
        return self.end

    # TODO
    # # Do we need a function to coalesce events? (Merge adjacent events)
    # def coalesce_events(self):
    #     pass

    # TODO
    def __str__(self):
        pass

    def add_event(self, event = None):
        if event != None:
            self.events.append(event)
            self.events = sorted(self.events, key = lambda e: e.start_time)

    def plot_gantt(self):
        # Ensure that end is updated
        self.compute_end()

        # Create rectangles for the plot
        rects = []
        for idx, event in enumerate(self.events):
            rects.append({'type': 'rect',
                          'x0': event.start_time,
                          'y0': idx,
                          'x1': event.start_time + event.duration,
                          'y1': idx+1,
                          'line': {
                              'color': 'rgba(53, 208, 255, 1)',
                              'width': 2,
                              },
                          'fillcolor': 'rgba(53, 208, 255, 0.7)',
            })
        
        trace0 = go.Scatter(
            x=[e.start_time + e.duration/2 for e in self.events],
            y=np.array(list(range(1, len(self.events)+1))) - 0.5,

            text=[ 'Agent {0}<br><b>T{1} - A{2}</b>'.format(e.agent_id, e.task_id, e.action_id) for e in self.events ],
            #textposition='middle center',
            #textposition='middle right',

            mode='text',
        )
        data = [trace0]

        # Make plot
        layout = {
            'xaxis': {
                'autorange': True,
                #'range': [0, self.compute_end()],
                'showgrid': False,
            },
            'yaxis': {
                'range': [0, len(self.events)+2]
            },
            'shapes': rects,
        }

        fig = {
            'data': data,
            'layout': layout,
        }

        iplot(fig, filename='shapes-rectangle')
