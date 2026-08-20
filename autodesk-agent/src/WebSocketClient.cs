using System;
using System.IO;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using ATS.AutodeskAgent.Interfaces;
using ATS.AutodeskAgent.Models;

namespace ATS.AutodeskAgent
{
    public class AgentWebSocketClient
    {
        private readonly AgentConfig _config;
        private readonly IInventorAdapter _inventorAdapter;
        private ClientWebSocket? _ws;
        private CancellationTokenSource _cts = new();

        public AgentWebSocketClient(AgentConfig config, IInventorAdapter inventorAdapter)
        {
            _config = config;
            _inventorAdapter = inventorAdapter;
        }

        public async Task StartAsync()
        {
            while (!_cts.IsCancellationRequested)
            {
                try
                {
                    _ws = new ClientWebSocket();
                    var wsUri = new Uri($"{_config.ServerUrl.TrimEnd('/')}/ws/agent/{_config.WorkstationIp}");
                    
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine($"[AgentWS] Connecting to Central AI Server at {wsUri}...");
                    Console.ResetColor();

                    await _ws.ConnectAsync(wsUri, _cts.Token);

                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine($"[AgentWS] Connected! Registering workstation ({_config.WorkstationIp})...");
                    Console.ResetColor();

                    // 1. Send Registration
                    var regDto = new AgentRegistrationDto
                    {
                        Type = "register",
                        AgentId = $"agent-{_config.WorkstationIp.Replace('.', '-')}",
                        WorkstationIp = _config.WorkstationIp,
                        Hostname = _config.Hostname,
                        ApplicationName = _config.ApplicationName,
                        ApplicationVersion = "2025",
                        Status = "READY"
                    };
                    await SendJsonAsync(regDto);

                    // 2. Start Background Heartbeat Loop
                    var heartbeatTask = StartHeartbeatLoopAsync(regDto.AgentId, _cts.Token);

                    // 3. Receive & Process Messages
                    await ReceiveLoopAsync(_cts.Token);
                }
                catch (Exception ex)
                {
                    Console.ForegroundColor = ConsoleColor.Yellow;
                    Console.WriteLine($"[AgentWS] Connection error: {ex.Message}. Reconnecting in {_config.ReconnectDelaySeconds}s...");
                    Console.ResetColor();
                }
                finally
                {
                    _ws?.Dispose();
                    _ws = null;
                }

                await Task.Delay(TimeSpan.FromSeconds(_config.ReconnectDelaySeconds));
            }
        }

        private async Task ReceiveLoopAsync(CancellationToken ct)
        {
            var buffer = new byte[8192];

            while (_ws != null && _ws.State == WebSocketState.Open && !ct.IsCancellationRequested)
            {
                using var ms = new MemoryStream();
                WebSocketReceiveResult result;

                do
                {
                    result = await _ws.ReceiveAsync(new ArraySegment<byte>(buffer), ct);
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        Console.WriteLine("[AgentWS] Server initiated close.");
                        return;
                    }
                    ms.Write(buffer, 0, result.Count);
                }
                while (!result.EndOfMessage);

                var jsonStr = Encoding.UTF8.GetString(ms.ToArray());
                await HandleIncomingMessageAsync(jsonStr);
            }
        }

        private async Task HandleIncomingMessageAsync(string jsonStr)
        {
            try
            {
                using var doc = JsonDocument.Parse(jsonStr);
                var root = doc.RootElement;
                if (!root.TryGetProperty("type", out var typeProp)) return;

                var type = typeProp.GetString();

                if (type == "registered")
                {
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine("[AgentWS] Registered successfully on Central Server. Status: READY.");
                    Console.ResetColor();
                }
                else if (type == "execute_job")
                {
                    var msg = JsonSerializer.Deserialize<JobDispatchMessage>(jsonStr);
                    if (msg?.Job != null)
                    {
                        _ = Task.Run(() => ProcessJobAsync(msg.Job));
                    }
                }
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[AgentWS] Error handling message: {ex.Message}");
                Console.ResetColor();
            }
        }

        private async Task ProcessJobAsync(JobPayloadDto job)
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine($"\n========================================================");
            Console.WriteLine($"[Job Dispatch] Job ID: {job.JobId}");
            Console.WriteLine($"[Job Dispatch] Tool: {job.ToolName}");
            Console.WriteLine($"[Job Dispatch] Prompt: '{job.Prompt}'");
            Console.WriteLine($"========================================================");
            Console.ResetColor();

            // Emit Progress
            await SendJsonAsync(new StepProgressDto
            {
                JobId = job.JobId,
                SessionId = job.SessionId,
                Step = "GEOMETRY_CREATED",
                Detail = "Autodesk Inventor executing CAD sketch and solid extrusion...",
                Status = "in_progress"
            });

            // Parse Parameters
            var boxParams = new BoxParameters();
            if (job.Parameters.TryGetValue("length_mm", out var l) && l.TryGetDouble(out var lVal)) boxParams.LengthMm = lVal;
            if (job.Parameters.TryGetValue("width_mm", out var w) && w.TryGetDouble(out var wVal)) boxParams.WidthMm = wVal;
            if (job.Parameters.TryGetValue("height_mm", out var h) && h.TryGetDouble(out var hVal)) boxParams.HeightMm = hVal;

            // Execute in Inventor
            var result = await _inventorAdapter.CreateBoxAsync(job.JobId, boxParams);

            // Send Result Back to Central Server
            await SendJsonAsync(result);
        }

        private async Task StartHeartbeatLoopAsync(string agentId, CancellationToken ct)
        {
            while (_ws != null && _ws.State == WebSocketState.Open && !ct.IsCancellationRequested)
            {
                try
                {
                    await Task.Delay(TimeSpan.FromSeconds(_config.HeartbeatIntervalSeconds), ct);
                    if (_ws.State == WebSocketState.Open)
                    {
                        var hb = new HeartbeatDto
                        {
                            AgentId = agentId,
                            WorkstationIp = _config.WorkstationIp,
                            Status = "READY"
                        };
                        await SendJsonAsync(hb);
                    }
                }
                catch
                {
                    break;
                }
            }
        }

        private async Task SendJsonAsync<T>(T payload)
        {
            if (_ws == null || _ws.State != WebSocketState.Open) return;
            var json = JsonSerializer.Serialize(payload);
            var bytes = Encoding.UTF8.GetBytes(json);
            await _ws.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None);
        }

        public void Stop()
        {
            _cts.Cancel();
        }
    }
}
