# CodeNamer-WebApp

基于语义分析的代码命名检查工具，支持**C#**和**Vue.js**代码审查和 NLP 命名规范检测的本地 Web 应用程序。

## 🚀 新功能亮点

- ✅ **多语言支持**: 现在支持 C#和 Vue.js 代码分析
- ✅ **Vue.js 专用规则**: 针对 Vue 组件的方法命名规范检查
- ✅ **智能解析**: 支持 Options API 和 Composition API
- ✅ **事件处理识别**: 自动识别事件处理方法并提供命名建议
- ✅ **重新设计界面**: 现代化的多语言选择界面

## 系统架构

- **后端**: Python 3.10+ + FastAPI
- **前端**: Vue.js 3 + TypeScript + Vite
- **C#解析器**: .NET 8 控制台应用程序（使用 Roslyn）
- **Vue 解析器**: Python 正则表达式解析器

## 环境要求

- Python 3.10+
- Node.js 16+
- .NET 8 SDK

## 项目结构

```
CodeNamer-WebApp/
├── backend/                 # Python FastAPI 后端
│   ├── main.py             # 主API服务器
│   ├── naming_analyzer.py  # 命名规范分析器
│   ├── vue_parser.py       # Vue.js代码解析器
│   └── test_vue_analysis.py # Vue功能测试
├── frontend/               # Vue.js 3 前端
│   └── src/components/CodeAnalyzer.vue # 重新设计的分析界面
├── csharp-parser-helper/   # .NET 8 C# 解析工具
├── start_vue_analysis.cmd  # 快速启动脚本
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

## 🎯 快速启动

### 方式一：使用启动脚本（推荐）

```bash
# Windows
start_vue_analysis.cmd
```

### 方式二：手动启动

```bash
# 启动后端
cd backend
uvicorn main:app --reload --port 8000

# 启动前端（新终端）
cd frontend
npm run dev
```

## 使用方法

1. 访问 http://localhost:5173
2. **选择编程语言**：C# 或 Vue.js
3. 粘贴您的代码到文本框中
4. 点击"分析代码"按钮
5. 查看分析结果和建议

## API 接口

- `POST /analyze` - 分析代码命名规范
  - 请求: `{"language": "csharp|vue", "code": "..."}`
  - 响应: `{"results": [...], "total_issues": 5, "parser_errors": [...]}`

## 📋 命名规范检查

### C# 规范

- **类名**: PascalCase，应为名词或名词短语
- **方法名**: PascalCase，应以动词开头
- **属性名**: PascalCase，应为名词或名词短语
- **字段名**: camelCase（私有）或 PascalCase（公共）
- **变量名**: camelCase，应具有描述性
- **参数名**: camelCase，应具有描述性
- **接口名**: 以 'I' 开头，使用 PascalCase

### Vue.js 规范

- **方法名**: camelCase，应具有描述性
- **事件处理方法**: 建议以 'handle' 或 'on' 开头
- **计算属性**: camelCase，应为描述性名词
- **避免**: 中文字符、特殊符号、过短的名称
- **异步方法**: 建议包含 'async' 或相关描述词

## 功能特性

- ✅ **多语言支持**: C# 和 Vue.js 代码分析
- ✅ **智能解析**: Options API 和 Composition API
- ✅ **实时分析**: 即时代码命名规范检查
- ✅ **语义验证**: 基于 NLP 的规则检查
- ✅ **现代界面**: 响应式 Web 界面，支持语言切换

## 技术特点

- 使用 Roslyn 进行 C# 代码解析
- Python 正则表达式解析 Vue.js 代码
- 基于 NLTK 的自然语言处理
- FastAPI 高性能后端
- Vue.js 3 现代前端框架
