using System.Text.Json.Serialization;

namespace ATS.AutodeskAgent.Models
{
    public class AgentRegistrationDto
    {
        [JsonPropertyName("type")]
        public string Type { get; set; } = "register";

        [JsonPropertyName("agent_id")]
        public string? AgentId { get; set; }

        [JsonPropertyName("workstation_ip")]
        public string WorkstationIp { get; set; } = string.Empty;

        [JsonPropertyName("hostname")]
        public string Hostname { get; set; } = string.Empty;

        [JsonPropertyName("application_name")]
        public string ApplicationName { get; set; } = "Inventor";

        [JsonPropertyName("application_version")]
        public string? ApplicationVersion { get; set; }

        [JsonPropertyName("status")]
        public string Status { get; set; } = "READY";
    }

    public class HeartbeatDto
    {
        [JsonPropertyName("type")]
        public string Type { get; set; } = "heartbeat";

        [JsonPropertyName("agent_id")]
        public string AgentId { get; set; } = string.Empty;

        [JsonPropertyName("workstation_ip")]
        public string WorkstationIp { get; set; } = string.Empty;

        [JsonPropertyName("status")]
        public string Status { get; set; } = "READY";
    }
}
