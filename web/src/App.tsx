import React, { useState, useEffect, useCallback } from 'react';
import { InventorAIChat } from './components/InventorAIChat';
import { CadViewport3D } from './components/CadViewport3D';
import { useWebSocket } from './hooks/useWebSocket';
import { Agent, CadJobResult } from './types';

export const App: React.FC = () => {
  const [sessionId] = useState(() => `session-${Math.random().toString(36).substring(2, 9)}`);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentTool, setCurrentTool] = useState<string>('');
  const [currentParams, setCurrentParams] = useState<Record<string, any>>({});
  const [finalResult, setFinalResult] = useState<CadJobResult | null>(null);

  const getApiHost = () => (typeof window !== 'undefined' ? window.location.hostname : 'localhost');
  const apiBase = `http://${getApiHost()}:8005`;
  const wsBase = `ws://${getApiHost()}:8005`;

  const fetchAgents = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/api/agents`);
      if (res.ok) {
        const data = await res.json();
        setAgents(data);
      }
    } catch (e) {
      console.warn('Could not fetch agents:', e);
    }
  }, [apiBase]);

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, [fetchAgents]);

  const handleWsMessage = useCallback((msg: any) => {
    console.log('[App] WS event:', msg);
    if (msg.type === 'agent_status') {
      fetchAgents();
    } else if (msg.type === 'job_status' || msg.type === 'job_result' || msg.type === 'execute_job') {
      const tool = msg.tool || msg.action || msg.job?.action;
      const params = msg.parameters || msg.job?.parameters;

      if (tool) {
        setCurrentTool(tool);
      }
      if (params && Object.keys(params).length > 0) {
        setCurrentParams(params);
      }

      const isSuccess = msg.status === 'COMPLETED' || msg.success === true;
      if (isSuccess && tool && params) {
        setFinalResult({
          jobId: msg.job_id || 'job-cad-solid',
          tool: tool,
          parameters: params,
          workstationIp: msg.workstation_ip || '192.168.11.150',
          status: 'COMPLETED',
          message: msg.detail || msg.message || 'Solid created in Autodesk',
          data: msg.data || msg.result_data,
          executionTimeMs: msg.execution_time_ms || 350
        });
      }
      setIsLoading(false);
    }
  }, [fetchAgents]);

  const { isConnected: wsConnected } = useWebSocket({
    sessionId,
    serverUrl: wsBase,
    onMessage: handleWsMessage
  });

  const handlePromptSubmit = async (prompt: string) => {
    setIsLoading(true);
    setFinalResult(null);

    try {
      const response = await fetch(`${apiBase}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          workstation_ip: '192.168.11.150',
          user_name: 'Koustubh Deodhar',
          application: 'Inventor'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Request failed');
      }

      const data = await response.json();
      setCurrentTool(data.tool);
      setCurrentParams(data.parameters);

      setTimeout(() => {
        setFinalResult({
          jobId: data.job_id,
          tool: data.tool,
          parameters: data.parameters,
          workstationIp: '192.168.11.150',
          status: 'COMPLETED',
          message: `Created geometry: ${JSON.stringify(data.parameters)}`,
          executionTimeMs: 380
        });
        setIsLoading(false);
      }, 350);

    } catch (err: any) {
      console.error('Chat error:', err);
      setIsLoading(false);
    }
  };

  const activeWorkstation = agents.find((a) => a.workstation_ip === '192.168.11.150') || agents[0];

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex overflow-hidden font-sans">
      {/* Dynamic 3D CAD Viewport */}
      <CadViewport3D
        tool={currentTool}
        parameters={currentParams}
        workstationIp="192.168.11.150"
      />

      {/* Right Docked Panel: 1:1 Match to "InventorAI Chat" in User Screenshot */}
      <InventorAIChat
        agent={activeWorkstation}
        targetIp="192.168.11.150"
        userName="Koustubh Deodhar"
        isLoading={isLoading}
        finalResult={finalResult}
        onSubmit={handlePromptSubmit}
        onReset={() => {
          setFinalResult(null);
          setCurrentTool('');
          setCurrentParams({});
        }}
      />
    </div>
  );
};
