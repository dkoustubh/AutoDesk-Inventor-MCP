import React, { useState } from 'react';
import { 
  Box, 
  Cpu, 
  Layers, 
  Sun, 
  Moon, 
  Monitor, 
  Maximize2, 
  Minimize2, 
  Settings, 
  Activity,
  CheckCircle2,
  HardDrive
} from 'lucide-react';
import { ThemeMode } from '../types';

interface TopToolbarProps {
  projectName: string;
  onProjectNameChange: (newName: string) => void;
  currentVersion: string;
  serverConnected: boolean;
  gemmaStatus: string;
  activeAgentsCount: number;
  theme: ThemeMode;
  onThemeChange: (theme: ThemeMode) => void;
  onOpenSettings: () => void;
}

export const TopToolbar: React.FC<TopToolbarProps> = ({
  projectName,
  onProjectNameChange,
  currentVersion,
  serverConnected,
  gemmaStatus,
  activeAgentsCount,
  theme,
  onThemeChange,
  onOpenSettings
}) => {
  const [isEditingName, setIsEditingName] = useState(false);
  const [tempName, setTempName] = useState(projectName);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  const handleNameSubmit = () => {
    setIsEditingName(false);
    if (tempName.trim()) {
      onProjectNameChange(tempName.trim());
    }
  };

  return (
    <header className="h-12 border-b border-slate-800 bg-slate-950/90 text-slate-200 px-4 flex items-center justify-between select-none z-30 shrink-0">
      {/* Left: Branding, Project & Version */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 px-2.5 py-1 rounded-md">
          <Box className="w-4 h-4 text-amber-400 stroke-[2.5]" />
          <span className="font-bold text-xs tracking-wider uppercase text-amber-300 font-mono">TEXT → CAD</span>
        </div>

        <div className="h-4 w-px bg-slate-800" />

        {/* Project Name */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-medium">Project:</span>
          {isEditingName ? (
            <input
              type="text"
              value={tempName}
              onChange={(e) => setTempName(e.target.value)}
              onBlur={handleNameSubmit}
              onKeyDown={(e) => e.key === 'Enter' && handleNameSubmit()}
              autoFocus
              className="bg-slate-900 border border-amber-500 text-xs px-2 py-0.5 rounded text-white font-medium outline-none"
            />
          ) : (
            <span
              onClick={() => setIsEditingName(true)}
              className="text-xs font-semibold text-white hover:text-amber-400 cursor-pointer px-1 py-0.5 rounded hover:bg-slate-900/60 transition-colors"
              title="Click to rename"
            >
              {projectName}
            </span>
          )}

          {/* Version Chip */}
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            {currentVersion}
          </span>
        </div>
      </div>

      {/* Center / Right: System & Hardware Status */}
      <div className="flex items-center space-x-3">
        {/* Gemma GPU Status */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-[11px] font-mono">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Gemma GPU:</span>
          <span className="text-slate-200">192.168.11.86</span>
          <span className={`w-2 h-2 rounded-full ${serverConnected ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-red-500'}`} />
        </div>

        {/* VRAM Status */}
        <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-[11px] font-mono text-slate-300">
          <HardDrive className="w-3.5 h-3.5 text-purple-400" />
          <span>96 GB VRAM</span>
        </div>

        {/* CAD Kernel Status */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-[11px] font-mono text-slate-300">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>OpenCascade 7.9</span>
        </div>

        {/* Workstation Agent Indicator */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-[11px] font-mono">
          <Activity className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-slate-400">Inventor COM:</span>
          <span className={`font-semibold ${activeAgentsCount > 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
            {activeAgentsCount > 0 ? 'Live (192.168.11.150)' : 'Standby'}
          </span>
        </div>

        <div className="h-4 w-px bg-slate-800" />

        {/* Theme Switcher */}
        <div className="flex items-center bg-slate-900 border border-slate-800 rounded p-0.5">
          <button
            onClick={() => onThemeChange('dark')}
            title="Dark Theme"
            className={`p-1 rounded ${theme === 'dark' ? 'bg-slate-800 text-amber-400' : 'text-slate-500 hover:text-slate-300'}`}
          >
            <Moon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onThemeChange('light')}
            title="Light Theme"
            className={`p-1 rounded ${theme === 'light' ? 'bg-slate-800 text-amber-400' : 'text-slate-500 hover:text-slate-300'}`}
          >
            <Sun className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Settings Button */}
        <button
          onClick={onOpenSettings}
          title="Workbench Settings"
          className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <Settings className="w-3.5 h-3.5" />
        </button>

        {/* Fullscreen Button */}
        <button
          onClick={toggleFullscreen}
          title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
          className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
        </button>
      </div>
    </header>
  );
};
