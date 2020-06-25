import pyodbc
import pandas as pd
import numpy as np

def open_db_cnx(db):
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
    if db == "psg":
        cnx = pyodbc.connect("Driver={SQL Server};"
                             "Server=parcap-sql01;"
                             "Database=par_stage;"
                             "Trusted_Connection=yes;")
    if db == "lgy":
        cnx = pyodbc.connect("Driver={SQL Server};"
                             "Server=parcap-sql01;"
                             "Database=par;"
                             "Trusted_Connection=yes;")

    return cnx

def get_db_data(stmt, db):
    cnx = open_db_cnx(db)
    df = pd.read_sql(stmt, cnx)
    cnx.close()
    return df

sql = ({"trx": ("select * from par_masterdata.fact.transactions",
                "lgy")
        })

def get_par_db_transactions(s=sql["trx"]):
    return get_db_data(s[0], s[1])

'''
def get_focus_list_data(s=sql["mfl"]):
    return get_db_data(s[0] + s[1] + s[2], s[3])


def get_holdings(s=sql["pnl"]):
    df = get_db_data(s[0] + s[1], s[2])
    df.columns = ["date", "month", "year", "investment", "symbol", "class",
                  "class2", "company", "industry", "manager", "manager2",
                  "shares", "exposure", "mv", "profit"]
    df.set_index("date", inplace=True)
    return df

def get_target_prices(s=sql["tpx"]):
    df = get_db_data(s[0] + s[1], s[2])
    cols = ["date_valuation", "inv_group_id", "current_price",
            "target_price_calc", "exposure", "entity"]
    df = df[cols]
    df.columns = ["date", "ticker", "close_price", "target_price",
                  "exposure", "manager"]
    df.set_index("date", inplace=True)
    return df
'''