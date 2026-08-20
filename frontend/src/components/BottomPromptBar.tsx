import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Sparkles, 
  Download, 
  RotateCcw, 
  FileBox, 
  Boxes, 
  FileCode, 
  Paperclip, 
  Trash2,
  ArrowRight
} from 'lucide-react';

interface BottomPromptBarProps {
  onGenerate: (prompt: string) => void;
  isGenerating: boolean;
  hasExistingModel: boolean;
  lastPrompt?: string;
  onDownloadFile: (fileType: 'step' | 'stl' | 'glb' | 'py' | 'json') => void;
}

const SAMPLE_PROMPTS = [
  "Create a 100 x 60 x 20 mm mounting plate with four 8 mm through holes",
  "Create a powered rotary conveyor turntable 1000x1000x550mm with 8 rollers and yellow guard",
  "Create a 3D PRB roller conveyor 2000x450x350mm with 5 steel rollers",
  "Create a 15mm cube on right side of 10mm cube",
  "Drill a 2mm diameter hole through top to down of 10mm cube",
  "Create a 14 teeth ISO sprocket with 12mm central shaft bore"
];

export const BottomPromptBar: React.FC<BottomPromptBarProps> = ({
  onGenerate,
  isGenerating,
  hasExistingModel,
  lastPrompt,
  onDownloadFile
}) => {
  const [prompt, setPrompt] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (prompt.trim() && !isGenerating) {
        onGenerate(prompt.trim());
        setPrompt('');
      }
    }
  };

  const handleSampleClick = (sample: string) => {
    setPrompt(sample);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  return (
    <div className="border-t border-slate-800 bg-slate-950/95 p-3 space-y-2 select-none z-30 shrink-0">
      {/* Sample / Quick Prompt Pills (Shown when no prompt is typed) */}
      {!prompt && (
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs no-scrollbar">
          <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider shrink-0 flex items-center space-x-1">
            <Sparkles className="w-3 h-3 text-amber-400" />
            <span>Try:</span>
          </span>
          {SAMPLE_PROMPTS.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => handleSampleClick(sample)}
              className="text-[11px] px-2.5 py-1 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-slate-800/80 hover:border-amber-500/40 text-slate-300 hover:text-white transition-all shrink-0 truncate max-w-md font-mono"
            >
              {sample}
            </button>
          ))}
        </div>
      )}

      {/* Iterative Context Badge */}
      {hasExistingModel && lastPrompt && (
        <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono bg-slate-900/60 px-2.5 py-1 rounded border border-slate-800/60">
          <span className="text-cyan-400 font-semibold">Iterating from:</span>
          <span className="truncate text-slate-300">"{lastPrompt}"</span>
          <ArrowRight className="w-3 h-3 text-amber-400 shrink-0" />
          <span className="text-amber-400 shrink-0">Describe modification</span>
        </div>
      )}

      {/* Main Input Row */}
      <div className="flex items-center space-x-2">
        <div className="relative flex-1 bg-slate-900 border border-slate-800 focus-within:border-amber-500 rounded-lg transition-all shadow-inner">
          <textarea
            ref={textareaRef}
            rows={1}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              hasExistingModel
                ? "Describe your modification (e.g. 'Make holes 10mm and add 2mm chamfer on top edges')..."
                : "Describe your CAD model in natural language (e.g. 'Create a 100 x 60 x 20 mm mounting plate with four 8 mm holes')..."
            }
            className="w-full bg-transparent text-white text-xs px-3 py-2.5 outline-none resize-none font-medium placeholder:text-slate-500 max-h-24 font-mono"
          />
        </div>

        {/* Generate / Refine Button */}
        <button
          onClick={() => {
            if (prompt.trim() && !isGenerating) {
              onGenerate(prompt.trim());
              setPrompt('');
            }
          }}
          disabled={!prompt.trim() || isGenerating}
          className={`h-10 px-5 rounded-lg font-bold text-xs flex items-center space-x-2 transition-all shrink-0 uppercase tracking-wider font-mono ${
            prompt.trim() && !isGenerating
              ? 'bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-slate-950 shadow-lg shadow-amber-500/20'
              : 'bg-slate-900 border border-slate-800 text-slate-600 cursor-not-allowed'
          }`}
        >
          <Send className="w-3.5 h-3.5" />
          <span>{hasExistingModel ? 'Refine CAD' : 'Generate CAD'}</span>
        </button>

        {/* Downloads Toolbar */}
        {hasExistingModel && (
          <div className="flex items-center space-x-1 pl-2 border-l border-slate-800">
            {/* STEP Button (Highlighted) */}
            <button
              onClick={() => onDownloadFile('step')}
              title="Download ISO-10303 .STEP 3D Solid Model"
              className="h-10 px-3 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/40 text-amber-300 hover:text-amber-200 font-mono font-bold text-xs flex items-center space-x-1.5 transition-all shadow-sm"
            >
              <FileBox className="w-3.5 h-3.5 text-amber-400" />
              <span>.STEP</span>
            </button>

            {/* STL Button */}
            <button
              onClick={() => onDownloadFile('stl')}
              title="Download .STL 3D Mesh"
              className="h-10 px-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-mono text-xs flex items-center space-x-1 transition-colors"
            >
              <Boxes className="w-3.5 h-3.5 text-cyan-400" />
              <span>.STL</span>
            </button>

            {/* Python Source Button */}
            <button
              onClick={() => onDownloadFile('py')}
              title="Download build123d Python Source"
              className="h-10 px-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-mono text-xs flex items-center space-x-1 transition-colors"
            >
              <FileCode className="w-3.5 h-3.5 text-purple-400" />
              <span>.PY</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
