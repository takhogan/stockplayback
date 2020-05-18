import plotly.graph_objects as go
from plotly.subplots import make_subplots

class StockCharter:
    def __init__(self, stock_data):
        self.data = [go.Candlestick(
                x=stock_data.index,
                open=stock_data['open'],
                high=stock_data['high'],
                low=stock_data['low'],
                close=stock_data['close']
        )]
        self.indicators = []
        self.fig = go.Figure(data=self.data)
        self.annotations = []
        self.smallfont = dict(
                family="Courier New, monospace",
                size=8,
                color="#000000"
        )

    def add_entry(self, price, time, text):
        self.fig.update_layout(
            showlegend=False,
            annotations=[dict(
                x=time, y=price, xref='x', yref='y',
                showarrow=True, xanchor='left', text=text)]
        )

    def add_state_table(self, time, state_table):
        new_annotations = [{
                'x': time,
                'y': str(0.95 - state_index / 20),
                'xref': 'x',
                'yref': 'paper',
                'showarrow': False,
                'xanchor': 'left',
                'font': self.smallfont,
                'text': state_table[state_index]
            } for state_index in range(0, len(state_table))] + self.annotations
        self.annotations = new_annotations
        print(len(self.annotations))

    def add_indicator(self, x, y):
        self.fig = make_subplots(rows=2,
                                 cols=1,
                                 row_heights=[0.3, 0.7])
        for graph_obj in self.data:
            self.fig.add_trace(graph_obj,
                               row=2,
                               col=1)
        indicator = go.Scatter(x=x,
                               y=y)
        self.indicators.append(indicator)
        for indicator in self.indicators:
            self.fig.add_trace(indicator,
                               row=1,
                               col=1)
    def add_trace(self, x, y):
        self.data.append(go.Scatter(x=x,
                                    y=y))
        self.fig.add_trace(go.Scatter(x=x,
                                      y=y))
    def show(self):
        self.fig.update_layout(
            showlegend=False,
            annotations=self.annotations
        )
        self.fig.show()
