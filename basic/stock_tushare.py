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
from .models import StockBasic, TradeCal, StockStrategyCode
from .serializers import TradeCalSerializer
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import logging
import numpy as np
from typing import List, Tuple, Dict
from decimal import Decimal
from django.db import transaction

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
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
        # 如果 start_date 和 end_date 是日期对象，则将其转换为字符串格式
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y%m%d')
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y%m%d')
        if "-" in start_date:
            start_date = start_date.replace("-", "")
        if "-" in end_date:
            end_date = end_date.replace("-", "")
        print("tushare的日期数据")
        print(start_date, end_date)
        # 使用转换后的字符串日期格式请求数据
        tushare_data = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)

        if tushare_data.empty:
            print("Tushare 返回空数据")
            return None

        # 存储数据到数据库
        trade_cal_data = []
        for index, row in tushare_data.iterrows():
            # 将 cal_date 和 pretrade_date 转换为日期格式
            cal_date = datetime.strptime(row['cal_date'], '%Y%m%d').date()
            pretrade_date = datetime.strptime(row['pretrade_date'], '%Y%m%d').date() if row['pretrade_date'] else None

            # 创建 TradeCal 实例
            trade_cal = TradeCal(
                exchange=row['exchange'],
                cal_date=cal_date,
                is_open=int(row['is_open']),
                pretrade_date=pretrade_date
            )
            trade_cal_data.append(trade_cal)

        # 批量插入数据
        TradeCal.objects.bulk_create(trade_cal_data)
        print("数据已成功插入数据库")
        return True
    except Exception as e:
        print(f"发生异常: {e}")
        return f"Failed to fetch data from Tushare: {str(e)}"


def get_previous_trade_days(trade_date, days=4):
    """
    获取指定日期（含）之前的N个交易日期。

    参数:
        trade_date (str): 日期字符串，格式为 YYYY-MM-DD
        days (int, optional): 需要获取的交易日数量，默认为4天

    返回值:
        list: 日期列表，格式为 YYYY-MM-DD
    """
    # 将 trade_date 转换为日期格式
    trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()

    # 只获取日期字段，并转换为字符串格式
    trade_dates = (
        TradeCal.objects
            .filter(cal_date__lte=trade_date, is_open='1')
            .order_by('-cal_date')
            .values_list('cal_date', flat=True)[:days]
    )

    # 将日期转换为字符串格式
    return [date.strftime("%Y-%m-%d") for date in trade_dates]


class DataValidator:
    """数据验证类"""

    @staticmethod
    def validate_date_data(df: pd.DataFrame, date: str) -> bool:
        """验证某一天的数据是否完整有效"""
        if df.empty:
            logger.warning(f"{date} 数据为空")
            return False

        # 检查必要字段是否存在
        required_columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.warning(f"{date} 数据缺少必要字段: {missing_cols}")
            return False

        # 检查数值是否合理
        if df['close'].isnull().any() or df['vol'].isnull().any():
            logger.warning(f"{date} 存在空值")
            return False

        # 检查价格是否合理
        if (df['close'] <= 0).any() or (df['high'] < df['low']).any():
            logger.warning(f"{date} 存在异常价格数据")
            return False

        return True

    @staticmethod
    def clean_and_validate_data(df: pd.DataFrame) -> pd.DataFrame:
        """清洗和验证数据"""
        try:
            # 删除重复数据
            df = df.drop_duplicates(['ts_code', 'trade_date'])

            # 处理空值
            numeric_columns = ['open', 'high', 'low', 'close', 'vol', 'up_limit', 'down_limit']
            df[numeric_columns] = df[numeric_columns].replace([np.inf, -np.inf], np.nan)

            # 检查异常值
            df = df[
                (df['close'] > 0) &  # 价格为正
                (df['high'] >= df['close']) &  # 最高价大于等于收盘价
                (df['low'] <= df['close']) &  # 最低价小于等于收盘价
                (df['vol'] >= 0)  # 成交量为正
                ]

            return df

        except Exception as e:
            logger.error(f"数据清洗过程中发生错误: {str(e)}")
            return pd.DataFrame()


@lru_cache(maxsize=128)
def fetch_daily_data(date_str: str, ts_code: str = None) -> pd.DataFrame:
    """
    获取日线数据，支持全部股票或单个股票

    参数:
    - date_str: 日期字符串
    - pro: tushare pro 实例
    - ts_code: 可选，股票代码

    返回:
    DataFrame: 股票日线数据
    """
    try:
        if ts_code:
            return pro.daily(trade_date=date_str, ts_code=ts_code)
        else:
            return pro.daily(trade_date=date_str)
    except Exception as e:
        logger.error(f"获取日线数据错误 {date_str}, {ts_code}: {str(e)}")
        return pd.DataFrame()


@lru_cache(maxsize=128)
def fetch_limit_data(date_str: str, ts_code: str = None) -> pd.DataFrame:
    """
    获取涨跌停数据，支持全部股票或单个股票

    参数:
    - date_str: 日期字符串
    - pro: tushare pro 实例
    - ts_code: 可选，股票代码

    返回:
    DataFrame: 股票涨跌停数据
    """
    try:
        if ts_code:
            return pro.stk_limit(trade_date=date_str, ts_code=ts_code)
        else:
            return pro.stk_limit(trade_date=date_str)
    except Exception as e:
        logger.error(f"获取涨跌停数据错误 {date_str}, {ts_code}: {str(e)}")
        return pd.DataFrame()


def process_single_date(date: str, valid_ts_codes: List[str]) -> Tuple[str, pd.DataFrame]:
    """处理单个日期的数据"""
    try:
        date_str = date.replace('-', '')

        # 获取数据
        daily_df = fetch_daily_data(date_str)
        limit_df = fetch_limit_data(date_str)

        # 验证数据
        if not DataValidator.validate_date_data(daily_df, date):
            return date, pd.DataFrame()

        # 过滤股票
        daily_df = daily_df[daily_df['ts_code'].isin(valid_ts_codes)]

        # 合并数据
        if not limit_df.empty:
            merged_df = pd.merge(
                daily_df,
                limit_df[['ts_code', 'up_limit', 'down_limit']],
                on='ts_code',
                how='left'
            )
        else:
            merged_df = daily_df

        return date, merged_df

    except Exception as e:
        logger.error(f"处理日期 {date} 时发生错误: {str(e)}")
        return date, pd.DataFrame()


def get_stock_data(trade_dates: List[str]) -> pd.DataFrame:
    """
    获取指定交易日的所有股票数据和涨跌停价格，并进行清洗和合并。

    参数:
        trade_dates (list): 交易日期列表

    返回值:
        pandas.DataFrame: 清洗并合并后的股票数据，包含涨跌停价格
    """

    # 获取非ST股票代码列表
    valid_ts_codes = get_non_st_stocks()

    # 存储所有日期的数据
    all_data = []

    # 使用线程池进行并行处理
    with ThreadPoolExecutor(max_workers=min(len(trade_dates), 5)) as executor:
        # 提交所有任务
        future_to_date = {
            executor.submit(process_single_date, date, valid_ts_codes): date
            for date in trade_dates
        }

        # 获取结果
        for future in as_completed(future_to_date):
            date = future_to_date[future]
            try:
                _, df = future.result()
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                logger.error(f"处理日期 {date} 的结果时发生错误: {str(e)}")

    # 合并所有数据
    if all_data:
        # 合并数据
        result = pd.concat(all_data, ignore_index=True)

        # 数据清洗和验证
        result = DataValidator.clean_and_validate_data(result)

        if result.empty:
            logger.error("数据清洗后结果为空")
            return pd.DataFrame()

        # 按照交易日期和股票代码排序
        result = result.sort_values(['trade_date', 'ts_code'], ascending=[False, True])

        # 添加涨跌停判断列
        result['hit_up_limit'] = result.apply(
            lambda x: np.isclose(x['close'], x['up_limit'], rtol=1e-5)
            if pd.notnull(x['up_limit']) else False,
            axis=1
        )
        result['hit_down_limit'] = result.apply(
            lambda x: np.isclose(x['close'], x['down_limit'], rtol=1e-5)
            if pd.notnull(x['down_limit']) else False,
            axis=1
        )

        logger.info(f"成功处理 {len(trade_dates)} 个交易日的数据")
        return result
    else:
        logger.error("====未能获取任何有效数据====")
        return pd.DataFrame()


def get_stock_history(end_date, days=4):
    """
    获取指定日期范围内的所有符合条件的股票数据。

    参数:
        end_date (str): 结束日期，格式为 YYYY-MM-DD
        days (int): 需要获取的天数

    返回值:
        pandas.DataFrame: 合并后的股票数据
    """
    # 获取交易日期列表
    trade_dates = get_previous_trade_days(end_date, days)

    # 获取并合并股票数据
    stock_data = get_stock_data(trade_dates=trade_dates)

    return stock_data


def get_last_trade_dates(selected_df: pd.DataFrame) -> pd.DataFrame:
    """
    获取筛选出的每只股票的股票代码（ts_code）和最后一个交易日（trade_date）。

    参数:
        selected_df (pandas.DataFrame): 筛选出的符合条件的股票数据

    返回:
        pandas.DataFrame: 包含每只股票的ts_code和最后一个交易日的DataFrame
    """
    # 获取每只股票的最后一个交易日
    last_trade_dates = selected_df.groupby('ts_code')['trade_date'].max().reset_index()

    return last_trade_dates


def filter_stocks_by_conditions(df: pd.DataFrame) -> pd.DataFrame:
    """
    筛选符合条件的股票数据：
    1. 第一天和第二天的涨停价（up_limit）等于收盘价（close）
    2. 第三天和第四天的收盘价（close）小于开盘价（open）

    参数:
        df (pandas.DataFrame): 输入的股票数据，包含至少四个交易日的数据

    返回:
        pandas.DataFrame: 筛选后的符合条件的股票数据
    """

    selected_stocks = []

    # 按股票代码（ts_code）分组并处理每组数据
    for ts_code, stock_data in df.groupby('ts_code'):
        # 确保每只股票的数据至少有四天
        if len(stock_data) >= 4:
            # 按交易日期升序排序
            stock_data = stock_data.sort_values('trade_date', ascending=True)

            # 检查条件：第一天和第二天的涨停价等于收盘价
            condition_1 = np.isclose(stock_data.iloc[0]['up_limit'], stock_data.iloc[0]['close'], rtol=1e-5) and \
                          np.isclose(stock_data.iloc[1]['up_limit'], stock_data.iloc[1]['close'], rtol=1e-5)

            # 检查条件：第三天和第四天的收盘价小于开盘价
            condition_2 = stock_data.iloc[2]['close'] < stock_data.iloc[2]['open'] and \
                          stock_data.iloc[3]['close'] < stock_data.iloc[3]['open']

            # 如果符合所有条件，将该股票数据添加到选中股票列表
            if condition_1 and condition_2:
                selected_stocks.append(stock_data)

    # 合并筛选后的所有股票数据
    if selected_stocks:
        return pd.concat(selected_stocks, ignore_index=True)
    else:
        return pd.DataFrame()  # 如果没有符合条件的股票，返回空的 DataFrame


def get_stock_data_30_days(ts_code: str, end_date: str) -> pd.DataFrame:
    """
    通过Tushare获取指定股票代码在end_date往前30天的交易数据。
    """
    try:
        # 获取最近 30 天的交易数据
        trade_data = pro.daily(ts_code=ts_code, end_date=end_date, limit=30)
        if trade_data is None or trade_data.empty:
            print(f"未能获取到 {ts_code} 在 {end_date} 前 30 天的交易数据")
            return pd.DataFrame()

        # 获取涨跌停价格
        limit_data = pro.stk_limit(ts_code=ts_code, end_date=end_date, limit=30)
        if limit_data is None or limit_data.empty:
            print(f"未能获取到 {ts_code} 的涨跌停价格数据")
            return pd.DataFrame()

        # 按日期升序排列
        trade_data = trade_data.sort_values('trade_date', ascending=True)
        limit_data = limit_data.sort_values('trade_date', ascending=True)

        # 合并交易数据与涨跌停价格
        merged_data = pd.merge(trade_data, limit_data, on=['ts_code', 'trade_date'], how='inner')

        # 返回合并后的数据
        return merged_data

    except Exception as e:
        print(f"获取数据时发生错误: {e}")
        return pd.DataFrame()


def analyze_selected_stocks(selected_df: pd.DataFrame) -> pd.DataFrame:
    """
    对筛选出的股票数据进行进一步分析，计算第一买点、第二买点和第三买点。

    参数:
        selected_df (pandas.DataFrame): 筛选出的符合条件的股票数据

    返回:
        pandas.DataFrame: 包含股票代码、交易日期和三个买点的分析结果
    """
    results = []

    for _, row in selected_df.iterrows():
        ts_code = row['ts_code']
        end_date = row['trade_date']
        print("ts_code: " + ts_code)
        print("end_date: " + end_date)

        # 获取该股票往前30天的数据
        stock_data_30_days = get_stock_data_30_days(ts_code, end_date)

        # 找到no_up_limit_date，即连续两天涨停价之前的第一个非涨停日
        no_up_limit_date = None
        for i in range(len(stock_data_30_days) - 2):
            if stock_data_30_days.iloc[i]['hit_up_limit'] == False and \
                    stock_data_30_days.iloc[i + 1]['hit_up_limit'] == True and \
                    stock_data_30_days.iloc[i + 2]['hit_up_limit'] == True:
                no_up_limit_date = stock_data_30_days.iloc[i]['trade_date']
                break

        # 如果没有找到符合条件的no_up_limit_date，跳过此股票
        if not no_up_limit_date:
            continue

        # 检查no_up_limit_date前10天是否有涨停
        no_up_limit_index = stock_data_30_days[stock_data_30_days['trade_date'] == no_up_limit_date].index[0]
        if any(stock_data_30_days.iloc[max(0, no_up_limit_index - 10):no_up_limit_index]['hit_up_limit']):
            continue

        # 获取no_up_limit_date前3天的数据
        if no_up_limit_index < 3:
            continue  # 确保有足够数据
        stock_data = stock_data_30_days.iloc[no_up_limit_index - 3:no_up_limit_index]

        # 计算买点
        first_buy_point = stock_data['high'].max()
        second_buy_point = (stock_data['high'].max() + stock_data['low'].min()) / 2
        third_buy_point = stock_data['low'].min()

        # 将结果加入列表
        results.append({
            'ts_code': ts_code,
            'trade_date': end_date,
            'first_buy_point': first_buy_point,
            'second_buy_point': second_buy_point,
            'third_buy_point': third_buy_point
        })

    return pd.DataFrame(results)


def insert_or_update_stock_strategy(ts_code, trade_date, highest_price, lowest_price, average_price, is_success):
    try:
        # 外键处理：确保 ts_code 是 StockBasic 的实例或主键
        if isinstance(ts_code, str):  # 如果是字符串主键
            ts_code_instance = StockBasic.objects.get(ts_code=ts_code)
        elif isinstance(ts_code, StockBasic):  # 如果是实例
            ts_code_instance = ts_code
        else:
            raise ValueError("无效的 ts_code 参数，必须是字符串或 StockBasic 实例")

        # 开始事务
        with transaction.atomic():
            # 尝试查找是否存在符合条件的记录
            obj = StockStrategyCode.objects.filter(ts_code=ts_code_instance, trade_date=trade_date).first()

            if obj:
                # 检查是否完全一致
                if (
                        Decimal(obj.highest_price) == Decimal(highest_price) and
                        Decimal(obj.lowest_price) == Decimal(lowest_price) and
                        Decimal(obj.average_price) == Decimal(average_price) and
                        obj.is_success == is_success
                ):
                    # 数据完全一致，直接返回
                    print("数据完全一致，跳过更新")
                    return obj, False
                else:
                    # 数据不一致，更新记录
                    obj.highest_price = highest_price
                    obj.lowest_price = lowest_price
                    obj.average_price = average_price
                    obj.is_success = is_success
                    obj.save()
                    print("数据已更新")
                    return obj, True
            else:
                # 数据不存在，插入新记录
                obj = StockStrategyCode.objects.create(
                    ts_code=ts_code_instance,
                    trade_date=trade_date,
                    highest_price=highest_price,
                    lowest_price=lowest_price,
                    average_price=average_price,
                    is_success=is_success
                )
                print("新记录已插入")
                return obj, True

    except StockBasic.DoesNotExist:
        print(f"StockBasic 中未找到 ts_code={ts_code}")
        return None, False
    except Exception as e:
        print(f"错误发生：{e}")
        return None, False

def analyze_stock(ts_code, strategy_date):
    """
    分析给定股票代码在策略日期之前的特定价格区间
    :param ts_code: 股票代码
    :param strategy_date: 策略日期（YYYYMMDD）
    :return: dict 包括最高价、最低价和平均价
    """
    # 确定日期范围：从策略日期往前一年
    strategy_date_obj = datetime.strptime(strategy_date, "%Y%m%d")
    start_date = (strategy_date_obj - timedelta(days=365)).strftime("%Y%m%d")

    # 获取股票的日线数据
    daily_df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=strategy_date)
    if daily_df.empty:
        raise ValueError(f"No daily data found for {ts_code} between {start_date} and {strategy_date}")

    # 获取股票的涨跌停数据
    limit_df = pro.stk_limit(ts_code=ts_code, start_date=start_date, end_date=strategy_date)
    if limit_df.empty:
        raise ValueError(f"No limit data found for {ts_code} between {start_date} and {strategy_date}")

    # 合并日线数据和涨跌停数据
    merged_df = pd.merge(daily_df, limit_df, on=["ts_code", "trade_date"], how="inner")

    # 标记涨停和跌停
    merged_df['is_limit_up'] = (merged_df['close'] >= merged_df['up_limit']).astype(int)
    merged_df['is_limit_down'] = (merged_df['close'] <= merged_df['down_limit']).astype(int)

    # 按日期降序排序
    merged_df = merged_df.sort_values(by="trade_date", ascending=False)

    # 筛选策略日期之前的连续两个涨停日期
    limit_up_days = merged_df[merged_df['is_limit_up'] == 1].head(2)
    if len(limit_up_days) < 2:
        raise ValueError("Less than 2 consecutive limit-up days found.")

    # 获取第一个涨停日期之前的非涨停数据
    first_limit_date = limit_up_days.iloc[0]['trade_date']
    non_limit_data = merged_df[(merged_df['trade_date'] < first_limit_date) & (merged_df['is_limit_up'] == 0)]

    # 获取前三个连续非涨停的交易日
    non_limit_days = non_limit_data.head(3)
    if len(non_limit_days) < 3:
        raise ValueError("Less than 3 non-limit days before the first limit-up day.")

    # 计算最高价、最低价和平均价
    highest_price = non_limit_days['high'].max()
    lowest_price = non_limit_days['low'].min()
    average_price = non_limit_days['close'].mean()
    trade_date = strategy_date
    insert_or_update_stock_strategy(ts_code, trade_date, highest_price, lowest_price, average_price, is_success=False)

    return {
        "highest_price": highest_price,
        "lowest_price": lowest_price,
        "average_price": average_price
    }












































































