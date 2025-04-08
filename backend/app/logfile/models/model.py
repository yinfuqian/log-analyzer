from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class Log(db.Model):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_name = Column(String(255), nullable=False)  # 
    log_file_path = Column(String(500), nullable=False)  # 日志文件的存储路径（例如：本地文件路径或URL）
    created_at = Column(DateTime, default=datetime.utcnow)  # 日志文件的创建时间
    count = db.Column(db.Integer, default=1)  # 确保这里是 Integer

    def __repr__(self):
        return f'<Log {self.id} - {self.module_name}>'



class QueryRecord(db.Model):
    __tablename__ = 'query_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)  # 产品 ID
    module_id = Column(Integer, ForeignKey('logs.id'), nullable=False)  # 关联日志模块
    log_file_path = Column(String(500), nullable=False)  # 日志文件存放地址
    branch_url = Column(String(500), nullable=False)  # 分支地址
    branch_version = Column(String(100), nullable=False)  # 分支版本
    created_at = Column(DateTime, default=datetime.utcnow)  # 记录创建时间
    answer = Column(Integer, nullable=True)  # 查询结果。0为成功，1为失败

    module = relationship("Log", backref="query_records")  # 关联 Log 表

    def __repr__(self):
        return f'<QueryRecord {self.id} - Product {self.product_id} - Module {self.module_id}>'