import pandas as pd
from collections import OrderedDict
from matplotlib import pyplot as plt

FMT = {"Figure Size": ((12, 5), (12, 5)),
       "Title Size": (12, 12),
       "AxLab Size": (10, 10)}
SRC = "Desktop"

if SRC == "Laptop":
    FIG, TIS, ALS = (FMT["Figure Size"][0], FMT["Title Size"][0],
                     FMT["AxLab Size"][0])
else:
    FIG, TIS, ALS = (FMT["Figure Size"][1], FMT["Title Size"][1],
                     FMT["AxLab Size"][1])


def ret_hist(ax, mean, vol, entity, name, title_hz, stat):
    ax.axvline(x=0, color="black")
    ax.axvline(x=mean, color="yellow")
    ax.axvline(x=-3*vol, color="red")
    ax.axvline(x=+3*vol, color="red")
    ax.set_ylabel("Frequency", fontsize=ALS)
    ax.set_xlabel("Daily " + stat, fontsize=ALS)
    ax.tick_params(axis='both', which='major', labelsize=ALS)
    ax.set_title(entity + " - " + name +
                 ": Daily Returns Distribution " + title_hz,
                 fontdict={"fontsize": TIS, "fontweight": "bold"})
    ax.set_xticklabels(['{:.0f}%'.format(x*100) for x in ax.get_xticks()])
    return ax


def vsk_line(ax, entity, name, stat, var_lev=5, title_prefix=""):
    if stat != "VaR":
        ax.set_title(entity + " - " + name + ": Historical " + stat,
                     fontdict={"fontsize": TIS, "fontweight": "bold"})
    else:
        ax.set_title(entity + " - " + name + ": " + title_prefix +
                     " Value at Risk @ " + str(var_lev) + "%",
                     fontdict={"fontsize": TIS, "fontweight": "bold"})

    ax.tick_params(axis='both', which='major', labelsize=ALS)
    ax.set_ylabel(stat, fontsize=ALS)
    ax.set_xlabel("")
    ax.legend(fontsize="xx-large", loc=0)

    if stat == "Volatility":
        ax.set_yticklabels(['{:.0f}%'.format(x*100) for x in ax.get_yticks()])

    if stat == "VaR":
        ax.set_yticklabels(['{:.1f}%'.format(x*100) for x in ax.get_yticks()])
    return ax


def drawdown(ax, entity, name, mode="level", config="absolute"):
    if mode == "level":
        if config == "absolute":
            ax.set_title(entity + " - " + name + ": Wealth Index and Peaks",
                         fontdict={"fontsize": TIS, "fontweight": "bold"})
        elif config == "relative":
            ax.set_title(entity + " - " + name + ": Relative Peaks",
                         fontdict={"fontsize": TIS, "fontweight": "bold"})
        ax.set_ylabel("Wealth (Base = $100)", fontsize=ALS)
        ax.set_xlabel("")
        ax.tick_params(axis='both', which='major', labelsize=ALS)
        ax.set_yticklabels(['${:,.0f}'.format(x) for x in ax.get_yticks()])
        ax.legend(fontsize="xx-large", loc=0)
        return ax
    elif mode == "pct":
        ax.set_title(entity + " - " + name + ": % Drawdown",
                     fontdict={"fontsize": TIS, "fontweight": "bold"})
        ax.set_ylabel("% Drawdown", fontsize=ALS)
        ax.set_xlabel("")
        ax.tick_params(axis='both', which='major', labelsize=ALS)
        ax.set_yticklabels(['{:.0f}%'.format(x*100) for x in ax.get_yticks()])
        return ax


def average_cor(data, fund, market, window, corr_ts):
    ax = data["Trailing SP500 Annualized Return"].plot(
            label="Trailing Market Return", figsize=FIG, legend=True)
    data["Average Correlation"].plot(label="Trailing Average Correlation",
                                     legend=True, secondary_y=True)

    ax.set_title(fund.name + " Correlation vs. " + market.name + " Trailing " +
                 str(window) + "-Day Annualized Return",
                 fontdict={"fontsize": TIS, "fontweight": "bold"})
    ax.set_xlabel("")
    ax.tick_params(axis='both', which='major', labelsize=ALS)
    textstr = r'$Correlation = %.2f$' % (corr_ts, )
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    ax.text(0.05, 0.05, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment="top", bbox=props)
    return ax


def cppi(dc, entity):
    ax = dc["CPPI Wealth"][entity].plot.line(
            label="CPPI Portfolio", figsize=FIG, legend=True)
    dc["Risky Wealth"][entity].plot.line(
            label="Unconstrained Portfolio", legend=True)
    dc["Hurdle"][entity].plot.line(
            label="Hurdle", legend=True)
    dc["Floor"][entity].plot.line(
            label="Floor", legend=True)
    dc["Peak"][entity].plot.line(
            label="Peak", legend=True)
    ax.set_title(entity + ": CPPI versus Unconstrained Portfolio",
                 fontdict={"fontsize": TIS, "fontweight": "bold"})
    ax.set_xlabel("")
    ax.set_ylabel("Wealth (Base = $100)", fontsize=ALS)
    ax.tick_params(axis='both', which='major', labelsize=ALS)

    stats_df = pd.DataFrame(OrderedDict({
            "CPPI Stats": dc["CPPI Stats"].loc[entity, :],
            "Unconstrained Stats": dc["Unconstrained Stats"].loc[entity, :]}))

    print(stats_df)
    return ax


def gbm_prices(prices, n_years, n_scenarios, mu, sigma):
    plt.figure(1)
    ax = prices.plot.line(figsize=FIG, legend=False)
    year = "year " if n_years == 1 else "years "
    ax.set_title("GBM Stock Price Evolution: " + 
                 str(n_scenarios) + " scenarios run over " + 
                 str(n_years) + " " + year + 
                 "with " + r"$\mu = $" + str(mu) + "%" + 
                 ", " + r"$\sigma = $" + str(sigma) + "%",
                 fontdict={"fontsize": TIS, "fontweight": "bold"})
    ax.set_ylabel("Price (Base = $100)", fontsize=ALS)
    ax.tick_params(axis='both', which='major', labelsize=ALS)
    plt.show()
    return