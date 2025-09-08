# CodeNamer-WebApp

基于语义分析的代码命名检查工具，支持C#代码审查和NLP命名规范检测的本地Web应用程序。

## 系统架构

- **后端**: Python 3.10+ + FastAPI
- **前端**: Vue.js 3 + TypeScript + Vite
- **解析器**: .NET 8 控制台应用程序（使用Roslyn）

## 环境要求

- Python 3.10+
- Node.js 16+
- .NET 8 SDK

## 项目结构

```
CodeNamer-WebApp/
├── backend/                 # Python FastAPI 后端
├── frontend/               # Vue.js 3 前端
├── csharp-parser-helper/   # .NET 8 C# 解析工具
└── README.md
```

## 安装说明

### 1. C# 解析器设置

```bash
cd csharp-parser-helper
dotnet build
```

### 2. 后端设置

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. 前端设置

```bash
cd frontend
npm install
npm run dev
```

## 使用方法

1. 启动后端服务器（运行在 http://localhost:8000）
2. 启动前端开发服务器（运行在 http://localhost:5173）
3. 打开浏览器并导航到前端URL
4. 在文本区域粘贴C#代码并点击"分析代码"
5. 查看语义命名分析结果

## API 接口

- `POST /analyze` - 分析代码命名规范
  - 请求: `{"language": "csharp", "code": "..."}`
  - 响应: `[{"line": 10, "name": "UserData", "ruleId": "F001", "message": "..."}]`

## 功能特性

- 实时C#代码分析
- 语义命名规范验证
- 基于NLP的规则检查
- 简洁响应式Web界面

## 技术特点

- 使用Roslyn进行C#代码解析
- 基于自然语言处理的命名分析
- 支持多种命名规范检查规则
- 提供详细的代码质量报告
