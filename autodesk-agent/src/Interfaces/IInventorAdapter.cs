using System.Threading.Tasks;
using ATS.AutodeskAgent.Models;

namespace ATS.AutodeskAgent.Interfaces
{
    public interface IInventorAdapter : IAutodeskApplication
    {
        Task<ExecutionResultDto> CreateBoxAsync(string jobId, BoxParameters parameters);
    }
}
