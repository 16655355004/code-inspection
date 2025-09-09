#!/usr/bin/env python3
"""
CodeNamer CLI - 命令行版本的 C# 代码命名规范分析工具
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from naming_analyzer import NamingAnalyzer

def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="CodeNamer - C# 代码命名规范分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --file MyClass.cs
  %(prog)s --directory src/
  %(prog)s --file Class1.cs --file Class2.cs
  %(prog)s --directory src/ --exclude-pattern "*.Test.cs"
        """
    )
    
    # 文件和目录参数 - 至少需要指定一个
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--file", "-f",
        action="append",
        dest="files",
        help="指定要分析的 C# 文件路径（可多次使用）"
    )
    input_group.add_argument(
        "--directory", "-d",
        help="指定要分析的目录路径（会递归扫描 .cs 文件）"
    )
    
    # 可选参数
    parser.add_argument(
        "--exclude-pattern",
        action="append",
        dest="exclude_patterns",
        help="排除文件的模式（如 '*.Test.cs'，可多次使用）"
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["console", "json"],
        default="console",
        help="输出格式（默认: console）"
    )
    
    parser.add_argument(
        "--severity",
        choices=["error", "warning", "info"],
        default="info",
        help="最低显示的问题严重级别（默认: info）"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细信息"
    )
    
    return parser.parse_args()

def find_cs_files(directory: Path, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
    """在目录中查找 C# 文件"""
    import fnmatch
    
    cs_files = []
    exclude_patterns = exclude_patterns or []
    
    for cs_file in directory.rglob("*.cs"):
        # 检查是否匹配排除模式
        should_exclude = False
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(cs_file.name, pattern):
                should_exclude = True
                break
        
        if not should_exclude:
            cs_files.append(cs_file)
    
    return cs_files

def analyze_file(file_path: Path, analyzer: NamingAnalyzer) -> dict:
    """分析单个 C# 文件"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # 获取 C# 解析器路径
        parser_path = Path(__file__).parent.parent / "csharp-parser-helper"
        exe_path = parser_path / "bin" / "Debug" / "net8.0" / "CSharpParserHelper.exe"
        
        # 检查解析器是否存在
        if not exe_path.exists():
            print(f"错误: C# 解析器不存在，请先构建: {exe_path}")
            print("运行命令: cd csharp-parser-helper && dotnet build")
            sys.exit(1)
        
        # 调用 C# 解析器
        result = subprocess.run(
            [str(exe_path), code_content],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                "file": str(file_path),
                "error": f"解析器错误: {result.stderr}",
                "results": [],
                "parser_errors": []
            }
        
        # 解析 JSON 输出
        try:
            # --- 终极调试：打印原始 JSON ---
            print(f"----------- RAW JSON FROM C# PARSER ({file_path.name}) -----------")
            print(result.stdout)
            print("---------------------------------------------")
            
            parsed_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            return {
                "file": str(file_path),
                "error": f"JSON 解析错误: {str(e)}",
                "results": [],
                "parser_errors": []
            }
        
        # 分析命名规范
        analysis_results = analyzer.analyze_names(parsed_data)
        parser_errors = parsed_data.get("errors", [])
        
        return {
            "file": str(file_path),
            "results": [result.dict() for result in analysis_results],
            "parser_errors": parser_errors,
            "total_issues": len(analysis_results)
        }
        
    except FileNotFoundError:
        return {
            "file": str(file_path),
            "error": f"文件不存在: {file_path}",
            "results": [],
            "parser_errors": []
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": f"分析失败: {str(e)}",
            "results": [],
            "parser_errors": []
        }

def filter_by_severity(results: List[dict], min_severity: str) -> List[dict]:
    """根据严重级别过滤结果"""
    severity_order = {"error": 3, "warning": 2, "info": 1}
    min_level = severity_order.get(min_severity, 1)
    
    filtered_results = []
    for result in results:
        if severity_order.get(result.get("severity", "info"), 1) >= min_level:
            filtered_results.append(result)
    
    return filtered_results

def print_console_output(analysis_results: List[dict], args: argparse.Namespace):
    """以控制台格式输出结果"""
    total_files = len(analysis_results)
    total_issues = sum(result.get("total_issues", 0) for result in analysis_results)
    files_with_issues = sum(1 for result in analysis_results if result.get("total_issues", 0) > 0)
    
    print(f"\n=== CodeNamer 分析结果 ===")
    print(f"分析文件数: {total_files}")
    print(f"发现问题数: {total_issues}")
    print(f"有问题的文件数: {files_with_issues}")
    print("=" * 50)
    
    for file_result in analysis_results:
        file_path = file_result["file"]
        
        # 显示错误
        if "error" in file_result:
            print(f"\n {file_path}")
            print(f"   错误: {file_result['error']}")
            continue
        
        # 显示解析器错误
        parser_errors = file_result.get("parser_errors", [])
        if parser_errors:
            print(f"\n  {file_path} - 解析器错误:")
            for error in parser_errors:
                print(f"   第 {error.get('line', '?')} 行: {error.get('message', '未知错误')}")
        
        # 过滤并显示命名问题
        results = filter_by_severity(file_result.get("results", []), args.severity)
        
        if results:
            print(f"\n {file_path} - 发现 {len(results)} 个命名问题:")
            
            for issue in results:
                severity_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(issue["severity"], "🔵")
                print(f"   {severity_icon} 第 {issue['line']} 行: {issue['name']}")
                print(f"      [{issue['rule_id']}] {issue['message']}")
        elif file_result.get("total_issues", 0) == 0:
            print(f"\n {file_path} - 无命名问题")

def print_json_output(analysis_results: List[dict], args: argparse.Namespace):
    """以 JSON 格式输出结果"""
    # 过滤结果
    for file_result in analysis_results:
        if "results" in file_result:
            file_result["results"] = filter_by_severity(file_result["results"], args.severity)
            file_result["total_issues"] = len(file_result["results"])
    
    output = {
        "summary": {
            "total_files": len(analysis_results),
            "total_issues": sum(result.get("total_issues", 0) for result in analysis_results),
            "files_with_issues": sum(1 for result in analysis_results if result.get("total_issues", 0) > 0)
        },
        "files": analysis_results
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

def main():
    """主函数"""
    args = parse_arguments()
    
    if args.verbose:
        print("CodeNamer CLI - C# 代码命名规范分析工具")
        print(f"最低严重级别: {args.severity}")
        print(f"输出格式: {args.output}")
    
    # 收集要分析的文件
    files_to_analyze = []
    
    if args.files:
        # 处理指定的文件
        for file_path in args.files:
            path = Path(file_path)
            if path.exists() and path.suffix.lower() == '.cs':
                files_to_analyze.append(path)
            else:
                print(f"警告: 跳过无效的 C# 文件: {file_path}")
    
    elif args.directory:
        # 处理目录
        directory = Path(args.directory)
        if not directory.exists():
            print(f"错误: 目录不存在: {args.directory}")
            sys.exit(1)
        
        files_to_analyze = find_cs_files(directory, args.exclude_patterns)
        
        if args.verbose:
            print(f"在目录 {args.directory} 中找到 {len(files_to_analyze)} 个 C# 文件")
    
    if not files_to_analyze:
        print("错误: 没有找到要分析的 C# 文件")
        sys.exit(1)
    
    # 初始化分析器
    analyzer = NamingAnalyzer()
    
    # 分析文件
    analysis_results = []
    for file_path in files_to_analyze:
        if args.verbose:
            print(f"正在分析: {file_path}")
        
        result = analyze_file(file_path, analyzer)
        analysis_results.append(result)
    
    # 输出结果
    if args.output == "json":
        print_json_output(analysis_results, args)
    else:
        print_console_output(analysis_results, args)
    
    # 设置退出码
    total_issues = sum(result.get("total_issues", 0) for result in analysis_results)
    if total_issues > 0:
        sys.exit(1)  # 有问题时返回非零退出码
    else:
        sys.exit(0)  # 无问题时返回零退出码

if __name__ == "__main__":
    main()
