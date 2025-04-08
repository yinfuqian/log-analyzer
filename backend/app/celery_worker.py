from celery import Celery
def make_celery(app):
    """根据 Flask 配置创建并返回 Celery 实例"""
    #print("Flask Config: ", app.config)  # 打印 Flask 配置，检查是否加载成功
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    # 自动发现任务模块
    celery.autodiscover_tasks(['checkmessages.tasks'])  # 确保 Celery 加载了任务
    return celery
