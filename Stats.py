import pandas as pd
import numpy as np
import scipy.stats as sps
from collections import OrderedDict
from numpy.linalg import multi_dot as mdot
from scipy.optimize import minimize
from datetime import timedelta

EX_PATH = "../extracts/"
VAR_MODES = ["historic", "parametric", "modified", "conditional"]
PPY = {"daily": 252, "monthly": 12, "quarterly": 4}


class Stats(object):
    def __init__(self, r, f, name, rf=0.04, var_lev=0.05, init=True):
        self.r0 = r
        self.r = r
        self.rf = rf
        self.f = f
        self.var_lev = var_lev
        self.min_date = self.r0.index.min()
        self.max_date = self.r0.index.max()
        self.hz = (self.r.index.min(), self.r.index.max())
        self.ppy = PPY[self.f]
        self.name = name

# ************************** CHANGE CLASS PARAMETERS **************************
    def change_hz(self, start="1989", end="2049"):
        self.r = self.r0[start:end]
        self.hz = (self.r.index.min(), self.r.index.max())

    def change_var_lev(self, var_lev):
        self.var_lev = var_lev

    def change_rf(self, rf):
        self.rf = rf

# ************************** STATISTICAL COMPUTATIONS *************************
    def hz_r(self, r, mode="cumulative"):
        if not isinstance(r, pd.Series):
            r = pd.DataFrame(r)
        if mode == "cumulative":
            return np.expm1(np.log1p(r).sum())
        if mode == "annualized":
            days = r.count()
            days = pd.Series(days)
            ann_factor = [self.ppy / x if x >= self.ppy else 1 for x in days]
            return (1 + self.hz_r(r, mode="cumulative")) ** ann_factor - 1
        if mode == "mean":
            return r.mean()
        if mode == "median":
            return r.median()

    def hz_vol(self, r, mode="periodic"):
        if mode == "periodic":
            return r.std(ddof=1)
        if mode == "annualized":
            return self.hz_vol(r, mode="periodic") * np.sqrt(self.ppy)

    def skewness(self, r):
        dmr = r - r.mean()
        s = r.std(ddof=0)
        return (dmr**3).mean() / s**3

    def kurtosis(self, r):
        dmr = r - r.mean()
        s = r.std(ddof=0)
        return (dmr**4).mean() / s**4

    def drawdowns(self, r: pd.Series, mode="max"):
        self.check_instance(r, "pd.Series", "drawdowns")
        wealth = 100 * (1 + r).cumprod()
        peaks = wealth.cummax()
        drawdown = (wealth - peaks) / peaks
        if mode == "series":
            dd = pd.DataFrame(OrderedDict({
                        "wealth": wealth,
                        "peaks": peaks,
                        "drawdown": drawdown}))
            dd.loc[dd.index.min() - timedelta(days=1)] = [100, 100, 0]
            dd.sort_index(inplace=True)
            return dd
        elif mode == "max":
            return drawdown.min()
        elif mode == "date":
            return drawdown.idxmin()

    def var(self, r: pd.Series, lev=5, mode="historic"):
        self.check_instance(r, "pd.Series", "var")
        z = sps.norm.ppf(lev/100)
        rm = self.hz_r(r, "mean")
        sd = self.hz_vol(r, "periodic")
        if mode == "historic":
            return -np.nanpercentile(r, lev)
        elif mode == "parametric":
            return -(rm + z*sd)
        elif mode == "modified":
            sk = self.skewness(r)
            kt = self.kurtosis(r)
            z = (z +
                 (z**2 - 1) * sk/6 +
                 (z**3 - 3*z) * (kt - 3)/24 -
                 (2*z**3 - 5*z) * (sk**2)/36)
            return -(rm + z*sd)
        elif mode == "conditional":
            is_beyond = r <= -self.var(r, lev=lev, mode="historic")
            return -self.hz_r(r[is_beyond], "mean")

    def jb_test(self, r: pd.Series, mode="stat"):
        self.check_instance(r, "pd.Series", "jb_test")
        r = r[~pd.isnull(r)]
        try:
            stat, p = sps.jarque_bera(r)
        except:
            stat, p = (np.nan, np.nan)
        return stat if mode == "stat" else p

    def stats(self, df=None):
        if df is None:
            r = self.r
        else:
            r = df

        var_dc = {x: r.agg(self.var, lev=self.var_lev*100, mode=x)
                  for x in VAR_MODES}
        stats_table = pd.DataFrame(OrderedDict({
            "Days": r.count(),
            "Start": r.agg(self.get_hz, mode="min"),
            "End": r.agg(self.get_hz, mode="max"),
            "Cumulative Return": self.hz_r(r),
            "Annualized Return": self.hz_r(r, mode="annualized"),
            "Annualized Volatility": self.hz_vol(r, mode="annualized"),
            "Annualized Sharpe Ratio":
                (1 / self.hz_vol(r, mode="annualized")) *
                (self.hz_r(r, mode="annualized") - self.rf),
            "Mean": self.hz_r(r, mode="mean"),
            "Volatility": self.hz_vol(r),
            "Skewness": self.skewness(r),
            "Kurtosis": self.kurtosis(r),
            "Max Drawdown": r.agg(self.drawdowns),
            "Max Drawdown Date": r.agg(self.drawdowns, mode="date"),
            "Historic VaR": var_dc["historic"],
            "Parametric VaR": var_dc["parametric"],
            "Modified VaR": var_dc["modified"],
            "Conditional VaR": var_dc["conditional"]
                }))
        return stats_table[stats_table["Days"] != 0]

# ********************** MARKOWITZS MEAN-VARIANCE SPACE ***********************
    def port_r(self, w, er):
        return np.dot(w.T, er)

    def port_vol(self, w, cov):
        return np.sqrt(mdot([w.T, cov, w]))

    def minimize_vol(self, target_er, er, cov):
        n = er.count()
        initial_w = np.repeat(1/n, n)
        bounds = ((0.0, 1.0),) * n
        ret_is_target = {"type": "eq", "args": (er,),
                         "fun": lambda w, er: target_er - self.port_r(w, er)}
        w_sum_to_1 = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        results = minimize(self.port_vol, initial_w, args=(cov,),
                           method="SLSQP", options={"disp": False},
                           constraints=(ret_is_target, w_sum_to_1),
                           bounds=bounds)
        return results.x

    def msr(self, er, cov):
        n = er.count()
        initial_w = np.repeat(1/n, n)
        bounds = ((0.0, 1.0),) * n
        w_sum_to_1 = {"type": "eq", "fun": lambda w: np.sum(w) - 1}

        def nsr(w, rfr, er, cov):
            r = self.port_r(w, er)
            vol = self.port_vol(w, cov)
            return -((r - self.rf)/vol)

        results = minimize(nsr, initial_w, args=(self.rf, er, cov),
                           method="SLSQP", options={"disp": False},
                           constraints=(w_sum_to_1), bounds=bounds)
        return results.x

    def gmv(self, cov):
        n = cov.shape[0]
        return self.msr(pd.Series(np.repeat(1, n)), cov)

    def optimal_w(self, n, er, cov):
        target_er = np.linspace(er.min(), er.max(), n)
        w = [self.minimize_vol(target_er, er, cov) for target_er in target_er]
        return w

    def mef(self, n, er, cov):
        w = self.optimal_w(n, er, cov)
        r = [self.port_r(w, er) for w in w]
        vol = [self.port_vol(w, cov) for w in w]
        return pd.DataFrame({"Return": r, "Volatility": vol})

# ************************************ CPPI ***********************************
    def average_cor(self, fund, market, window=252):
        if (fund.name == "ROE") | (fund.name == "EWFL") | \
                (fund.name == "CWFL") | (fund.name == "SP500"):
                    f = fund.r.drop(["PAR"], axis=1)
        elif fund.name:
            try:
                f = fund.r.drop(["Portfolio"], axis=1)
            except:
                f = fund.r
        f = f.dropna(how="all", axis=0)
        m = market.r["Paul"]

        m_tr_r = m.rolling(window=window).agg(market.hz_r, mode="annualized")
        f_tr_cor = f.rolling(window=window).corr()
        f_tr_cor_mean = f_tr_cor.groupby(level="date"). \
            apply(lambda cormat: np.nanmean(cormat.values))

        corr_df = pd.DataFrame(OrderedDict({
                "Average Correlation": f_tr_cor_mean,
                "Trailing SP500 Annualized Return": m_tr_r
                }))

        corr_df.dropna(how="any", axis=0, inplace=True)
        corr_ts = f_tr_cor_mean.corr(m_tr_r)
        return [corr_ts, corr_df]

    def cppi(self, risky_r, safe_r=None, m=4, account0=100, floor_pct=0.80,
             rf=0.03, drawdown=None, start="1989", end="2049"):
        r = risky_r[start:end]
        dates = r.index
        n_step = len(dates)
        port = account0
        hurdle = account0
        floor = account0 * floor_pct
        peak = account0
        if isinstance(r, pd.Series):
            r = pd.DataFrame(r, columns=["R"])
        if safe_r is None:
            s = pd.DataFrame().reindex_like(r)
            s.values[:] = rf / self.ppy
        else:
            np.nan

        h = pd.DataFrame().reindex_like(r)
        h.values[:] = (1.2)**(1/252) - 1

        port_hist = pd.DataFrame().reindex_like(r)
        r_w_hist = pd.DataFrame().reindex_like(r)
        cushion_hist = pd.DataFrame().reindex_like(r)
        peak_hist = pd.DataFrame().reindex_like(r)
        floor_hist = pd.DataFrame().reindex_like(r)
        hurdle_hist = pd.DataFrame().reindex_like(r)

        for step in range(n_step):
            if drawdown is not None:
                floor = peak * (1 - drawdown)
            peak = np.maximum(peak, port)
            cushion = (port - floor) / port
            r_w = m * cushion
            r_w = np.minimum(r_w, 1)
            r_w = np.maximum(r_w, 0)
            s_w = 1 - r_w
            r_alloc = port * r_w
            s_alloc = port * s_w

            port = r_alloc * (1 + r.iloc[step]) + s_alloc * (1 + s.iloc[step])
            hurdle = hurdle * (1 + h.iloc[step])

            cushion_hist.iloc[step] = cushion
            r_w_hist.iloc[step] = r_w
            port_hist.iloc[step] = port
            floor_hist.iloc[step] = floor
            peak_hist.iloc[step] = peak
            hurdle_hist.iloc[step] = hurdle

        r_wealth = account0 * (1 + r).cumprod()

        cppi_backtest = {
                "CPPI Wealth": port_hist,
                "Risky Wealth": r_wealth,
                "Hurdle": hurdle_hist,
                "Risk Budget": cushion_hist,
                "Risk Allocation": r_w_hist,
                "Initial Portfolio Value": account0,
                "Risk Multiplier": m,
                "Floor Level": floor_pct,
                "Risky Portfolio": r,
                "Safe Returns": s,
                "Drawdown Level": drawdown,
                "Peak": peak_hist,
                "Floor": floor_hist,
                "CPPI Stats": self.stats(port_hist.pct_change()),
                "Unconstrained Stats": self.stats(r_wealth.pct_change())}

        return cppi_backtest

    def gbm(self, n_years=1, n_scenarios=10, mu=7, sigma=15,
            frequency="daily", price0=100):
        steps_per_year = PPY[frequency]
        dt = 1 / steps_per_year
        mu /= 100
        sigma /= 100
        n_steps = int(n_years * steps_per_year)
        xi = np.random.normal(size=(n_steps, n_scenarios))
        rets = mu*dt + sigma*np.sqrt(dt)*xi
        rets[0] = 0
        rets = pd.DataFrame(rets)
        prices = price0*(1+rets).cumprod()
        return prices

# ****************************** TIME INFORMATION *****************************
    def get_hz(self, r: pd.Series, mode="min"):
        self.check_instance(r, "pd.Series", "get_hz")
        r = r[~pd.isnull(r)]
        return r.index.min() if mode == "min" else r.index.max()

# ************************************ I/O ************************************
    def dump_file(self, mode="stats"):
        if mode == "stats":
            self.stats().to_csv(EX_PATH + "Statistics.csv")

    def check_instance(self, r, type, fun):
        if type == "pd.Series":
            if not isinstance(r, pd.Series):
                raise TypeError(fun + "() can only take a pandas Series")
