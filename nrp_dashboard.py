import pandas as pd
import numpy as np
import db_scripts as dbs
from Stats import Stats
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.layouts import row, column, gridplot
from bokeh.charts import Histogram, defaults
from bokeh.models.widgets import Panel, Tabs


TMP = "./temp-data-sources/"
ROE = "manager_roes.csv"
IOC = (("database", True), ("file", False))
IOS = IOC[1]

if IOS[0] == "database":
    pnl = dbs.get_manager_roes()
elif IOS[0] == "file":
    pnl = pd.read_csv(TMP + ROE, header=0, index_col=0, parse_dates=True)

pnl.to_csv(TMP + ROE) if IOS[1] else np.nan
roe = pd.pivot_table(pnl, values="roe", index="date", columns="manager")
roe = Stats(roe, "daily", "ROE")

TGP = pd.Series([roe])


def fillgaps(data):
    s = []
    data.r.apply(lambda col: s.append(col.loc[col.first_valid_index():
                                      col.last_valid_index()].fillna(0)))
    data.r = pd.DataFrame(s).transpose()
    data.r0 = pd.DataFrame(s).transpose()

TGP.apply(lambda x: fillgaps(x))


def bokeh_ts(source, col, title, xlab="", ylab="", width=500, height=300,
             color="firebrick", alpha=0.5, line_width=2):
    p = figure(title=title,
               plot_width=width,
               plot_height=height,
               x_axis_type="datetime",
               x_axis_label=xlab,
               y_axis_label=ylab)
    p.line(x="date",
           y=col,
           color=color,
           alpha=alpha,
           line_width=line_width,
           source=source)
    return p


def bokeh_multiline(df, title, width=1000, height=500,
                    color="firebrick", alpha=0.5, line_width=1):
    p = figure(title=title,
               plot_width=width,
               plot_height=height)
    p.multi_line(xs=[df.index] * len(df.columns),
                 ys=[df[col].values for col in df],
                 color=color,
                 alpha=alpha,
                 line_width=line_width)
    return p


def chart_stats(entity="PAR", obj=roe, window=252, start=1989, end=2049,
                var_lev=5, bins=150):
    s = obj
    start = str(start)
    end = str(end)
    r = s.r0[entity][start:end].dropna()
    df = pd.DataFrame(r)
    begin = r.index.min().strftime("%m/%d/%Y")
    finish = r.index.max().strftime("%m/%d/%Y")
    n = str(r.count())

    title_vol = entity + " " + s.name + " - Volatility " + \
        "(" + begin + " - " + finish + ", " + n + " observations)"
        
    title_skew = entity + " " + s.name + " - Skewness " + \
        "(" + begin + " - " + finish + ", " + n + " observations)"

    title_kurt = entity + " " + s.name + " - Kurtosis " + \
        "(" + begin + " - " + finish + ", " + n + " observations)"

    obj_ret_hist = Histogram(df[entity], width= 500, height=300, bins=bins)
    
    roll_vol = r.rolling(window).apply(lambda x,
        mode="annualized":s.hz_vol(x, mode))

    roll_skew = r.rolling(window).apply(lambda x: s.skewness(x))

    roll_kurt = r.rolling(window).apply(lambda x: s.kurtosis(x))

    stats_df = pd.DataFrame({"Vol": roll_vol,
                            "Skew": roll_skew,
                            "Kurt": roll_kurt})
    stats_source = ColumnDataSource(stats_df)

    vol = bokeh_ts(stats_source, "Vol", title_vol)
    skew = bokeh_ts(stats_source, "Skew", title_skew)
    kurt = bokeh_ts(stats_source, "Kurt", title_kurt)

    vol.x_range = skew.x_range = kurt.x_range

    tab1 = Panel(child=obj_ret_hist, title='Daily Returns Analysis')
    tab2 = Panel(child=row(vol, skew, kurt),
                 title='Statistical Moments')

    stats_layout = Tabs(tabs=[tab1, tab2])

    show(stats_layout)

'''
test = Stats(pd.DataFrame({}), "daily", "TEST")
mcd = test.gbm(n_scenarios=5)
bokeh_multiline(mcd, t="GBM Stock Price Paths")

row1 = [None, vol]
row2 = [skew, kurt]
stats_layout = gridplot([row1, row2])
'''