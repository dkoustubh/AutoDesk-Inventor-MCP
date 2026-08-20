using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace ATS.AutodeskAgent.Models
{
    public class JobDispatchMessage
    {
        [JsonPropertyName("type")]
        public string Type { get; set; } = string.Empty;

        [JsonPropertyName("job")]
        public JobPayloadDto Job { get; set; } = new();
    }

    public class JobPayloadDto
    {
        [JsonPropertyName("job_id")]
        public string JobId { get; set; } = string.Empty;

        [JsonPropertyName("prompt")]
        public string Prompt { get; set; } = string.Empty;

        [JsonPropertyName("tool_name")]
        public string ToolName { get; set; } = string.Empty;

        [JsonPropertyName("session_id")]
        public string SessionId { get; set; } = string.Empty;

        [JsonPropertyName("workstation_ip")]
        public string WorkstationIp { get; set; } = string.Empty;

        [JsonPropertyName("parameters")]
        public Dictionary<string, JsonElement> Parameters { get; set; } = new();
    }

    public class BoxParameters
    {
        public double LengthMm { get; set; } = 30.0;
        public double WidthMm { get; set; } = 30.0;
        public double HeightMm { get; set; } = 30.0;
        public bool Centered { get; set; } = true;
    }
}
