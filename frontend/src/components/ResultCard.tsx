import React from 'react';
import { CheckCircle2, Box, Layers, Cpu, Clock, Check } from 'lucide-react';
import { CadJobResult } from '../types';

interface ResultCardProps {
  result: CadJobResult;
  onReset: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result, onReset }) => {
  return (
    <div className="bg-[#0f172a]/95 border border-emerald-500/40 rounded-xl p-6 shadow-2xl backdrop-blur-md relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
      
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Design Created Successfully</h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">Autodesk Inventor Native Geometry Generated</p>
          </div>
        </div>

        <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono px-3 py-1 rounded-full font-semibold">
          JOB COMPLETED
        </span>
      </div>

      <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/80 border border-slate-800 rounded-lg p-4 font-mono text-xs">
        <div>
          <span className="text-slate-500 block text-[11px]">APPLICATION</span>
          <span className="text-slate-200 font-semibold mt-0.5 block">Autodesk Inventor</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[11px]">DIMENSIONS</span>
          <span className="text-amber-400 font-bold mt-0.5 block">
            {result.parameters?.length_mm || 30} × {result.parameters?.width_mm || 30} × {result.parameters?.height_mm || 30} mm
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[11px]">WORKSTATION</span>
          <span className="text-slate-200 mt-0.5 block">{result.workstationIp}</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[11px]">JOB ID</span>
          <span className="text-cyan-400 mt-0.5 block">{result.jobId}</span>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between pt-2">
        <p className="text-xs text-slate-400">
          Operation executed via official Autodesk Inventor COM API.
        </p>
        <button
          onClick={onReset}
          className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono px-4 py-2 rounded-md transition-colors"
        >
          New Command
        </button>
      </div>
    </div>
  );
};
