using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using AtsAutodeskAgent.Models;

namespace AtsAutodeskAgent.Adapters
{
    public class InventorAdapter : IAutodeskAdapter
    {
        private dynamic? _inventorApp;
        public string ApplicationName => "Autodesk Inventor";
        public bool IsConnected => _inventorApp != null;

        public async Task<bool> ConnectAsync()
        {
            return await Task.Run(() =>
            {
                try
                {
                    // Try to attach to active Inventor instance
                    try
                    {
                        _inventorApp = Marshal.GetActiveObject("Inventor.Application");
                        Console.WriteLine("[InventorAdapter] Attached to running Autodesk Inventor instance.");
                    }
                    catch
                    {
                        // Launch new Inventor instance if not running
                        Console.WriteLine("[InventorAdapter] Starting new Autodesk Inventor instance...");
                        Type? invType = Type.GetTypeFromProgID("Inventor.Application");
                        if (invType != null)
                        {
                            _inventorApp = Activator.CreateInstance(invType);
                            _inventorApp.Visible = true;
                            Console.WriteLine("[InventorAdapter] Inventor launched and visible.");
                        }
                    }

                    return _inventorApp != null;
                }
                catch (Exception ex)
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"[InventorAdapter] COM connection error: {ex.Message}");
                    Console.ResetColor();
                    _inventorApp = null;
                    return false;
                }
            });
        }

        public async Task<ExecutionResult> CreateBoxAsync(CreateBoxParams parameters)
        {
            var sw = Stopwatch.StartNew();
            return await Task.Run(() =>
            {
                if (_inventorApp == null)
                {
                    return new ExecutionResult
                    {
                        Success = false,
                        Message = "Autodesk Inventor is not connected or COM instance is null.",
                        ExecutionTimeMs = 0
                    };
                }

                try
                {
                    Console.WriteLine($"[InventorAdapter] Executing CreateBox: {parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm} mm (Centered: {parameters.Centered})");

                    // 1. Create a new Part Document (kPartDocumentObject = 12290)
                    dynamic partDoc = _inventorApp.Documents.Add(12290, _inventorApp.FileManager.GetTemplateFile(12290), true);
                    dynamic partDef = partDoc.ComponentDefinition;
                    dynamic transientGeometry = _inventorApp.TransientGeometry;

                    // 2. Select XY Work Plane (WorkPlanes[3] in Inventor is typically the XY Plane)
                    dynamic xyPlane = partDef.WorkPlanes[3];

                    // 3. Create a 2D Sketch on the XY Plane
                    dynamic sketch = partDef.Sketches.Add(xyPlane);

                    // Convert mm to cm (Autodesk Inventor internal units are centimeters)
                    double lenCm = parameters.LengthMm / 10.0;
                    double widCm = parameters.WidthMm / 10.0;
                    double hgtCm = parameters.HeightMm / 10.0;

                    double x1 = parameters.Centered ? -lenCm / 2.0 : 0.0;
                    double y1 = parameters.Centered ? -widCm / 2.0 : 0.0;
                    double x2 = parameters.Centered ? lenCm / 2.0 : lenCm;
                    double y2 = parameters.Centered ? widCm / 2.0 : widCm;

                    // 4. Create Two Point Rectangle in Sketch
                    dynamic pt1 = transientGeometry.CreatePoint2d(x1, y1);
                    dynamic pt2 = transientGeometry.CreatePoint2d(x2, y2);
                    sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2);

                    // 5. Create Extrude Feature (kJoinOperation = 20481, kPositiveExtentDirection = 20993)
                    dynamic profile = sketch.Profiles.AddForSolid();
                    dynamic extrudeDef = partDef.Features.ExtrudeFeatures.CreateExtrudeDefinition(profile, 20481);
                    extrudeDef.SetDistanceExtent(hgtCm, 20993);

                    dynamic extrudeFeature = partDef.Features.ExtrudeFeatures.Add(extrudeDef);

                    // 6. Refresh / Fit View
                    _inventorApp.ActiveView.Fit();

                    sw.Stop();
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine($"[InventorAdapter] Successfully created {parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm} mm Box in Inventor ({sw.ElapsedMilliseconds} ms)");
                    Console.ResetColor();

                    return new ExecutionResult
                    {
                        Success = true,
                        Message = $"Created {parameters.LengthMm}x{parameters.WidthMm}x{parameters.HeightMm} mm solid cube in Autodesk Inventor",
                        ExecutionTimeMs = (int)sw.ElapsedMilliseconds,
                        Data = new Dictionary<string, object>
                        {
                            { "application", "Autodesk Inventor" },
                            { "dimensions", $"{parameters.LengthMm} x {parameters.WidthMm} x {parameters.HeightMm} mm" },
                            { "volume_mm3", parameters.LengthMm * parameters.WidthMm * parameters.HeightMm },
                            { "centered", parameters.Centered }
                        }
                    };
                }
                catch (Exception ex)
                {
                    sw.Stop();
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"[InventorAdapter] Failed to create box: {ex.Message}");
                    Console.ResetColor();

                    return new ExecutionResult
                    {
                        Success = false,
                        Message = $"Inventor API Exception: {ex.Message}",
                        ExecutionTimeMs = (int)sw.ElapsedMilliseconds
                    };
                }
            });
        }

        public void Disconnect()
        {
            _inventorApp = null;
        }
    }
}
