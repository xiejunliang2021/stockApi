"""
Django settings for stockApi project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
from datetime import timedelta
from pathlib import Path
# 下面是没有完成的安装，以后记得安装，它的作用是从环境变量中读取数据
from decouple import config
import oracledb
import os


try:
    oracledb.init_oracle_client()
except Exception as e:
    print(f"Oracle Client 初始化失败: {e}")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-w##)7-bapjl@1vpsauzj291_5#!=!#5nqx6lspel8_$th^r*u$"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 注册JWT权限校验工具
    'rest_framework_simplejwt',
    "rest_framework",
    # 解决跨域问题
    "corsheaders",
    # 权限校验
    # 'permission',
    # 过滤器
    'django_filters',
    "basic",
    "tactics",
    "users",
    # 自动生成接口文档
    'coreapi',
]

MIDDLEWARE = [
    # 支持跨域请
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "stockApi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "stockApi.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': config('DATABASE_NAME', default='default_db_name'),
#        'USER': config('USER_MYSQL',),
#        'PASSWORD': config('PASSWORD_MYSQL', ),
#        'HOST': config('HOST_MYSQL',),
#        'PORT': config('PORT_MYSQL'),
#        'OPTIONS': {
#            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#            'connect_timeout': 20,
#            'read_timeout': 60,
#            'write_timeout': 60,
#        },
#    },
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': config('NAME_ORACLE',),
        'USER': config('USER_ORACLE',),
        'PASSWORD': config('PASSWORD_ORACLE',),
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'wallet_location': config('WALLET_LOCATION',),
            'retry_count': 20,
            'retry_delay': 3,
            'ssl_server_dn_match': True
        },
    }

   }
#
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 允许所有用户跨域访问
CORS_ORIGIN_ALLOW_ALL = False
# 允许的跨域来源
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # 你的前端地址
]

# 如果需要支持带有凭证的请求
CORS_ALLOW_CREDENTIALS = True
# 指定自定义的用户模型
AUTH_USER_MODEL = 'users.User'

CSRF_COOKIE_NAME = "csrftoken"

# DRF配置鉴权方式
REST_FRAMEWORK = {
    # 配置登录鉴权方式
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    ),
    # 配置过滤器
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    # 接口文档的配置
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # 配置分页
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # 每页返回的数据条数
}

SIMPLE_JWT = {
    # 对于大部分情况，设置以下两项就可以了，以下为默认配置项目，可根据需要进行调整
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # Access Token的有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Refresh Token的有效期
    # 是否自动刷新Refresh Token
    'ROTATE_REFRESH_TOKENS': False,
    # 刷新Refresh Token时是否将旧Token加入黑名单，如果设置为False，则旧的刷新令牌仍然可以用于获取新的访问令牌。
    # 需要将'rest_framework_simplejwt.token_blacklist'加入到'INSTALLED_APPS'的配置中
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',  # 加密算法
    'SIGNING_KEY': SECRET_KEY,  # 签名密匙，这里使用Django的SECRET_KEY
    # 如为True，则在每次使用访问令牌进行身份验证时，更新用户最后登录时间
    "UPDATE_LAST_LOGIN": False,
    # 用于验证JWT签名的密钥返回的内容。可以是字符串形式的密钥，也可以是一个字典。
    "VERIFYING_KEY": "",
    "AUDIENCE": None,  # JWT中的"Audience"声明,用于指定该JWT的预期接收者。
    "ISSUER": None,  # JWT中的"Issuer"声明，用于指定该JWT的发行者。
    "JSON_ENCODER": None,  # 用于序列化JWT负载的JSON编码器。默认为Django的JSON编码器。
    "JWK_URL": None,  # 包含公钥的URL，用于验证JWT签名。
    "LEEWAY": 0,  # 允许的时钟偏差量，以秒为单位。用于在验证JWT的过期时间和生效时间时考虑时钟偏差。
    # 用于指定JWT在HTTP请求头中使用的身份验证方案。默认为"Bearer"
    "AUTH_HEADER_TYPES": ("Bearer",),
    # 包含JWT的HTTP请求头的名称。默认为"HTTP_AUTHORIZATION"
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    # 用户模型中用作用户ID的字段。默认为"id"。
    "USER_ID_FIELD": "id",
    # JWT负载中包含用户ID的声明。默认为"user_id"。
    "USER_ID_CLAIM": "user_id",
    # 用于指定用户身份验证规则的函数或方法。默认使用Django的默认身份验证方法进行身份验证。
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    #  用于指定可以使用的令牌类。默认为"rest_framework_simplejwt.tokens.AccessToken"。
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    # JWT负载中包含令牌类型的声明。默认为"token_type"。
    "TOKEN_TYPE_CLAIM": "token_type",
    # 用于指定可以使用的用户模型类。默认为"rest_framework_simplejwt.models.TokenUser"。
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    # JWT负载中包含JWT ID的声明。默认为"jti"。
    "JTI_CLAIM": "jti",
    # 在使用滑动令牌时，JWT负载中包含刷新令牌过期时间的声明。默认为"refresh_exp"。
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    # 滑动令牌的生命周期。默认为5分钟。
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    # 滑动令牌可以用于刷新的时间段。默认为1天。
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    # 用于生成访问令牌和刷新令牌的序列化器。
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    # 用于刷新访问令牌的序列化器。默认
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    # 用于验证令牌的序列化器。
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    # 用于列出或撤销已失效JWT的序列化器。
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    # 用于生成滑动令牌的序列化器。
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    # 用于刷新滑动令牌的序列化器。
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

# 使用自定义的认证类进行登录(登录是验证用户信息)
AUTHENTICATION_BACKENDS = [
    'common.authenticate.MyBackend',
    'permission.backends.PermissionBackend',
]

PERMISSION_CHECK_AUTHENTICATION_BACKENDS = False
PERMISSION_CHECK_TEMPLATES_OPTIONS_BUILTINS = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "debug.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


