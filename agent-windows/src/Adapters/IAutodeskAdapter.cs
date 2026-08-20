using System.Threading.Tasks;
using AtsAutodeskAgent.Models;

namespace AtsAutodeskAgent.Adapters
{
    public interface IAutodeskAdapter
    {
        string ApplicationName { get; }
        bool IsConnected { get; }
        Task<bool> ConnectAsync();
        Task<ExecutionResult> CreateBoxAsync(CreateBoxParams parameters);
        void Disconnect();
    }
}
