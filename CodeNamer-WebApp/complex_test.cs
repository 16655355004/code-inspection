// 命名空间
namespace ComplexLinter.App
{
    using System;
    using System.Collections.Generic;

    // --- 数据模型与枚举 ---

    // [正确] 枚举名是名词，PascalCase
    public enum ProcessStatus
    {
        Success,
        Failure,
        Timeout
    }

    // [正确] 类名是名词，PascalCase
    public class User
    {
        public int Id { get; set; }
        public string UserName { get; set; }
    }

    // --- 接口定义 ---

    // [正确] 接口名以 'I' 开头，PascalCase (规则 I001)
    public interface IUserRepository
    {
        User GetUser(int userId);
        void SaveUser(User userToSave);
    }

    // [错误] 接口名未以 'I' 开头 (规则 I001)
    public interface UserCache
    {
        void ClearCache();
    }

    // --- 数据访问层 ---

    public class SqlUserRepository : IUserRepository
    {
        // [正确] 私有字段以下划线+camelCase (规则 F001)
        private readonly string _connectionString;

        // [错误] 私有字段使用了全大写 (规则 F001)
        private static int _MAX_CONNECTIONS;

        // [错误] 参数名使用了 snake_case (规则 PA001)
        public SqlUserRepository(string connection_string)
        {
            _connectionString = connection_string;
        }

        public User GetUser(int userId)
        {
            // 模拟数据库查询
            return new User { Id = userId, UserName = "DatabaseUser" };
        }

        // [错误] 方法名是名词短语，不是动词开头 (规则 M002)
        // [错误] 参数名太短 (规则 PA002)
        public void UserSave(User u)
        {
            // 模拟保存用户
            Console.WriteLine($"Saving user {u.UserName}");
        }
    }
    
    // --- 业务逻辑层 ---

    public class DataProcessingService
    {
        private readonly IUserRepository _userRepository;

        // [正确] 布尔属性以 'Is' 开头
        public bool IsServiceActive { get; private set; }

        public DataProcessingService(IUserRepository repo)
        {
            _userRepository = repo;
            IsServiceActive = true;
        }

        // [错误] 方法名是名词短语 (规则 M002)
        public ProcessStatus BatchProcess()
        {
            if (!IsServiceActive)
            {
                return ProcessStatus.Failure;
            }

            // [错误] 局部变量使用了 PascalCase (规则 V001)
            var UserList = new List<User> { _userRepository.GetUser(1), _userRepository.GetUser(2) };

            // [错误] 局部变量名太短 (规则 V002)
            var c = UserList.Count;
            Console.WriteLine($"Processing {c} users.");

            foreach(var user in UserList)
            {
                // [错误] 局部变量使用了 snake_case (规则 V001)
                string user_name_upper = user.UserName.ToUpper();
                Console.WriteLine(user_name_upper);
            }
            return ProcessStatus.Success;
        }

        // [错误] 方法名使用了 snake_case (规则 M001 & M002)
        // [错误] 参数名使用了 PascalCase (规则 PA001)
        public bool health_check(string Url)
        {
            return !string.IsNullOrEmpty(Url);
        }
    }
}
