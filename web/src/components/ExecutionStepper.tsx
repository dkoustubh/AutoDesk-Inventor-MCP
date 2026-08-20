import React from 'react';
import { CheckCircle2, Clock, Loader2, AlertCircle, Cpu, ShieldCheck, Monitor, Box } from 'lucide-react';
import { ExecutionStep } from '../types';

interface ExecutionStepperProps {
  steps: ExecutionStep[];
  currentTool?: string;
  parameters?: Record<string, any>;
}

export const ExecutionStepper: React.FC<ExecutionStepperProps> = ({ steps, currentTool, parameters }) => {
  return (
    <div className="bg-[#0f172a]/90 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 text-xs font-mono">
        <span className="text-slate-400 font-bold uppercase tracking-wider flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <span>Real-Time Execution Pipeline</span>
        </span>
        {currentTool && (
          <span className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 px-2 py-0.5 rounded text-[11px]">
            {currentTool}
          </span>
        )}
      </div>

      <div className="mt-4 space-y-3">
        {steps.map((s, index) => {
          const isCompleted = s.status === 'completed';
          const isActive = s.status === 'active';
          const isFailed = s.status === 'failed';
          const isPending = s.status === 'pending';

          return (
            <div
              key={s.id || index}
              className={`p-3 rounded-lg border transition-all ${
                isActive
                  ? 'bg-slate-900/90 border-amber-500/50 shadow-md shadow-amber-500/5'
                  : isCompleted
                  ? 'bg-slate-900/40 border-slate-800/80'
                  : isFailed
                  ? 'bg-rose-950/20 border-rose-800/60'
                  : 'bg-slate-950/20 border-slate-900 opacity-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {isActive && <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />}
                    {isFailed && <AlertCircle className="w-4 h-4 text-rose-400" />}
                    {isPending && <Clock className="w-4 h-4 text-slate-600" />}
                  </div>
                  <div>
                    <h4 className={`text-xs font-medium ${isActive ? 'text-amber-300 font-semibold' : isCompleted ? 'text-slate-200' : isFailed ? 'text-rose-300' : 'text-slate-500'}`}>
                      {s.label}
                    </h4>
                    {s.detail && (
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5 leading-relaxed">{s.detail}</p>
                    )}
                  </div>
                </div>

                {s.timestamp && (
                  <span className="text-[10px] text-slate-500 font-mono flex-shrink-0 ml-2">
                    {s.timestamp}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {parameters && Object.keys(parameters).length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-800/80">
          <div className="text-[11px] font-mono text-slate-400 mb-1.5 uppercase">Validated CAD Intent Payload:</div>
          <pre className="bg-[#090d16] border border-slate-800 rounded p-3 text-[11px] font-mono text-amber-400/90 overflow-x-auto">
            {JSON.stringify({ tool: currentTool || "inventor.create_box", parameters }, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
