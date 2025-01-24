# stockApi

## 程序流程
    **现在里面的代码写的非常杂乱，想到哪里写道哪里，以后需要做的是将代码细化**

### 获取股票基本信息


### 获取股票的基本数据


### 对获取的数据进行分析






### 安装必要的包
    - conda install pandas
    - pip install django-filter
    - pip install coreapi
    - pip install tushare

### 添加了查询当天是否开盘的功能
    - 数据查询的日期start_date和end_dates(start_date为必须输入,如果只输入start_date则查询当天的数据）

### 修改了模型类trade_cal里面的字段类型


### 添加股票基本数据
    - 使用post请求发送数据 /api/basics/tushare/basic/

### 获取股票全部基础数据，通过过滤可以查询数据
    - /api/basics/basic/

### 输入日期（date）获取当天是否开盘，如果没有当天的数据，则插入当年的数据
    - exp: /api/basics/date_is_open/?2022-03-05

### 分析传递过来的数据trade_date和ts_code，找到符合条件的最高，最低和平均买点
    - /api/basics/get_stock_list/


### TODU：
1.完成analyze_data函数，
2.重新写一个视图函数，将对analyze_data获取的代码进行分析

获取数据-->清洗数据-->分析数据
chatgpt给出的代码
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# 假设你已经在 config 中设置了 Tushare token
from config import TUSHARE_TOKEN

# 设置 Tushare token
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

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
    
    return {
        "highest_price": highest_price,
        "lowest_price": lowest_price,
        "average_price": average_price
    }

# 示例调用
ts_code = "000001.SZ"  # 替换为实际股票代码
strategy_date = "20241118"  # 替换为实际策略日期

try:
    result = analyze_stock(ts_code, strategy_date)
    print(result)
except ValueError as e:
    print(f"Error: {e}")




























=======
>>>>>>> 9bff5c9937f2a2f14890e5c916290724c6a0707c




