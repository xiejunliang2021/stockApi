from django.db import models

# Create your models here.


class StockBasic(models.Model):
    """ 股票代码 """
    ts_code = models.CharField(max_length=10, primary_key=True, verbose_name='ts代码')
    symbol = models.CharField(max_length=10, verbose_name='股票代码')
    name = models.CharField(max_length=20, verbose_name='股票名称')
    area = models.CharField(max_length=20, verbose_name='地区', null=True, blank=True)
    market = models.CharField(max_length=20, verbose_name='市场类别', null=True, blank=True)
    list_status = models.CharField(max_length=5, verbose_name='上市状态', null=True, blank=True)
    exchange = models.CharField(max_length=20, verbose_name='交易所', null=True, blank=True)
    industry = models.CharField(max_length=20, verbose_name='所属行业', null=True, blank=True)
    list_date = models.CharField(max_length=20, verbose_name='上市日期')

    class Meta:
        db_table = 'code'
        verbose_name = '股票基础信息表'

    def __str__(self):
        return self.name



class TradeCal(models.Model):
    exchange = models.CharField(max_length=10, verbose_name='交易所')
    cal_date = models.DateField(verbose_name='日历日期')
    is_open = models.IntegerField(verbose_name='是否交易')
    pretrade_date = models.DateField(verbose_name='上一个交易日')

    class Meta:
        db_table = 'trade_cal'
        verbose_name = '交易日历表'


class Daily(models.Model):
    ts_code = models.ForeignKey(
        StockBasic,
        to_field='ts_code',  # 指定外键字段为 ts_code
        on_delete=models.CASCADE,
        db_column='ts_code_id',  # 数据库中列名保持一致
        verbose_name='股票代码'
    )
    trade_date = models.CharField(max_length=10, verbose_name='交易日期')
    open = models.DecimalField(verbose_name='开盘价', decimal_places=2, max_digits=7, default=0)
    close = models.DecimalField(verbose_name='收盘价', decimal_places=2, max_digits=7, default=0)
    high = models.DecimalField(verbose_name='最高价', decimal_places=2, max_digits=7, default=0)
    low = models.DecimalField(verbose_name='最低价', decimal_places=2, max_digits=7, default=0)
    pre_close = models.DecimalField(verbose_name='昨收价', decimal_places=2, max_digits=7, default=0)
    change = models.DecimalField(verbose_name='涨跌额', decimal_places=2, max_digits=7, default=0)
    pch_chg = models.DecimalField(verbose_name='涨跌幅', decimal_places=2, max_digits=7, default=0)
    vol = models.DecimalField(verbose_name='成交量', decimal_places=2, max_digits=12, default=0)
    amount = models.DecimalField(verbose_name='成交额', decimal_places=2, max_digits=12, default=0)

    class Meta:
        db_table = 'daily'
        verbose_name = '股票日线行情表'

    def __str__(self):
        return self.ts_code


class StockStrategyCode(models.Model):
    """
    如果你希望同一支股票在某个交易日只有一条记录，可以在模型中添加联合唯一约束，确保 ts_code 和 trade_date 的组合唯一
    """
    ts_code = models.ForeignKey(
        to=StockBasic,
        verbose_name='股票代码',
        on_delete=models.CASCADE
    )
    trade_date = models.CharField(max_length=10, verbose_name='交易日期')
    is_success = models.BooleanField(verbose_name="是否成功", default=False)
    highest_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="最高买点")
    lowest_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="最低买点")
    average_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="平均买点")

    class Meta:
        # 这种方式能避免重复插入数据，同时可以根据需要更新现有数据
        constraints = [
            models.UniqueConstraint(fields=['ts_code', 'trade_date'], name='unique_ts_code_trade_date')
        ]
        # 如果你的表中数据量较大，建议对 ts_code 和 trade_date 添加索引以提高查询效率
        indexes = [
            models.Index(fields=['ts_code'], name='idx_ts_code'),
            models.Index(fields=['trade_date'], name='idx_trade_date'),
        ]




































