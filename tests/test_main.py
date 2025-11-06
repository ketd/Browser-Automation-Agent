"""
测试浏览器自动化代理预制件的核心功能
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.main import execute_browser_task, _process_success_result, _process_error_result


class TestExecuteBrowserTask:
    """测试 execute_browser_task 函数"""

    def test_invalid_url(self):
        """测试无效的 URL 参数"""
        result = execute_browser_task(url="", query="测试查询")
        assert result["success"] is False
        assert result["error_code"] == "INVALID_URL"

    def test_invalid_query(self):
        """测试无效的 query 参数"""
        result = execute_browser_task(url="https://example.com", query="")
        assert result["success"] is False
        assert result["error_code"] == "INVALID_QUERY"

    def test_missing_api_url(self):
        """测试缺少 BROWSER_API_URL 环境变量"""
        # 确保环境变量不存在
        os.environ.pop('BROWSER_API_URL', None)

        result = execute_browser_task(
            url="https://example.com",
            query="测试查询"
        )
        assert result["success"] is False
        assert result["error_code"] == "MISSING_API_URL"

    @patch.dict(os.environ, {'BROWSER_API_URL': 'http://localhost:52101'})
    @patch('src.main.requests.post')
    def test_success_with_text_result(self, mock_post):
        """测试成功返回文本结果"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "query": "访问 https://example.com，然后提取页面内容",
            "response": "成功提取页面内容",
            "result": {
                "type": "text",
                "content": "这是页面内容"
            }
        }
        mock_post.return_value = mock_response

        result = execute_browser_task(
            url="https://example.com",
            query="提取页面内容"
        )

        assert result["success"] is True
        assert result["message"] == "成功提取页面内容"
        assert result["result"]["type"] == "text"
        assert result["result"]["data"]["content"] == "这是页面内容"

    @patch.dict(os.environ, {'BROWSER_API_URL': 'http://localhost:52101'})
    @patch('src.main.requests.post')
    @patch('src.main.requests.get')
    @patch('src.main.DATA_OUTPUTS', Path('/tmp/test_outputs'))
    def test_success_with_file_result(self, mock_get, mock_post):
        """测试成功返回文件结果"""
        # 模拟 API 响应
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "status": "success",
            "query": "访问 https://example.com，然后下载PDF文件",
            "response": "成功下载文件",
            "result": {
                "type": "file_reference",
                "file_id": "test-file-id",
                "filename": "test.pdf",
                "mime_type": "application/pdf",
                "size_bytes": 1024
            }
        }
        mock_post.return_value = mock_post_response

        # 模拟文件下载
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.content = b"PDF content"
        mock_get.return_value = mock_get_response

        # 创建临时输出目录
        Path('/tmp/test_outputs').mkdir(parents=True, exist_ok=True)

        result = execute_browser_task(
            url="https://example.com",
            query="下载PDF文件"
        )

        assert result["success"] is True
        assert result["message"] == "成功下载文件"
        assert result["result"]["type"] == "file"
        assert len(result["result"]["files"]) == 1
        assert result["result"]["files"][0]["filename"] == "test.pdf"

        # 清理
        output_file = Path('/tmp/test_outputs/test.pdf')
        if output_file.exists():
            output_file.unlink()

    @patch.dict(os.environ, {'BROWSER_API_URL': 'http://localhost:52101'})
    @patch('src.main.requests.post')
    def test_api_error(self, mock_post):
        """测试 API 返回错误"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "error",
            "error": {
                "code": "TASK_FAILED",
                "message": "任务执行失败"
            }
        }
        mock_post.return_value = mock_response

        result = execute_browser_task(
            url="https://example.com",
            query="测试查询"
        )

        assert result["success"] is False
        assert result["error_code"] == "TASK_FAILED"

    @patch.dict(os.environ, {'BROWSER_API_URL': 'http://localhost:52101'})
    @patch('src.main.requests.post')
    def test_timeout(self, mock_post):
        """测试超时"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        result = execute_browser_task(
            url="https://example.com",
            query="测试查询",
            timeout=10
        )

        assert result["success"] is False
        assert result["error_code"] == "TIMEOUT"

    @patch.dict(os.environ, {'BROWSER_API_URL': 'http://localhost:52101'})
    @patch('src.main.requests.post')
    def test_request_exception(self, mock_post):
        """测试请求异常"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("连接失败")

        result = execute_browser_task(
            url="https://example.com",
            query="测试查询"
        )

        assert result["success"] is False
        assert result["error_code"] == "API_ERROR"


class TestProcessResults:
    """测试结果处理函数"""

    def test_process_success_result_text(self):
        """测试处理文本结果"""
        api_result = {
            "status": "success",
            "response": "成功提取内容",
            "result": {
                "type": "text",
                "content": "这是内容"
            }
        }

        result = _process_success_result(api_result)

        assert result["success"] is True
        assert result["message"] == "成功提取内容"
        assert result["result"]["type"] == "text"
        assert result["result"]["data"]["content"] == "这是内容"

    def test_process_success_result_no_result(self):
        """测试处理无具体结果"""
        api_result = {
            "status": "success",
            "response": "任务完成"
        }

        result = _process_success_result(api_result)

        assert result["success"] is True
        assert result["message"] == "任务完成"
        assert result["result"]["type"] == "text"
        assert result["result"]["data"]["content"] == "任务完成"

    def test_process_error_result_with_dict(self):
        """测试处理错误结果（字典格式）"""
        api_result = {
            "status": "error",
            "error": {
                "code": "TEST_ERROR",
                "message": "测试错误"
            }
        }

        result = _process_error_result(api_result)

        assert result["success"] is False
        assert result["error"] == "测试错误"
        assert result["error_code"] == "TEST_ERROR"

    def test_process_error_result_with_string(self):
        """测试处理错误结果（字符串格式）"""
        api_result = {
            "status": "error",
            "error": "简单错误信息"
        }

        result = _process_error_result(api_result)

        assert result["success"] is False
        assert result["error"] == "简单错误信息"
        assert result["error_code"] == "TASK_FAILED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
