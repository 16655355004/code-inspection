import re
import nltk
from typing import List, Dict, Any, Callable
from models import AnalysisResult

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

class NamingAnalyzer:
    def __init__(self):
        self.rules = {
            # C# 规则
            "C001": "类名应使用帕斯卡命名法（PascalCase）",
            "C002": "类名应为名词或名词短语",
            "M001": "方法名应使用帕斯卡命名法（PascalCase）",
            "M002": "方法名应以动词开头",
            "P001": "属性名应使用帕斯卡命名法（PascalCase）",
            "P002": "属性名应为名词或名词短语",
            "F001": "字段名应使用驼峰命名法（camelCase，私有）或帕斯卡命名法（PascalCase，公有）",
            "F002": "字段名应为名词或名词短语",
            "V001": "变量名应使用驼峰命名法（camelCase）",
            "V002": "变量名应具有描述性（除循环变量外避免单字母）",
            "PA001": "参数名应使用驼峰命名法（camelCase）",
            "PA002": "参数名应具有描述性",
            "I001": "接口名应以大写字母'I'开头并使用帕斯卡命名法（PascalCase）",

            # Vue.js 规则
            "VM001": "Vue方法名应使用驼峰命名法（camelCase）",
            "VM002": "Vue方法名应具有描述性",
            "VM003": "事件处理方法应以'handle'或'on'开头",
            "VM004": "方法名应避免使用中文字符或特殊符号",
            "VM005": "异步方法建议包含'async'或相关描述词",
            "VM006": "计算属性名应为有意义的名词",
            "VM007": "watch方法名应与被监听属性一致"
        }
        
        self.IGNORED_PREFIXES = {
            "Visit", "Override", "Handle", "On", "Test", "Setup", 
            "TearDown", "Benchmark", "Mock", "Stub"
        }
        
        self.handler_map: Dict[str, Callable[[str, int], List[AnalysisResult]]] = {
            "class": self._analyze_class_name,
            "interface": self._analyze_interface_name,
            "method": self._analyze_method_name,
            "property": self._analyze_property_name,
            "field": self._analyze_field_name,
            "variable": self._analyze_variable_name,
            "parameter": self._analyze_parameter_name,
        }

        # Vue.js 特定的处理器映射
        self.vue_handler_map: Dict[str, Callable[[str, int, str], List[AnalysisResult]]] = {
            "method": self._analyze_vue_method_name,
            "variable": self._analyze_vue_variable_name,
            "computed": self._analyze_vue_computed_name,
            "parameter": self._analyze_vue_parameter_name,
        }
    
    def analyze_names(self, parsed_data: Dict[str, Any], language: str = "csharp") -> List[AnalysisResult]:
        results = []
        names = parsed_data.get("names", [])

        for name_info in names:
            name_type = name_info.get("Type", "").lower()
            name = name_info.get("Name", "")
            line = name_info.get("Line", 0)
            data_type = name_info.get("DataType", "")

            if not name or name.startswith("<") or name.startswith("_"):
                continue

            # 根据语言选择不同的处理器
            if language.lower() == "vue":
                # 对于Vue，使用DataType字段来确定处理器
                actual_type = data_type if data_type else name_type
                handler = self.vue_handler_map.get(actual_type)
                if handler:
                    results.extend(handler(name, line, data_type))
            else:
                handler = self.handler_map.get(name_type)
                if handler:
                    results.extend(handler(name, line))

        return results
    
    def _analyze_class_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not self._is_pascal_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="C001", message=f"类名 '{name}' 应使用帕斯卡命名法（PascalCase）", severity="warning"))
        if not self._is_noun_phrase(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="C002", message=f"类名 '{name}' 应为名词或名词短语", severity="info"))
        return results
    
    def _analyze_interface_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not name.startswith("I") or not self._is_pascal_case(name[1:]):
            results.append(AnalysisResult(line=line, name=name, rule_id="I001", message=f"接口名 '{name}' 应以大写字母'I'开头并使用帕斯卡命名法（PascalCase）", severity="warning"))
        return results
    
    def _analyze_method_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        
        if name in ["Main", "ToString", "GetHashCode", "Equals", "Dispose"]:
            return results
        
        if any(name.startswith(prefix) for prefix in self.IGNORED_PREFIXES):
            return results
        
        if not self._is_pascal_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="M001", message=f"方法名 '{name}' 应使用帕斯卡命名法（PascalCase）", severity="warning"))
        if not self._starts_with_verb(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="M002", message=f"方法名 '{name}' 应以动词开头", severity="info"))
        return results
    
    def _analyze_property_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not self._is_pascal_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="P001", message=f"属性名 '{name}' 应使用帕斯卡命名法（PascalCase）", severity="warning"))
        
        boolean_prefixes = ["Is", "Has", "Can", "Should", "Will", "Would", "Could", "Must", "Might"]
        is_boolean_property = any(name.startswith(prefix) for prefix in boolean_prefixes)
        
        if not is_boolean_property and not self._is_noun_phrase(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="P002", message=f"属性名 '{name}' 应为名词或名词短语", severity="info"))
        return results
    
    def _analyze_field_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if name.startswith("_"):
            field_name = name.lstrip("_")
            if field_name.isupper() or "_" in field_name:
                results.append(AnalysisResult(line=line, name=name, rule_id="F001", message=f"私有字段名 '{name}' 应使用驼峰命名法（camelCase，去除下划线后）", severity="warning"))
            elif not self._is_camel_case(field_name):
                results.append(AnalysisResult(line=line, name=name, rule_id="F001", message=f"私有字段名 '{name}' 应使用驼峰命名法（camelCase，去除下划线后）", severity="warning"))
        elif not self._is_pascal_case(name):
             results.append(AnalysisResult(line=line, name=name, rule_id="F001", message=f"公有/内部字段名 '{name}' 应使用帕斯卡命名法（PascalCase）", severity="warning"))
        return results
    
    def _analyze_variable_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not self._is_camel_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="V001", message=f"变量名 '{name}' 应使用驼峰命名法（camelCase）", severity="warning"))
        if len(name) == 1 and name not in "ijkxyz":
            results.append(AnalysisResult(line=line, name=name, rule_id="V002", message=f"变量名 '{name}' 应更具描述性", severity="info"))
        return results

    def _analyze_vue_method_name(self, name: str, line: int, method_type: str) -> List[AnalysisResult]:
        """分析Vue.js方法名"""
        results = []

        # 跳过Vue生命周期方法
        vue_lifecycle = {
            'beforeCreate', 'created', 'beforeMount', 'mounted',
            'beforeUpdate', 'updated', 'beforeUnmount', 'unmounted',
            'beforeDestroy', 'destroyed', 'activated', 'deactivated',
            'errorCaptured', 'renderTracked', 'renderTriggered',
            'onBeforeMount', 'onMounted', 'onBeforeUpdate', 'onUpdated',
            'onBeforeUnmount', 'onUnmounted', 'onActivated', 'onDeactivated',
            'onErrorCaptured', 'onRenderTracked', 'onRenderTriggered'
        }

        if name in vue_lifecycle:
            return results

        # VM001: Vue方法名应使用camelCase
        if not self._is_camel_case(name):
            suggested_name = self._to_camel_case(name)
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM001",
                message=f"Vue方法名 '{name}' 应使用驼峰命名法（camelCase）。建议：'{suggested_name}'",
                severity="warning"
            ))

        # VM002: Vue方法名应具有描述性
        if len(name) <= 2 and name not in ["go", "do", "is", "on"]:
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM002",
                message=f"Vue方法名 '{name}' 应更具描述性",
                severity="info"
            ))

        # VM003: 事件处理方法应以'handle'或'on'开头
        if method_type == 'event_handler' and not (name.startswith('handle') or name.startswith('on')):
            suggested_name = f"handle{name[0].upper()}{name[1:]}" if name else "handleEvent"
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM003",
                message=f"事件处理方法 '{name}' 应以'handle'或'on'开头。建议：'{suggested_name}'",
                severity="info"
            ))

        # VM004: 避免使用中文字符或特殊符号
        if re.search(r'[\u4e00-\u9fff]', name) or re.search(r'[^\w]', name):
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM004",
                message=f"方法名 '{name}' 应避免使用中文字符或特殊符号",
                severity="warning"
            ))

        # VM005: 异步方法建议包含'async'或相关描述词
        # 这个检查需要在解析器中提供is_async信息，暂时跳过

        # VM006: Computed属性名应为描述性名词
        if method_type == 'computed' and not self._is_noun_phrase(name):
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM006",
                message=f"计算属性名 '{name}' 应为有意义的名词",
                severity="info"
            ))

        return results

    def _analyze_vue_variable_name(self, name: str, line: int, var_type: str) -> List[AnalysisResult]:
        """分析Vue.js变量名（ref/reactive）"""
        results = []

        # VM001: Vue变量名应使用camelCase
        if not self._is_camel_case(name):
            suggested_name = self._to_camel_case(name)
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM001",
                message=f"Vue变量名 '{name}' 应使用驼峰命名法（camelCase）。建议：'{suggested_name}'",
                severity="warning"
            ))

        # VM002: Vue变量名应具有描述性
        if len(name) <= 2 and name not in ["id", "x", "y", "z"]:
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM002",
                message=f"Vue变量名 '{name}' 应更具描述性",
                severity="info"
            ))

        # VM004: 避免使用中文字符或特殊符号
        if re.search(r'[\u4e00-\u9fff]', name) or re.search(r'[^\w]', name):
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM004",
                message=f"变量名 '{name}' 应避免使用中文字符或特殊符号",
                severity="warning"
            ))

        return results

    def _analyze_vue_computed_name(self, name: str, line: int, computed_type: str) -> List[AnalysisResult]:
        """分析Vue.js计算属性名"""
        results = []

        # VM001: Vue计算属性名应使用camelCase
        if not self._is_camel_case(name):
            suggested_name = self._to_camel_case(name)
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM001",
                message=f"Vue计算属性名 '{name}' 应使用驼峰命名法（camelCase）。建议：'{suggested_name}'",
                severity="warning"
            ))

        # VM006: Computed属性名应为描述性名词
        verb_prefixes = ['get', 'set', 'fetch', 'load', 'save', 'update', 'delete', 'create', 'make', 'build', 'generate']
        for prefix in verb_prefixes:
            if name.startswith(prefix) and len(name) > len(prefix):
                suggested_name = name[len(prefix):]
                suggested_name = suggested_name[0].lower() + suggested_name[1:] if suggested_name else name
                results.append(AnalysisResult(
                    line=line,
                    name=name,
                    rule_id="VM006",
                    message=f"计算属性名 '{name}' 应为名词，不应为动词。建议：'{suggested_name}'",
                    severity="info"
                ))
                break

        # VM004: 避免使用中文字符或特殊符号
        if re.search(r'[\u4e00-\u9fff]', name) or re.search(r'[^\w]', name):
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM004",
                message=f"计算属性名 '{name}' 应避免使用中文字符或特殊符号",
                severity="warning"
            ))

        return results

    def _analyze_vue_parameter_name(self, name: str, line: int, param_type: str) -> List[AnalysisResult]:
        """分析Vue.js参数名"""
        results = []

        # VM001: Vue参数名应使用camelCase
        if not self._is_camel_case(name):
            suggested_name = self._to_camel_case(name)
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM001",
                message=f"Vue参数名 '{name}' 应使用驼峰命名法（camelCase）。建议：'{suggested_name}'",
                severity="warning"
            ))

        # VM002: Vue参数名应具有描述性
        if len(name) <= 2 and name not in ["id", "x", "y", "z", "ex"]:
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM002",
                message=f"Vue参数名 '{name}' 应更具描述性",
                severity="info"
            ))

        # VM004: 避免使用中文字符或特殊符号
        if re.search(r'[\u4e00-\u9fff]', name) or re.search(r'[^\w]', name):
            results.append(AnalysisResult(
                line=line,
                name=name,
                rule_id="VM004",
                message=f"参数名 '{name}' 应避免使用中文字符或特殊符号",
                severity="warning"
            ))

        return results

    def _analyze_parameter_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not self._is_camel_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="PA001", message=f"参数名 '{name}' 应使用驼峰命名法（camelCase）", severity="warning"))
        if len(name) <= 2 and name not in ["id", "x", "y", "z", "ex"]:
            results.append(AnalysisResult(line=line, name=name, rule_id="PA002", message=f"参数名 '{name}' 应更具描述性", severity="info"))
        return results


    def _is_pascal_case(self, name: str) -> bool:
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))

    def _is_camel_case(self, name: str) -> bool:
        return bool(re.match(r'^[a-z][a-zA-Z0-9]*$', name))

    def _split_case(self, name: str) -> List[str]:
        return re.findall(r'[A-Z][a-z0-9]*|[a-z]+[a-z0-9]*', name)

    def _starts_with_verb(self, name: str) -> bool:
        try:
            words = self._split_case(name)
            if not words:
                return False
            
            first_word = words[0].lower()
            common_verbs = {
                "get", "set", "is", "has", "can", "should", "will", "would", "could",
                "add", "remove", "delete", "create", "update", "save", "load", "insert",
                "find", "search", "filter", "sort", "validate", "check", "verify",
                "calculate", "compute", "process", "handle", "execute", "run", "perform",
                "start", "stop", "pause", "resume", "reset", "clear", "clean", "flush",
                "build", "make", "construct", "destroy", "dispose", "release",
                "batch", "parse", "format", "convert", "transform", "map", "reduce", "merge",
                "generate", "render", "display", "show", "hide", "toggle", "switch", "process",
                "send", "receive", "transmit", "broadcast", "publish", "subscribe",
                "connect", "disconnect", "bind", "unbind", "attach", "detach",
                "open", "close", "read", "write", "copy", "move", "rename", "backup",
                "import", "export", "sync", "upload", "download", "fetch", "push", "pull",
                "enable", "disable", "activate", "deactivate", "initialize", "finalize",
                "begin", "end", "complete", "finish", "cancel", "abort", "retry",
                "lock", "unlock", "encrypt", "decrypt", "compress", "decompress",
                "serialize", "deserialize", "encode", "decode", "hash", "sign",
                "click", "select", "choose", "pick", "drag", "drop", "scroll", "zoom",
                "navigate", "redirect", "refresh", "reload", "submit", "apply", "confirm",
                "query", "count", "sum", "average", "group", "join", "split", "slice",
                "append", "prepend", "replace", "substitute", "trim", "pad", "fill",
                "track", "monitor", "observe", "watch", "listen", "notify", "alert",
                "log", "record", "store", "cache", "buffer", "queue", "schedule"
            }
            if first_word in common_verbs:
                return True

            tokens = nltk.word_tokenize(first_word)
            if tokens:
                pos_tags = nltk.pos_tag(tokens)
                return pos_tags[0][1].startswith('VB')
        except Exception as e:
            print(f"Error during NLTK verb check for '{name}': {e}")
        return False

    def _is_noun_phrase(self, name: str) -> bool:
        try:
            words = self._split_case(name)
            if not words:
                return False
            
            last_word = words[-1].lower()
            tokens = nltk.word_tokenize(last_word)
            if tokens:
                pos_tags = nltk.pos_tag(tokens)
                return pos_tags[0][1].startswith('NN')
        except Exception as e:
            print(f"Error during NLTK noun check for '{name}': {e}")
        return False

    def _to_camel_case(self, name: str) -> str:
        """将名称转换为camelCase"""
        if not name:
            return name

        # 处理下划线分隔的名称
        if '_' in name:
            parts = name.split('_')
            if parts:
                return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

        # 处理全大写的名称（需要在PascalCase之前检查）
        if name.isupper() and len(name) > 1:
            return name.lower()

        # 处理PascalCase转camelCase
        if name and name[0].isupper():
            return name[0].lower() + name[1:]

        return name