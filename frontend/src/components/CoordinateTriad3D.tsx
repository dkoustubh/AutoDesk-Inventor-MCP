import React from 'react';

interface CoordinateTriad3DProps {
  rotX: number;
  rotY: number;
}

export const CoordinateTriad3D: React.FC<CoordinateTriad3DProps> = ({ rotX, rotY }) => {
  return (
    <div className="absolute bottom-6 left-6 z-20 select-none pointer-events-none">
      <div
        className="relative w-20 h-20 flex items-center justify-center"
        style={{
          perspective: 600
        }}
      >
        {/* 3D Rotating Triad Container (Rotates synchronously with ViewCube and Solid Model) */}
        <div
          className="relative w-0 h-0 flex items-center justify-center transition-transform duration-75"
          style={{
            transformStyle: 'preserve-3d',
            transform: `rotateX(${rotX}deg) rotateY(${rotY}deg)`
          }}
        >
          {/* Origin Center Sphere */}
          <div
            className="absolute w-3 h-3 -left-1.5 -top-1.5 rounded-full bg-slate-800 border border-slate-600 shadow-md"
            style={{ transform: 'translateZ(0px)' }}
          />

          {/* +X AXIS (RED Arrow pointing +X) */}
          <div
            className="absolute h-1 bg-red-600 origin-left flex items-center shadow-sm"
            style={{
              width: 44,
              left: 0,
              top: -2,
              transform: 'rotateY(0deg)'
            }}
          >
            {/* Arrowhead */}
            <div
              className="absolute -right-2 w-0 h-0 border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-l-[8px] border-l-red-600"
            />
            {/* X Label */}
            <span className="absolute -right-5 text-[11px] font-mono font-extrabold text-red-600 drop-shadow-sm">
              X
            </span>
          </div>

          {/* +Y AXIS (GREEN Arrow pointing +Y / 90deg) */}
          <div
            className="absolute w-1 bg-emerald-600 origin-top flex flex-col items-center shadow-sm"
            style={{
              height: 44,
              left: -2,
              top: -44,
              transform: 'rotateX(0deg)'
            }}
          >
            {/* Arrowhead */}
            <div
              className="absolute -top-2 w-0 h-0 border-l-[4px] border-l-transparent border-r-[4px] border-r-transparent border-b-[8px] border-b-emerald-600"
            />
            {/* Y Label */}
            <span className="absolute -top-6 text-[11px] font-mono font-extrabold text-emerald-600 drop-shadow-sm">
              Y
            </span>
          </div>

          {/* +Z AXIS (BLUE Arrow pointing +Z normal out of plane) */}
          <div
            className="absolute h-1 bg-blue-600 origin-left flex items-center shadow-sm"
            style={{
              width: 44,
              left: 0,
              top: -2,
              transform: 'rotateY(-90deg)'
            }}
          >
            {/* Arrowhead */}
            <div
              className="absolute -right-2 w-0 h-0 border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-l-[8px] border-l-blue-600"
            />
            {/* Z Label */}
            <span className="absolute -right-5 text-[11px] font-mono font-extrabold text-blue-600 drop-shadow-sm">
              Z
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
