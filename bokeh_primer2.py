import pandas as pd
import numpy as np
import db_scripts as dbs
from Stats import Stats
from bokeh.io import curdoc
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.layouts import row, column, gridplot, widgetbox
from bokeh.models import HoverTool
from bokeh.models.widgets import Panel, Tabs, Slider

test = Stats(pd.DataFrame({}), "daily", "TEST")

trials = 1
mu = 0
sigma = 40
mcd = test.gbm(n_scenarios=trials, mu=mu, sigma=sigma)

def callback2(attr, old, new):
    mu = slider2.value
    sigma = slider3.value
    new_data = test.gbm(n_scenarios=trials, mu=mu, sigma=sigma)
    source.data = {"x": new_data.index, "y": new_data.values}

slider2 = Slider(title="mu", start=-20, end=20, step=1, value=mu)
slider3 = Slider(title="sigma", start=0, end=50, step=1, value=sigma)
slider2.on_change("value", callback2)
slider3.on_change("value", callback2)
source = ColumnDataSource({"x": mcd.index, "y": mcd.values})

plot2 = figure(title="GBM Stock Price Paths",
               plot_width=1000,
               plot_height=500)

plot2.line("x", "y", color="firebrick", alpha=0.5, line_width=1, source=source)

layout2 = column(slider2, slider3, plot2)
curdoc().add_root(layout2)
'''