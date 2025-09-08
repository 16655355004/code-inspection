using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Newtonsoft.Json;
using System.Text;

namespace CSharpParserHelper;

public class Program
{
    public static void Main(string[] args)
    {
        try
        {
            if (args.Length == 0)
            {
                Console.Error.WriteLine("Usage: CSharpParserHelper <code-string>");
                Environment.Exit(1);
            }

            string code = args[0];
            var ast = ParseCode(code);
            string json = JsonConvert.SerializeObject(ast, Formatting.None);
            Console.WriteLine(json);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Error: {ex.Message}");
            Environment.Exit(1);
        }
    }

    private static object ParseCode(string code)
    {
        var tree = CSharpSyntaxTree.ParseText(code);
        var root = tree.GetCompilationUnitRoot();
        
        var walker = new NameExtractorWalker();
        walker.Visit(root);
        
        // 转换为与 Python 后端兼容的格式
        var names = walker.Elements.Select(e => new
        {
            Type = e.ElementType.ToLower(),
            Name = e.Name,
            Line = e.Line,
            DataType = e.DataType
        }).ToList();
        
        return new
        {
            names = names,
            errors = tree.GetDiagnostics()
                .Where(d => d.Severity == DiagnosticSeverity.Error)
                .Select(d => new { message = d.GetMessage(), line = d.Location.GetLineSpan().StartLinePosition.Line + 1 })
                .ToList()
        };
    }
}

public class NameExtractorWalker : CSharpSyntaxWalker
{
    public List<CodeElement> Elements { get; } = new();

    public override void VisitClassDeclaration(ClassDeclarationSyntax node)
    {
        // 提取类声明信息
        AddElement("Class", node.Identifier.ValueText, GetLineNumber(node), "class");
        
        // 确保继续遍历类内部的成员
        base.VisitClassDeclaration(node);
    }

    public override void VisitInterfaceDeclaration(InterfaceDeclarationSyntax node)
    {
        // 提取接口声明信息
        AddElement("Interface", node.Identifier.ValueText, GetLineNumber(node), "interface");
        
        // 确保继续遍历接口内部的成员
        base.VisitInterfaceDeclaration(node);
    }

    public override void VisitMethodDeclaration(MethodDeclarationSyntax node)
    {
        // 提取方法声明信息，包括返回类型
        string returnType = node.ReturnType.ToString();
        AddElement("Method", node.Identifier.ValueText, GetLineNumber(node), returnType);
        
        // 继续遍历方法内部
        base.VisitMethodDeclaration(node);
    }

    public override void VisitPropertyDeclaration(PropertyDeclarationSyntax node)
    {
        // 提取属性声明信息，包括属性类型
        string propertyType = node.Type.ToString();
        AddElement("Property", node.Identifier.ValueText, GetLineNumber(node), propertyType);
        
        // 继续遍历属性内部（如 getter/setter）
        base.VisitPropertyDeclaration(node);
    }

    public override void VisitFieldDeclaration(FieldDeclarationSyntax node)
    {
        // 提取字段声明信息
        string fieldType = node.Declaration.Type.ToString();
        foreach (var variable in node.Declaration.Variables)
        {
            AddElement("Field", variable.Identifier.ValueText, GetLineNumber(node), fieldType);
        }
        
        base.VisitFieldDeclaration(node);
    }

    public override void VisitLocalDeclarationStatement(LocalDeclarationStatementSyntax node)
    {
        // 提取局部变量声明信息 - 这是处理局部变量的正确方法
        string variableType = node.Declaration.Type.ToString();
        foreach (var variable in node.Declaration.Variables)
        {
            AddElement("Variable", variable.Identifier.ValueText, GetLineNumber(node), variableType);
        }
        
        base.VisitLocalDeclarationStatement(node);
    }

    public override void VisitParameter(ParameterSyntax node)
    {
        if (!string.IsNullOrEmpty(node.Identifier.ValueText))
        {
            string parameterType = node.Type?.ToString() ?? "unknown";
            AddElement("Parameter", node.Identifier.ValueText, GetLineNumber(node), parameterType);
        }
        
        base.VisitParameter(node);
    }

    private void AddElement(string elementType, string name, int line, string dataType)
    {
        Elements.Add(new CodeElement
        {
            ElementType = elementType,
            Name = name,
            Line = line,
            DataType = dataType
        });
    }

    private static int GetLineNumber(SyntaxNode node)
    {
        return node.GetLocation().GetLineSpan().StartLinePosition.Line + 1;
    }
}

public class CodeElement
{
    public string ElementType { get; set; } = "";
    public string Name { get; set; } = "";
    public int Line { get; set; }
    public string DataType { get; set; } = "";
}

public class NameInfo
{
    public string Type { get; set; } = "";
    public string Name { get; set; } = "";
    public int Line { get; set; }
}
