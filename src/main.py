"""
浏览器自动化代理预制件

通过自然语言执行浏览器自动化任务,支持信息提取和文件下载。
调用后端浏览器自动化 API 服务完成任务。
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import requests

# 输出文件路径（Gateway 会自动上传此目录中的文件）
DATA_OUTPUTS = Path("data/outputs")


def execute_browser_task(url: str, query: str, timeout: int = 600) -> dict:
    """
    执行浏览器自动化任务

    通过自然语言描述任务，自动执行浏览器操作。
    支持网页访问、信息提取、文件下载等操作。

    Args:
        url: 目标网页 URL
        query: 任务描述（自然语言），例如：
            - "提取页面的主要内容"
            - "下载最新的PDF文件"
            - "找到逾期承兑人名单并下载"
        timeout: 任务超时时间（秒），默认 600（10分钟）

    Returns:
        包含任务执行结果的字典：
        {
            "success": True/False,
            "message": "任务执行描述",
            "result": {
                "type": "text" | "file" | "mixed",
                "data": {...},        # type=text 时存在
                "files": [...]        # type=file 时存在
            },
            "error": "错误信息"  # 失败时存在
        }

    Examples:
        >>> execute_browser_task(
        ...     url="https://example.com",
        ...     query="提取页面标题和主要内容"
        ... )
        {'success': True, 'message': '成功提取页面内容', 'result': {...}}

        >>> execute_browser_task(
        ...     url="https://example.com/files",
        ...     query="下载最新的PDF文件"
        ... )
        {'success': True, 'message': '成功下载1个文件', 'result': {...}}
    """
    try:
        # 参数验证
        if not url or not isinstance(url, str):
            return {
                "success": False,
                "error": "url 参数必须是非空字符串",
                "error_code": "INVALID_URL"
            }

        if not query or not isinstance(query, str):
            return {
                "success": False,
                "error": "query 参数必须是非空字符串",
                "error_code": "INVALID_QUERY"
            }

        # 获取后端 API 地址
        api_base_url = os.environ.get('BROWSER_API_URL')
        if not api_base_url:
            return {
                "success": False,
                "error": "未配置 BROWSER_API_URL 环境变量",
                "error_code": "MISSING_API_URL"
            }

        # 构建完整查询（包含 URL）
        full_query = f"访问 {url}，然后{query}"

        # 调用后端 API
        api_url = f"{api_base_url.rstrip('/')}/agent/task"
        response = requests.post(
            api_url,
            json={"query": full_query},
            timeout=timeout
        )

        # 检查 HTTP 状态
        response.raise_for_status()
        api_result = response.json()

        # 解析 API 返回结果
        if api_result.get("status") == "success":
            return _process_success_result(api_result)
        else:
            return _process_error_result(api_result)

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"任务超时（{timeout}秒）",
            "error_code": "TIMEOUT"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"API 请求失败: {str(e)}",
            "error_code": "API_ERROR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }


def _process_success_result(api_result: Dict[str, Any]) -> dict:
    """
    处理成功的 API 结果

    Args:
        api_result: API 返回的原始结果

    Returns:
        处理后的结果字典
    """
    result_data = api_result.get("result")
    response_text = api_result.get("response", "任务执行成功")

    # 情况1: 返回文件引用
    if result_data and result_data.get("type") == "file_reference":
        file_info = _download_file_from_api(api_result)
        if file_info:
            return {
                "success": True,
                "message": response_text,
                "result": {
                    "type": "file",
                    "files": [file_info]
                }
            }
        else:
            return {
                "success": False,
                "error": "文件下载失败",
                "error_code": "FILE_DOWNLOAD_ERROR"
            }

    # 情况2: 返回内联文件
    elif result_data and result_data.get("type") == "file_inline":
        file_info = _save_inline_file(result_data)
        if file_info:
            return {
                "success": True,
                "message": response_text,
                "result": {
                    "type": "file",
                    "files": [file_info]
                }
            }
        else:
            return {
                "success": False,
                "error": "文件保存失败",
                "error_code": "FILE_SAVE_ERROR"
            }

    # 情况3: 返回文本数据
    elif result_data and result_data.get("type") == "text":
        return {
            "success": True,
            "message": response_text,
            "result": {
                "type": "text",
                "data": {
                    "content": result_data.get("content", "")
                }
            }
        }

    # 情况4: 无具体结果，只有响应文本
    else:
        return {
            "success": True,
            "message": response_text,
            "result": {
                "type": "text",
                "data": {
                    "content": response_text
                }
            }
        }


def _process_error_result(api_result: Dict[str, Any]) -> dict:
    """
    处理失败的 API 结果

    Args:
        api_result: API 返回的原始结果

    Returns:
        错误结果字典
    """
    error_info = api_result.get("error")
    if isinstance(error_info, dict):
        error_message = error_info.get("message", "任务执行失败")
        error_code = error_info.get("code", "TASK_FAILED")
    else:
        error_message = str(error_info) if error_info else "任务执行失败"
        error_code = "TASK_FAILED"

    return {
        "success": False,
        "error": error_message,
        "error_code": error_code
    }


def _download_file_from_api(api_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    从 API 结果中下载文件到 data/outputs/

    Args:
        api_result: API 返回的原始结果

    Returns:
        文件信息字典，失败返回 None
    """
    try:
        result_data = api_result.get("result", {})
        file_id = result_data.get("file_id")
        filename = result_data.get("filename", "downloaded_file")
        mime_type = result_data.get("mime_type", "application/octet-stream")

        if not file_id:
            return None

        # 构建下载 URL
        api_base_url = os.environ.get('BROWSER_API_URL')
        download_url = f"{api_base_url.rstrip('/')}/downloads/{file_id}"

        # 下载文件
        response = requests.get(download_url, timeout=60)
        response.raise_for_status()

        # 确保输出目录存在
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)

        # 保存文件
        output_path = DATA_OUTPUTS / filename
        output_path.write_bytes(response.content)

        return {
            "filename": filename,
            "size_bytes": len(response.content),
            "mime_type": mime_type
        }

    except Exception:
        return None


def _save_inline_file(result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    保存内联文件（base64 编码）到 data/outputs/

    Args:
        result_data: 包含文件内容的结果数据

    Returns:
        文件信息字典，失败返回 None
    """
    try:
        import base64

        filename = result_data.get("filename", "downloaded_file")
        mime_type = result_data.get("mime_type", "application/octet-stream")
        content_base64 = result_data.get("content")

        if not content_base64:
            return None

        # 解码 base64 内容
        file_bytes = base64.b64decode(content_base64)

        # 确保输出目录存在
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)

        # 保存文件
        output_path = DATA_OUTPUTS / filename
        output_path.write_bytes(file_bytes)

        return {
            "filename": filename,
            "size_bytes": len(file_bytes),
            "mime_type": mime_type
        }

    except Exception:
        return None
