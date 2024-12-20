# Generated by Django 4.2.16 on 2024-11-04 03:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StockBasic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts_code', models.CharField(max_length=10, verbose_name='ts代码')),
                ('symbol', models.CharField(max_length=10, verbose_name='股票代码')),
                ('name', models.CharField(max_length=20, verbose_name='股票名称')),
                ('area', models.CharField(blank=True, max_length=20, null=True, verbose_name='地区')),
                ('market', models.CharField(default='1', max_length=20, verbose_name='市场类别')),
                ('list_status', models.CharField(default='L', max_length=5, verbose_name='上市状态')),
                ('exchange', models.CharField(max_length=20, verbose_name='交易所')),
                ('industry', models.CharField(default='1', max_length=20, verbose_name='所属行业')),
                ('list_date', models.CharField(max_length=20, verbose_name='上市日期')),
            ],
            options={
                'verbose_name': '股票基础信息表',
                'db_table': 'code',
            },
        ),
        migrations.CreateModel(
            name='TradeCal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange', models.CharField(max_length=6, verbose_name='交易所')),
                ('cal_date', models.CharField(max_length=20, verbose_name='日历日期')),
                ('is_open', models.CharField(max_length=6, verbose_name='是否交易')),
                ('pretrade_date', models.CharField(max_length=6, verbose_name='上一个交易日')),
            ],
            options={
                'verbose_name': '交易日历表',
                'db_table': 'trade_cal',
            },
        ),
        migrations.CreateModel(
            name='Daily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_date', models.CharField(max_length=10, verbose_name='交易日期')),
                ('open', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='开盘价')),
                ('close', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='收盘价')),
                ('high', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='最高价')),
                ('low', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='最低价')),
                ('pre_close', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='昨收价')),
                ('change', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='涨跌额')),
                ('pch_chg', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='涨跌幅')),
                ('vol', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='成交量')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='成交额')),
                ('ts_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='basic.stockbasic', verbose_name='股票代码')),
            ],
            options={
                'verbose_name': '股票日线行情表',
                'db_table': 'daily',
            },
        ),
    ]
