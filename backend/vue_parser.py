import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class VueMethod:
    name: str
    line: int
    method_type: str  # 'method', 'computed', 'watch', 'lifecycle', 'event_handler'
    is_async: bool = False

class VueParser:
    """Vue.js 单文件组件解析器，专门用于提取方法名"""
    
    def __init__(self):
        # Vue 生命周期方法
        self.lifecycle_methods = {
            'beforeCreate', 'created', 'beforeMount', 'mounted',
            'beforeUpdate', 'updated', 'beforeUnmount', 'unmounted',
            'beforeDestroy', 'destroyed', 'activated', 'deactivated',
            'errorCaptured', 'renderTracked', 'renderTriggered'
        }
        
        # Vue 3 Composition API 生命周期
        self.composition_lifecycle = {
            'onBeforeMount', 'onMounted', 'onBeforeUpdate', 'onUpdated',
            'onBeforeUnmount', 'onUnmounted', 'onActivated', 'onDeactivated',
            'onErrorCaptured', 'onRenderTracked', 'onRenderTriggered'
        }
    
    def parse_vue_file(self, content: str) -> Dict[str, Any]:
        """解析Vue文件内容，返回方法信息"""
        try:
            methods = []
            errors = []
            
            # 提取 <script> 标签内容
            script_content = self._extract_script_content(content)
            if not script_content:
                return {
                    "names": [],
                    "errors": [{"message": "No <script> section found", "line": 1}]
                }
            
            # 解析方法
            methods.extend(self._parse_options_api_methods(script_content))
            methods.extend(self._parse_composition_api_methods(script_content))
            methods.extend(self._parse_regular_functions(script_content))
            
            # 转换为标准格式
            names = []
            for method in methods:
                names.append({
                    "Type": "method",
                    "Name": method.name,
                    "Line": method.line,
                    "DataType": method.method_type,
                    "IsAsync": method.is_async
                })
            
            return {
                "names": names,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "names": [],
                "errors": [{"message": f"Parse error: {str(e)}", "line": 1}]
            }
    
    def _extract_script_content(self, content: str) -> Optional[str]:
        """提取 <script> 标签中的内容"""
        # 匹配 <script> 标签，支持各种属性
        script_pattern = r'<script[^>]*>(.*?)</script>'
        match = re.search(script_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1)
        return None
    
    def _parse_options_api_methods(self, script_content: str) -> List[VueMethod]:
        """解析 Options API 中的方法"""
        methods = []
        lines = script_content.split('\n')
        
        # 查找 methods 对象
        in_methods_block = False
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检测 methods 块开始
            if re.match(r'methods\s*:\s*\{', stripped):
                in_methods_block = True
                brace_count = 1
                continue
            
            if in_methods_block:
                # 计算大括号层级
                brace_count += stripped.count('{') - stripped.count('}')
                
                # 如果大括号层级回到0，说明 methods 块结束
                if brace_count <= 0:
                    in_methods_block = False
                    continue
                
                # 解析方法定义
                method = self._parse_method_line(stripped, i)
                if method:
                    method.method_type = 'method'
                    methods.append(method)
        
        # 解析 computed 和 watch
        methods.extend(self._parse_computed_methods(script_content))
        methods.extend(self._parse_watch_methods(script_content))
        methods.extend(self._parse_lifecycle_methods(script_content))
        
        return methods
    
    def _parse_composition_api_methods(self, script_content: str) -> List[VueMethod]:
        """解析 Composition API 中的方法和变量"""
        methods = []
        lines = script_content.split('\n')

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # 解析 const/let/var 函数定义
            func_patterns = [
                r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(\s*[^)]*\s*\)\s*=>\s*\{',
                r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\([^)]*\)\s*\{',
                r'function\s+(\w+)\s*\([^)]*\)\s*\{'
            ]

            for pattern in func_patterns:
                match = re.search(pattern, stripped)
                if match:
                    method_name = match.group(1)
                    is_async = 'async' in stripped
                    method_type = self._determine_method_type(method_name)

                    methods.append(VueMethod(
                        name=method_name,
                        line=i,
                        method_type=method_type,
                        is_async=is_async
                    ))

            # 解析 ref/reactive/computed 变量声明
            ref_patterns = [
                r'(?:const|let|var)\s+(\w+)\s*=\s*ref\s*\(',
                r'(?:const|let|var)\s+(\w+)\s*=\s*reactive\s*\(',
                r'(?:const|let|var)\s+(\w+)\s*=\s*computed\s*\('
            ]

            for pattern in ref_patterns:
                match = re.search(pattern, stripped)
                if match:
                    var_name = match.group(1)
                    var_type = 'computed' if 'computed' in stripped else 'variable'

                    methods.append(VueMethod(
                        name=var_name,
                        line=i,
                        method_type=var_type,
                        is_async=False
                    ))

            # 解析普通变量声明（在函数内部）
            # 检查是否在函数内部（简单的缩进检测）
            if stripped and (line.startswith('  ') or line.startswith('\t')):
                var_patterns = [
                    r'(?:const|let|var)\s+(\w+)\s*=\s*(?!ref\s*\(|reactive\s*\(|computed\s*\(|function|async|\()',
                ]

                for pattern in var_patterns:
                    match = re.search(pattern, stripped)
                    if match:
                        var_name = match.group(1)
                        # 跳过一些常见的非变量声明
                        if var_name not in ['import', 'export', 'from', 'as']:
                            methods.append(VueMethod(
                                name=var_name,
                                line=i,
                                method_type='variable',
                                is_async=False
                            ))

            # 解析函数参数
            param_patterns = [
                r'(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?\(\s*([^)]+)\s*\)\s*=>\s*\{',
                r'(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?function\s*\(\s*([^)]*)\s*\)\s*\{',
                r'function\s+\w+\s*\(\s*([^)]*)\s*\)\s*\{'
            ]

            for pattern in param_patterns:
                match = re.search(pattern, stripped)
                if match and match.group(1).strip():
                    params_str = match.group(1)
                    # 解析参数列表
                    params = self._parse_parameters(params_str, i)
                    methods.extend(params)

        return methods
    
    def _parse_regular_functions(self, script_content: str) -> List[VueMethod]:
        """解析普通函数定义"""
        methods = []
        lines = script_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 解析箭头函数和普通函数
            patterns = [
                r'(\w+)\s*:\s*(?:async\s+)?\(\s*[^)]*\s*\)\s*=>\s*\{',  # method: () => {}
                r'(\w+)\s*:\s*(?:async\s+)?function\s*\([^)]*\)\s*\{',   # method: function() {}
                r'(\w+)\s*\([^)]*\)\s*\{',  # method() {}
            ]
            
            for pattern in patterns:
                match = re.search(pattern, stripped)
                if match:
                    method_name = match.group(1)
                    is_async = 'async' in stripped
                    
                    # 跳过已知的Vue选项
                    if method_name in ['data', 'props', 'emits', 'components', 'directives']:
                        continue
                    
                    method_type = self._determine_method_type(method_name)
                    
                    methods.append(VueMethod(
                        name=method_name,
                        line=i,
                        method_type=method_type,
                        is_async=is_async
                    ))
        
        return methods
    
    def _parse_computed_methods(self, script_content: str) -> List[VueMethod]:
        """解析 computed 属性"""
        methods = []
        lines = script_content.split('\n')
        
        in_computed_block = False
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if re.match(r'computed\s*:\s*\{', stripped):
                in_computed_block = True
                brace_count = 1
                continue
            
            if in_computed_block:
                brace_count += stripped.count('{') - stripped.count('}')
                
                if brace_count <= 0:
                    in_computed_block = False
                    continue
                
                method = self._parse_method_line(stripped, i)
                if method:
                    method.method_type = 'computed'
                    methods.append(method)
        
        return methods
    
    def _parse_watch_methods(self, script_content: str) -> List[VueMethod]:
        """解析 watch 方法"""
        methods = []
        lines = script_content.split('\n')
        
        in_watch_block = False
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if re.match(r'watch\s*:\s*\{', stripped):
                in_watch_block = True
                brace_count = 1
                continue
            
            if in_watch_block:
                brace_count += stripped.count('{') - stripped.count('}')
                
                if brace_count <= 0:
                    in_watch_block = False
                    continue
                
                method = self._parse_method_line(stripped, i)
                if method:
                    method.method_type = 'watch'
                    methods.append(method)
        
        return methods
    
    def _parse_lifecycle_methods(self, script_content: str) -> List[VueMethod]:
        """解析生命周期方法"""
        methods = []
        lines = script_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查生命周期方法
            for lifecycle in self.lifecycle_methods:
                pattern = rf'{lifecycle}\s*\([^)]*\)\s*\{{'
                if re.search(pattern, stripped):
                    methods.append(VueMethod(
                        name=lifecycle,
                        line=i,
                        method_type='lifecycle',
                        is_async='async' in stripped
                    ))
        
        return methods
    
    def _parse_method_line(self, line: str, line_num: int) -> Optional[VueMethod]:
        """解析单行方法定义"""
        # 匹配各种方法定义格式
        patterns = [
            r'(\w+)\s*\([^)]*\)\s*\{',  # methodName() {}
            r'(\w+)\s*:\s*(?:async\s+)?function\s*\([^)]*\)\s*\{',  # methodName: function() {}
            r'(\w+)\s*:\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{',  # methodName: () => {}
            r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',  # async methodName() {}
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                method_name = match.group(1)
                is_async = 'async' in line
                
                return VueMethod(
                    name=method_name,
                    line=line_num,
                    method_type='method',
                    is_async=is_async
                )
        
        return None
    
    def _parse_parameters(self, params_str: str, line_num: int) -> List[VueMethod]:
        """解析函数参数"""
        params = []
        if not params_str.strip():
            return params

        # 分割参数，处理TypeScript类型注解
        param_list = []
        current_param = ""
        paren_count = 0

        for char in params_str:
            if char == ',' and paren_count == 0:
                if current_param.strip():
                    param_list.append(current_param.strip())
                current_param = ""
            else:
                if char in '({[<':
                    paren_count += 1
                elif char in ')}]>':
                    paren_count -= 1
                current_param += char

        if current_param.strip():
            param_list.append(current_param.strip())

        # 提取参数名
        for param in param_list:
            # 处理解构参数和类型注解
            param_match = re.match(r'(\w+)(?:\s*:\s*[^=]+)?(?:\s*=\s*.+)?', param.strip())
            if param_match:
                param_name = param_match.group(1)
                params.append(VueMethod(
                    name=param_name,
                    line=line_num,
                    method_type='parameter',
                    is_async=False
                ))

        return params

    def _determine_method_type(self, method_name: str) -> str:
        """根据方法名判断方法类型"""
        if method_name in self.lifecycle_methods or method_name in self.composition_lifecycle:
            return 'lifecycle'
        elif method_name.startswith(('handle', 'on')):
            return 'event_handler'
        elif method_name.startswith(('get', 'set', 'is', 'has', 'can')):
            return 'computed'
        else:
            return 'method'
