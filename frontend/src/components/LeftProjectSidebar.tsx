import React, { useState } from 'react';
import { 
  FolderTree, 
  History, 
  FileCode, 
  FileBox, 
  Download, 
  Plus, 
  Copy, 
  RotateCcw, 
  Trash2, 
  ChevronLeft, 
  ChevronRight,
  FileText,
  CheckCircle2,
  Boxes
} from 'lucide-react';
import { CADVersion } from '../types';

interface LeftProjectSidebarProps {
  versions: CADVersion[];
  currentVersionId: string;
  onSelectVersion: (versionId: string) => void;
  onNewModel: () => void;
  onDuplicateVersion: () => void;
  onRestoreVersion: () => void;
  onDeleteVersion: (versionId: string) => void;
  onDownloadFile: (fileType: 'step' | 'stl' | 'glb' | 'py' | 'json') => void;
  onViewSourceFile: (fileType: 'py' | 'plan' | 'validation') => void;
}

export const LeftProjectSidebar: React.FC<LeftProjectSidebarProps> = ({
  versions,
  currentVersionId,
  onSelectVersion,
  onNewModel,
  onDuplicateVersion,
  onRestoreVersion,
  onDeleteVersion,
  onDownloadFile,
  onViewSourceFile
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const activeVersion = versions.find(v => v.id === currentVersionId) || versions[versions.length - 1];

  return (
    <aside 
      className={`border-r border-slate-800 bg-slate-950/80 flex flex-col transition-all duration-200 select-none z-20 shrink-0 ${
        isCollapsed ? 'w-10' : 'w-64'
      }`}
    >
      {/* Sidebar Header / Collapse Toggle */}
      <div className="h-9 border-b border-slate-800 px-3 flex items-center justify-between text-xs font-semibold text-slate-400">
        {!isCollapsed && (
          <div className="flex items-center space-x-1.5">
            <FolderTree className="w-3.5 h-3.5 text-amber-400" />
            <span className="uppercase tracking-wider text-[11px] text-slate-300 font-mono">Project Explorer</span>
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {isCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
        </button>
      </div>

      {isCollapsed ? (
        <div className="flex-1 flex flex-col items-center py-3 space-y-4 text-slate-400">
          <button onClick={onNewModel} title="New Model" className="p-2 rounded hover:bg-slate-800 hover:text-amber-400">
            <Plus className="w-4 h-4" />
          </button>
          <button onClick={() => onDownloadFile('step')} title="Download STEP" className="p-2 rounded hover:bg-slate-800 hover:text-amber-400">
            <Download className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-3 space-y-4">
          {/* SECTION 1: VERSIONS */}
          <div>
            <div className="flex items-center justify-between text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider mb-2">
              <div className="flex items-center space-x-1.5">
                <History className="w-3.5 h-3.5 text-cyan-400" />
                <span>Versions</span>
              </div>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-900 border border-slate-800 text-slate-400">
                {versions.length}
              </span>
            </div>

            <div className="space-y-1">
              {versions.length === 0 ? (
                <div className="px-3 py-4 rounded-md border border-dashed border-slate-800 text-center text-slate-500 text-[11px] font-mono">
                  No versions yet.
                  <br />
                  <span className="text-[10px] text-slate-600">Enter a prompt to create the first model.</span>
                </div>
              ) : (
                versions.slice().reverse().map((v) => {
                  const isActive = v.id === currentVersionId;
                  return (
                    <div
                      key={v.id}
                      onClick={() => onSelectVersion(v.id)}
                      className={`px-2.5 py-2 rounded-md cursor-pointer transition-all border ${
                        isActive
                          ? 'bg-amber-500/10 border-amber-500/40 text-white shadow-sm'
                          : 'bg-slate-900/50 border-slate-800/60 text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className={`font-mono text-xs font-bold ${isActive ? 'text-amber-400' : 'text-slate-400'}`}>
                            {v.versionNumber}
                          </span>
                          {isActive && (
                            <span className="text-[9px] uppercase px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 font-mono">
                              Active
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {new Date(v.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p className="text-[11px] truncate mt-1 text-slate-300 font-normal">
                        {v.prompt || 'Initial CAD Model'}
                      </p>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* SECTION 2: CAD FILES */}
          <div>
            <div className="flex items-center justify-between text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider mb-2">
              <div className="flex items-center space-x-1.5">
                <FileBox className="w-3.5 h-3.5 text-emerald-400" />
                <span>CAD Artifacts</span>
              </div>
            </div>

            <div className="space-y-1 font-mono text-xs">
              {/* STEP */}
              <div className="flex items-center justify-between px-2.5 py-1.5 rounded bg-slate-900/60 border border-slate-800/80 hover:border-amber-500/30 group">
                <div className="flex items-center space-x-2">
                  <FileBox className="w-3.5 h-3.5 text-amber-400" />
                  <span className="text-slate-200">model.step</span>
                </div>
                <button
                  onClick={() => onDownloadFile('step')}
                  className="text-slate-500 group-hover:text-amber-400 hover:bg-slate-800 p-1 rounded transition-colors"
                  title="Download ISO-10303 STEP File"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* STL */}
              <div className="flex items-center justify-between px-2.5 py-1.5 rounded bg-slate-900/60 border border-slate-800/80 hover:border-cyan-500/30 group">
                <div className="flex items-center space-x-2">
                  <Boxes className="w-3.5 h-3.5 text-cyan-400" />
                  <span className="text-slate-200">model.stl</span>
                </div>
                <button
                  onClick={() => onDownloadFile('stl')}
                  className="text-slate-500 group-hover:text-cyan-400 hover:bg-slate-800 p-1 rounded transition-colors"
                  title="Download STL Mesh"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Python build123d Script */}
              <div className="flex items-center justify-between px-2.5 py-1.5 rounded bg-slate-900/60 border border-slate-800/80 hover:border-purple-500/30 group">
                <div 
                  onClick={() => onViewSourceFile('py')}
                  className="flex items-center space-x-2 cursor-pointer hover:text-purple-400 flex-1"
                >
                  <FileCode className="w-3.5 h-3.5 text-purple-400" />
                  <span className="text-slate-200">model.py</span>
                </div>
                <button
                  onClick={() => onDownloadFile('py')}
                  className="text-slate-500 group-hover:text-purple-400 hover:bg-slate-800 p-1 rounded transition-colors"
                  title="Download Python Source"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Plan JSON */}
              <div className="flex items-center justify-between px-2.5 py-1.5 rounded bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 group">
                <div 
                  onClick={() => onViewSourceFile('plan')}
                  className="flex items-center space-x-2 cursor-pointer hover:text-slate-300 flex-1"
                >
                  <FileText className="w-3.5 h-3.5 text-blue-400" />
                  <span className="text-slate-200">plan.json</span>
                </div>
                <button
                  onClick={() => onDownloadFile('json')}
                  className="text-slate-500 group-hover:text-blue-400 hover:bg-slate-800 p-1 rounded transition-colors"
                  title="Download Plan JSON"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* SECTION 3: ACTIONS */}
          <div>
            <div className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Actions
            </div>
            <div className="grid grid-cols-2 gap-1.5 text-xs font-medium">
              <button
                onClick={onNewModel}
                className="flex items-center justify-center space-x-1.5 px-2 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-amber-500/50 transition-colors"
              >
                <Plus className="w-3.5 h-3.5 text-amber-400" />
                <span>New Model</span>
              </button>

              <button
                onClick={onDuplicateVersion}
                className="flex items-center justify-center space-x-1.5 px-2 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-cyan-500/50 transition-colors"
              >
                <Copy className="w-3.5 h-3.5 text-cyan-400" />
                <span>Duplicate</span>
              </button>

              <button
                onClick={onRestoreVersion}
                className="flex items-center justify-center space-x-1.5 px-2 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-emerald-500/50 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
                <span>Restore</span>
              </button>

              <button
                onClick={() => onDeleteVersion(currentVersionId)}
                disabled={versions.length <= 1}
                className={`flex items-center justify-center space-x-1.5 px-2 py-1.5 rounded bg-slate-900 border border-slate-800 transition-colors ${
                  versions.length <= 1 ? 'opacity-40 cursor-not-allowed text-slate-600' : 'text-slate-300 hover:text-red-400 hover:border-red-500/50'
                }`}
              >
                <Trash2 className="w-3.5 h-3.5 text-red-400" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};
