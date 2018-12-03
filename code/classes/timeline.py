import plotly.plotly as py
import plotly.graph_objs as go

class Event:
    def __init__(self, start_time = -1, duration = -1, action = -1, agent = -1):
        self.start_time = start_time
        self.duration = duration
        self.task = action.parent
        self.action = action
        self.agent = agent
    
    def __str__(self):
        return ''.join([
             '[ Time: ', str(self.start_time), '-', str(self.start_time + self.duration), ', ', \
             'Duration: ', str(self.duration), ', ', \
             'Task(Action/Total): ', str(self.task._id), '(', str(self.action._id), '/', str(self.action.total_acts), ')', ', ', \
             'Agent: ', str(self.agent._id), ' ]'])

class Timeline:
    def __init__(self):
        self.events = []             # Array of Events
        self.end = None
    
    def compute_end(self):
        self.end = max([lambda e: e.start_time + e.duration for e in self.events])
        return self.end

    def __str__(self):
        pass

    def plot_gantt(self):
        # Ensure that end is updated
        self.compute_end()

        # Create rectangles for the plot
        rects = []
        for idx, event in enumerate(events):
            rects.append({'type': 'rect',
                          'x0': event.start_time,
                          'y0': idx,
                          'x1': event.start_time + event.duration,
                          'y1': idx+1,
                          'line': {
                              'color': 'rgba(128, 0, 128, 1)',
                              'width': 2,
                              },
                          'fillcolor': 'rgba(128, 0, 128, 0.7)',
            })
        
        # Make plot
        layout = {
            'xaxis': {
                'range': [0, self.compute_end()],
                'showgrid': False,
            },
            'yaxis': {
                'range': [0, len(events)+2]
            },
            'shapes': rects,
        }
        fig = {
            'layout': layout,
        }

        py.iplot(fig, filename='shapes-rectangle')
