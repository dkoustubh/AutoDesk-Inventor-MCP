import React, { useState } from 'react';
import { Send, Sparkles, Box, Terminal } from 'lucide-react';

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  isLoading: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('Create a cube of 3 cm.');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmit(prompt.trim());
  };

  const samplePrompts = [
    'Create a cube of 3 cm.',
    'Create a 30 × 30 × 30 mm cube in Autodesk Inventor.',
    'Create a box with length 50 mm, width 25 mm, height 10 mm.'
  ];

  return (
    <div className="bg-[#0f172a]/90 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
      <div className="flex items-center space-x-2 text-xs font-mono text-slate-400 mb-3">
        <Terminal className="w-4 h-4 text-amber-400" />
        <span>NATURAL LANGUAGE CAD PROMPT</span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Create a cube of 3 cm..."
            disabled={isLoading}
            className="w-full bg-[#090d16] border border-slate-700 focus:border-amber-500 rounded-lg px-4 py-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/20 font-mono transition-all"
          />
          <button
            type="submit"
            disabled={isLoading || !prompt.trim()}
            className="absolute right-2 top-2 bottom-2 px-4 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 disabled:opacity-50 text-slate-950 font-bold text-xs uppercase tracking-wider rounded-md flex items-center space-x-2 transition-all shadow-md shadow-amber-500/10 active:scale-95"
          >
            {isLoading ? (
              <span className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-slate-950 animate-ping" />
                <span>Processing</span>
              </span>
            ) : (
              <>
                <span>Generate Design</span>
                <Send className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

        <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs font-mono">
          <span className="text-slate-500 whitespace-nowrap text-[11px]">Quick Tests:</span>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setPrompt(p)}
              className="bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 px-2.5 py-1 rounded text-[11px] whitespace-nowrap transition-colors"
            >
              {p}
            </button>
          ))}
        </div>
      </form>
    </div>
  );
};
