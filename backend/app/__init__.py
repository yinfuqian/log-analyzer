import logging
import os
from flask import Flask
from .config import Config
from extensions import db, migrate, init_redis
from app.product.routes.routes import product_bp
from app.modules.routes.routes import module_bp
from app.logfile.routes.routes import logfile_bp
from app.analysis.routes.routes import analysis_bp
from .routes import dashboard_bp
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # 配置日志记录
    setup_logging(app)

    # 初始化 Flask 扩展
    db.init_app(app)
    migrate.init_app(app, db)

    # 解决 Working outside of application context 问题
    global redis
    redis = init_redis(app)  # 在 Flask `app` 初始化后，再初始化 Redis

    # 注册蓝图，并为蓝图指定路径前缀
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(module_bp, url_prefix='/module')
    app.register_blueprint(logfile_bp, url_prefix='/logfile')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app


def setup_logging(app):
    """设置日志记录"""
    # 创建日志文件夹
    log_dir = app.config['LOG_DIR']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 配置日志处理器
    handler = logging.FileHandler(app.config['LOGGING_FILE'])
    handler.setLevel(app.config['LOGGING_LEVEL'])
    
    # 配置日志格式
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    
    # 将日志处理器添加到 Flask 的日志中
    app.logger.addHandler(handler)
    
    # 设置日志级别
    app.logger.setLevel(app.config['LOGGING_LEVEL'])

    # 启动时打印日志
    app.logger.info("启动日志：应用已启动并初始化完成")

def run_app():
    app = create_app()
    host = app.config['SERVER_HOST']
    port = app.config['SERVER_PORT']
    
    # 启动应用
    app.run(host=host, port=port)
