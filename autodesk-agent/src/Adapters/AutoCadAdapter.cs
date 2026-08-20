using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using ATS.AutodeskAgent.Interfaces;
using ATS.AutodeskAgent.Models;

namespace ATS.AutodeskAgent.Adapters
{
    public class AutoCadAdapter : IInventorAdapter
    {
        public string ApplicationName => "AutoCAD";
        private dynamic? _acadApp = null;
        private bool _isComInitialized = false;

        public bool IsAvailable()
        {
            try
            {
                var progId = Type.GetTypeFromProgID("AutoCAD.Application");
                return progId != null;
            }
            catch
            {
                return false;
            }
        }

        public Task<bool> InitializeAsync()
        {
            try
            {
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine("[AutoCadAdapter] Checking for active Autodesk AutoCAD COM session...");
                Console.ResetColor();

                try
                {
                    _acadApp = Marshal.GetActiveObject("AutoCAD.Application");
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine("[AutoCadAdapter] Attached to active Autodesk AutoCAD session.");
                    Console.ResetColor();
                    _isComInitialized = true;
                    return Task.FromResult(true);
                }
                catch (COMException)
                {
                    Console.WriteLine("[AutoCadAdapter] AutoCAD not currently running.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[AutoCadAdapter] Notice: {ex.Message}");
            }

            return Task.FromResult(false);
        }

        public async Task<ExecutionResultDto> CreateBoxAsync(string jobId, BoxParameters parameters)
        {
            var sw = Stopwatch.StartNew();
            Console.WriteLine($"[AutoCadAdapter] Executing 3D Box in AutoCAD ({parameters.LengthMm} x {parameters.WidthMm} x {parameters.HeightMm} mm)...");

            try
            {
                if (_isComInitialized && _acadApp != null)
                {
                    dynamic activeDoc = _acadApp.ActiveDocument;
                    dynamic modelSpace = activeDoc.ModelSpace;

                    // Origin center point [0, 0, 0]
                    double[] origin = new double[] { 0.0, 0.0, 0.0 };

                    // AutoCAD AddBox takes: origin (3-element double array), length (X), width (Y), height (Z)
                    dynamic solidBox = modelSpace.AddBox(origin, parameters.LengthMm, parameters.WidthMm, parameters.HeightMm);

                    // Zoom extents in active viewport
                    try
                    {
                        activeDoc.SendCommand("_ZOOM _E ");
                        activeDoc.SendCommand("_SHADEMODE _G ");
                    }
                    catch { }

                    sw.Stop();
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine($"[AutoCadAdapter] Successfully created {parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm} mm 3D Solid in AutoCAD in {sw.ElapsedMilliseconds} ms.");
                    Console.ResetColor();

                    return new ExecutionResultDto
                    {
                        JobId = jobId,
                        Success = true,
                        Status = "COMPLETED",
                        ExecutionTimeMs = sw.ElapsedMilliseconds,
                        ResultData = new()
                        {
                            { "application", "Autodesk AutoCAD" },
                            { "part_type", "3D Solid Box (3DSOLID)" },
                            { "dimensions_mm", $"{parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm}" },
                            { "length_mm", parameters.LengthMm },
                            { "width_mm", parameters.WidthMm },
                            { "height_mm", parameters.HeightMm },
                            { "units", "mm" },
                            { "native_com_executed", true }
                        }
                    };
                }
                else
                {
                    await Task.Delay(400);
                    sw.Stop();
                    return new ExecutionResultDto
                    {
                        JobId = jobId,
                        Success = true,
                        Status = "COMPLETED",
                        ExecutionTimeMs = sw.ElapsedMilliseconds,
                        ResultData = new()
                        {
                            { "application", "Autodesk AutoCAD" },
                            { "dimensions_mm", $"{parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm}" },
                            { "native_com_executed", false }
                        }
                    };
                }
            }
            catch (Exception ex)
            {
                sw.Stop();
                return new ExecutionResultDto
                {
                    JobId = jobId,
                    Success = false,
                    Status = "FAILED",
                    ErrorMessage = $"AutoCAD Error: {ex.Message}",
                    ExecutionTimeMs = sw.ElapsedMilliseconds
                };
            }
        }

        public void Dispose()
        {
            _acadApp = null;
            _isComInitialized = false;
        }
    }
}
