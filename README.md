# 🤖 浏览器自动化代理预制件

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/managed%20by-uv-F67909.svg)](https://github.com/astral-sh/uv)

> **通过自然语言执行浏览器自动化任务，支持网页访问、信息提取和文件下载**

## 📋 目录

- [什么是浏览器自动化代理？](#什么是浏览器自动化代理)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [开发指南](#开发指南)
- [API 文档](#api-文档)
- [常见问题](#常见问题)

## 什么是浏览器自动化代理？

浏览器自动化代理是一个可被 AI 调用的预制件，封装了强大的浏览器自动化能力。通过简单的自然语言描述，即可执行复杂的网页操作任务。

### 核心特性

- 🎯 **自然语言交互**: 无需编写复杂代码，用自然语言描述任务即可
- 🌐 **强大的浏览器能力**: 基于 Playwright 的企业级浏览器自动化
- 📄 **智能文件处理**: 自动下载并保存文件（PDF、图片、Excel等）
- 🔍 **灵活的数据提取**: 智能提取网页信息和结构化数据
- ⚡ **即插即用**: 无需配置浏览器环境，直接调用 API 服务

## 功能特性

### ✅ 支持的操作

- 访问任意网页
- 提取页面内容（文本、数据、元数据）
- 下载文件（PDF、图片、Excel、压缩包等）
- 页面交互（点击、填写表单、滚动等）
- 多步骤复杂任务（导航、搜索、下载等组合操作）

### 📊 返回结果类型

- **文本结果**: 提取的页面内容、数据等
- **文件结果**: 下载的文件（自动保存到输出目录）
- **混合结果**: 同时返回文本和文件

## 快速开始

### 1. 环境准备

```bash
# 安装 uv（如果尚未安装）
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 克隆仓库
git clone https://github.com/your-org/browser-automation-agent.git
cd browser-automation-agent

# 同步依赖
uv sync --dev
```

### 2. 配置环境变量

在平台上配置以下 Secret（或本地测试时设置环境变量）：

```bash
export BROWSER_API_URL="http://your-browser-api-server:52101"
```

### 3. 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/test_main.py::TestExecuteBrowserTask::test_success_with_text_result -v
```

## 使用示例

### 示例 1: 提取网页内容

```python
from src.main import execute_browser_task

# 提取页面主要内容
result = execute_browser_task(
    url="https://example.com",
    query="提取页面的标题和主要内容"
)

print(result)
# {
#     "success": True,
#     "message": "成功提取页面内容",
#     "result": {
#         "type": "text",
#         "data": {
#             "content": "..."
#         }
#     }
# }
```

### 示例 2: 下载文件

```python
# 下载 PDF 文件
result = execute_browser_task(
    url="https://disclosure.shcpe.com.cn/#/notice/noticeTicket/acpt-overdue-list",
    query="找到最新的逾期承兑人名单PDF文件并下载"
)

print(result)
# {
#     "success": True,
#     "message": "成功下载 1 个文件",
#     "result": {
#         "type": "file",
#         "files": [
#             {
#                 "filename": "截至2025年9月30日承兑人逾期名单.pdf",
#                 "size_bytes": 348308,
#                 "mime_type": "application/pdf"
#             }
#         ]
#     }
# }
```

### 示例 3: 复杂多步骤任务

```python
# 搜索并提取数据
result = execute_browser_task(
    url="https://example.com/products",
    query="找到所有价格在100-500元之间的产品，提取名称、价格和库存信息"
)
```

### 示例 4: 批量下载

```python
# 下载所有图片
result = execute_browser_task(
    url="https://example.com/gallery",
    query="下载页面上所有的产品图片"
)
```

## 开发指南

### 项目结构

```
browser-automation-agent/
├── src/
│   ├── __init__.py           # 模块导出
│   └── main.py              # 核心实现
├── tests/
│   └── test_main.py         # 单元测试
├── data/
│   └── outputs/             # 输出文件目录（Gateway 自动上传）
├── prefab-manifest.json     # 函数元数据
├── pyproject.toml          # 项目配置
└── README.md               # 本文档
```

### 本地开发

```bash
# 安装开发依赖
uv sync --dev

# 安装 pre-commit hooks（推荐）
uv run pre-commit install

# 代码风格检查
uv run flake8 src/ --max-line-length=120

# 验证 manifest 一致性
uv run python scripts/validate_manifest.py

# 运行测试
uv run pytest tests/ -v --cov=src
```

### 添加新功能

1. 修改 `src/main.py` 中的函数逻辑
2. 更新 `prefab-manifest.json` 中的函数描述
3. 在 `tests/test_main.py` 中添加测试
4. 运行验证脚本确保一致性

## API 文档

### `execute_browser_task`

执行浏览器自动化任务。

**参数**:

| 参数名 | 类型 | 必需 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `url` | string | 是 | - | 目标网页 URL |
| `query` | string | 是 | - | 任务描述（自然语言） |
| `timeout` | integer | 否 | 120 | 超时时间（秒） |

**返回值**:

```typescript
{
  success: boolean;           // 是否成功
  message?: string;           // 任务描述（成功时）
  result?: {                  // 任务结果（成功时）
    type: "text" | "file" | "mixed";
    data?: {                  // type=text 时存在
      content: string;
    };
    files?: [                 // type=file 时存在
      {
        filename: string;
        size_bytes: number;
        mime_type: string;
      }
    ];
  };
  error?: string;             // 错误信息（失败时）
  error_code?: string;        // 错误代码（失败时）
}
```

**错误代码**:

| 错误代码 | 说明 |
|---------|------|
| `INVALID_URL` | URL 参数无效 |
| `INVALID_QUERY` | query 参数无效 |
| `MISSING_API_URL` | 未配置 BROWSER_API_URL |
| `TIMEOUT` | 任务执行超时 |
| `API_ERROR` | API 请求失败 |
| `FILE_DOWNLOAD_ERROR` | 文件下载失败 |
| `FILE_SAVE_ERROR` | 文件保存失败 |
| `TASK_FAILED` | 任务执行失败 |
| `UNEXPECTED_ERROR` | 未知错误 |

## 配置说明

### 必需的 Secrets

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `BROWSER_API_URL` | 浏览器自动化后端 API 地址 | `http://192.168.1.218:52101` |

### 后端 API 要求

后端服务需要提供以下接口：

1. **任务执行接口**: `POST /agent/task`
   ```json
   // 请求
   {
     "query": "访问 https://example.com，然后提取页面内容"
   }
   
   // 响应
   {
     "status": "success",
     "response": "任务完成描述",
     "result": {
       "type": "text" | "file_reference" | "file_inline",
       ...
     }
   }
   ```

2. **文件下载接口**: `GET /downloads/{file_id}`
   - 返回文件的二进制内容

## 常见问题

### Q: 如何配置后端 API 地址？

**A**: 在平台上配置 `BROWSER_API_URL` Secret，或本地测试时设置环境变量：
```bash
export BROWSER_API_URL="http://your-api-server:52101"
```

### Q: 支持哪些类型的文件下载？

**A**: 支持所有类型的文件，包括：
- PDF 文档
- 图片（JPG、PNG、GIF 等）
- Office 文档（Excel、Word 等）
- 压缩包（ZIP、RAR 等）
- 任意二进制文件

### Q: 如何处理需要登录的网站？

**A**: 在 `query` 中描述登录步骤，例如：
```python
result = execute_browser_task(
    url="https://example.com/login",
    query="使用用户名 'test' 和密码 '123456' 登录，然后访问个人中心下载报告"
)
```

### Q: 任务执行超时怎么办？

**A**: 可以增加 `timeout` 参数：
```python
result = execute_browser_task(
    url="https://example.com",
    query="...",
    timeout=300  # 5分钟
)
```

### Q: 如何查看详细的执行日志？

**A**: 后端 API 返回的 `debug_trace` 字段包含详细的执行日志和工具调用记录。

## 发布流程

```bash
# 1. 更新版本号（prefab-manifest.json 和 pyproject.toml 必须一致）
# 2. 提交代码
git add .
git commit -m "Release v0.1.0"

# 3. 创建并推送 tag
git tag v0.1.0
git push origin v0.1.0

# GitHub Actions 会自动构建并发布
```

## 技术栈

- **语言**: Python 3.11+
- **HTTP 客户端**: requests
- **测试框架**: pytest
- **包管理**: uv
- **后端服务**: 浏览器自动化 API（支持 Playwright MCP）

## License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**: 本预制件需要配合浏览器自动化后端服务使用。确保后端服务已部署并正常运行。
