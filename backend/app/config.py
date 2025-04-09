import os

class Config:
    # 存储类型: 'local'（本地存储） | 'minio'（MinIO） | 'nas'（NAS）
    STORAGE_TYPE = 'local'  

    # 本地存储路径
    LOCAL_STORAGE_DIR = '/data/upload'  
    if not os.path.exists(LOCAL_STORAGE_DIR):
        os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

    # MinIO 配置todo
    MINIO_ENDPOINT = 'http://172.16.20.153:9000'
    MINIO_ACCESS_KEY = 'minioadmin'
    MINIO_SECRET_KEY = 'minioadmin'
    MINIO_BUCKET_NAME = 'logs'

    # NAS 配置 todo
    NAS_STORAGE_PATH = '/mnt/nas/logs'  # 挂载的 NAS 目录

    # 日志配置
    LOG_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logs')  
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

    LOGGING_LEVEL = 'DEBUG'
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_FILE = os.path.join(LOG_DIR, 'app.log')

    # 数据库 & Redis 配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:admin1234@172.16.20.153/log_analyzer'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = 'redis://172.16.20.153:6379'

    # Git 用户密码（敏感信息建议用环境变量）
    GIT_USER = 'tianxiaofan'
    GIT_PASSWORD = 'PyQdSBvG'

    ## openai信息
    OPENAI_KEY = 'sk-bfe03ca9190a49cfa2a559df3ca87d83'
    OPENAI_URL = 'https://api.deepseek.com'
    
    ## 日志格式
    LOG_CODE_PATTERNS = [
        r'([\w\.]+)\(([\w\.]+):(\d+)\)',           # com.zhuiyi.MyService(MyService.java:123)
        r'at\s+([\w\.]+)\(([\w\.]+):(\d+)\)',       # at com.zhuiyi.Handler(Handler.java:88)
        r'\[([\w\.]+)\]\[(\d+)\]',                 # [com.zhuiyi.auth.AuthInterceptor][43]
    ]
    
    ## 支持的文件类型
    SUPPORTED_LANGUAGES = ['.java']  # 支持的文件类型（根据需求调整）


    ## 异步配置
    CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis 作为消息队列
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Redis 作为结果存储
