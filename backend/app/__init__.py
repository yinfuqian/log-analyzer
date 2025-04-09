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
    
    setup_logging(app)

    db.init_app(app)
    migrate.init_app(app, db)

    global redis
    redis = init_redis(app)
    
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(module_bp, url_prefix='/module')
    app.register_blueprint(logfile_bp, url_prefix='/logfile')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app

def setup_logging(app):
    log_dir = app.config['LOG_DIR']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = logging.FileHandler(app.config['LOGGING_FILE'])
    handler.setLevel(app.config['LOGGING_LEVEL'])

    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOGGING_LEVEL'])
    app.logger.info("启动日志：应用已启动并初始化完成")
