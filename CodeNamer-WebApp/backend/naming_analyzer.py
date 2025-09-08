import re
import nltk
from typing import List, Dict, Any, Callable
from models import AnalysisResult

# --- NLTK Data Download ---
# 确保必要的 NLTK 数据包已下载
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

class NamingAnalyzer:
    """
    A class to analyze code naming conventions based on syntax and semantics (Part-of-Speech).
    """
    def __init__(self):
        self.rules = {
            "C001": "Class names should use PascalCase",
            "C002": "Class names should be nouns or noun phrases",
            "M001": "Method names should use PascalCase",
            "M002": "Method names should start with a verb",
            "P001": "Property names should use PascalCase",
            "P002": "Property names should be nouns or noun phrases",
            "F001": "Field names should use camelCase (private) or PascalCase (public)",
            "F002": "Field names should be nouns or noun phrases",
            "V001": "Variable names should use camelCase",
            "V002": "Variable names should be descriptive (avoid single letters except for loops)",
            "PA001": "Parameter names should use camelCase",
            "PA002": "Parameter names should be descriptive",
            "I001": "Interface names should start with 'I' and use PascalCase"
        }
        
        # 使用 set 以获得更快的查找性能
        self.IGNORED_PREFIXES = {
            "Visit", "Override", "Handle", "On", "Test", "Setup", 
            "TearDown", "Benchmark", "Mock", "Stub"
        }
        
        # --- 重构亮点 1: 使用字典分发代替 if/elif 链 ---
        self.handler_map: Dict[str, Callable[[str, int], List[AnalysisResult]]] = {
            "class": self._analyze_class_name,
            "interface": self._analyze_interface_name,
            "method": self._analyze_method_name,
            "property": self._analyze_property_name,
            "field": self._analyze_field_name,
            "variable": self._analyze_variable_name,
            "parameter": self._analyze_parameter_name,
        }
    
    def analyze_names(self, parsed_data: Dict[str, Any]) -> List[AnalysisResult]:
        """
        Analyzes a list of code names from parsed data and returns a list of violations.
        """
        results = []
        names = parsed_data.get("names", [])
        
        for name_info in names:
            name_type = name_info.get("Type", "").lower() # 转为小写以匹配 handler_map
            name = name_info.get("Name", "")
            line = name_info.get("Line", 0)
            
            # Skip empty names or compiler-generated names
            if not name or name.startswith("<") or name.startswith("_"):
                continue
            
            # 使用字典分发调用对应的处理函数
            handler = self.handler_map.get(name_type)
            if handler:
                results.extend(handler(name, line))
        
        return results
    
    def _analyze_class_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not self._is_pascal_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="C001", message=f"Class name '{name}' should use PascalCase", severity="warning"))
        if not self._is_noun_phrase(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="C002", message=f"Class name '{name}' should be a noun or noun phrase", severity="info"))
        return results
    
    def _analyze_interface_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not name.startswith("I") or not self._is_pascal_case(name[1:]):
            results.append(AnalysisResult(line=line, name=name, rule_id="I001", message=f"Interface name '{name}' should start with 'I' and use PascalCase", severity="warning"))
        return results
    
    def _analyze_method_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        
        # Skip special .NET methods
        if name in ["Main", "ToString", "GetHashCode", "Equals", "Dispose"]:
            return results
        
        if any(name.startswith(prefix) for prefix in self.IGNORED_PREFIXES):
            return results
        
        if not self._is_pascal_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="M001", message=f"Method name '{name}' should use PascalCase", severity="warning"))
        if not self._starts_with_verb(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="M002", message=f"Method name '{name}' should start with a verb", severity="info"))
        return results
    
    def _analyze_property_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not self._is_pascal_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="P001", message=f"Property name '{name}' should use PascalCase", severity="warning"))
        
        # Skip noun phrase check for boolean properties (Is*, Has*, Can*, Should*, etc.)
        boolean_prefixes = ["Is", "Has", "Can", "Should", "Will", "Would", "Could", "Must", "Might"]
        is_boolean_property = any(name.startswith(prefix) for prefix in boolean_prefixes)
        
        if not is_boolean_property and not self._is_noun_phrase(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="P002", message=f"Property name '{name}' should be a noun or noun phrase", severity="info"))
        return results
    
    def _analyze_field_name(self, name: str, line: int) -> List[AnalysisResult]:
        # This logic assumes a simple convention. Real-world C# can be more complex.
        results = []
        if name.startswith("_"):
            field_name = name.lstrip("_")
            # Check if it's all uppercase (like MAX_CONNECTIONS) - this should be camelCase
            if field_name.isupper() or "_" in field_name:
                results.append(AnalysisResult(line=line, name=name, rule_id="F001", message=f"Private field name '{name}' should use camelCase (after underscore)", severity="warning"))
            elif not self._is_camel_case(field_name):
                results.append(AnalysisResult(line=line, name=name, rule_id="F001", message=f"Private field name '{name}' should use camelCase (after underscore)", severity="warning"))
        elif not self._is_pascal_case(name):
             results.append(AnalysisResult(line=line, name=name, rule_id="F001", message=f"Public/internal field name '{name}' should use PascalCase", severity="warning"))
        return results
    
    def _analyze_variable_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not self._is_camel_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="V001", message=f"Variable name '{name}' should use camelCase", severity="warning"))
        if len(name) == 1 and name not in "ijkxyz":
            results.append(AnalysisResult(line=line, name=name, rule_id="V002", message=f"Variable name '{name}' should be more descriptive", severity="info"))
        return results
    
    def _analyze_parameter_name(self, name: str, line: int) -> List[AnalysisResult]:
        results = []
        if not self._is_camel_case(name):
            results.append(AnalysisResult(line=line, name=name, rule_id="PA001", message=f"Parameter name '{name}' should use camelCase", severity="warning"))
        if len(name) <= 2 and name not in ["id", "x", "y", "z", "ex"]:
            results.append(AnalysisResult(line=line, name=name, rule_id="PA002", message=f"Parameter name '{name}' should be more descriptive", severity="info"))
        return results

    # --- Helper Methods ---

    def _is_pascal_case(self, name: str) -> bool:
        """Check if name follows PascalCase convention."""
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))

    def _is_camel_case(self, name: str) -> bool:
        """Check if name follows camelCase convention."""
        return bool(re.match(r'^[a-z][a-zA-Z0-9]*$', name))

    def _split_case(self, name: str) -> List[str]:
        """Splits PascalCase and camelCase into words."""
        return re.findall(r'[A-Z][a-z0-9]*|[a-z]+[a-z0-9]*', name)

    def _starts_with_verb(self, name: str) -> bool:
        """Check if name starts with a verb using NLTK."""
        try:
            words = self._split_case(name)
            if not words:
                return False
            
            first_word = words[0].lower()
            # NLTK can be slow, a simple prefix check can be a fast path
            # 大幅扩充常见动词集合以解决 GenerateReport 等误报问题
            common_verbs = {
                # 基础动词
                "get", "set", "is", "has", "can", "should", "will", "would", "could",
                "add", "remove", "delete", "create", "update", "save", "load", "insert",
                "find", "search", "filter", "sort", "validate", "check", "verify",
                "calculate", "compute", "process", "handle", "execute", "run", "perform",
                "start", "stop", "pause", "resume", "reset", "clear", "clean", "flush",
                "build", "make", "construct", "destroy", "dispose", "release",
                "batch", "parse", "format", "convert", "transform", "map", "reduce", "merge",
                # 常见编程动词 - 解决 GenerateReport 误报
                "generate", "render", "display", "show", "hide", "toggle", "switch", "process",
                "send", "receive", "transmit", "broadcast", "publish", "subscribe",
                "connect", "disconnect", "bind", "unbind", "attach", "detach",
                "open", "close", "read", "write", "copy", "move", "rename", "backup",
                "import", "export", "sync", "upload", "download", "fetch", "push", "pull",
                "enable", "disable", "activate", "deactivate", "initialize", "finalize",
                "begin", "end", "complete", "finish", "cancel", "abort", "retry",
                "lock", "unlock", "encrypt", "decrypt", "compress", "decompress",
                "serialize", "deserialize", "encode", "decode", "hash", "sign",
                # UI/UX 相关动词
                "click", "select", "choose", "pick", "drag", "drop", "scroll", "zoom",
                "navigate", "redirect", "refresh", "reload", "submit", "apply", "confirm",
                # 数据操作动词
                "query", "count", "sum", "average", "group", "join", "split", "slice",
                "append", "prepend", "replace", "substitute", "trim", "pad", "fill",
                # 状态管理动词
                "track", "monitor", "observe", "watch", "listen", "notify", "alert",
                "log", "record", "store", "cache", "buffer", "queue", "schedule"
            }
            if first_word in common_verbs:
                return True

            tokens = nltk.word_tokenize(first_word)
            if tokens:
                pos_tags = nltk.pos_tag(tokens)
                return pos_tags[0][1].startswith('VB') # VB* means any form of verb
        except Exception as e:
            print(f"Error during NLTK verb check for '{name}': {e}")
        return False

    def _is_noun_phrase(self, name: str) -> bool:
        """Check if name represents a noun or noun phrase (stricter)."""
        # Heuristic: The last word in a phrase is often the head noun.
        try:
            words = self._split_case(name)
            if not words:
                return False
            
            last_word = words[-1].lower()
            tokens = nltk.word_tokenize(last_word)
            if tokens:
                pos_tags = nltk.pos_tag(tokens)
                return pos_tags[0][1].startswith('NN') # NN* means any form of noun
        except Exception as e:
            print(f"Error during NLTK noun check for '{name}': {e}")
        return False