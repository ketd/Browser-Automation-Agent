"""
浏览器自动化代理预制件

通过自然语言执行浏览器自动化任务,支持信息提取和文件下载。
调用后端浏览器自动化 API 服务完成任务。

主要功能:
1. execute_browser_task: 执行浏览器自动化任务
   - 支持自然语言描述任务
   - 支持会话连续性（通过 session_id）
   - 自动处理文件下载（内联或引用方式）
   - 返回调试信息（执行时长、使用的工具等）

2. download_bundle: 下载会话中生成的所有文件
   - 将会话中的所有文件打包为 ZIP
   - 适用于多文件任务结果

环境变量配置:
- BROWSER_API_URL: 后端 API 服务地址（必需）

使用示例:
    >>> # 单个 URL
    >>> result = execute_browser_task(
    ...     urls="https://example.com",
    ...     query="提取页面标题和主要内容"
    ... )
    >>> print(result['success'])  # True
    >>> print(result['session_id'])  # 'a1b2c3d4-...'

    >>> # 多个 URL
    >>> result = execute_browser_task(
    ...     urls=["https://example.com", "https://github.com"],
    ...     query="分别访问这些网站并截图"
    ... )
    >>> print(len(result['files']))  # 2

    >>> # 会话连续性
    >>> session = result['session_id']
    >>> result2 = execute_browser_task(
    ...     urls="https://example.com/page2",
    ...     query="继续分析下一页",
    ...     session_id=session
    ... )

    >>> # 下载文件包
    >>> bundle = download_bundle(session)
    >>> print(bundle['files'][0])

返回结构:
    {
        "success": True/False,
        "message": "任务执行描述",
        "session_id": "会话ID",
        "files": ["文件名"],  # 仅当有文件时
        "error": "错误信息"  # 失败时存在
    }
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import requests

# 输出文件路径（Gateway 会自动上传此目录中的文件）
DATA_OUTPUTS = Path("data/outputs")


def execute_browser_task(
    urls: str | list[str],
    query: str,
    session_id: Optional[str] = None,
    timeout: int = 600
) -> dict:
    """
    执行浏览器自动化任务

    通过自然语言描述任务，自动执行浏览器操作。
    支持网页访问、信息提取、文件下载等操作。
    支持会话连续性，可通过 session_id 保持上下文。

    Args:
        urls: 目标网页 URL，可以是单个 URL 字符串或 URL 列表
              - 单个: "https://example.com"
              - 多个: ["https://example.com", "https://github.com"]
        query: 任务描述（自然语言），例如：
            - "提取页面的主要内容"
            - "下载最新的PDF文件"
            - "找到逾期承兑人名单并下载"
            - "分别访问这些网站并截图"（多URL时）
        session_id: 会话ID（可选），用于保持对话连续性。
                   如果提供，将在相同会话中执行任务。
        timeout: 任务超时时间（秒），默认 600（10分钟）

    Returns:
        包含任务执行结果的字典：
        {
            "success": True/False,
            "message": "任务执行描述",
            "session_id": "会话ID（用于后续请求或下载文件包）",
            "files": ["文件名1", "文件名2"],  # 仅当有文件时存在
            "error": "错误信息"  # 失败时存在
        }

    Examples:
        >>> # 单个 URL
        >>> result = execute_browser_task(
        ...     urls="https://example.com",
        ...     query="提取页面标题和主要内容"
        ... )
        >>> print(result['success'])  # True

        >>> # 多个 URL
        >>> result = execute_browser_task(
        ...     urls=["https://example.com", "https://github.com"],
        ...     query="分别访问这些网站并截图"
        ... )
        >>> print(result['files'])  # ['screenshot1.png', 'screenshot2.png']

        >>> # 使用会话连续性
        >>> session = result['session_id']
        >>> result2 = execute_browser_task(
        ...     urls="https://example.com/page2",
        ...     query="继续分析下一页",
        ...     session_id=session
        ... )

        >>> # 下载文件
        >>> result3 = execute_browser_task(
        ...     urls="https://example.com/files",
        ...     query="下载最新的PDF文件"
        ... )
        >>> if result3.get('files'):
        ...     print(f"下载了文件: {result3['files']}")
    """
    try:
        # 参数验证和规范化
        if isinstance(urls, str):
            # 单个 URL
            url_list = [urls]
        elif isinstance(urls, list):
            # URL 列表
            if not urls or not all(isinstance(u, str) for u in urls):
                return {
                    "success": False,
                    "error": "URL 列表格式不正确"
                }
            url_list = urls
        else:
            return {
                "success": False,
                "error": "URL 格式不正确，应为字符串或字符串列表"
            }

        if not query or not isinstance(query, str):
            return {
                "success": False,
                "error": "任务描述不能为空"
            }

        # 获取后端 API 地址
        api_base_url = os.environ.get('BROWSER_API_URL')
        if not api_base_url:
            return {
                "success": False,
                "error": "未配置 API 地址"
            }

        # 构建完整查询（包含 URL）
        if len(url_list) == 1:
            # 单个 URL
            full_query = f"访问 {url_list[0]}，然后{query}"
        else:
            # 多个 URL
            urls_text = "、".join(url_list)
            full_query = f"访问以下网站：{urls_text}。然后{query}"

        # 构建请求数据
        request_data = {"query": full_query}
        if session_id:
            request_data["session_id"] = session_id

        # 调用后端 API
        api_url = f"{api_base_url.rstrip('/')}/agent/task"
        response = requests.post(
            api_url,
            json=request_data,
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
            "error": "任务超时"
        }
    except requests.exceptions.RequestException:
        return {
            "success": False,
            "error": "API 请求失败"
        }
    except Exception:
        return {
            "success": False,
            "error": "任务执行失败"
        }


def _process_success_result(api_result: Dict[str, Any]) -> dict:
    """
    处理成功的 API 结果

    Args:
        api_result: API 返回的原始结果

    Returns:
        处理后的结果字典，简化用户界面
    """
    result_data = api_result.get("result")
    response_text = api_result.get("response", "任务执行成功")
    session_id = api_result.get("session_id")

    # 构建基础响应（简化版，不包含技术细节）
    base_response = {
        "success": True,
        "message": response_text,
        "session_id": session_id
    }

    # 情况1: 返回文件引用
    if result_data and result_data.get("type") == "file_reference":
        file_info = _download_file_from_api(api_result)
        if file_info:
            # 简化文件信息，只返回文件名
            base_response["files"] = [file_info.get("filename")]
            return base_response
        else:
            return {
                "success": False,
                "error": "文件下载失败",
                "session_id": session_id
            }

    # 情况2: 返回内联文件
    elif result_data and result_data.get("type") == "file_inline":
        file_info = _save_inline_file(result_data)
        if file_info:
            # 简化文件信息，只返回文件名
            base_response["files"] = [file_info.get("filename")]
            return base_response
        else:
            return {
                "success": False,
                "error": "文件保存失败",
                "session_id": session_id
            }

    # 情况3: 返回文本数据
    elif result_data and result_data.get("type") == "text":
        # 文本内容直接放在 message 中，不需要额外的 result 字段
        return base_response

    # 情况4: 无具体结果，只有响应文本
    else:
        return base_response


def _process_error_result(api_result: Dict[str, Any]) -> dict:
    """
    处理失败的 API 结果

    Args:
        api_result: API 返回的原始结果

    Returns:
        简化的错误结果字典
    """
    error_info = api_result.get("error")
    session_id = api_result.get("session_id")

    if isinstance(error_info, dict):
        error_message = error_info.get("message", "任务执行失败")
    else:
        error_message = str(error_info) if error_info else "任务执行失败"

    result = {
        "success": False,
        "error": error_message
    }

    # 添加 session_id（如果存在）
    if session_id:
        result["session_id"] = session_id

    return result


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
        if not api_base_url:
            return None

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


def download_bundle(session_id: str, timeout: int = 120) -> dict:
    """
    下载会话中生成的所有文件（打包为 ZIP）

    将会话中生成的所有文件打包下载到 data/outputs/ 目录。
    适用于包含多个文件的任务结果。

    Args:
        session_id: 会话ID（从 execute_browser_task 返回结果中获取）
        timeout: 下载超时时间（秒），默认 120（2分钟）

    Returns:
        包含下载结果的字典：
        {
            "success": True/False,
            "message": "下载描述",
            "files": ["bundle_xxx.zip"],  # 成功时的文件名
            "error": "错误信息"  # 失败时存在
        }

    Examples:
        >>> # 执行任务并获取 session_id
        >>> result = execute_browser_task(
        ...     urls="https://example.com/files",
        ...     query="下载所有PDF文件"
        ... )
        >>> session = result['session_id']

        >>> # 下载文件包
        >>> bundle_result = download_bundle(session)
        >>> if bundle_result['success']:
        ...     print(f"已下载文件包: {bundle_result['files'][0]}")
    """
    try:
        # 参数验证
        if not session_id or not isinstance(session_id, str):
            return {
                "success": False,
                "error": "会话ID格式不正确"
            }

        # 获取后端 API 地址
        api_base_url = os.environ.get('BROWSER_API_URL')
        if not api_base_url:
            return {
                "success": False,
                "error": "未配置 API 地址"
            }

        # 构建下载 URL
        bundle_url = f"{api_base_url.rstrip('/')}/downloads/bundle/{session_id}"

        # 下载文件包
        response = requests.get(bundle_url, timeout=timeout)
        response.raise_for_status()

        # 确保输出目录存在
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)

        # 保存 ZIP 文件
        filename = f"bundle_{session_id[:8]}.zip"
        output_path = DATA_OUTPUTS / filename
        output_path.write_bytes(response.content)

        return {
            "success": True,
            "message": "成功下载文件包",
            "files": [filename]
        }

    except requests.exceptions.HTTPError as e:
        # 处理特定 HTTP 错误
        if e.response.status_code == 404:
            error_msg = "未找到该会话的文件"
        elif e.response.status_code == 410:
            error_msg = "文件已过期"
        else:
            error_msg = "下载失败"

        return {
            "success": False,
            "error": error_msg
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "下载超时"
        }
    except Exception:
        return {
            "success": False,
            "error": "下载失败"
        }
