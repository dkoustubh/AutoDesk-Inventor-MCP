using System;
using System.IO;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using AtsAutodeskAgent.Adapters;
using AtsAutodeskAgent.Models;

namespace AtsAutodeskAgent.Services
{
    public class AgentClient
    {
        private readonly string _serverUrl;
        private readonly string _workstationIp;
        private readonly IAutodeskAdapter _adapter;
        private ClientWebSocket? _webSocket;
        private readonly CancellationTokenSource _cts = new();

        public AgentClient(string serverUrl, string workstationIp, IAutodeskAdapter adapter)
        {
            _serverUrl = serverUrl.TrimEnd('/');
            _workstationIp = workstationIp;
            _adapter = adapter;
        }

        public async Task StartAsync()
        {
            Console.WriteLine($"===================================================");
            Console.WriteLine($" ATS Autodesk Agent v1.0.0");
            Console.WriteLine($" Target Server : {_serverUrl}");
            Console.WriteLine($" Workstation IP: {_workstationIp}");
            Console.WriteLine($" Adapter       : {_adapter.ApplicationName}");
            Console.WriteLine($"===================================================");

            // Connect to CAD Adapter first
            bool cadReady = await _adapter.ConnectAsync();
            if (!cadReady)
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("[Agent] Warning: Autodesk CAD connection failed. Will keep retrying upon job receipt.");
                Console.ResetColor();
            }

            while (!_cts.Token.IsCancellationRequested)
            {
                try
                {
                    _webSocket = new ClientWebSocket();
                    string wsUri = $"{_serverUrl.Replace("http://", "ws://").Replace("https://", "wss://")}/ws/agent/{_workstationIp}";
                    Console.WriteLine($"[Agent] Connecting WebSocket to {wsUri}...");

                    await _webSocket.ConnectAsync(new Uri(wsUri), _cts.Token);
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine($"[Agent] Connected to Central AI Server! Registered status: READY");
                    Console.ResetColor();

                    // Start Heartbeat loop in background
                    _ = Task.Run(() => HeartbeatLoopAsync(_webSocket, _cts.Token));

                    // Listen for incoming jobs
                    await ReceiveLoopAsync(_webSocket, _cts.Token);
                }
                catch (Exception ex)
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"[Agent] WebSocket disconnected: {ex.Message}. Retrying in 5 seconds...");
                    Console.ResetColor();
                    await Task.Delay(5000, _cts.Token);
                }
            }
        }

        private async Task HeartbeatLoopAsync(ClientWebSocket ws, CancellationToken ct)
        {
            while (!ct.IsCancellationRequested && ws.State == WebSocketState.Open)
            {
                try
                {
                    var hb = new { type = "HEARTBEAT", workstation_ip = _workstationIp, status = "READY" };
                    byte[] bytes = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(hb));
                    await ws.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, ct);
                    await Task.Delay(15000, ct);
                }
                catch
                {
                    break;
                }
            }
        }

        private async Task ReceiveLoopAsync(ClientWebSocket ws, CancellationToken ct)
        {
            var buffer = new byte[8192];
            while (!ct.IsCancellationRequested && ws.State == WebSocketState.Open)
            {
                using var ms = new MemoryStream();
                WebSocketReceiveResult result;
                do
                {
                    result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), ct);
                    ms.Write(buffer, 0, result.Count);
                } while (!result.EndOfMessage);

                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", ct);
                    break;
                }

                string message = Encoding.UTF8.GetString(ms.ToArray());
                await HandleServerMessageAsync(ws, message, ct);
            }
        }

        private async Task HandleServerMessageAsync(ClientWebSocket ws, string message, CancellationToken ct)
        {
            try
            {
                using var doc = JsonDocument.Parse(message);
                var root = doc.RootElement;
                if (root.TryGetProperty("type", out var typeProp) && typeProp.GetString() == "EXECUTE_JOB")
                {
                    var jobElement = root.GetProperty("job");
                    string jobId = jobElement.GetProperty("job_id").GetString() ?? "unknown";
                    string action = jobElement.GetProperty("action").GetString() ?? "";

                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine($"[Agent] >>> Received Job [{jobId}]: {action}");
                    Console.ResetColor();

                    // Notify Progress: Initializing CAD
                    await SendProgressAsync(ws, jobId, "INVENTOR_EXECUTING", "Opening document and building geometry in Inventor...", ct);

                    ExecutionResult execResult;
                    if (action == "inventor.create_box")
                    {
                        var boxParams = JsonSerializer.Deserialize<CreateBoxParams>(jobElement.GetProperty("parameters").GetRawText()) ?? new CreateBoxParams();
                        execResult = await _adapter.CreateBoxAsync(boxParams);
                    }
                    else
                    {
                        execResult = new ExecutionResult
                        {
                            Success = false,
                            Message = $"Unsupported action: {action}"
                        };
                    }

                    // Return Job Result
                    var responsePayload = new
                    {
                        type = "JOB_RESULT",
                        job_id = jobId,
                        success = execResult.Success,
                        message = execResult.Message,
                        execution_time_ms = execResult.ExecutionTimeMs,
                        data = execResult.Data
                    };

                    byte[] respBytes = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(responsePayload));
                    await ws.SendAsync(new ArraySegment<byte>(respBytes), WebSocketMessageType.Text, true, ct);
                    Console.WriteLine($"[Agent] <<< Returned Job Result [{jobId}]: Success={execResult.Success}");
                }
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[Agent] Error processing server message: {ex.Message}");
                Console.ResetColor();
            }
        }

        private async Task SendProgressAsync(ClientWebSocket ws, string jobId, string step, string detail, CancellationToken ct)
        {
            var msg = new
            {
                type = "JOB_PROGRESS",
                job_id = jobId,
                step = step,
                detail = detail
            };
            byte[] bytes = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(msg));
            await ws.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, ct);
        }

        public void Stop()
        {
            _cts.Cancel();
            _adapter.Disconnect();
        }
    }
}
