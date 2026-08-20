import React, { useState, useEffect, useRef } from 'react';
import { Send, Check, Loader2, Mic, MicOff, Maximize2, ShieldCheck, Box } from 'lucide-react';
import { Agent, ExecutionStep, CadJobResult } from '../types';

interface CopilotSidebarProps {
  agent?: Agent;
  targetIp: string;
  userName: string;
  steps: ExecutionStep[];
  isLoading: boolean;
  finalResult: CadJobResult | null;
  onSubmit: (prompt: string) => void;
  onReset: () => void;
  onToggleFullMode: () => void;
}

export const CopilotSidebar: React.FC<CopilotSidebarProps> = ({
  agent,
  targetIp,
  userName,
  steps,
  isLoading,
  finalResult,
  onSubmit,
  onReset,
  onToggleFullMode
}) => {
  const [prompt, setPrompt] = useState('Create a cube of 3 cm.');
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef<any>(null);

  const isOnline = agent?.status === 'READY' || agent?.is_active || true; // Active workstation link
  const activeApp = agent?.application_name || "AutoCAD / Inventor";

  // Speech Recognition API setup
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');
        setPrompt(transcript);
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
      } catch (err) {
        console.warn('Speech start err:', err);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
    onSubmit(prompt.trim());
  };

  const samplePrompts = [
    'Create a cube of 3 cm.',
    'Create a 30 × 30 × 30 mm cube',
    'Create a box 50 x 25 x 10 mm'
  ];

  return (
    <div className="w-full max-w-md bg-white text-slate-900 border-r border-slate-200 h-screen flex flex-col shadow-sm font-sans select-none">
      {/* 1. Header (Clean & Minimal) */}
      <div className="px-5 py-4 bg-white border-b border-slate-100 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-sm font-bold tracking-tight text-slate-900">ATS Copilot</h1>
            <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>{targetIp}</span>
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono mt-0.5">Autodesk {activeApp}</p>
        </div>

        <button
          onClick={onToggleFullMode}
          title="Toggle Full Dashboard"
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Main Body: Timeline Steps 1 to 5 */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-6">
        <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
          Execution Progress
        </div>

        {/* Vertical Timeline from Step 1 to 5 with Green Dots */}
        <div className="relative pl-6 space-y-6 before:absolute before:left-[11px] before:top-3 before:bottom-3 before:w-[2px] before:bg-slate-200">
          {steps.map((s, index) => {
            const stepNum = index + 1;
            const isCompleted = s.status === 'completed';
            const isActive = s.status === 'active';
            const isPending = s.status === 'pending';
            const isFailed = s.status === 'failed';

            return (
              <div key={s.id || index} className="relative group">
                {/* Timeline Dot / Indicator */}
                <div
                  className={`absolute -left-[24px] top-0.5 w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-mono font-bold transition-all duration-300 ${
                    isCompleted
                      ? 'bg-emerald-500 text-white shadow-sm shadow-emerald-500/20 ring-4 ring-emerald-50'
                      : isActive
                      ? 'bg-amber-500 text-white animate-pulse ring-4 ring-amber-50'
                      : isFailed
                      ? 'bg-rose-500 text-white'
                      : 'bg-white border-2 border-slate-300 text-slate-400'
                  }`}
                >
                  {isCompleted ? <Check className="w-3.5 h-3.5 stroke-[3]" /> : isActive ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : stepNum}
                </div>

                {/* Step Content */}
                <div className="min-w-0">
                  <div className="flex items-center justify-between">
                    <h3
                      className={`text-xs font-semibold tracking-tight transition-colors ${
                        isCompleted
                          ? 'text-slate-900'
                          : isActive
                          ? 'text-amber-700 font-bold'
                          : isFailed
                          ? 'text-rose-700'
                          : 'text-slate-400'
                      }`}
                    >
                      {s.label}
                    </h3>
                    {s.timestamp && (
                      <span className="text-[10px] text-slate-400 font-mono ml-2">{s.timestamp}</span>
                    )}
                  </div>

                  {s.detail && (
                    <p
                      className={`text-[11px] font-mono mt-0.5 leading-relaxed break-words ${
                        isCompleted
                          ? 'text-slate-600'
                          : isActive
                          ? 'text-amber-800 font-medium'
                          : isFailed
                          ? 'text-rose-600'
                          : 'text-slate-400'
                      }`}
                    >
                      {s.detail}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Result Confirmation Card when Done */}
        {finalResult && (
          <div className="bg-emerald-50/80 border border-emerald-200 rounded-xl p-4 space-y-3 animate-fade-in shadow-xs">
            <div className="flex items-center space-x-2 text-emerald-800 font-bold text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>Solid Created in Autodesk ({targetIp})</span>
            </div>

            <div className="bg-white rounded-lg p-3 text-[11px] font-mono space-y-1.5 border border-emerald-100 text-slate-700">
              <div className="flex justify-between">
                <span className="text-slate-400">Dimensions:</span>
                <span className="font-bold text-slate-900">
                  {finalResult.parameters?.length_mm || 30} × {finalResult.parameters?.width_mm || 30} × {finalResult.parameters?.height_mm || 30} mm
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Application:</span>
                <span>Autodesk {activeApp}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Job ID:</span>
                <span className="text-slate-500">{finalResult.jobId}</span>
              </div>
            </div>

            <button
              onClick={onReset}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-medium py-1.5 rounded-lg text-xs transition-colors"
            >
              New Command
            </button>
          </div>
        )}
      </div>

      {/* 3. Bottom Input Bar (Simple & Clean) */}
      <div className="p-4 bg-white border-t border-slate-100 space-y-3">
        {/* Quick Suggestion Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 text-[11px] font-mono">
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setPrompt(p)}
              className="bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600 hover:text-slate-900 px-2.5 py-1 rounded-md whitespace-nowrap transition-colors"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input Box */}
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type or click 🎙️ (e.g. 'Create a cube of 3 cm')..."
            disabled={isLoading}
            className="w-full bg-slate-50 border border-slate-200 focus:border-slate-400 focus:bg-white rounded-xl px-4 py-3 pr-20 text-xs text-slate-900 placeholder-slate-400 focus:outline-none font-mono transition-all"
          />

          <div className="absolute right-2 flex items-center space-x-1">
            {speechSupported && (
              <button
                type="button"
                onClick={toggleListening}
                className={`p-2 rounded-lg transition-all ${
                  isListening
                    ? 'bg-rose-500 text-white animate-bounce'
                    : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
                }`}
                title={isListening ? "Listening... Click to stop" : "Click to speak"}
              >
                {isListening ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5 text-amber-600" />}
              </button>
            )}

            <button
              type="submit"
              disabled={isLoading || !prompt.trim()}
              className="p-2 bg-slate-900 hover:bg-slate-800 disabled:opacity-30 text-white rounded-lg transition-all shadow-xs"
              title="Send to Autodesk (Enter)"
            >
              {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            </button>
          </div>
        </form>

        <div className="text-[10px] text-slate-400 font-mono text-center">
          Press <kbd className="px-1 py-0.2 bg-slate-100 border border-slate-200 rounded font-semibold text-slate-600">Enter</kbd> to generate in Autodesk
        </div>
      </div>
    </div>
  );
};
