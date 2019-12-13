import pandas as pd
import numpy as np
import par_stats_graphics as gph
import db_scripts as dbs
from Stats import Stats
from matplotlib import pyplot as plt
from collections import OrderedDict
from datetime import timedelta


EXP = "./extracts/"
DSP = ".././par-data-sources/"
TMP = "./temp-data-sources/"
QAP = "./qa-data-sources/"
ROE = "manager_roes.csv"
BMK = "benchmark_data.xlsx"
STK = "focus_list_prices_and_market_caps_abridged.xlsx"
FMT = {"Figure Size": ((12, 5), (12, 5)),
       "Title Size": (12, 12),
       "AxLab Size": (10, 10)}
SRC = "Desktop"
VAR = ["historic", "modified", "conditional"]
IOC = (("database", True), ("csv", False))
IOS = IOC[0]

# ***************************** CONFIGURE DISPLAY *****************************
if SRC == "Laptop":
    FIG, TIS, ALS = (FMT["Figure Size"][0], FMT["Title Size"][0],
                     FMT["AxLab Size"][0])
else:
    FIG, TIS, ALS = (FMT["Figure Size"][1], FMT["Title Size"][1],
                     FMT["AxLab Size"][1])

# *************************** LOAD PRODUCTION DATA ****************************
if IOS[0] == "database":
    pnl = dbs.get_manager_roes()
elif IOS[0] == "csv":
    pnl = pd.read_csv(TMP + ROE, header=0, index_col=0, parse_dates=True)

bmk = pd.read_excel(TMP + BMK, header=0, index_col=1, parse_dates=True)
stk = pd.read_excel(TMP + STK, header=0, index_col=1, parse_dates=True)

# *************************** DUMP PRODUCTION DATA ****************************
pnl.to_csv(DSP + ROE) if IOS[1] else np.nan
pnl.to_csv(TMP + ROE) if IOS[1] else np.nan

# ************************ TRANSFORM PRODUCTION DATA **************************
roe = pd.pivot_table(pnl, values="roe", index="date", columns="manager")

bmk_cols = ["Manager", "EWFL", "CWFL", "SP500"]
bmk = bmk[bmk_cols]
bmk.columns = ["manager", "ewfl", "cwfl", "sp500"]
bmk.index.names = ["date"]
ewfl = pd.pivot_table(bmk, values="ewfl", index="date", columns="manager")
cwfl = pd.pivot_table(bmk, values="cwfl", index="date", columns="manager")
sp500 = pd.pivot_table(bmk, values="sp500", index="date", columns="manager")

stk_cols = ["Security", "Close"]
stk = stk[stk_cols]
stk.columns = ["stock", "price"]
stk.index.names = ["date"]
stk = pd.pivot_table(stk, values="price", index="date", columns="stock")
stk = stk.pct_change()

# *************************** TRADITIONAL GROUPS ******************************
roe = Stats(roe, "daily", "ROE")
ewfl = Stats(ewfl, "daily", "EWFL")
cwfl = Stats(cwfl, "daily", "CWFL")
sp500 = Stats(sp500, "daily", "SP500")
stk = Stats(stk, "daily", "STOCKS")
TGP = pd.Series([roe, ewfl, cwfl, sp500, stk])


def fillgaps(data):
    s = []
    data.r.apply(lambda col: s.append(col.loc[col.first_valid_index():
                                      col.last_valid_index()].fillna(0)))
    data.r = pd.DataFrame(s).transpose()
    data.r0 = pd.DataFrame(s).transpose()

TGP.apply(lambda x: fillgaps(x))


# ***************************** DYNAMIC GROUPs ********************************
def create_group(stocks=["UAL", "JBLU"], weights=[50, 50],
                 group_name="Custom", start="1989-12-31", end="2049-12-31"):

    g = stk.r[stocks]
    g = g[start:end]

    # calculate group return
    cum_g = (1 + g).cumprod() * weights
    cum_g.loc[g.index.min() - timedelta(days=1)] = weights
    cum_g.insert(g.shape[1], "Portfolio", cum_g.sum(axis=1))
    cum_g.sort_index(inplace=True)
    port_r = cum_g["Portfolio"].pct_change()
    g.insert(g.shape[1], "Portfolio", port_r)

    return Stats(g, "daily", group_name)


# **************************** CHARTING FEATURES ******************************
def chart_stats(entity="PAR", series=roe, stat="Volatility",
                start="1989", end="2049", var_lev=5,
                bins=100, window=252, size=FIG):

    s = series
    r = s.r0[entity][start:end].dropna()
    begin = r.index.min().strftime("%m/%d/%Y")
    end = r.index.max().strftime("%m/%d/%Y")
    n = str(r.count())
    title_hz = "(" + begin + " - " + end + ", " + n + " observations)"

    if stat == "Returns":
        count, bin_edges = np.histogram(r)
        ax = r.plot(kind="hist", xticks=bin_edges, bins=bins, figsize=size)
        gph.ret_hist(ax, s.hz_r(r, mode="mean"), s.hz_vol(r, mode="periodic"),
                     entity, s.name, title_hz, stat)
        return

    if stat == "VaR":
        roll = pd.DataFrame(OrderedDict({
                x: r.rolling(window).apply(lambda v, lev=var_lev, mode=x:
                                           s.var(pd.Series(v), lev, mode))
                for x in VAR}))
        roll.columns = ["Historic", "Modified", "Conditional"]

        gph.vsk_line(roll.plot(kind="line", figsize=size, linewidth=2),
                     entity, s.name, stat, var_lev,
                     "Rolling " + str(window) + "-Day")

        cum = pd.DataFrame(OrderedDict({
                x: r.rolling(len(r), min_periods=window).
                apply(lambda x, lev=var_lev, mode=x:
                      s.var(pd.Series(x), lev, mode)) for x in VAR}))
        cum.columns = ["Historic", "Modified", "Conditional"]

        gph.vsk_line(cum.plot(kind="line", figsize=size, linewidth=2),
                     entity, s.name, stat, var_lev, "Cumulative")
        return

    if stat == "Volatility":
        rolling_stat = r.rolling(window). \
            apply(lambda x, mode="annualized": s.hz_vol(x, mode))
        cum_stat = r.rolling(len(r), min_periods=window). \
            apply(lambda x, mode="annualized": s.hz_vol(x, mode))

    if stat == "Skewness":
        rolling_stat = r.rolling(window).apply(lambda x: s.skewness(x))
        cum_stat = r.rolling(len(r), min_periods=window). \
            apply(lambda x: s.skewness(x))

    if stat == "Kurtosis":
        rolling_stat = r.rolling(window).apply(lambda x: s.kurtosis(x))
        cum_stat = r.rolling(len(r), min_periods=window). \
            apply(lambda x: s.kurtosis(x))

    ax = rolling_stat.plot(kind="line", figsize=size, linewidth=2,
                           label="Rolling " + str(window) + "-Day")
    cum_stat.plot(kind="line", figsize=size, linewidth=2,
                  label="Cumulative")
    gph.vsk_line(ax, entity, s.name, stat)


def chart_drawdown(entity="PAR", series=roe, config="absolute",
                   start="1989", end="2049", size=FIG):
    s = series
    r = s.r0[entity][start:end].dropna()

    if config == "absolute":
        dd_lev = pd.DataFrame(OrderedDict({
                "Wealth Index": s.drawdowns(r, mode="series")["wealth"],
                "Peaks": s.drawdowns(r, mode="series")["peaks"]
                }))
        gph.drawdown(dd_lev.plot(kind="line", figsize=size, linewidth=2),
                     entity, s.name, mode="level")
        plt.show()

        dd_pct = s.drawdowns(r, mode="series")["drawdown"]
        gph.drawdown(dd_pct.plot(kind="line", figsize=size, linewidth=2),
                     entity, s.name, mode="pct")

    if config == "relative":
        peaks_df = pd.DataFrame(OrderedDict({
                x.name: x.drawdowns(x.r0[entity][start:end].dropna(),
                                    mode="series")["peaks"]
                for x in [roe, sp500, ewfl, cwfl]}))
        peaks_df.columns = ["ROE", "SP500", "EWFL", "CWFL"]
        peaks_df.dropna(inplace=True)
        gph.drawdown(peaks_df.plot.line(figsize=size, linewidth=2),
                     entity, s.name, mode="level", config="relative")


def chart_average_cor(fund=roe, market=sp500, window=252):
    corr_ts, corr_df = fund.average_cor(fund, market, window)
    gph.average_cor(corr_df, fund, market, window, corr_ts)


def chart_cppi(entity="PAR", fund=roe, safe_asset=None, risk_multiplier=4,
               initial_wealth=100, floor_pct=0.80, risk_free_rate=0.03,
               drawdown_constraint=None, start="1989", end="2049"):
    cppi_dc = fund.cppi(fund.r, safe_asset, risk_multiplier, initial_wealth,
                        floor_pct, risk_free_rate, drawdown_constraint,
                        start, end)
    gph.cppi(cppi_dc, entity)


def chart_gbm_paths(n_years=1, n_scenarios=100, mu=7, sigma=15,
                    frequency="daily", price0=100, fund=roe):
    prices = fund.gbm(n_years, n_scenarios, mu, sigma, frequency, price0)
    gph.gbm_prices(prices, n_years, n_scenarios, mu, sigma)

def chart_markowitz_mvs(group=["Paul", "Kevin"], series=roe, n=100, rfr=0.04,
                        start="1989", end="2049",
                        show_cml=True, show_ndp=True, show_gmv=True,
                        style=".-", size=FIG):
    s = series
    s.change_hz(start, end)
    er = s.stats().loc[group, "Annualized Return"]
    regroup = list(er.index)
    cov = s.r[regroup].cov()
    mef = s.mef(n, er, cov)
    ax = mef.plot.scatter(x="Volatility", y="Return", figsize=size)

    if show_cml:
        ax.set_xlim(left=0)
        w_msr = s. msr(er, cov)
        r_msr = s.port_r(w_msr, er)
        vol_msr = s.port_vol(w_msr, cov)
        cml_x = [0, vol_msr]
        cml_y = [rfr, r_msr]
        ax.plot(cml_x, cml_y, color='green', marker='o',
                linestyle='dashed', linewidth=4, markersize=20)
    if show_ndp:
        n = er.count()
        w_ew = np.repeat(1/n, n)
        r_ew = s.port_r(w_ew, er)
        vol_ew = s.port_vol(w_ew, cov)
        ax.plot([vol_ew], [r_ew], color='goldenrod', marker='o', markersize=20)
    if show_gmv:
        w_gmv = s.gmv(cov)
        r_gmv = s.port_r(w_gmv, er)
        vol_gmv = s.port_vol(w_gmv, cov)
        ax.plot([vol_gmv], [r_gmv], color='midnightblue', marker='o',
                markersize=20)

    return ax