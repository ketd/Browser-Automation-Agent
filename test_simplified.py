#!/usr/bin/env python3
"""
测试简化后的返回结构
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from main import execute_browser_task, download_bundle

os.environ['BROWSER_API_URL'] = 'http://192.168.1.218:52100'

def test_simplified_response():
    """测试简化后的返回结构"""
    print("🧪 测试简化后的返回结构\n")

    # 测试 1: 文本任务
    print("=" * 50)
    print("测试 1: 文本任务")
    print("=" * 50)
    result = execute_browser_task(
        urls="https://example.com",
        query="提取页面标题"
    )

    print(f"返回字段: {list(result.keys())}")
    print(f"✓ success: {result.get('success')}")
    print(f"✓ message: {result.get('message')[:80]}...")
    print(f"✓ session_id: {result.get('session_id')}")
    print(f"✓ files: {result.get('files', '无')}")
    print()

    # 测试 2: 文件任务
    print("=" * 50)
    print("测试 2: 文件任务（截图）")
    print("=" * 50)
    result2 = execute_browser_task(
        urls="https://example.com",
        query="截图保存"
    )

    print(f"返回字段: {list(result2.keys())}")
    print(f"✓ success: {result2.get('success')}")
    print(f"✓ message: {result2.get('message')[:80]}...")
    print(f"✓ session_id: {result2.get('session_id')}")
    print(f"✓ files: {result2.get('files')}")
    print()

    # 测试 3: Bundle 下载
    if result2.get('success') and result2.get('session_id'):
        print("=" * 50)
        print("测试 3: Bundle 下载")
        print("=" * 50)
        bundle = download_bundle(result2['session_id'])

        print(f"返回字段: {list(bundle.keys())}")
        print(f"✓ success: {bundle.get('success')}")
        print(f"✓ message: {bundle.get('message')}")
        print(f"✓ files: {bundle.get('files')}")
        print()

    print("=" * 50)
    print("✅ 简化后的返回结构清晰易用！")
    print("=" * 50)
    print("\n对比：")
    print("  旧版本: 多层嵌套 (result.type, result.files, debug_trace, error_code)")
    print("  新版本: 扁平化结构 (success, message, session_id, files, error)")

if __name__ == "__main__":
    test_simplified_response()
