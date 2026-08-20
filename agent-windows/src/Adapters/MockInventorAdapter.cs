using System;
using System.Diagnostics;
using System.Threading.Tasks;
using AtsAutodeskAgent.Models;

namespace AtsAutodeskAgent.Adapters
{
    public class MockInventorAdapter : IAutodeskAdapter
    {
        public string ApplicationName => "Autodesk Inventor (Simulated)";
        public bool IsConnected { get; private set; } = false;

        public async Task<bool> ConnectAsync()
        {
            await Task.Delay(300);
            IsConnected = true;
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("[MockInventorAdapter] Connected to simulated Autodesk Inventor engine.");
            Console.ResetColor();
            return true;
        }

        public async Task<ExecutionResult> CreateBoxAsync(CreateBoxParams parameters)
        {
            var sw = Stopwatch.StartNew();
            Console.WriteLine($"[MockInventorAdapter] Simulating PartDoc -> Sketch -> Extrude ({parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm} mm)...");
            await Task.Delay(800); // Simulate CAD computation
            sw.Stop();

            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine($"[MockInventorAdapter] Box {parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm} mm created successfully ({sw.ElapsedMilliseconds} ms)");
            Console.ResetColor();

            return new ExecutionResult
            {
                Success = true,
                Message = $"Simulated {parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm} mm box creation in Inventor",
                ExecutionTimeMs = (int)sw.ElapsedMilliseconds,
                Data = new Dictionary<string, object>
                {
                    { "application", "Autodesk Inventor (Mock/Simulation)" },
                    { "dimensions", $"{parameters.LengthMm} x {parameters.WidthMm} x {parameters.HeightMm} mm" },
                    { "volume_mm3", parameters.LengthMm * parameters.WidthMm * parameters.HeightMm },
                    { "centered", parameters.Centered }
                }
            };
        }

        public void Disconnect()
        {
            IsConnected = false;
        }
    }
}
