from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import status, mixins
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from common.permissions import UserPermissions
from .serializers import BasicSerializer, TradeCalSerializer
from .filters import StockBasicFilter
from .stock_tushare import *
# 下面的库已经安装，但是在读取的时候会报错，它的作用是Gemini
import google.generativeai as genai
from decouple import config

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


class BasicView(GenericViewSet,
                mixins.ListModelMixin):
    """
    获取股票全部基础数据，通过过滤可以查询数据
    """
    queryset = StockBasic.objects.all()
    serializer_class = BasicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StockBasicFilter
    # 权限认证(设置认证用户才能查看当前信息）
    permission_classes = [IsAuthenticated, UserPermissions]


class TradeCalView(GenericViewSet,
                   mixins.ListModelMixin,
                   ):
    """
    输入日期（date）获取当天是否开盘，如果没有当天的数据，则插入当年的数据
    """
    queryset = TradeCal.objects.all()
    serializer_class = TradeCalSerializer

    def list(self, request, *args, **kwargs):
        # 获取查询参数中的日期
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': '日期参数缺失'}, status=status.HTTP_400_BAD_REQUEST)

        # 将字符串日期转换为日期对象
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': '日期格式错误，应为 YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        # 查询指定日期的数据
        queryset = TradeCal.objects.filter(cal_date=date_obj)

        # 如果数据库中没有数据，则调用 fetch_and_store_trade_data 函数插入数据
        if not queryset.exists():
            # 获取当前年份的开始和结束日期
            start_date = f"{date_obj.year}-01-01"
            end_date = f"{date_obj.year}-12-31"

            # 调用 fetch_and_store_trade_data 函数
            fetch_result = fetch_and_store_trade_data(start_date, end_date)
            if fetch_result is not True:
                return Response({'error': fetch_result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 重新查询指定日期的数据
            queryset = TradeCal.objects.filter(cal_date=date_obj)

        # 序列化查询结果并返回
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def analyze_data(request):
    """
    :param request: 前端穿过来的数据，包括start_date
    :return: 通过计算获得需要的符合策略的代码和日期
    """
    try:
        # 获取请求中的数据
        data = request.data
        # 获取开始计算日期
        start_date = data.get('start_date')
        # 获取股票交易日历的四天的数据
        trade_dates = get_previous_trade_days(trade_date=start_date)
        # 获取四天的数据并进行合并
        df = get_stock_data(trade_dates=trade_dates)
        # 筛选股票
        selected_df = filter_stocks_by_conditions(df)
        # 获取股票代码和最后一个交易日
        last_trade_dates_df = get_last_trade_dates(selected_df)
        print("最后一个交易日和股票代码")
        print(last_trade_dates_df)
        print(last_trade_dates_df.ts_code)
        print(selected_df)
        # print("================================================================")
        # analyzed_results = analyze_selected_stocks(selected_df)
        # print(analyzed_results)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": last_trade_dates_df}, status=status.HTTP_200_OK)


class StockListView(APIView):
    """
    分析传递过来的数据trade_date和ts_code，找到符合条件的最高，最低和平均买点
    现在的策略是给出当前时间往前一年的数据中进行查询连续两个涨停之前的三个连续非涨停价
    后续需要进行优化
    """

    def post(self, request):
        data = request.data
        trade_date = data.get("trade_date")
        ts_code = data.get("ts_code")
        ts_name = get_stock_name(ts_code)
        # 先查询数据库中是否已经存在数据
        try:
            existing_record = StockStrategyCode.objects.get(ts_code=ts_code, trade_date=trade_date)
            # 如果存在，返回数据库中的数据
            response_data = {
                "trade_date": trade_date,
                "ts_code": ts_code,
                "ts_name": ts_name,
                "highest_price": str(existing_record.highest_price),
                "lowest_price": str(existing_record.lowest_price),
                "average_price": str(existing_record.average_price),
                "message": "数据已存在，从数据库中获取"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except StockStrategyCode.DoesNotExist:
            # 如果没有记录，执行分析函数
            df = analyze_stock(ts_code, trade_date)

            # 返回分析结果
            return Response({
                "trade_date": trade_date,
                "ts_code": ts_code,
                "highest_price": df["highest_price"],
                "lowest_price": df["lowest_price"],
                "average_price": df["average_price"],
                "message": "数据已更新"
            }, status=status.HTTP_200_OK)


@api_view(['POST'])
def ask_gemini(request):
    # 获取 API Key
    # GOOGLE_API_KEY = config('gemini-api-key')  # 从 settings.py 中读取
    # print(GOOGLE_API_KEY)
    GOOGLE_API_KEY = 'AIzaSyBIn96AX6g7q2QmlSOYvdxqMeZGVTHO9E0'
    # 确保 API Key 已设置
    if not GOOGLE_API_KEY:
        return Response({'error': 'Google API Key 未设置'}, status=500)

    genai.configure(api_key=GOOGLE_API_KEY)

    # 设置模型，这里使用 gemini-pro 模型
    model = genai.GenerativeModel('gemini-pro')

    # 获取前端发送的问题
    question = request.data.get('question')

    # 确保问题不为空
    if not question:
        return Response({'error': '问题不能为空'}, status=400)

    # 调用 Gemini 模型
    try:
        response = model.generate_content(question)
        answer = response.text
        logger.info(f"Gemini answer: {answer}")  # 打印 Gemini 回答
        print(f"Gemini answer: {answer}")  # 打印 Gemini 回答
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    # 返回答案
    return Response({'answer': answer})
