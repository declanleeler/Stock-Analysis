import numpy as np
import pandas as pd

import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'sql_helpers')))

from sql_helpers.sql_query import query_table
from sql_helpers.sql_upload import insert_data
from datetime import date
from dateutil.relativedelta import relativedelta

def suggested_reweightings(ti):
    """
    Compares and outputs the recommended adjusted weights
    """
    today = date.today().strftime("%m/%d/%Y")

    three_months_ago_d = date.today() + relativedelta(months=-3)
    three_months_ago = three_months_ago_d.strftime("%m/%d/%Y")

    one_months_ago_d = date.today() + relativedelta(months=-1)
    one_months_ago = one_months_ago_d.strftime("%m/%d/%Y")
    one_months_ago_minus_one_day_d = one_months_ago_d + relativedelta(days=-1)
    one_months_ago_minus_one_day = one_months_ago_minus_one_day_d.strftime("%m/%d/%Y")

    optimized_df = pd.read_json(ti.xcom_pull(key="optimized_weights", task_ids=["optimize_portfolio"])[0])

    # load weights from stock holdings
    stock_holdings = query_table("IS3107_STOCKS_DATA", "STOCKS_DATA", "STOCK_HOLDINGS", three_months_ago_d, date.today())
    original_weights = list(stock_holdings.TOP10_WEIGHT)
    tickers = list(stock_holdings.TICKER)
    print('tickers')
    print(tickers)
    reweighting = pd.DataFrame(columns = ["Ticker", "Adjustment"])
    reweighting["Ticker"]= tickers
    
    for ticker in tickers:
        reweighting.loc[reweighting["Ticker"]==ticker,1] = (original_weights[original_weights["ticker"]==ticker].weight) -optimized_df[ticker] 

    print("reweighting")
    print(reweighting)

    ### Push into XCOM 
    ti.xcom_push(key="reweighting", value=reweighting.to_json())

    


