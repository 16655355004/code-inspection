import json
import subprocess
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import CodeAnalysisRequest, CodeAnalysisResponse, AnalysisResult
from naming_analyzer import NamingAnalyzer

app = FastAPI(title="CodeNamer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = NamingAnalyzer()

@app.get("/")
async def root():
    return {"message": "CodeNamer API is running"}

@app.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code for naming convention issues"""
    
    if request.language.lower() != "csharp":
        raise HTTPException(status_code=400, detail="Only C# is currently supported")
    
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    try:
        
        parser_path = Path(__file__).parent.parent / "csharp-parser-helper"
        exe_path = parser_path / "bin" / "Debug" / "net8.0" / "CSharpParserHelper.exe"
        
        
        if not exe_path.exists():
            build_result = subprocess.run(
                ["dotnet", "build"],
                cwd=parser_path,
                capture_output=True,
                text=True
            )
            if build_result.returncode != 0:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to build C# parser: {build_result.stderr}"
                )
        
       
        result = subprocess.run(
            [str(exe_path), request.code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Parser error: {result.stderr}"
            )
        
       
        try:
           
            print("----------- RAW JSON FROM C# PARSER -----------")
            print(result.stdout)
            print("---------------------------------------------")
            
            parsed_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse parser output: {str(e)}"
            )
        
        
        analysis_results = analyzer.analyze_names(parsed_data)
        parser_errors = parsed_data.get("errors", [])
        
        return CodeAnalysisResponse(
            results=analysis_results,
            total_issues=len(analysis_results),
            parser_errors=parser_errors
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Parser timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
