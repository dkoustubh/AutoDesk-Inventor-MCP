import React from 'react';
import { 
  Cpu, 
  Code, 
  Box, 
  CheckCircle2, 
  Download, 
  Check, 
  AlertTriangle,
  Loader2
} from 'lucide-react';
import { PipelineStage } from '../types';

interface GenerationProgressBarProps {
  stage: PipelineStage;
  durationMs?: number;
  errorMessage?: string;
}

const STAGES: { id: PipelineStage; label: string; icon: React.FC<{ className?: string }> }[] = [
  { id: 'planning', label: 'Gemma Planning', icon: Cpu },
  { id: 'generating', label: 'build123d Code', icon: Code },
  { id: 'kernel', label: 'OpenCascade Solid', icon: Box },
  { id: 'validating', label: 'BRep Validation', icon: CheckCircle2 },
  { id: 'exporting', label: 'Exporting STEP', icon: Download },
  { id: 'completed', label: 'Verified Solid', icon: Check }
];

export const GenerationProgressBar: React.FC<GenerationProgressBarProps> = ({
  stage,
  durationMs,
  errorMessage
}) => {
  if (stage === 'idle') return null;

  const currentIdx = STAGES.findIndex(s => s.id === stage);
  const isFailed = stage === 'failed';

  return (
    <div className="bg-slate-900/90 border-t border-slate-800 px-4 py-2 flex items-center justify-between text-xs font-mono select-none z-20 shrink-0">
      {/* Pipeline Steps */}
      <div className="flex items-center space-x-2 overflow-x-auto">
        {STAGES.map((s, idx) => {
          const isDone = currentIdx > idx || stage === 'completed';
          const isCurrent = s.id === stage;
          const Icon = s.icon;

          return (
            <React.Fragment key={s.id}>
              <div 
                className={`flex items-center space-x-1.5 px-2 py-1 rounded transition-all ${
                  isCurrent 
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm' 
                    : isDone
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'text-slate-600'
                }`}
              >
                {isCurrent ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-amber-400" />
                ) : isDone ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Icon className="w-3.5 h-3.5" />
                )}
                <span className="font-semibold text-[11px]">{s.label}</span>
              </div>

              {idx < STAGES.length - 1 && (
                <span className={`text-[10px] ${isDone ? 'text-emerald-500' : 'text-slate-700'}`}>→</span>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Right: Duration or Error message */}
      <div className="flex items-center space-x-3 shrink-0 pl-3">
        {durationMs !== undefined && durationMs > 0 && (
          <span className="text-slate-400 text-[11px]">
            Execution: <strong className="text-emerald-400">{durationMs.toFixed(0)} ms</strong>
          </span>
        )}
        {isFailed && errorMessage && (
          <div className="flex items-center space-x-1 text-red-400 font-semibold text-[11px]">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span className="truncate max-w-xs">{errorMessage}</span>
          </div>
        )}
      </div>
    </div>
  );
};
