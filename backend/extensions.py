from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis



db = SQLAlchemy()
migrate = Migrate()
redis = None  # 这里不初始化，在 `create_app()` 里初始化

def init_redis(app):
    """根据 Flask 配置初始化 Redis 连接"""
    redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")  # 默认 Redis 地址
    return Redis.from_url(redis_url, decode_responses=True)
