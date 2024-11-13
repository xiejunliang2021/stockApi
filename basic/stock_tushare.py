# -*- coding: UTF-8 -*-
'''
@Project ：stockApi 
@File ：stock_tushare.py
@Author ：Anita_熙烨（路虽远，行则降至！事虽难，做则必成！）
@Date ：2024/11/12 10:39 
@JianShu : 
'''
import tushare as ts
from datetime import datetime, timedelta
from .config import ts_token
from .models import StockBasic, TradeCal


# 初始化 Tushare API
ts.set_token(ts_token)
pro = ts.pro_api()


def get_non_st_stocks():
    """获取符合条件的非 ST 股票的 ts_code 列表"""
    non_st_stocks = StockBasic.objects.exclude(
        name__contains='ST'
    ).exclude(
        # 在 Django ORM 中，startswith 和 endswith 只能接受单个字符串参数，而不能直接传入列表。
        ts_code__startswith='3'
    ).exclude(
        ts_code__startswith='688'
    ).exclude(
        ts_code__endswith='BJ'
    ).values_list('ts_code', flat=True)

    return list(non_st_stocks)


def get_last_four_trading_days():
    """获取最近的四个交易日日期"""
    today = datetime.today().strftime('%Y%m%d')
    trade_cal = pro.trade_cal(exchange='SSE', is_open='1', start_date='20230101', end_date=today)
    recent_trade_days = trade_cal.tail(4)['cal_date'].tolist()  # 获取最近的四个交易日
    return recent_trade_days


def fetch_and_store_trade_data(start_date, end_date):
    """
    使用 Tushare API 获取指定日期范围的交易日数据并存储到数据库中。
    """
    try:
        tushare_data = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        if tushare_data.empty:
            return None

        # 存储数据到数据库
        trade_cal_data = [
            TradeCal(
                exchange=row['exchange'],
                cal_date=row['cal_date'],
                is_open=str(row['is_open']),
                pretrade_date=row['pretrade_date']
            ) for index, row in tushare_data.iterrows()
        ]
        TradeCal.objects.bulk_create(trade_cal_data)
        return True
    except Exception as e:
        return f"Failed to fetch data from Tushare: {str(e)}"


def fetch_data_for_stocks(trade_days, ts_codes):
    """根据给定的交易日期和非 ST 股票代码获取日线数据"""
    all_data = []
    for ts_code in ts_codes:
        # 获取指定日期范围内的日线数据
        daily_data = pro.daily(ts_code=ts_code, start_date=trade_days[-1], end_date=trade_days[0])
        # 确保数据包含所有四个交易日
        if len(daily_data) == 4:
            all_data.append(daily_data)
    return all_data



