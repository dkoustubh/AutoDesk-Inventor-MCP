using System;

namespace ATS.AutodeskAgent
{
    public class AgentConfig
    {
        public string ServerUrl { get; set; } = "ws://192.168.11.94:8005";
        public string WorkstationIp { get; set; } = "192.168.11.150";
        public string Hostname { get; set; } = Environment.MachineName;
        public string UserName { get; set; } = "Koustubh Deodhar";
        public string ApplicationName { get; set; } = "Inventor";
        public int HeartbeatIntervalSeconds { get; set; } = 15;
        public int ReconnectDelaySeconds { get; set; } = 5;

        public static AgentConfig Load()
        {
            var config = new AgentConfig();
            
            var serverEnv = Environment.GetEnvironmentVariable("ATS_SERVER_URL");
            if (!string.IsNullOrWhiteSpace(serverEnv))
                config.ServerUrl = serverEnv;

            var ipEnv = Environment.GetEnvironmentVariable("ATS_WORKSTATION_IP");
            if (!string.IsNullOrWhiteSpace(ipEnv))
                config.WorkstationIp = ipEnv;

            return config;
        }
    }
}
