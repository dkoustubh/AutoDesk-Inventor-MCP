using System;
using System.Threading;
using System.Threading.Tasks;
using ATS.AutodeskAgent.Adapters;

namespace ATS.AutodeskAgent
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            Console.Title = "ATS Engineering AI — Autodesk Agent";
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine(@"
   ___ _____ ___   _       _            _           _        _                    _   
  / _ \_   _/ __| /_\ _  _| |_ ___  __| |___ ___| |__    /_\  __ _ ___ _ _  _| |_ 
 / /_\ \| | \__ \/ _ \ || |  _/ _ \/ _` / -_|_-< / /_   / _ \/ _` / -_) ' \/ _` |  _|_
/_/   \_\_| |___/_/ \_\_,_|\__\___/\__,_\___/__/|____| /_/ \_\__, \___|_||_\__,_|\__|
                                                             |___/                    
            ");
            Console.ResetColor();

            Console.WriteLine("==================================================================");
            Console.WriteLine("  ATS Autodesk Agent (Phase 1 — Inventor Connector)");
            Console.WriteLine("==================================================================");

            var config = AgentConfig.Load();

            // Override via CLI arguments if provided
            if (args.Length >= 1) config.ServerUrl = args[0];
            if (args.Length >= 2) config.WorkstationIp = args[1];

            Console.WriteLine($"Server URL:     {config.ServerUrl}");
            Console.WriteLine($"Workstation IP: {config.WorkstationIp}");
            Console.WriteLine($"Host Name:      {config.Hostname}");
            Console.WriteLine($"User:           {config.UserName}");
            Console.WriteLine($"Application:    {config.ApplicationName}");
            Console.WriteLine("------------------------------------------------------------------");

            // 1. Initialize Multi-CAD COM Adapter (AutoCAD & Inventor)
            var cadAdapter = new AutodeskCompositeAdapter();
            await cadAdapter.InitializeAsync();

            // 2. Start WebSocket Persistent Agent Loop
            var client = new AgentWebSocketClient(config, cadAdapter);
            
            var cts = new CancellationTokenSource();
            Console.CancelKeyPress += (s, e) =>
            {
                e.Cancel = true;
                client.Stop();
                cts.Cancel();
                Console.WriteLine("\nShutting down Autodesk Agent...");
            };

            await client.StartAsync();
        }
    }
}
