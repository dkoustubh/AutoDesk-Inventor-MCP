import math
from fastapi import APIRouter, Query, Response
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/render", tags=["CAD Image Renderer"])

@router.get("/cad.svg")
async def render_cad_svg(
    shape: str = Query("box"),
    l: float = Query(10.0),
    w: float = Query(10.0),
    h: float = Query(10.0),
    hole: float = Query(0.0),
    teeth: int = Query(16),
    bore: float = Query(12.0),
    top_type: str = Query(""),
    top_size: float = Query(0.0)
):
    """
    Renders dynamic 3D isometric CAD drawings as standard SVG images with CORS headers.
    """
    if "cone" in shape:
        # 3D Tapered Cone SVG
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="260" viewBox="0 0 400 260" style="background:#ffffff; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <defs>
    <linearGradient id="coneGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="50%" stop-color="#0284c7" />
      <stop offset="100%" stop-color="#0369a1" />
    </linearGradient>
    <filter id="cadShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity="0.15" />
    </filter>
  </defs>

  <rect x="2" y="2" width="396" height="256" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
  <rect x="2" y="2" width="396" height="32" rx="10" fill="#0f172a" />
  <text x="14" y="21" fill="#38bdf8" font-size="12" font-weight="bold" font-family="monospace">AUTODESK INVENTOR 2026 — 3D CONE SOLID</text>

  <g filter="url(#cadShadow)" transform="translate(200, 140)">
    <!-- Base Ellipse -->
    <ellipse cx="0" cy="50" rx="70" ry="24" fill="#0284c7" stroke="#0369a1" stroke-width="2.5" />
    <!-- Cone Body -->
    <path d="M -70,50 L 0,-60 L 70,50 Z" fill="url(#coneGrad)" stroke="#0284c7" stroke-width="2" />
    <!-- Front curved base -->
    <path d="M -70,50 A 70 24 0 0 0 70 50" fill="none" stroke="#0369a1" stroke-width="2.5" />
    
    <text x="0" y="-70" text-anchor="middle" fill="#0f172a" font-size="11" font-family="monospace" font-weight="bold">Apex (H: {h}mm)</text>
    <text x="0" y="55" text-anchor="middle" fill="#ffffff" font-size="11" font-family="monospace" font-weight="bold">Base R{l}mm (Ø{l*2}mm)</text>
  </g>

  <text x="200" y="245" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="bold" font-family="monospace">Parametric Cone: Base Radius {l}mm • Height {h}mm</text>
</svg>"""

    elif "rhombus" in shape or "diamond" in shape:
        # 3D Rhombus Prism SVG
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="260" viewBox="0 0 400 260" style="background:#ffffff; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <defs>
    <filter id="cadShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity="0.15" />
    </filter>
  </defs>

  <rect x="2" y="2" width="396" height="256" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
  <rect x="2" y="2" width="396" height="32" rx="10" fill="#0f172a" />
  <text x="14" y="21" fill="#f59e0b" font-size="12" font-weight="bold" font-family="monospace">AUTODESK INVENTOR 2026 — RHOMBUS PRISM</text>

  <g filter="url(#cadShadow)" transform="translate(200, 130)">
    <!-- Top Face Diamond -->
    <polygon points="0,-45 80,0 0,45 -80,0" fill="#93c5fd" stroke="#2563eb" stroke-width="2.5" />
    <!-- Front-Left Face -->
    <polygon points="-80,0 0,45 0,85 -80,40" fill="#cbd5e1" stroke="#475569" stroke-width="2.5" />
    <!-- Front-Right Face -->
    <polygon points="0,45 80,0 80,40 0,85" fill="#94a3b8" stroke="#334155" stroke-width="2.5" />

    <text x="0" y="5" text-anchor="middle" fill="#1e3a8a" font-size="11" font-family="monospace" font-weight="bold">Dx: {l}mm • Dy: {w}mm</text>
    <text x="0" y="70" text-anchor="middle" fill="#0f172a" font-size="10" font-family="monospace" font-weight="bold">Thk: {h}mm</text>
  </g>

  <text x="200" y="245" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="bold" font-family="monospace">Rhombus Prism: Diagonal {l}×{w} mm • Thickness {h}mm</text>
</svg>"""

    if "roller" in shape or "cylinder" in shape or shape == "conveyor_roller":
        # 3D Isometric Conveyor Roller SVG (Full 3D Solid Assembly)
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="460" height="270" viewBox="0 0 460 270" style="background:#ffffff; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <defs>
    <linearGradient id="rollerGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#f1f5f9" />
      <stop offset="25%" stop-color="#cbd5e1" />
      <stop offset="50%" stop-color="#94a3b8" />
      <stop offset="75%" stop-color="#475569" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
    <linearGradient id="shaftGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#e2e8f0" />
      <stop offset="50%" stop-color="#64748b" />
      <stop offset="100%" stop-color="#334155" />
    </linearGradient>
    <filter id="cadShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity="0.18" />
    </filter>
  </defs>

  <rect x="2" y="2" width="456" height="266" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
  <rect x="2" y="2" width="456" height="32" rx="10" fill="#0f172a" />
  <text x="14" y="21" fill="#38bdf8" font-size="12" font-weight="bold" font-family="monospace">AUTODESK INVENTOR 2026 — 3D CONVEYOR ROLLER</text>

  <g filter="url(#cadShadow)" transform="translate(60, 140)">
    <!-- Left Protruding Shaft Pin -->
    <rect x="-40" y="-10" width="40" height="20" rx="3" fill="url(#shaftGrad)" stroke="#1e293b" stroke-width="1.5" />
    <ellipse cx="-40" cy="0" rx="5" ry="10" fill="#cbd5e1" stroke="#1e293b" stroke-width="1.5" />

    <!-- Main 3D Roller Tube Body -->
    <rect x="0" y="-45" width="280" height="90" fill="url(#rollerGrad)" stroke="#334155" stroke-width="2" />

    <!-- Left End-Cap Hub -->
    <ellipse cx="0" cy="0" rx="18" ry="45" fill="#475569" stroke="#1e293b" stroke-width="2" />

    <!-- Right End-Cap Face (3D Isometric Circle) -->
    <ellipse cx="280" cy="0" rx="18" ry="45" fill="#94a3b8" stroke="#1e293b" stroke-width="2" />
    <ellipse cx="280" cy="0" rx="9" ry="22" fill="#cbd5e1" stroke="#334155" stroke-width="1.5" />

    <!-- Right Protruding Shaft Pin -->
    <rect x="280" y="-10" width="40" height="20" rx="3" fill="url(#shaftGrad)" stroke="#1e293b" stroke-width="1.5" />
    <ellipse cx="320" cy="0" rx="5" ry="10" fill="#cbd5e1" stroke="#1e293b" stroke-width="1.5" />

    <!-- Dimension Annotation Overlays -->
    <text x="140" y="-55" text-anchor="middle" fill="#0f172a" font-size="12" font-family="monospace" font-weight="bold">Tube Length L: {h or 500} mm</text>
    <text x="140" y="5" text-anchor="middle" fill="#ffffff" font-size="12" font-family="monospace" font-weight="bold">Tube Outer Ø{l or 60} mm</text>
    <text x="330" y="28" text-anchor="middle" fill="#0369a1" font-size="10" font-family="monospace" font-weight="bold">Shaft Ø15mm</text>
  </g>

  <text x="230" y="250" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="bold" font-family="monospace">Conveyor Roller: Outer Ø{l or 60}mm • Tube Length {h or 500}mm • Solid Steel</text>
</svg>"""

    elif "sprocket" in shape or teeth > 0 and teeth != 16:
        # 3D Isometric Sprocket Solid SVG (3D Extruded Gear with Angled Flank Faces)
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="270" viewBox="0 0 400 270" style="background:#ffffff; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <defs>
    <linearGradient id="gearFaceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a" />
      <stop offset="50%" stop-color="#f59e0b" />
      <stop offset="100%" stop-color="#b45309" />
    </linearGradient>
    <linearGradient id="gearSideGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#92400e" />
      <stop offset="100%" stop-color="#451a03" />
    </linearGradient>
    <filter id="gearShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity="0.2" />
    </filter>
  </defs>

  <rect x="2" y="2" width="396" height="266" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
  <rect x="2" y="2" width="396" height="32" rx="10" fill="#0f172a" />
  <text x="14" y="21" fill="#f59e0b" font-size="12" font-weight="bold" font-family="monospace">AUTODESK INVENTOR 2026 — 3D ISOMETRIC SPROCKET</text>

  <g filter="url(#gearShadow)" transform="translate(200, 140)">
    <!-- 3D Extruded Rear Shadow/Thickness Body -->
    <g transform="translate(0, 14)">
      <circle cx="0" cy="0" r="70" fill="url(#gearSideGrad)" stroke="#451a03" stroke-width="2" />
      <!-- Teeth Profiles Rear -->
      <polygon points="-75,-15 -85,0 -75,15 -60,0" fill="#78350f" />
      <polygon points="75,-15 85,0 75,15 60,0" fill="#78350f" />
      <polygon points="-15,-75 0,-85 15,-75 0,-60" fill="#78350f" />
      <polygon points="-15,75 0,85 15,75 0,60" fill="#78350f" />
    </g>

    <!-- 3D Front Isometric Gear Face -->
    <circle cx="0" cy="0" r="70" fill="url(#gearFaceGrad)" stroke="#78350f" stroke-width="2.5" />
    
    <!-- 3D Front Radial Teeth Flanks -->
    <polygon points="-75,-15 -85,0 -75,15 -60,0" fill="#f59e0b" stroke="#78350f" stroke-width="1.5" />
    <polygon points="75,-15 85,0 75,15 60,0" fill="#f59e0b" stroke="#78350f" stroke-width="1.5" />
    <polygon points="-15,-75 0,-85 15,-75 0,-60" fill="#f59e0b" stroke="#78350f" stroke-width="1.5" />
    <polygon points="-15,75 0,85 15,75 0,60" fill="#f59e0b" stroke="#78350f" stroke-width="1.5" />
    <polygon points="-55,-55 -65,-65 -45,-65" fill="#f59e0b" stroke="#78350f" stroke-width="1.5" />
    <polygon points="55,-55 65,-65 45,-65" fill="#f59e0b" stroke="#78350f" stroke-width="1.5" />
    <polygon points="-55,55 -65,65 -45,65" fill="#f59e0b" stroke="#78350f" stroke-width="1.5" />
    <polygon points="55,55 65,65 45,65" fill="#f59e0b" stroke="#78350f" stroke-width="1.5" />

    <!-- Center Raised Hub Boss -->
    <circle cx="0" cy="0" r="34" fill="#d97706" stroke="#92400e" stroke-width="2" />

    <!-- Center Bore Hole with Keyway -->
    <path d="M -16,0 A 16 16 0 1 0 16 0 A 16 16 0 0 0 -16 0 M -4,-16 L 4,-16 L 4,-22 L -4,-22 Z" fill="#0f172a" stroke="#451a03" stroke-width="2" />
    <text x="0" y="5" text-anchor="middle" fill="#fef08a" font-size="11" font-family="monospace" font-weight="bold">Ø{bore}mm</text>
    <text x="0" y="-40" text-anchor="middle" fill="#78350f" font-size="9" font-family="monospace" font-weight="bold">Thickness {h}mm</text>
  </g>

  <text x="200" y="250" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="bold" font-family="monospace">3D Solid Sprocket: Ø{l}mm • {teeth} Teeth • Face Thickness {h}mm</text>
</svg>"""
    elif "hole" in shape or hole > 0:
        # Box with Hole SVG
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="260" viewBox="0 0 400 260" style="background:#ffffff; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <defs>
    <filter id="cadShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity="0.15" />
    </filter>
  </defs>

  <rect x="2" y="2" width="396" height="256" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
  <rect x="2" y="2" width="396" height="32" rx="10" fill="#0f172a" />
  <text x="14" y="21" fill="#38bdf8" font-size="12" font-weight="bold" font-family="monospace">AUTODESK INVENTOR 2026 — DRILLED SOLID</text>

  <g filter="url(#cadShadow)" transform="translate(200, 130)">
    <!-- Base Box -->
    <polygon points="0,-50 100,-5 0,40 -100,-5" fill="#93c5fd" stroke="#2563eb" stroke-width="2.5" />
    <polygon points="-100,-5 0,40 0,95 -100,50" fill="#cbd5e1" stroke="#475569" stroke-width="2.5" />
    <polygon points="0,40 100,-5 100,50 0,95" fill="#94a3b8" stroke="#334155" stroke-width="2.5" />

    <!-- Center Hole Ellipse -->
    <ellipse cx="0" cy="-5" rx="20" ry="9" fill="#0f172a" stroke="#1e3a8a" stroke-width="2" />
    <text x="0" y="-18" text-anchor="middle" fill="#1e3a8a" font-size="11" font-family="monospace" font-weight="bold">Ø{hole}mm Hole</text>
  </g>

  <text x="200" y="245" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="bold" font-family="monospace">{l}×{w}×{h} mm Solid Cube with Ø{hole} mm Through-Hole</text>
</svg>"""
    elif "compound" in shape or top_size > 0 or top_type:
        # Stacked / Compound 3D Solids (e.g. 10mm cube with 5mm cube on top)
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="270" viewBox="0 0 400 270" style="background:#ffffff; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <defs>
    <filter id="cadShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity="0.15" />
    </filter>
  </defs>

  <rect x="2" y="2" width="396" height="266" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
  <rect x="2" y="2" width="396" height="32" rx="10" fill="#0f172a" />
  <text x="14" y="21" fill="#38bdf8" font-size="12" font-weight="bold" font-family="monospace">AUTODESK INVENTOR 2026 — COMPOUND SOLID</text>

  <g filter="url(#cadShadow)" transform="translate(200, 150)">
    <!-- Base Cube 10mm -->
    <polygon points="0,-40 90,-5 0,30 -90,-5" fill="#93c5fd" stroke="#2563eb" stroke-width="2.5" />
    <polygon points="-90,-5 0,30 0,75 -90,40" fill="#cbd5e1" stroke="#475569" stroke-width="2.5" />
    <polygon points="0,30 90,-5 90,40 0,75" fill="#94a3b8" stroke="#334155" stroke-width="2.5" />

    <!-- Top Stacked Cube 5mm -->
    <g transform="translate(0, -45)">
      <polygon points="0,-25 50,-5 0,15 -50,-5" fill="#fdba74" stroke="#ea580c" stroke-width="2" />
      <polygon points="-50,-5 0,15 0,40 -50,20" fill="#fed7aa" stroke="#c2410c" stroke-width="2" />
      <polygon points="0,15 50,-5 50,20 0,40" fill="#f97316" stroke="#9a3412" stroke-width="2" />
      <text x="0" y="-32" text-anchor="middle" fill="#ea580c" font-size="11" font-family="monospace" font-weight="bold">Top {top_size or 5}mm {top_type or 'Cube'}</text>
    </g>

    <text x="-45" y="60" fill="#0f172a" font-size="11" font-family="monospace" font-weight="bold">{l}mm</text>
    <text x="45" y="60" fill="#0f172a" font-size="11" font-family="monospace" font-weight="bold">{w}mm</text>
  </g>

  <text x="200" y="252" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="bold" font-family="monospace">Base {l}mm Cube + Stacked {top_size or 5}mm {top_type or 'Cube'} on Top</text>
</svg>"""
    else:
        # Standard Solid Box / Cuboid SVG
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="260" viewBox="0 0 400 260" style="background:#ffffff; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <defs>
    <filter id="cadShadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-opacity="0.15" />
    </filter>
  </defs>

  <rect x="2" y="2" width="396" height="256" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2" />
  <rect x="2" y="2" width="396" height="32" rx="10" fill="#0f172a" />
  <text x="14" y="21" fill="#f59e0b" font-size="12" font-weight="bold" font-family="monospace">AUTODESK INVENTOR 2026 — 3D SOLID BODY</text>

  <g filter="url(#cadShadow)" transform="translate(200, 135)">
    <!-- Top Face -->
    <polygon points="0,-50 100,-5 0,40 -100,-5" fill="#93c5fd" stroke="#2563eb" stroke-width="2.5" />
    <!-- Front Face -->
    <polygon points="-100,-5 0,40 0,90 -100,45" fill="#cbd5e1" stroke="#475569" stroke-width="2.5" />
    <!-- Right Face -->
    <polygon points="0,40 100,-5 100,45 0,90" fill="#94a3b8" stroke="#334155" stroke-width="2.5" />

    <text x="-50" y="70" fill="#0f172a" font-size="11" font-family="monospace" font-weight="bold">{l}mm</text>
    <text x="50" y="70" fill="#0f172a" font-size="11" font-family="monospace" font-weight="bold">{w}mm</text>
    <text x="12" y="65" fill="#1e293b" font-size="11" font-family="monospace" font-weight="bold">H: {h}mm</text>
  </g>

  <text x="200" y="245" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="bold" font-family="monospace">{l} × {w} × {h} mm Parametric 3D Solid Model</text>
</svg>"""

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache"
        }
    )

@router.get("/viewer.html", response_class=HTMLResponse)
async def get_interactive_viewer(
    shape: str = Query("box"),
    l: float = Query(10.0),
    w: float = Query(10.0),
    h: float = Query(10.0)
):
    """
    Returns a self-contained 3D interactive WebGL viewport embeddable via iframe into Open WebUI.
    """
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ margin: 0; background: #f8fafc; overflow: hidden; font-family: sans-serif; }}
    #viewport {{ width: 100vw; height: 100vh; }}
    .badge {{ position: absolute; top: 8px; left: 8px; background: rgba(15,23,42,0.85); color: #38bdf8; font-size: 11px; padding: 4px 8px; border-radius: 4px; font-family: monospace; }}
  </style>
</head>
<body>
  <div class="badge">AUTODESK 3D VIEWPORT: {l}x{w}x{h}mm</div>
  <iframe src="http://192.168.11.94:5173" style="width:100%;height:100%;border:none;"></iframe>
</body>
</html>"""
