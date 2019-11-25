import pyodbc
import pandas as pd
import numpy as np

sql = ({"roe": ("select * from par_masterdata.python.",
                "manager_roes order by manager, date",
                "pmd"),
        "mfl": ("select * from par_masterdata.python.",
                "focus_list_data where date between '12/31/2005' and ",
                "'12/31/2019' order by methodology, manager, date, symbol ",
                "pmd"),
        "pnl": ("select * from par_masterdata.python.",
                "holdings order by manager, date",
                "pmd")
        })


def open_par_masterdata_connection(db):
    if db == "pmd":
        cnx = pyodbc.connect("Driver={SQL Server};"
                             "Server=parcap-sql01;"
                             "Database=par_masterdata;"
                             "Trusted_Connection=yes;")

    if db == "pbi":
        cnx = pyodbc.connect("Driver={SQL Server};"
                             "Server=parcap-sql01;"
                             "Database=par_bi;"
                             "Trusted_Connection=yes;")

    return cnx


def get_db_data(sql_stmt, db):
    cnx = open_par_masterdata_connection(db)
    df = pd.read_sql(sql_stmt, cnx)
    cnx.close()
    return df


def get_manager_roes(s=sql["roe"]):
    df = get_db_data(s[0] + s[1], s[2])
    df["ln_roe"] = np.log(1 + df.roe)
    df.columns = ["date", "month", "year", "manager",
                  "profit", "flow", "equity0", "roe", "ln_roe"]
    df.set_index("date", inplace=True)
    return df


def get_focus_list_data(s=sql["mfl"]):
    return get_db_data(s[0] + s[1] + s[2], s[3])


def get_holdings(s=sql["pnl"]):
    df = get_db_data(s[0] + s[1], s[2])
    df.columns = ["date", "month", "year", "investment", "symbol", "class",
                  "class2", "company", "industry", "manager", "manager2",
                  "shares", "exposure", "mv", "profit"]
    df.set_index("date", inplace=True)
    return df
