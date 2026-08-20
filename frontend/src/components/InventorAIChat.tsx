import React, { useState, useRef, useEffect } from 'react';
import { Send, RotateCcw, Check, Loader2, Sparkles, Mic, MicOff, Terminal, ArrowRight } from 'lucide-react';
import { Agent, ExecutionStep, CadJobResult } from '../types';

interface Message {
  id: string;
  sender: 'user' | 'system' | 'ai';
  text?: string;
  type?: 'welcome' | 'user' | 'system_alert' | 'executing' | 'success' | 'error';
  data?: any;
  timestamp?: string;
}

interface InventorAIChatProps {
  agent?: Agent;
  targetIp: string;
  userName: string;
  isLoading: boolean;
  finalResult: CadJobResult | null;
  onSubmit: (prompt: string) => void;
  onReset: () => void;
}

const SAMPLE_PROMPTS = [
  'Create a powered rotary conveyor turntable',
  'Create a 3D PRB roller conveyor',
  'Create a 15mm cube on right side of 10mm cube',
  'Drill a 2mm diameter hole through top to down of 10mm cube',
  'Create a sprocket with 14 teeth',
  'Create a ribbed mounting angle bracket',
  'Create a cylinder of diameter 20 and height 50',
  'Create a 10mm cube'
];

export const InventorAIChat: React.FC<InventorAIChatProps> = ({
  agent,
  targetIp,
  userName,
  isLoading,
  finalResult,
  onSubmit,
  onReset
}) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'ai',
      type: 'welcome'
    },
    {
      id: 'reset-note',
      sender: 'system',
      type: 'system_alert',
      text: 'Conversation ready. Connected to Autodesk MCP Gateway!'
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Typewriter typography animation state
  const [promptIndex, setPromptIndex] = useState(0);
  const [typedText, setTypedText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentFullText = SAMPLE_PROMPTS[promptIndex];
    let timeout: any;

    if (!isDeleting && typedText.length < currentFullText.length) {
      timeout = setTimeout(() => {
        setTypedText(currentFullText.slice(0, typedText.length + 1));
      }, 55);
    } else if (!isDeleting && typedText.length === currentFullText.length) {
      timeout = setTimeout(() => {
        setIsDeleting(true);
      }, 2200);
    } else if (isDeleting && typedText.length > 0) {
      timeout = setTimeout(() => {
        setTypedText(currentFullText.slice(0, typedText.length - 1));
      }, 28);
    } else if (isDeleting && typedText.length === 0) {
      setIsDeleting(false);
      setPromptIndex((prev) => (prev + 1) % SAMPLE_PROMPTS.length);
    }

    return () => clearTimeout(timeout);
  }, [typedText, isDeleting, promptIndex]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Handle final result
  useEffect(() => {
    if (finalResult) {
      const p = finalResult.parameters || {};
      let successMsg = `✓ Created geometry in Autodesk`;

      if (finalResult.tool?.includes('bracket')) {
        successMsg = `✓ Created Ribbed Mounting Angle Bracket (Width 70mm × Height 55mm with Ø15mm Boss & Ø10mm Base Holes)`;
      } else if (finalResult.tool?.includes('sprocket') || p.teeth_count) {
        successMsg = `✓ Created sprocket: Ø${p.outer_diameter_mm || 50}mm with ${p.teeth_count || 14} teeth`;
      } else if (finalResult.tool?.includes('box_with_hole') || (p.hole_diameter_mm && p.length_mm)) {
        successMsg = `✓ Created drilled cube: ${p.length_mm || 10}×${p.width_mm || 10}×${p.height_mm || 10}mm with Ø${p.hole_diameter_mm || 2}mm drill hole`;
      } else if (finalResult.tool?.includes('cylinder') || (p.diameter_mm && p.height_mm)) {
        const d = p.diameter_mm || ((p.radius_mm || 10) * 2);
        successMsg = `✓ Created cylinder: Ø${d}mm × ${p.height_mm || 50}mm`;
      } else if (finalResult.tool?.includes('cone')) {
        successMsg = `✓ Created cone: Base R${p.base_radius_mm || 20}mm × Height ${p.height_mm || 40}mm`;
      } else {
        const l = p.length_mm || 30;
        const w = p.width_mm || 30;
        const h = p.height_mm || 30;
        successMsg = `✓ Created 3D box: ${l}mm × ${w}mm × ${h}mm`;
      }

      setMessages((prev) => [
        ...prev.filter((m) => m.type !== 'executing'),
        {
          id: `success-${Date.now()}`,
          sender: 'ai',
          type: 'success',
          text: successMsg
        }
      ]);
    }
  }, [finalResult]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput('');

    setMessages((prev) => [
      ...prev,
      {
        id: `user-${Date.now()}`,
        sender: 'user',
        type: 'user',
        text: userText
      },
      {
        id: `exec-${Date.now()}`,
        sender: 'system',
        type: 'executing'
      }
    ]);

    onSubmit(userText);
  };

  const handleApplySuggestion = (text: string) => {
    setInput(text);
  };

  const handleResetChat = () => {
    onReset();
    setMessages([
      {
        id: 'welcome',
        sender: 'ai',
        type: 'welcome'
      },
      {
        id: `reset-${Date.now()}`,
        sender: 'system',
        type: 'system_alert',
        text: 'Conversation reset. Ready for new CAD models!'
      }
    ]);
  };

  return (
    <div className="w-full max-w-sm bg-[#ffffff] border-l border-[#d1d5db] h-screen flex flex-col font-sans select-none shadow-lg text-slate-800">
      {/* 1. Top Blue Header */}
      <div className="bg-[#1b75d0] px-4 py-3 text-white flex items-center justify-between shadow-sm">
        <div>
          <h1 className="text-sm font-bold tracking-tight">InventorAI Chat</h1>
          <p className="text-[11px] text-blue-100 font-sans opacity-90">Create CAD models with natural language</p>
        </div>

        <button
          onClick={handleResetChat}
          className="bg-[#2684e5] hover:bg-[#1a6ec7] text-white text-[11px] font-medium px-2.5 py-1 rounded shadow-xs transition-colors border border-blue-300/40 font-mono"
        >
          Reset
        </button>
      </div>

      {/* 2. Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-[#f8fafc]">
        {messages.map((m) => {
          if (m.type === 'welcome') {
            return (
              <div key={m.id} className="bg-white border border-[#e2e8f0] rounded-xl p-3.5 shadow-sm space-y-3">
                <div className="flex items-center space-x-2 border-b border-slate-100 pb-2">
                  <div className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
                  <span className="font-bold text-slate-900 text-xs font-mono">Welcome to InventorAI!</span>
                </div>

                {/* Animated Typography Prompt Carousel */}
                <div className="space-y-1.5">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider font-mono">
                    Try Prompt:
                  </div>
                  
                  <div
                    onClick={() => handleApplySuggestion(typedText)}
                    className="group bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-300 rounded-lg p-2.5 cursor-pointer transition-all flex items-center justify-between"
                  >
                    <div className="font-mono text-xs text-blue-700 font-bold flex items-center">
                      <span>"{typedText}"</span>
                      <span className="w-1.5 h-3.5 bg-blue-600 ml-1 animate-pulse" />
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 transition-colors" />
                  </div>
                </div>

                {/* Quick Suggestion Chips */}
                <div className="pt-1 flex flex-wrap gap-1.5">
                  {SAMPLE_PROMPTS.slice(0, 3).map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleApplySuggestion(prompt)}
                      className="text-[10px] font-mono bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded-md border border-slate-200/80 transition-colors truncate max-w-full"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            );
          }

          if (m.type === 'system_alert') {
            return (
              <div key={m.id} className="flex justify-center">
                <span className="bg-[#fffbeb] text-[#b45309] border border-[#fef3c7] text-[10.5px] px-3 py-1 rounded-full font-medium shadow-2xs font-mono">
                  {m.text}
                </span>
              </div>
            );
          }

          if (m.type === 'user') {
            return (
              <div key={m.id} className="flex justify-end">
                <div className="bg-[#eaf5ea] text-[#166534] border border-[#d1ebd1] px-3.5 py-1.5 rounded-lg text-xs font-medium max-w-[85%] shadow-2xs">
                  {m.text}
                </div>
              </div>
            );
          }

          if (m.type === 'executing') {
            return (
              <div key={m.id} className="bg-slate-900/90 border border-slate-700 rounded-xl p-3.5 space-y-2.5 text-xs shadow-lg animate-fade-in text-slate-200">
                <div className="flex items-center justify-between border-b border-slate-700/60 pb-2">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
                    <span className="font-bold text-amber-300">CAD Modeling Pipeline</span>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded">GPU: 192.168.11.86</span>
                </div>

                <div className="relative pt-2 pb-1">
                  <div className="absolute top-4 left-3 right-3 h-[2px] bg-slate-700 z-0" />
                  <div className="grid grid-cols-5 gap-1 relative z-10 text-center">
                    <div className="flex flex-col items-center space-y-1">
                      <div className="w-5 h-5 rounded-full bg-emerald-500 text-slate-950 text-[10px] font-mono font-bold flex items-center justify-center">✓</div>
                      <span className="text-[9px] font-mono text-slate-300">Prompt</span>
                    </div>
                    <div className="flex flex-col items-center space-y-1">
                      <div className="w-5 h-5 rounded-full bg-amber-400 text-slate-950 text-[10px] font-mono font-bold flex items-center justify-center animate-pulse">2</div>
                      <span className="text-[9px] font-mono text-amber-300 font-semibold">Gemma</span>
                    </div>
                    <div className="flex flex-col items-center space-y-1">
                      <div className="w-5 h-5 rounded-full bg-slate-700 text-slate-400 text-[10px] font-mono font-bold flex items-center justify-center">3</div>
                      <span className="text-[9px] font-mono text-slate-400">Validate</span>
                    </div>
                    <div className="flex flex-col items-center space-y-1">
                      <div className="w-5 h-5 rounded-full bg-slate-700 text-slate-400 text-[10px] font-mono font-bold flex items-center justify-center">4</div>
                      <span className="text-[9px] font-mono text-slate-400">Dispatch</span>
                    </div>
                    <div className="flex flex-col items-center space-y-1">
                      <div className="w-5 h-5 rounded-full bg-slate-700 text-slate-400 text-[10px] font-mono font-bold flex items-center justify-center">5</div>
                      <span className="text-[9px] font-mono text-slate-400">3D CAD</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          }

          if (m.type === 'success') {
            return (
              <div key={m.id} className="bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl p-3.5 space-y-1 text-xs shadow-xs">
                <div className="flex items-center space-x-1.5 font-bold text-emerald-900 font-mono">
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span>Autodesk Geometry Created</span>
                </div>
                <p className="text-[11.5px] leading-relaxed text-emerald-700 font-sans">{m.text}</p>
              </div>
            );
          }

          return null;
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* 3. Bottom Input Bar */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-200 bg-white space-y-2">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type CAD prompt (e.g. Create a 10mm cube)..."
            disabled={isLoading}
            className="w-full pl-3 pr-10 py-2 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-slate-50/50 disabled:bg-slate-100 disabled:text-slate-400 placeholder:text-slate-400 font-mono"
          />

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-1.5 p-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-300 text-white rounded-md transition-colors"
          >
            {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          </button>
        </div>
      </form>
    </div>
  );
};
