using System;

namespace TestNamespace
{
    public class TestClass
    {
        // 字段测试
        private int _maxRetries = 3;
        public string userName;
        
        // 属性测试
        public string UserName { get; set; }
        
        // 方法测试（包含参数和局部变量）
        public void ProcessData(string inputData, int timeout)
        {
            // 局部变量测试
            string processedResult = "";
            int counter = 0;
            
            for (int i = 0; i < timeout; i++)
            {
                processedResult += inputData;
                counter++;
            }
        }
        
        // 接口方法测试
        public bool ValidateInput(string data)
        {
            bool isValid = false;
            return isValid;
        }
    }
    
    public interface ITestInterface
    {
        void DoSomething(string parameter);
    }
}
