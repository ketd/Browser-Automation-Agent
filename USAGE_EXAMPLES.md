# 使用示例

## 配置环境

首先设置浏览器自动化 API 的地址：

```bash
export BROWSER_API_URL="http://192.168.1.218:52101"
```

## 示例 1: 提取网页内容

```python
from src.main import execute_browser_task

result = execute_browser_task(
    url="https://example.com",
    query="提取页面的标题和主要内容"
)

if result["success"]:
    print(f"✅ {result['message']}")
    print(f"内容: {result['result']['data']['content']}")
else:
    print(f"❌ 错误: {result['error']}")
```

## 示例 2: 下载 PDF 文件

```python
result = execute_browser_task(
    url="https://disclosure.shcpe.com.cn/#/notice/noticeTicket/acpt-overdue-list",
    query="找到最新的逾期承兑人名单PDF文件并下载"
)

if result["success"]:
    print(f"✅ {result['message']}")
    for file in result['result']['files']:
        print(f"  📄 {file['filename']} ({file['size_bytes']} bytes)")
else:
    print(f"❌ 错误: {result['error']}")
```

## 示例 3: 提取结构化数据

```python
result = execute_browser_task(
    url="https://example.com/products",
    query="列出所有产品的名称和价格"
)

if result["success"]:
    print(f"✅ {result['message']}")
    # 处理提取的数据
    data = result['result']['data']
    print(data)
else:
    print(f"❌ 错误: {result['error']}")
```

## 示例 4: 多步骤操作

```python
result = execute_browser_task(
    url="https://example.com",
    query="点击'产品'菜单，然后找到所有价格超过1000元的产品，提取它们的详细信息"
)

if result["success"]:
    print(f"✅ {result['message']}")
    print(result['result'])
else:
    print(f"❌ 错误: {result['error']}")
```

## 示例 5: 批量下载图片

```python
result = execute_browser_task(
    url="https://example.com/gallery",
    query="下载页面上所有的产品图片",
    timeout=300  # 增加超时时间
)

if result["success"]:
    print(f"✅ {result['message']}")
    print(f"下载了 {len(result['result']['files'])} 个文件")
else:
    print(f"❌ 错误: {result['error']}")
```

## 错误处理

```python
result = execute_browser_task(
    url="https://example.com",
    query="执行某个任务"
)

if not result["success"]:
    error_code = result.get("error_code")
    error_msg = result.get("error")
    
    if error_code == "TIMEOUT":
        print("任务超时，请尝试增加 timeout 参数")
    elif error_code == "MISSING_API_URL":
        print("请配置 BROWSER_API_URL 环境变量")
    elif error_code == "API_ERROR":
        print(f"API 请求失败: {error_msg}")
    else:
        print(f"任务失败: {error_msg}")
```

## 实际应用场景

### 场景 1: 定期抓取数据

```python
import schedule
import time

def scrape_data():
    result = execute_browser_task(
        url="https://example.com/data",
        query="提取最新的数据并保存"
    )
    # 处理结果...

# 每天上午 9 点执行
schedule.every().day.at("09:00").do(scrape_data)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 场景 2: 批量处理 URL

```python
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
]

for url in urls:
    result = execute_browser_task(
        url=url,
        query="提取页面内容"
    )
    if result["success"]:
        print(f"✅ {url} 处理成功")
    else:
        print(f"❌ {url} 处理失败: {result['error']}")
```

### 场景 3: 自动化报表生成

```python
# 1. 下载数据
download_result = execute_browser_task(
    url="https://example.com/reports",
    query="下载最新的月度报告Excel文件"
)

# 2. 处理数据
if download_result["success"]:
    # 使用 pandas 等工具处理下载的文件
    import pandas as pd
    file_path = f"data/outputs/{download_result['result']['files'][0]['filename']}"
    df = pd.read_excel(file_path)
    # 生成分析报告...
```

## 注意事项

1. **超时设置**: 复杂任务可能需要更长的执行时间，建议根据实际情况调整 `timeout` 参数
2. **文件输出**: 所有下载的文件都保存在 `data/outputs/` 目录，Gateway 会自动上传
3. **查询描述**: 尽量使用清晰、具体的自然语言描述任务
4. **错误重试**: 对于重要任务，建议添加错误重试逻辑

