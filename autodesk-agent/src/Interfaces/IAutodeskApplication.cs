using System.Threading.Tasks;

namespace ATS.AutodeskAgent.Interfaces
{
    public interface IAutodeskApplication
    {
        string ApplicationName { get; }
        bool IsAvailable();
        Task<bool> InitializeAsync();
        void Dispose();
    }
}
