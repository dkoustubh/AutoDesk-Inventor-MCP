using System;
using System.Threading.Tasks;
using ATS.AutodeskAgent.Interfaces;
using ATS.AutodeskAgent.Models;

namespace ATS.AutodeskAgent.Adapters
{
    public class AutodeskCompositeAdapter : IInventorAdapter
    {
        private readonly InventorAdapter _inventor = new();
        private readonly AutoCadAdapter _autocad = new();
        private string _activeApp = "Inventor";

        public string ApplicationName => _activeApp;

        public bool IsAvailable() => _inventor.IsAvailable() || _autocad.IsAvailable();

        public async Task<bool> InitializeAsync()
        {
            bool invInit = await _inventor.InitializeAsync();
            bool cadInit = await _autocad.InitializeAsync();

            if (cadInit)
            {
                _activeApp = "AutoCAD";
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("[AutodeskAgent] Active target: Autodesk AutoCAD");
                Console.ResetColor();
                return true;
            }

            _activeApp = "Inventor";
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("[AutodeskAgent] Active target: Autodesk Inventor");
            Console.ResetColor();
            return invInit;
        }

        public async Task<ExecutionResultDto> CreateBoxAsync(string jobId, BoxParameters parameters)
        {
            if (_activeApp == "AutoCAD")
            {
                return await _autocad.CreateBoxAsync(jobId, parameters);
            }
            return await _inventor.CreateBoxAsync(jobId, parameters);
        }

        public void Dispose()
        {
            _inventor.Dispose();
            _autocad.Dispose();
        }
    }
}
