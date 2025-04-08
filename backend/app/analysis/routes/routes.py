import os
import re,subprocess
import logging
from flask import Blueprint, request, jsonify, current_app as app
from openai import OpenAI
from app.logfile.models.model import QueryRecord  
from datetime import datetime
from app import db


# 配置 Flask Blueprint 和日志格式
analysis_bp = Blueprint("analysis", __name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

@analysis_bp.route("/branch_get", methods=["POST"])
def get_branch_info():
    """ 获取分支信息 """
    data = request.json
    address = data.get("branchAddress")
    tag_version = data.get("tagVersion")
    if not address or not tag_version:
        logging.error("缺少必要的字段: address, tag_version")
        return jsonify({"error": "缺少必要的字段: address, tag_version"}), 400
    # 克隆 Git 仓库
    repo_path = clone_git_repo(address, tag_version)
    if not repo_path:
        logging.error("克隆 Git 仓库失败")
        return jsonify({"error": "克隆 Git 仓库失败"}), 500
    # 获取分支信息
    try:
        logging.info("获取 Git 仓库的分支信息")
        result = subprocess.run(
            ["git", "branch", "-r"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        branches = result.stdout.decode("utf-8").splitlines()
        logging.info(f"分支信息获取成功: {branches}")
    except subprocess.CalledProcessError as e:
        logging.error(f"获取分支信息失败: {e}")
        return jsonify({"error": "获取分支信息失败"}), 500
      # 返回仓库路径和分支信息
    return jsonify({
        "branches": branches,
        "repo_path": repo_path  # 返回仓库路径
    })


def clone_git_repo(address, tag_version):
    """ 克隆指定的 Git 仓库 """
    GIT_USER = app.config.get("GIT_USER")
    GIT_PASSWORD = app.config.get("GIT_PASSWORD")

    repo_name = address.split("/")[-1].replace(".git", "")
    repo_dir = os.path.join("/tmp", repo_name)

    if os.path.exists(repo_dir):
        logging.info(f"Git 仓库已存在，使用现有目录: {repo_dir}")
        return repo_dir

    repo_address = address.replace("https://", f"https://{GIT_USER}:{GIT_PASSWORD}@")
    try:
        logging.info(f"开始克隆 Git 仓库: {address}, 标签版本: {tag_version}")
        subprocess.run(
            ["git", "clone", "-b", tag_version, repo_address, repo_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logging.info(f"Git 仓库克隆成功: {repo_dir}")
        return repo_dir
    except subprocess.CalledProcessError as e:
        logging.error(f"Git 克隆失败: {e}")
        return None

@analysis_bp.route("/log_analysis", methods=["POST"])
def analyze_log_and_code():
    logging.info("==> 进入 analyze_log_and_code 接口")
    data = request.json
    logging.info(f"接收到的请求数据: {data}")
    # 检查日志文件路径和仓库路径
    log_file_path = data.get("file_path")
    repo_path = data.get("repo_path")
    
    logging.info(f"日志文件路径: {log_file_path}")
    logging.info(f"仓库路径: {repo_path}")

    if not log_file_path or not os.path.exists(log_file_path):
        logging.error(f"文件路径无效或文件不存在: {log_file_path}")
        return jsonify({"error": "文件路径无效或文件不存在"}), 400
    if not repo_path or not os.path.exists(repo_path):
        logging.error(f"无效的仓库路径: {repo_path}")
        return jsonify({"error": "无效的仓库路径"}), 400
    # 尝试读取日志内容
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            log_content = f.read()
        logging.info(f"成功读取日志文件: {log_file_path}，长度: {len(log_content)} 字符")
    except Exception as e:
        logging.exception(f"读取日志失败: {e}")
        return jsonify({"error": "读取日志失败"}), 500

    # 日志分析：调用 DeepSeek 分析日志
    logging.info("调用 analyze_log_with_deepseek 分析日志")
    log_analysis = analyze_log_with_deepseek(log_content)
    if not log_analysis:
        logging.error("日志分析返回为空")
        
        # 插入查询记录，状态为失败（1）
        insert_query_record(data, 1)
        return jsonify({"error": "日志分析失败"}), 500
    logging.info(f"日志分析返回结果:\n{log_analysis}")

    # 从日志中提取错误信息（只提取第一个堆栈行）
    logging.info("调用 extract_error_info_from_log 从日志内容中提取错误信息")
    error_info = extract_error_info_from_log(log_content)
    if not error_info:
        logging.error("未能提取到错误信息")
        return jsonify({"error": "无法从日志中提取错误信息"}), 400
    logging.info(f"提取的错误信息: {error_info}")

    # 解析仓库中实际文件路径
    logging.info("调用 resolve_file_paths 解析仓库中的实际文件路径")
    resolved_errors = resolve_file_paths(repo_path, error_info)
    logging.info(f"解析后的文件路径信息: {resolved_errors}")

    # 提取代码片段
    logging.info("调用 extract_code_snippets 根据解析结果提取代码片段")
    code_snippets = extract_code_snippets(resolved_errors)
    logging.info(f"提取到的代码片段: {code_snippets}")

    # 综合代码和日志分析，调用 DeepSeek 进行错误定位分析
    logging.info("调用 analyze_code_with_deepseek 进行综合分析")
    code_analysis = analyze_code_with_deepseek(log_analysis, code_snippets)
    if code_analysis:
        insert_query_record(data, 0)
        logging.info("综合分析成功")
    else:
        logging.error("综合分析失败")
        insert_query_record(data, 1)
    logging.info("完成综合分析，准备返回结果")
    response_payload = {
        "log_analysis": log_analysis,
        "code_snippets": code_snippets,
        "code_analysis": code_analysis
    }
    #logging.info(f"返回的响应数据: {response_payload}")
    return jsonify(response_payload)

def analyze_log_with_deepseek(log_content):
    logging.info("==> 进入 analyze_log_with_deepseek")
    api_key = app.config.get("OPENAI_KEY")
    base_url = app.config.get("OPENAI_URL")
    logging.info(f"DeepSeek 配置 - API_KEY: {'存在' if api_key else '缺失'}, BASE_URL: {base_url}")

    if not api_key or not base_url:
        raise ValueError("API Key 或 Base URL 未配置")

    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        logging.info("调用 DeepSeek API 进行日志分析")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个日志分析专家"},
                {"role": "user", "content": f"请分析以下日志并给出错误的原因：\n\n{log_content}"}
            ],
            stream=False
        )
        result = response.choices[0].message.content
        logging.info("DeepSeek 日志分析成功")
        return result
    except Exception as e:
        logging.exception(f"调用 DeepSeek 日志分析失败: {e}")
        return None

def extract_error_info_from_log(log_content):
    logging.info("==> 进入 extract_error_info_from_log")
    error_info = []
    error_line = re.search(r'(Exception|Error):\s*(.*)', log_content)
    error_message = error_line.group(0).strip() if error_line else "未知错误"
    logging.info(f"匹配到的错误描述: {error_message}")

    # 从上到下只取第一条堆栈信息，格式示例: " at com.example.Class(File.java:123)"
    stack_match = re.search(r'\s+at\s+[\w\.]+\(([\w\.]+):(\d+)\)', log_content)
    if stack_match:
        file_name = stack_match.group(1)
        line_str = stack_match.group(2)
        try:
            line_number = int(line_str)
        except ValueError:
            logging.warning("转换行号失败，默认赋值为 1")
            line_number = 1
        logging.info(f"提取到堆栈信息: 文件 {file_name}, 行号 {line_number}")
        error_info.append({
            "file": file_name,
            "line": line_number,
            "error": error_message
        })
    else:
        logging.info("未匹配到堆栈信息，使用默认错误信息")
        error_info.append({
            "file": None,
            "line": None,
            "error": error_message
        })
    return error_info

def resolve_file_paths(repo_path, error_info):
    logging.info("==> 进入 resolve_file_paths")
    resolved = []
    for err in error_info:
        target = err["file"]
        found_path = None
        logging.info(f"在仓库 '{repo_path}' 中查找文件: {target}")
        # 遍历 repo_path 下所有文件，如果匹配文件名则认为找到
        for root, _, files in os.walk(repo_path):
            if target in files:
                found_path = os.path.join(root, target)
                logging.info(f"找到目标文件: {found_path}")
                break
        if found_path:
            resolved.append({
                "file": found_path,
                "line": err["line"],
                "error": err["error"]
            })
        else:
            logging.warning(f"目标文件 {target} 未在仓库 {repo_path} 中找到")
    return resolved

def extract_code_snippets(resolved_errors):
    logging.info("==> 进入 extract_code_snippets")
    code_snippets = []
    for err in resolved_errors:
        file_path = err.get("file")
        line_number = err.get("line")
        logging.info(f"处理文件: {file_path}，目标行号: {line_number}")
        if not file_path or not os.path.exists(file_path):
            logging.warning(f"无效或不存在的文件路径: {file_path}")
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            start = max(0, line_number - 5)
            end = min(len(lines), line_number + 5)
            snippet = "".join(lines[start:end])
            logging.info(f"提取 {file_path} 中 {line_number} 行附近的代码片段，范围: {start}~{end}")
            code_snippets.append({
                "file": os.path.relpath(file_path),
                "line": line_number,
                "snippet": snippet
            })
        except Exception as e:
            logging.warning(f"读取文件 {file_path} 失败: {e}")
    return code_snippets

def analyze_code_with_deepseek(log_analysis, code_snippets):
    logging.info("==> 进入 analyze_code_with_deepseek")
    api_key = app.config.get("OPENAI_KEY")
    base_url = app.config.get("OPENAI_URL")
    logging.info(f"DeepSeek 配置检查 - API_KEY: {'存在' if api_key else '缺失'}, BASE_URL: {base_url}")

    if not api_key or not base_url:
        raise ValueError("API Key 或 Base URL 未配置")

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    context_lines = []
    for snippet in code_snippets:
        context_lines.append(
            f"文件：{snippet['file']} 第 {snippet['line']} 行附近\n```\n{snippet['snippet']}\n```"
        )
    context = "\n".join(context_lines)

    prompt = (
        f"以下是日志分析内容：\n{log_analysis}\n\n"
        "以下是相关代码片段，请结合日志分析判断可能的错误原因：\n"
        f"{context}"
    )
    logging.info(f"构造的 prompt:\n{prompt}")

    try:
        logging.info("调用 DeepSeek API 进行综合代码和日志分析")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个经验丰富的后端专家"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        result = response.choices[0].message.content
        logging.info("DeepSeek 综合分析成功")
        return result
    except Exception as e:
        logging.exception(f"调用 DeepSeek 进行代码分析失败: {e}")
        return "代码分析失败，无法定位具体错误"

def insert_query_record(data, status):
    try:
        query_record = QueryRecord(
            product_id=data.get("productId"),
            module_id=data.get("moduleId"),
            log_file_path=data.get("file_path"),
            branch_url=data.get("branchAddress"),
            branch_version=data.get("tagVersion"),
            created_at=datetime.utcnow(),
            answer=status 
        )
        db.session.add(query_record)
        db.session.commit()
        logging.info(f"成功插入查询记录: {query_record}")
    except Exception as e:
        logging.exception(f"插入查询记录失败: {e}")
        db.session.rollback()