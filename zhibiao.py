import baostock as bs
import pandas as pd
import talib as ta
import datetime
import numpy as np
from stock_pandas import StockDataFrame


code = 'sz.002241'
start_date = '2000-01-01'
end_date = '2022-03-25'

# global_dateday = None
global_dateday = '2022-04-07'
lg = bs.login()

params = []
kdj_params = '9,3,3'
with open('input_params.txt', 'r') as f:
    code_list = f.readlines()
    for index, item in enumerate(code_list):
        item = item.strip()
        if index == 2:
            kdj_params = item
        item = item.split(',')
        
        params += [int(i) for i in item]

    print(params)

def get_data(code, end_date, start_date='2000-01-01'):
    #Step1： 获取数据
    print(code)
    rs = bs.query_history_k_data_plus(code,
                                    "date,code,open,high,low,close,preclose,volume,amount,turn",
                                    start_date=start_date, end_date=end_date, frequency="d", adjustflag='2')#注意adjustflag取前复权
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(
        'float64')
    df = df.rename(columns={'date': 'datetime'})
    df.index = pd.DatetimeIndex(df['datetime'])
    # bs.logout()
    import time
    time_start=time.time()
    
    #Step2： 利用Pandas 计算MACD
    
    short_ema = df['close'].ewm(span=params[0]).mean()
    long_ema = df['close'].ewm(span=params[1]).mean()
    df.loc[:, 'DIFF'] = short_ema - long_ema
    df.loc[:, 'DEA'] = df['DIFF'].ewm(span=params[2]).mean()
    df.loc[:, 'MACD'] = 2 * (df['DIFF'] - df['DEA'])
    df["rsi_6"] = ta.RSI(df['close'], timeperiod=params[3])
    df["rsi_12"] = ta.RSI(df['close'], timeperiod=params[4])
    df["rsi_24"] = ta.RSI(df['close'], timeperiod=params[5])

    # low_list = df['low'].rolling(9, min_periods=9).min()
    # low_list.fillna(value=df['low'].expanding().min(), inplace=True)
    # high_list = df['high'].rolling(9, min_periods=9).max()
    # high_list.fillna(value = df['high'].expanding().max(), inplace=True)
    # rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    # df['k'] = pd.DataFrame(rsv).ewm(com=2).mean()
    # df['d'] = df['k'].ewm(com=2).mean()
    # df['j'] = 3 * df['k'] - 2 * df['d']
    time_end=time.time()
    format = '%Y-%m-%d'
    dateday = datetime.date.today().strftime(format)
    if global_dateday:
        dateday = global_dateday

    stock = StockDataFrame(df)
    kdj = stock[[f'kdj.k:{kdj_params}', f'kdj.d:{kdj_params}', f'kdj.j:{kdj_params}']]
    df['k'] = kdj.loc[dateday][0]
    df['d'] =  kdj.loc[dateday][1]
    df['j'] =  kdj.loc[dateday][2]

    # import ipdb;ipdb.set_trace()

    df_filter = df[df['datetime']==dateday]
    # import ipdb;ipdb.set_trace()
    return deal_df(df_filter)


def deal_df(df):
    df_new = pd.DataFrame()
    df_new['时间'] = df['datetime']
    df_new['股票代码'] = df['code']
    df_new['当前股价'] = df['close']
    df_new['开盘股价'] = df['open']
    df_new['涨跌幅'] = (df['close'] - df['preclose'].astype(float) ) / df['preclose'].astype(float) 
    df_new['收盘股价'] = df['preclose']
    df_new['最高价'] = df['high']
    df_new['最低价'] = df['low']
    df_new['成交量'] = df['volume']
    df_new['成交额'] = df['amount']
    df_new['换手（实）'] = df['turn']
    df_new['MACD'] = df['MACD']
    df_new['DIFF'] = df['DIFF']
    df_new['DEA'] = df['DEA']
    df_new['rsi_6'] = df['rsi_6']
    df_new['rsi_12'] = df['rsi_12']
    df_new['rsi_24'] = df['rsi_24']
    df_new['k'] = df['k']
    df_new['d'] = df['d']
    df_new['j'] = df['j']
    # import ipdb;ipdb.set_trace()
    return df_new
if __name__ == '__main__':
    get_data(code, start_date, end_date)