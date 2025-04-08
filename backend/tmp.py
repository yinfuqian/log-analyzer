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
