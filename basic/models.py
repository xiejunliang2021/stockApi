from django.db import models

# Create your models here.


class StockBasic(models.Model):
    """ 股票代码 """
    ts_code = models.CharField(max_length=10, verbose_name='ts代码')
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

    # 在数据返回的时候返回股票名称
    def __str__(self):
        return self.name


class TradeCal(models.Model):
    exchange = models.CharField(max_length=10, verbose_name='交易所')
    cal_date = models.CharField(max_length=20, verbose_name='日历日期')
    is_open = models.CharField(max_length=10, verbose_name='是否交易')
    pretrade_date = models.CharField(max_length=10, verbose_name='上一个交易日')

    class Meta:
        db_table = 'trade_cal'
        verbose_name = '交易日历表'


class Daily(models.Model):
    ts_code = models.ForeignKey(to=StockBasic, verbose_name='股票代码', on_delete=models.CASCADE)
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



































