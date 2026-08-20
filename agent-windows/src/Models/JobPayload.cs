using System.Text.Json.Serialization;

namespace AtsAutodeskAgent.Models
{
    public class CreateBoxParams
    {
        [JsonPropertyName("length_mm")]
        public double LengthMm { get; set; } = 30.0;

        [JsonPropertyName("width_mm")]
        public double WidthMm { get; set; } = 30.0;

        [JsonPropertyName("height_mm")]
        public double HeightMm { get; set; } = 30.0;

        [JsonPropertyName("centered")]
        public bool Centered { get; set; } = true;
    }

    public class JobPayload
    {
        [JsonPropertyName("job_id")]
        public string JobId { get; set; } = string.Empty;

        [JsonPropertyName("action")]
        public string Action { get; set; } = string.Empty;

        [JsonPropertyName("parameters")]
        public System.Text.Json.JsonElement Parameters { get; set; }

        [JsonPropertyName("user_name")]
        public string UserName { get; set; } = "Koustubh Deodhar";

        [JsonPropertyName("workstation_ip")]
        public string WorkstationIp { get; set; } = "192.168.11.150";
    }

    public class ExecutionResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public int ExecutionTimeMs { get; set; }
        public Dictionary<string, object> Data { get; set; } = new();
    }
}
