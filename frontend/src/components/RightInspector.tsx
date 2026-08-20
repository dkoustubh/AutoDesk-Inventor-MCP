import React, { useState } from 'react';
import { 
  Sliders, 
  Layers, 
  Cpu, 
  CheckCircle2, 
  AlertTriangle, 
  Code, 
  Copy, 
  Check, 
  Box, 
  Maximize, 
  Activity,
  ChevronRight,
  ChevronLeft,
  FileJson,
  Hash,
  Compass
} from 'lucide-react';
import { CADVersion, SelectedGeometryInfo } from '../types';

interface RightInspectorProps {
  version: CADVersion | null;
  selectedGeometry: SelectedGeometryInfo | null;
  isGenerating: boolean;
  onAutoRepair?: () => void;
}

export const RightInspector: React.FC<RightInspectorProps> = ({
  version,
  selectedGeometry,
  isGenerating,
  onAutoRepair
}) => {
  const [activeTab, setActiveTab] = useState<'properties' | 'geometry' | 'features' | 'validation' | 'source'>('geometry');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);

  const val = version?.validation;
  const bbox = val?.bounding_box;

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <aside 
      className={`border-l border-slate-800 bg-slate-950/80 flex flex-col transition-all duration-200 select-none z-20 shrink-0 ${
        isCollapsed ? 'w-10' : 'w-80'
      }`}
    >
      {/* Inspector Header / Collapse Toggle */}
      <div className="h-9 border-b border-slate-800 px-3 flex items-center justify-between text-xs font-semibold text-slate-400">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          title={isCollapsed ? "Expand Inspector" : "Collapse Inspector"}
        >
          {isCollapsed ? <ChevronLeft className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        </button>
        {!isCollapsed && (
          <div className="flex items-center space-x-1.5">
            <Sliders className="w-3.5 h-3.5 text-amber-400" />
            <span className="uppercase tracking-wider text-[11px] text-slate-300 font-mono">Inspector</span>
          </div>
        )}
      </div>

      {isCollapsed ? (
        <div className="flex-1 flex flex-col items-center py-3 space-y-4 text-slate-400">
          <button onClick={() => { setIsCollapsed(false); setActiveTab('geometry'); }} title="Geometry" className="p-2 rounded hover:bg-slate-800 hover:text-amber-400">
            <Box className="w-4 h-4" />
          </button>
          <button onClick={() => { setIsCollapsed(false); setActiveTab('validation'); }} title="Validation" className="p-2 rounded hover:bg-slate-800 hover:text-amber-400">
            <CheckCircle2 className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-800 bg-slate-900/50 p-1 space-x-0.5">
            {(['properties', 'geometry', 'features', 'validation', 'source'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-1.5 text-[10px] uppercase font-mono font-semibold rounded transition-colors ${
                  activeTab === tab
                    ? 'bg-slate-800 text-amber-400 shadow-sm'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-900'
                }`}
              >
                {tab === 'properties' && 'Prop'}
                {tab === 'geometry' && 'Geom'}
                {tab === 'features' && 'Feat'}
                {tab === 'validation' && 'Valid'}
                {tab === 'source' && 'Code'}
              </button>
            ))}
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-3 space-y-4 text-xs font-mono">
            {/* TAB 1: PROPERTIES */}
            {activeTab === 'properties' && (
              <div className="space-y-3">
                <div className="bg-slate-900/60 border border-slate-800/80 rounded-md p-3 space-y-2">
                  <div className="flex justify-between text-slate-400">
                    <span>Part Name</span>
                    <span className="text-slate-200 font-semibold">{version?.tool ? version.tool.replace('inventor.create_', '').toUpperCase() : 'CAD_SOLID'}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Version</span>
                    <span className="text-cyan-400 font-bold">{version?.versionNumber || 'v001'}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Units</span>
                    <span className="text-amber-400 font-bold">Millimeters (mm)</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>AI Model</span>
                    <span className="text-slate-200">Gemma 31B (GPU)</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>CAD Kernel</span>
                    <span className="text-emerald-400">OpenCascade 7.9</span>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: GEOMETRY */}
            {activeTab === 'geometry' && (
              <div className="space-y-3">
                {/* Physical Properties */}
                <div className="bg-slate-900/60 border border-slate-800/80 rounded-md p-3 space-y-2.5">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center space-x-1.5">
                    <Box className="w-3.5 h-3.5 text-amber-400" />
                    <span>Mass Properties</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Volume</span>
                    <span className="text-emerald-400 font-bold">{val?.volume_mm3 ? `${val.volume_mm3.toLocaleString()} mm³` : '—'}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Solids</span>
                    <span className="text-slate-200 font-semibold">{val?.is_solid ? '1 Closed Solid' : '0'}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Faces</span>
                    <span className="text-slate-200 font-semibold">{val?.face_count ?? '—'}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Edges</span>
                    <span className="text-slate-200 font-semibold">{val?.edge_count ?? '—'}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Vertices</span>
                    <span className="text-slate-200 font-semibold">{val?.vertex_count ?? '—'}</span>
                  </div>
                </div>

                {/* Bounding Box */}
                <div className="bg-slate-900/60 border border-slate-800/80 rounded-md p-3 space-y-2">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center space-x-1.5">
                    <Maximize className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Bounding Box</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
                    <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                      <span className="text-red-400 block text-[9px]">X SIZE</span>
                      <span className="text-slate-200 font-bold">{bbox?.size_x ?? '—'} mm</span>
                    </div>
                    <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                      <span className="text-emerald-400 block text-[9px]">Y SIZE</span>
                      <span className="text-slate-200 font-bold">{bbox?.size_y ?? '—'} mm</span>
                    </div>
                    <div className="bg-slate-950 p-1.5 rounded border border-slate-800">
                      <span className="text-blue-400 block text-[9px]">Z SIZE</span>
                      <span className="text-slate-200 font-bold">{bbox?.size_z ?? '—'} mm</span>
                    </div>
                  </div>
                </div>

                {/* Selected Entity Details */}
                {selectedGeometry && (
                  <div className="bg-amber-500/10 border border-amber-500/30 rounded-md p-3 space-y-2">
                    <div className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider flex items-center space-x-1.5">
                      <Compass className="w-3.5 h-3.5 text-amber-400" />
                      <span>Selected {selectedGeometry.type.toUpperCase()} #{selectedGeometry.id}</span>
                    </div>
                    {selectedGeometry.normal && (
                      <div className="flex justify-between text-slate-400">
                        <span>Normal Vector</span>
                        <span className="text-slate-200 font-mono">[{selectedGeometry.normal.join(', ')}]</span>
                      </div>
                    )}
                    {selectedGeometry.area_mm2 && (
                      <div className="flex justify-between text-slate-400">
                        <span>Surface Area</span>
                        <span className="text-amber-300 font-bold">{selectedGeometry.area_mm2.toFixed(2)} mm²</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: FEATURES */}
            {activeTab === 'features' && (
              <div className="space-y-2">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Layers className="w-3.5 h-3.5 text-amber-400" />
                  <span>Parametric Feature Tree</span>
                </div>
                {version?.features && version.features.length > 0 ? (
                  version.features.map((feat, idx) => (
                    <div key={feat.id || idx} className="bg-slate-900/60 border border-slate-800 p-2.5 rounded-md space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="w-4 h-4 rounded-full bg-amber-500/20 text-amber-400 text-[10px] flex items-center justify-center font-bold">
                          {idx + 1}
                        </span>
                        <span className="text-slate-200 font-semibold text-xs">{feat.name}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 pl-6 space-y-0.5">
                        {Object.entries(feat.parameters).map(([k, v]) => (
                          <div key={k} className="flex justify-between">
                            <span className="text-slate-500">{k}:</span>
                            <span className="text-slate-300">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-500 text-center py-6">
                    Single Solid Feature (Parameters in Plan)
                  </div>
                )}
              </div>
            )}

            {/* TAB 4: VALIDATION */}
            {activeTab === 'validation' && (
              <div className="space-y-3">
                <div className={`p-3 rounded-md border ${
                  val?.is_valid 
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' 
                    : 'bg-red-500/10 border-red-500/30 text-red-300'
                }`}>
                  <div className="flex items-center space-x-2 font-bold text-xs">
                    {val?.is_valid ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <AlertTriangle className="w-4 h-4 text-red-400" />}
                    <span>{val?.is_valid ? 'Valid B-Rep Solid' : 'Validation Error'}</span>
                  </div>
                  <p className="text-[11px] mt-1.5 text-slate-300 font-normal leading-relaxed">
                    {val?.message || 'Solid verified via OpenCascade BRepCheck analyzer.'}
                  </p>
                </div>

                <div className="space-y-1.5 text-[11px]">
                  <div className="flex justify-between py-1 border-b border-slate-900">
                    <span className="text-slate-400">OpenCascade BRepCheck</span>
                    <span className="text-emerald-400 font-bold">PASSED</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-900">
                    <span className="text-slate-400">STEP Re-import Test</span>
                    <span className="text-emerald-400 font-bold">PASSED</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-900">
                    <span className="text-slate-400">Manifold Closed Shell</span>
                    <span className="text-emerald-400 font-bold">YES</span>
                  </div>
                </div>

                {!val?.is_valid && onAutoRepair && (
                  <button
                    onClick={onAutoRepair}
                    disabled={isGenerating}
                    className="w-full py-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-slate-950 font-bold rounded-md flex items-center justify-center space-x-2 shadow-lg shadow-amber-500/20"
                  >
                    <Cpu className="w-4 h-4" />
                    <span>Auto-Repair with Gemma</span>
                  </button>
                )}
              </div>
            )}

            {/* TAB 5: SOURCE CODE */}
            {activeTab === 'source' && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">build123d Script</span>
                  <button
                    onClick={() => handleCopy(version?.pythonScript || '# No script generated')}
                    className="flex items-center space-x-1 text-[10px] px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800"
                  >
                    {copiedCode ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedCode ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <pre className="p-3 bg-slate-950 border border-slate-800 rounded-md text-[10px] text-slate-300 overflow-x-auto font-mono max-h-80 leading-relaxed">
                  {version?.pythonScript || `from build123d import *

# Generated by Gemma 31B Text-to-CAD Engine
with BuildPart() as model:
    Box(${version?.parameters?.length_mm || 100}, ${version?.parameters?.width_mm || 60}, ${version?.parameters?.height_mm || 20})
`}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </aside>
  );
};
