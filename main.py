import easyquotation
from zhibiao import get_data
import datetime
import pandas as pd

quotation = easyquotation.use('tencent')
format = '%Y-%m-%d'
format2 = '%Y%m%d'
dateday = datetime.date.today().strftime(format)
datefilename = datetime.date.today().strftime(format2)

order = ['时间','股票代码','股票名称','当前股价','开盘股价','收盘股价','涨跌幅', '最高价','最低价','成交量','成交额','换手（实）','MACD','DIFF','DEA','rsi_6','rsi_12','rsi_24','k','d','j']

def codeformat(code):
    return code.replace('.', '')

with open('input.txt', 'r') as f:
    code_list = f.read().split(',')
    code_list = [code.strip() for code in code_list]
    code_data = quotation.stocks(code_list, prefix=True)
    df_list = []
    for code in code_list:
        df = get_data(code, dateday)
        df['股票名称'] = code_data[codeformat(code)]['name']
        df = df[order]
        df_list.append(df)
    # import ipdb;ipdb.set_trace()
    df_all = pd.concat(df_list)
    df_all.to_csv(f'zb_{datefilename}.csv', encoding='utf-8')


 # 新浪 ['sina'] 腾讯 ['tencent', 'qq'] 
# print(quotation.real('002241')) # 支持直接指定前缀，如 'sh000001'
print( )
# print(quotation.market_snapshot(prefix=True))