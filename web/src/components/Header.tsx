import React from 'react';
import { Cpu, Activity, ShieldCheck, Layers } from 'lucide-react';

interface HeaderProps {
  serverConnected: boolean;
  activeAgentsCount: number;
}

export const Header: React.FC<HeaderProps> = ({ serverConnected, activeAgentsCount }) => {
  return (
    <header className="border-b border-slate-800 bg-[#0d131f]/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Layers className="w-5 h-5 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold tracking-tight text-white uppercase">ATS Engineering AI</h1>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                Phase 1 MVP
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">Autodesk Inventor Orchestrator</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* AI Server Indicator */}
          <div className="flex items-center space-x-2 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-md text-xs font-mono">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">AI Server:</span>
            <span className="text-slate-200">192.168.11.86</span>
            <span className={`w-2 h-2 rounded-full ${serverConnected ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-red-500'}`} />
          </div>

          {/* Connected Workstations Badge */}
          <div className="flex items-center space-x-2 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-md text-xs font-mono">
            <Activity className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400">Agents:</span>
            <span className="text-slate-200 font-semibold">{activeAgentsCount} Online</span>
          </div>
        </div>
      </div>
    </header>
  );
};
