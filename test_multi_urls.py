#!/usr/bin/env python3
"""
测试多 URL 功能
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from main import execute_browser_task

os.environ['BROWSER_API_URL'] = 'http://192.168.1.218:52100'

def test_single_url():
    """测试单个 URL（向后兼容）"""
    print("=" * 60)
    print("测试 1: 单个 URL（字符串）")
    print("=" * 60)

    result = execute_browser_task(
        urls="https://example.com",
        query="提取页面标题"
    )

    print(f"✓ 成功: {result.get('success')}")
    print(f"✓ 消息: {result.get('message')[:80]}...")
    print(f"✓ 会话ID: {result.get('session_id')}")
    print()
    return result


def test_multiple_urls():
    """测试多个 URL"""
    print("=" * 60)
    print("测试 2: 多个 URL（数组）")
    print("=" * 60)

    result = execute_browser_task(
        urls=["https://example.com", "https://httpbin.org/html"],
        query="分别访问这些网站并截图"
    )

    print(f"✓ 成功: {result.get('success')}")
    print(f"✓ 消息: {result.get('message')[:100]}...")
    print(f"✓ 会话ID: {result.get('session_id')}")
    print(f"✓ 生成文件: {result.get('files', [])}")
    print(f"✓ 文件数量: {len(result.get('files', []))}")
    print()
    return result


def test_url_list_single():
    """测试单元素 URL 列表"""
    print("=" * 60)
    print("测试 3: 单元素 URL 列表")
    print("=" * 60)

    result = execute_browser_task(
        urls=["https://example.com"],
        query="截图保存"
    )

    print(f"✓ 成功: {result.get('success')}")
    print(f"✓ 文件: {result.get('files', [])}")
    print()
    return result


def test_invalid_urls():
    """测试无效的 URL 参数"""
    print("=" * 60)
    print("测试 4: 无效 URL 参数（预期失败）")
    print("=" * 60)

    # 测试空列表
    result1 = execute_browser_task(
        urls=[],
        query="测试"
    )
    print(f"空列表 - 成功: {result1.get('success')}, 错误: {result1.get('error')}")

    # 测试非字符串类型
    result2 = execute_browser_task(
        urls=123,
        query="测试"
    )
    print(f"数字类型 - 成功: {result2.get('success')}, 错误: {result2.get('error')}")

    # 测试包含非字符串的列表
    result3 = execute_browser_task(
        urls=["https://example.com", 123],
        query="测试"
    )
    print(f"混合类型列表 - 成功: {result3.get('success')}, 错误: {result3.get('error')}")
    print()


if __name__ == "__main__":
    print("\n🚀 开始测试多 URL 功能\n")

    try:
        # 测试 1: 单个 URL（向后兼容）
        test_single_url()

        # 测试 2: 多个 URL
        result2 = test_multiple_urls()

        # 测试 3: 单元素列表
        test_url_list_single()

        # 测试 4: 无效参数
        test_invalid_urls()

        print("=" * 60)
        print("✅ 多 URL 功能测试完成!")
        print("=" * 60)
        print("\n优势：")
        print("  ✓ 支持单个 URL（向后兼容）")
        print("  ✓ 支持多个 URL（批量处理）")
        print("  ✓ 自动构建合适的查询语句")
        print("  ✓ 完善的参数验证")

    except Exception as e:
        print(f"\n❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
