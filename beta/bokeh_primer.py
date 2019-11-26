import numpy as np
import pandas as pd

# ******************************** BOKEH STACK ********************************
from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import output_file, show
from bokeh.models import HoverTool, CategoricalColorMapper


ds = pd.read_csv("literacy_birth_rate.csv", header=0)
aapl = pd.read_csv("aapl.csv", header=0, parse_dates=True)
aapl = aapl[["date", "adj_close"]]

female_literacy = list(ds["female_literacy"])
fertility = list(ds["fertility"])

p = figure(x_axis_label="fertility (children per woman)",
           y_axis_label="female_literacy (% population)")

fertility_africa = ds[ds["Continent"]=="AF"]["fertility"]
female_literacy_africa = ds[ds["Continent"]=="AF"]["female_literacy"]

fertility_latam = ds[ds["Continent"]=="LAT"]["fertility"]
female_literacy_latam = ds[ds["Continent"]=="LAT"]["female_literacy"]

# Add a circle glyph to the figure p
p.circle(fertility_latam, female_literacy_latam, color="blue",
         size=10, alpha=0.8)
p.circle(fertility_africa, female_literacy_africa, color="red",
         size=10, alpha=0.8)

# Call the output_file() function and specify the name of the file
output_file("fert_lit.html")

# Display the plot
show(p)

q = figure(x_axis_type="datetime", x_axis_label='Date',
           y_axis_label='Price ($)')

date = pd.to_datetime(aapl["date"])
price = aapl["adj_close"]

# Plot date along the x axis and price along the y axis
q.line(date, price)
q.circle(date, price, fill_color="white", size=4)

# Specify the name of the output file and show the result
output_file('line.html')
show(q)

# Create array using np.linspace: x
x = np.linspace(0, 5, 100)

# Create array using np.cos: y
y = np.cos(x)

# Add circles at x and y
r = figure()
r.circle(x, y)

# Specify the name of the output file and show the result
output_file('numpy.html')

show(r)

# Create a figure with the "box_select" tool: p
p = figure(x_axis_label="Year", y_axis_label="Time", tools="box_select")

# Add circle glyphs to the figure p with the selected and non-selected properties
p.circle(x="Year", y="Time", selection_color="red",
         nonselection_color="blue", nonselection_alpha=0.1,
         source=source)

# Specify the name of the output file and show the result
output_file('selection_glyph.html')
show(p)


# import the HoverTool

# Add circle glyphs to figure p
p.circle(x, y, size=10,
         fill_color="grey", alpha=0.1, line_color=None,
         hover_fill_color="firebrick", hover_alpha=0.5,
         hover_line_color="white")

# Create a HoverTool: hover
hover = HoverTool(tooltips=None, mode="vline")

# Add the hover tool to the figure p
p.add_tools(hover)

# Specify the name of the output file and show the result
output_file('hover_glyph.html')
show(p)


# Convert df to a ColumnDataSource: source
source = ColumnDataSource(df)

# Make a CategoricalColorMapper object: color_mapper
color_mapper = CategoricalColorMapper(factors=['Europe', 'Asia', 'US'],
                                      palette=['red', 'green', 'blue'])

# Add a circle glyph to the figure p
p.circle('weight', 'mpg', source=source,
            color=dict(field="origin", transform=color_mapper),
            legend='origin')

# Specify the name of the output file and show the result
output_file('colormap.html')
show(p)


# Create a ColumnDataSource from df: source
source = ColumnDataSource(df)

# Add circle glyphs to the figure p
p.circle(x="Year", y="Time", size=8, color="color", source=source)

# Specify the name of the output file and show the result
output_file('sprint.html')
show(p)


# Add the first circle glyph to the figure p
p.circle('fertility', 'female_literacy', source=latin_america, size=10, color="red", legend=
"Latin America")

# Add the second circle glyph to the figure p
p.circle('fertility', 'female_literacy', source=africa, size=10, color="blue", legend="Africa")

# Assign the legend to the bottom left: p.legend.location
p.legend.location="bottom_left"

# Fill the legend background with the color 'lightgray': p.legend.background_fill_color
p.legend.background_fill_color="lightgray"

# Specify the name of the output_file and show the result
output_file('fert_lit_groups.html')
show(p)









# ********************************* HOVERTOOL *********************************
# Create a HoverTool object (bokeh.models)
hover = HoverTool(tooltips=[("Country", "@Country")])

# Add the HoverTool object to figure p
p.add_tools(hover)
