from flask import Blueprint, request, jsonify, current_app as app
from app.logfile.models import Log
from extensions import db
import os
import logging
import datetime
import re
from .utils import *


# 设置日志配置
logfile_bp = Blueprint('logfile', __name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@logfile_bp.route('/upload', methods=['POST'])
def upload_log():
    app.logger.debug("开始处理上传请求")  # 调试日志
    # 检查文件是否存在
    if 'file' not in request.files:
        app.logger.error("文件上传失败: 没有文件字段")
        return jsonify({"error": "请提供文件"}), 400
    file = request.files['file']
    original_filename = file.filename  # 获取原始文件名
   
    
    # 获取表单数据
    product_id = request.form.get('product_id', None)
    module_id = request.form.get('module_id', None)
    address = request.form.get('address', None)
    tag_version = request.form.get('tag_version', None)
    app.logger.debug(f"表单数据: product_id={product_id}, module_id={module_id}, address={address}, tag_version={tag_version}")  # 调试日志

    # 确保所有必需字段存在
    if not all([product_id, module_id, tag_version, address]):
        return jsonify({"error": "缺少必要的字段: 产品ID、模块ID、分支名称，分支版本"}), 400

    # 获取产品、模块、分支信息
    product_name = get_product_name_by_id(product_id)
    module_name = get_module_name_by_id(module_id)
    address, tag_version = get_branch_address_by_name(address, tag_version)
    app.logger.debug(f"获取的产品名称: {product_name}, 模块名称: {module_name}, 分支地址: {address}, 分支版本: {tag_version}")  # 调试日志

    # 确保所有获取的值有效
    if not all([product_name, module_name, address, tag_version]):
        return jsonify({"error": "数据库中存在无效的ID，请检查输入"}), 400

   
    # 生成唯一文件名，保留原始后缀
    timestamp = datetime.datetime.now().strftime("%Y%m%d")  # 仅精确到年月日
    original_extension = os.path.splitext(original_filename)[1]  # 提取原始文件后缀
    log_name = f"{product_name}-{module_name}-{address}-{tag_version}-{timestamp}{original_extension}"
    app.logger.debug(f"生成的日志文件名: {log_name}")

    app.logger.debug(f"开始处理日志文件: {original_filename}")
    # 删除原始文件名中的非法字符
    log_name = sanitize_filename(log_name)
    app.logger.debug(f"清理后的日志文件名: {log_name}")
    app.logger.debug(f"开始处理错误日志，去重")
    
    # 提取非正常日志（错误、警告等）
    lines = file.readlines()  # 获取文件所有行
    error_logs = extract_error_logs(lines)  # 提取错误日志
    
    # 处理日志：移除时间字段并去重
    processed_error_logs = process_log_file(error_logs)
    unique_error_logs = remove_duplicates(processed_error_logs)
    
    # 保存处理后的错误日志
    app.logger.debug(f"保存处理后的错误日志文件: {log_name}")
    processed_file_path = save_processed_log_file(unique_error_logs, log_name)
    
    # 查找是否已有相同 log_name 的日志
    log_entry = Log.query.filter_by(log_name=log_name).first()
    
    if log_entry:
        log_entry.count += 1  # 已存在则更新 count
    else:
        log_entry = Log(
            log_file_path=processed_file_path,  # 保存的是处理后的文件路径
            log_name=log_name,
            count=1  # 第一次上传时 count 为 1
        )
        db.session.add(log_entry)
    db.session.commit()

    return jsonify({"message": "文件上传并处理成功", "file_path": processed_file_path, "upload_count": log_entry.count}), 200

