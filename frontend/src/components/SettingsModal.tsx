import React, { useState } from 'react';
import { X, Settings, Check, Sliders, Server, Monitor } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  units: string;
  onUnitsChange: (units: 'mm' | 'cm' | 'inch') => void;
  gridSpacing: number;
  onGridSpacingChange: (val: number) => void;
  apiBase: string;
  onApiBaseChange: (val: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  units,
  onUnitsChange,
  gridSpacing,
  onGridSpacingChange,
  apiBase,
  onApiBaseChange
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full shadow-2xl overflow-hidden font-mono text-xs text-slate-300 select-none">
        {/* Header */}
        <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-2">
            <Settings className="w-4 h-4 text-amber-400" />
            <span className="font-bold text-sm text-white uppercase">Workbench Settings</span>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4">
          {/* Units */}
          <div className="space-y-1.5">
            <label className="text-slate-400 font-semibold uppercase text-[10px]">Default CAD Units</label>
            <div className="grid grid-cols-3 gap-2">
              {(['mm', 'cm', 'inch'] as const).map((u) => (
                <button
                  key={u}
                  onClick={() => onUnitsChange(u)}
                  className={`py-2 rounded border transition-all ${
                    units === u
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 font-bold'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {u === 'mm' ? 'Millimeters (mm)' : u === 'cm' ? 'Centimeters (cm)' : 'Inches (in)'}
                </button>
              ))}
            </div>
          </div>

          {/* Grid Spacing */}
          <div className="space-y-1.5">
            <label className="text-slate-400 font-semibold uppercase text-[10px]">Engineering Grid Spacing (mm)</label>
            <div className="grid grid-cols-3 gap-2">
              {[10, 50, 100].map((spacing) => (
                <button
                  key={spacing}
                  onClick={() => onGridSpacingChange(spacing)}
                  className={`py-2 rounded border transition-all ${
                    gridSpacing === spacing
                      ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300 font-bold'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {spacing} mm Grid
                </button>
              ))}
            </div>
          </div>

          {/* API Base URL */}
          <div className="space-y-1.5">
            <label className="text-slate-400 font-semibold uppercase text-[10px]">Text-to-CAD Gateway Endpoint</label>
            <div className="flex items-center space-x-2 bg-slate-950 border border-slate-800 rounded px-3 py-2">
              <Server className="w-4 h-4 text-purple-400 shrink-0" />
              <input
                type="text"
                value={apiBase}
                onChange={(e) => onApiBaseChange(e.target.value)}
                className="bg-transparent text-white w-full outline-none text-xs font-mono"
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-slate-800 bg-slate-950 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold uppercase tracking-wider text-xs"
          >
            Save & Close
          </button>
        </div>
      </div>
    </div>
  );
};
