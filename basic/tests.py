from django.test import TestCase

import os
import oracledb


def test_connection():
    # 打印环境变量进行验证
    print("TNS_ADMIN:", os.getenv('TNS_ADMIN'))

    # 设置钱包位置
    wallet_location = r"D:\Api\stockApi\stockApi\Wallet_Mhuabenwuxin"  # 替换为你的实际路径
    os.environ["TNS_ADMIN"] = wallet_location

    try:
        # 使用 thin 模式连接
        connection = oracledb.connect(
            user="huabenwuxin_mlb",
            password="19881215Xjl_",
            dsn="geb977e4f1273f7_mhuabenwuxin_high",
            config_dir=wallet_location,
            wallet_location=wallet_location,
            wallet_password=None
        )
        print("连接成功!")

        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        result = cursor.fetchone()
        print("数据库时间:", result[0])

        cursor.close()
        connection.close()

    except oracledb.Error as error:
        print("连接错误:", error)
        # 打印更详细的错误信息
        print("错误类型:", type(error))
        print("错误详情:", str(error))


def test_connection_thick():
    """使用 thick 模式进行连接测试"""
    try:
        # 初始化 thick 模式
        oracledb.init_oracle_client(
            lib_dir=r"D:\oracle\instantclient-basic-windows.x64-19.25.0.0.0dbru")  # 替换为你的 Oracle Client 路径

        # 使用 thick 模式连接
        connection = oracledb.connect(
            user="huabenwuxin_mlb",
            password="19881215Xjl_",
            dsn="geb977e4f1273f7_mhuabenwuxin_high"
        )
        print("Thick 模式连接成功!")

        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        result = cursor.fetchone()
        print("数据库时间:", result[0])

        cursor.close()
        connection.close()

    except oracledb.Error as error:
        print("Thick 模式连接错误:", error)


if __name__ == "__main__":
    print("\n正在测试 thin 模式连接...")
    test_connection()

    print("\n正在测试 thick 模式连接...")
    test_connection_thick()