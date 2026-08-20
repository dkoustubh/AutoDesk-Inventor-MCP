using System;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using AtsAutodeskAgent.Adapters;
using AtsAutodeskAgent.Services;

namespace AtsAutodeskAgent
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            Console.Title = "ATS Autodesk Agent - 192.168.11.150";

            string serverUrl = Environment.GetEnvironmentVariable("ATS_SERVER_URL") ?? "http://192.168.11.86:8005";
            string workstationIp = Environment.GetEnvironmentVariable("WORKSTATION_IP") ?? "192.168.11.150";
            bool useMock = args.Length > 0 && args[0].ToLower() == "--mock";

            IAutodeskAdapter adapter;
            if (useMock || !RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                Console.WriteLine("[Mode] Running in SIMULATED / MOCK mode.");
                adapter = new MockInventorAdapter();
            }
            else
            {
                Console.WriteLine("[Mode] Running in LIVE Autodesk Inventor COM mode.");
                adapter = new InventorAdapter();
            }

            var agent = new AgentClient(serverUrl, workstationIp, adapter);

            Console.CancelKeyPress += (s, e) =>
            {
                Console.WriteLine("Shutting down ATS Autodesk Agent...");
                agent.Stop();
                e.Cancel = true;
            };

            await agent.StartAsync();
        }
    }
}
