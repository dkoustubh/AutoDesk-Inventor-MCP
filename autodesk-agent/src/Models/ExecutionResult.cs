using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace ATS.AutodeskAgent.Models
{
    public class ExecutionResultDto
    {
        [JsonPropertyName("type")]
        public string Type { get; set; } = "job_result";

        [JsonPropertyName("job_id")]
        public string JobId { get; set; } = string.Empty;

        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("status")]
        public string Status { get; set; } = "COMPLETED";

        [JsonPropertyName("error_message")]
        public string? ErrorMessage { get; set; }

        [JsonPropertyName("execution_time_ms")]
        public long ExecutionTimeMs { get; set; }

        [JsonPropertyName("result_data")]
        public Dictionary<string, object> ResultData { get; set; } = new();
    }

    public class StepProgressDto
    {
        [JsonPropertyName("type")]
        public string Type { get; set; } = "step_progress";

        [JsonPropertyName("job_id")]
        public string JobId { get; set; } = string.Empty;

        [JsonPropertyName("session_id")]
        public string SessionId { get; set; } = string.Empty;

        [JsonPropertyName("step")]
        public string Step { get; set; } = string.Empty;

        [JsonPropertyName("detail")]
        public string Detail { get; set; } = string.Empty;

        [JsonPropertyName("status")]
        public string Status { get; set; } = "in_progress";
    }
}
