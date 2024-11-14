from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status, mixins
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import BasicSerializer, TradeCalSerializer
from .filters import StockBasicFilter
from .stock_tushare import *

# Register Tushare token once, rather than initializing in each request
ts.set_token(ts_token)
pro = ts.pro_api()


@api_view(['GET'])
def get_trade_status(request):
    """
    :param request: start_date，end_date
    :return: 来返回当前的股票日历，如果数据库中没有当前的数据则从tushare获取数据并写入到数据库中
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if not start_date:
        return Response({'error': 'Start_date不能为空'}, status=400)
    if not end_date:
        end_date = start_date

    # 格式化日期为 YYYY-MM-DD
    start_date = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')

    # 获取当前年份
    current_year = datetime.now().year

    # 判断前端传递的日期是否是12月20日以后
    if int(start_date[:4]) == current_year and int(start_date[5:7]) >= 12 and int(start_date[8:10]) >= 20:
        # 查询下一年的数据（如果需要）
        next_year = current_year + 1
        next_year_start_date = f'{next_year}-01-01'
        next_year_end_date = f'{next_year}-12-31'

        # 检查下一年是否已有数据
        if not TradeCal.objects.filter(cal_date__gte=next_year_start_date, cal_date__lte=next_year_end_date).exists():
            # 插入下一年数据
            result = fetch_and_store_trade_data(next_year_start_date, next_year_end_date)
            if result is not True:
                return Response({'error': result}, status=500)

    # 检查当前年份是否已有数据
    current_year_start_date = f'{current_year}-01-01'
    current_year_end_date = f'{current_year}-12-31'
    print(current_year_start_date)
    if not TradeCal.objects.filter(cal_date__gte=current_year_start_date, cal_date__lte=current_year_end_date).exists():
        # 插入当前年份的数据
        result = fetch_and_store_trade_data(current_year_start_date, current_year_end_date)
        if result is not True:
            return Response({'error': result}, status=500)

    # 查询指定日期范围的交易日历数据
    trade_data = TradeCal.objects.filter(cal_date__gte=start_date, cal_date__lte=end_date)

    if not trade_data:
        return Response({'error': '找不到指定范围内的数据'}, status=404)

    # 返回查询到的数据
    trade_data_list = [{
        'exchange': trade.exchange,
        'cal_date': trade.cal_date,
        'is_open': trade.is_open,
        'pretrade_date': trade.pretrade_date
    } for trade in trade_data]

    return Response(trade_data_list)


