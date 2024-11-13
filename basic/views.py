from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status, mixins
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import BasicSerializer
from .filters import StockBasicFilter
from .stock_tushare import *

# Register Tushare token once, rather than initializing in each request
ts.set_token(ts_token)
pro = ts.pro_api()


@api_view(['GET', 'POST'])
def basic_list(request):
    """
    GET: 获取股票基础数据
    POST: 从 Tushare 获取并创建新数据，如果数据库中已存在数据则先删除再写入。
    :param request:
    :return: Response object with JSON data
    """
    if request.method == 'GET':
        # 查询所有股票基础数据
        stock_basic = StockBasic.objects.all()
        if stock_basic.exists():
            serializer = BasicSerializer(stock_basic, many=True)
            return Response({"data": serializer.data, "code": 200, "message": "成功"}, status=status.HTTP_200_OK)
        else:
            return Response({"data": '', "code": 404, "message": "数据没有找到"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        # 从 Tushare 获取股票基本数据
        try:
            data = pro.query(
                'stock_basic', exchange='', list_status='L',
                fields='ts_code,symbol,name,area,market,list_status,exchange,industry,list_date'
            )

            if not data.empty:
                # 如果数据库中有数据，先删除所有记录
                if StockBasic.objects.exists():
                    StockBasic.objects.all().delete()

                # 将数据转换为 Django ORM 所需格式
                print("开始将数据进行转换")
                stock_data = [
                    StockBasic(
                        ts_code=row['ts_code'],
                        symbol=row['symbol'],
                        name=row['name'],
                        area=row['area'],
                        market=row['market'],
                        list_status=row['list_status'],
                        exchange=row['exchange'],
                        industry=row['industry'],
                        list_date=row['list_date'],

                    )
                    for _, row in data.iterrows()
                ]
                print("开始插入数据")
                # 使用 bulk_create 插入数据
                StockBasic.objects.bulk_create(stock_data, batch_size=500)
                print("开始序列化数据")
                # 序列化已创建的数据
                serializer = BasicSerializer(stock_data, many=True)
                return Response({"code": 200, "message": "数据创建成功", "data": serializer.data},
                                status=status.HTTP_201_CREATED)

            else:
                return Response({"code": 404, "message": "从 Tushare 没有获取到数据"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"code": 400, "message": "数据没有创建成功", "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_trade_status(request):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if not start_date:
        return Response({'error': 'Start_date不能为空'}, status=400)
    if not end_date:
        end_date = start_date

    # 格式化日期
    start_date = datetime.strptime(start_date, '%Y%m%d').strftime('%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d').strftime('%Y%m%d')

    # 获取当前年份
    current_year = datetime.now().year

    # 判断前端传递的日期是否是12月20日以后
    if int(start_date[:4]) == current_year and int(start_date[4:6]) >= 12 and int(start_date[6:8]) >= 20:
        # 查询下一年的数据（如果需要）
        next_year = current_year + 1
        next_year_start_date = f'{next_year}0101'
        next_year_end_date = f'{next_year}1231'

        # 检查下一年是否已有数据
        if not TradeCal.objects.filter(cal_date__gte=next_year_start_date, cal_date__lte=next_year_end_date).exists():
            # 插入下一年数据
            result = fetch_and_store_trade_data(next_year_start_date, next_year_end_date)
            if result is not True:
                return Response({'error': result}, status=500)

    # 检查当前年份是否已有数据
    current_year_start_date = f'{current_year}0101'
    current_year_end_date = f'{current_year}1231'
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


class BasicView(GenericViewSet,
                mixins.ListModelMixin):
    queryset = StockBasic.objects.all()
    serializer_class = BasicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StockBasicFilter


@api_view(['POST'])
def analyze_data(request):
    try:
        # 获取请求中的数据
        data = request.data
        ts_code = data.get('ts_code')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        # 获取股票的交易日历
        stock_date = get_previous_trade_days(trade_date=start_date)
        print("--------------------------------------------------------")
        print(stock_date)


        # 使用 Tushare 获取数据
        tushare_data = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df_code = get_non_st_stocks()

        # 执行数据分析
        analysis_result = {
            "code": tushare_data['ts_code'],
            "open": tushare_data['open'],
            "close": tushare_data['close']
        }

        # 返回分析结果
        return Response(analysis_result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
























