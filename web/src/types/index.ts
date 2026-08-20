export interface Agent {
  id: string;
  workstation_ip: string;
  hostname?: string;
  application_name: string;
  application_version?: string;
  status: 'READY' | 'BUSY' | 'OFFLINE';
  is_active: boolean;
  last_heartbeat: string;
}

export interface ExecutionStep {
  id: string;
  step: string;
  label: string;
  detail: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  timestamp?: string;
}

export interface CadJobResult {
  jobId: string;
  tool: string;
  parameters: Record<string, any>;
  workstationIp: string;
  status: string;
  message: string;
  data?: Record<string, any>;
  executionTimeMs?: number;
}
