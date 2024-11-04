from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status, mixins
from django_filters.rest_framework import DjangoFilterBackend
import tushare as ts
from .models import StockBasic
from .serializers import BasicSerializer
from .config import ts_token
from .filters import StockBasicFilter

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
    queryset = StockBasic.objects.all()
    serializer_class = BasicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StockBasicFilter




























