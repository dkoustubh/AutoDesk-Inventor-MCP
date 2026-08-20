import React from 'react';
import { Monitor, CheckCircle2, XCircle, Clock, UserCheck } from 'lucide-react';
import { Agent } from '../types';

interface WorkstationStatusProps {
  agent?: Agent;
  targetIp: string;
  userName: string;
}

export const WorkstationStatus: React.FC<WorkstationStatusProps> = ({
  agent,
  targetIp = "192.168.11.150",
  userName = "Koustubh Deodhar"
}) => {
  const isOnline = agent?.status === 'READY' || agent?.is_active;

  return (
    <div className="bg-[#0f172a]/90 border border-slate-800 rounded-xl p-5 shadow-xl relative overflow-hidden backdrop-blur-md">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 via-cyan-500 to-emerald-500 opacity-60" />
      
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-lg border ${isOnline ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>
            <Monitor className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-semibold text-white">Autodesk Workstation</h3>
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium ${
                isOnline ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
              }`}>
                {isOnline ? 'ONLINE / READY' : 'OFFLINE'}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">{targetIp} (MECH-PC)</p>
          </div>
        </div>

        <div className="text-right">
          <div className="inline-flex items-center space-x-1 text-xs text-slate-300 font-mono bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
            <UserCheck className="w-3.5 h-3.5 text-amber-400" />
            <span>{userName}</span>
          </div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-3 pt-3 border-t border-slate-800/80 text-xs">
        <div>
          <span className="text-slate-500 block font-mono text-[11px]">TARGET CAD</span>
          <span className="text-slate-200 font-medium flex items-center space-x-1 mt-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            <span>Autodesk Inventor</span>
          </span>
        </div>
        <div>
          <span className="text-slate-500 block font-mono text-[11px]">DISPATCH QUEUE</span>
          <span className="text-slate-200 font-mono mt-0.5 block truncate">queue:autodesk:{targetIp}</span>
        </div>
        <div>
          <span className="text-slate-500 block font-mono text-[11px]">API ADAPTER</span>
          <span className="text-slate-200 font-mono mt-0.5 block">COM Interop (C#)</span>
        </div>
      </div>
    </div>
  );
};
