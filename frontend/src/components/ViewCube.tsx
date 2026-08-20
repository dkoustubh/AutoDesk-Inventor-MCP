import React, { useState, useRef, useEffect } from 'react';
import { Home } from 'lucide-react';

export type ViewOrientation = 'ISO' | 'TOP' | 'FRONT' | 'RIGHT' | 'CUSTOM';

interface ViewCubeProps {
  rotX: number;
  rotY: number;
  onRotate: (rx: number, ry: number) => void;
  onResetIso: () => void;
  onSnapView: (view: 'TOP' | 'FRONT' | 'RIGHT') => void;
}

export const ViewCube: React.FC<ViewCubeProps> = ({
  rotX,
  rotY,
  onRotate,
  onResetIso,
  onSnapView
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef<{ x: number; y: number; startRotX: number; startRotY: number }>({ x: 0, y: 0, startRotX: rotX, startRotY: rotY });

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    dragStartRef.current = {
      x: e.clientX,
      y: e.clientY,
      startRotX: rotX,
      startRotY: rotY
    };
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - dragStartRef.current.x;
      const dy = e.clientY - dragStartRef.current.y;

      const newRotY = (dragStartRef.current.startRotY + dx * 0.6) % 360;
      const newRotX = Math.max(-85, Math.min(85, dragStartRef.current.startRotX - dy * 0.6));

      onRotate(newRotX, newRotY);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, onRotate]);

  return (
    <div className="absolute top-14 right-6 z-20 flex flex-col items-center select-none">
      {/* Home Button (Autodesk Standard Top-Left Home Icon) */}
      <button
        onClick={onResetIso}
        title="Home (Isometric View)"
        className="absolute -top-3 -left-3 z-30 p-1.5 bg-[#222936] hover:bg-[#333e52] text-slate-300 hover:text-amber-400 border border-slate-600 rounded-md shadow-lg transition-all active:scale-95 cursor-pointer"
      >
        <Home className="w-3.5 h-3.5" />
      </button>

      {/* 3D Rotatable ViewCube Container */}
      <div
        onMouseDown={handleMouseDown}
        className={`relative w-28 h-28 flex items-center justify-center cursor-grab active:cursor-grabbing ${
          isDragging ? 'scale-105' : ''
        } transition-transform duration-75`}
        style={{ perspective: 600 }}
      >
        {/* CSS 3D Cube that rotates live with drag */}
        <div
          className="relative w-16 h-16 transition-transform duration-75 ease-out shadow-2xl"
          style={{
            transformStyle: 'preserve-3d',
            transform: `rotateX(${rotX}deg) rotateY(${rotY}deg)`
          }}
        >
          {/* TOP FACE */}
          <div
            onClick={(e) => { e.stopPropagation(); onSnapView('TOP'); }}
            className="absolute inset-0 bg-[#cbd5e1] hover:bg-[#93c5fd] active:bg-[#38bdf8] border border-[#64748b] text-[#1e293b] font-mono text-[10px] font-extrabold flex items-center justify-center transition-colors shadow-inner cursor-pointer"
            style={{ transform: 'rotateX(90deg) translateZ(32px)' }}
          >
            TOP
          </div>

          {/* BOTTOM FACE */}
          <div
            className="absolute inset-0 bg-[#94a3b8] border border-[#475569] text-[#334155] font-mono text-[10px] font-bold flex items-center justify-center"
            style={{ transform: 'rotateX(-90deg) translateZ(32px)' }}
          >
            BOTTOM
          </div>

          {/* FRONT FACE */}
          <div
            onClick={(e) => { e.stopPropagation(); onSnapView('FRONT'); }}
            className="absolute inset-0 bg-[#94a3b8] hover:bg-[#93c5fd] active:bg-[#38bdf8] border border-[#475569] text-[#0f172a] font-mono text-[10px] font-extrabold flex items-center justify-center transition-colors shadow-inner cursor-pointer"
            style={{ transform: 'translateZ(32px)' }}
          >
            FRONT
          </div>

          {/* BACK FACE */}
          <div
            className="absolute inset-0 bg-[#64748b] border border-[#334155] text-slate-200 font-mono text-[10px] font-bold flex items-center justify-center"
            style={{ transform: 'rotateY(180deg) translateZ(32px)' }}
          >
            BACK
          </div>

          {/* RIGHT FACE */}
          <div
            onClick={(e) => { e.stopPropagation(); onSnapView('RIGHT'); }}
            className="absolute inset-0 bg-[#64748b] hover:bg-[#93c5fd] active:bg-[#38bdf8] border border-[#334155] text-white font-mono text-[10px] font-extrabold flex items-center justify-center transition-colors shadow-inner cursor-pointer"
            style={{ transform: 'rotateY(90deg) translateZ(32px)' }}
          >
            RIGHT
          </div>

          {/* LEFT FACE */}
          <div
            className="absolute inset-0 bg-[#475569] border border-[#1e293b] text-slate-300 font-mono text-[10px] font-bold flex items-center justify-center"
            style={{ transform: 'rotateY(-90deg) translateZ(32px)' }}
          >
            LEFT
          </div>
        </div>
      </div>

      {/* Rotation Telemetry */}
      <div className="mt-1 bg-[#121721]/90 border border-slate-700/80 px-2 py-0.5 rounded text-[9px] font-mono text-slate-400">
        Drag to 3D Orbit ({Math.round(rotX)}°, {Math.round(rotY)}°)
      </div>
    </div>
  );
};
