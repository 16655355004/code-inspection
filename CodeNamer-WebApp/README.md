# CodeNamer-WebApp

A local web application for semantic code naming analysis, supporting C# code review with NLP-based naming convention checks.

## Architecture

- **Backend**: Python 3.10+ with FastAPI
- **Frontend**: Vue.js 3 with TypeScript and Vite
- **Parser Helper**: .NET 8 console application using Roslyn

## Prerequisites

- Python 3.10+
- Node.js 16+
- .NET 8 SDK

## Project Structure

```
CodeNamer-WebApp/
├── backend/                 # Python FastAPI backend
├── frontend/               # Vue.js 3 frontend
├── csharp-parser-helper/   # .NET 8 C# parser tool
└── README.md
```

## Setup Instructions

### 1. C# Parser Helper

```bash
cd csharp-parser-helper
dotnet build
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Start the backend server (runs on http://localhost:8000)
2. Start the frontend development server (runs on http://localhost:5173)
3. Open your browser and navigate to the frontend URL
4. Paste C# code in the textarea and click "Analyze Code"
5. View the semantic naming analysis results

## API Endpoints

- `POST /analyze` - Analyze code naming conventions
  - Request: `{"language": "csharp", "code": "..."}`
  - Response: `[{"line": 10, "name": "UserData", "ruleId": "F001", "message": "..."}]`

## Features

- Real-time C# code analysis
- Semantic naming convention validation
- NLP-based rule checking
- Clean, responsive web interface
