import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import {
  Download,
  Layers,
  Ruler,
  Box,
  Eye,
  PenTool,
  Printer,
  Compass,
  Maximize2,
  Home
} from 'lucide-react';

interface CadViewport3DProps {
  tool?: string;
  parameters?: Record<string, any>;
  lastPrompt?: string;
  workstationIp?: string;
}

export const CadViewport3D: React.FC<CadViewport3DProps> = ({
  tool = '',
  parameters = {},
  lastPrompt = '',
  workstationIp = '192.168.11.150'
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const modelGroupRef = useRef<THREE.Group | null>(null);

  // 3 Modes: 'design' (3D Solid Shaded), '3d_raw' (3D Raw Dimensions Rotatable), 'drawing' (2D Blueprint Sheet)
  const [viewMode, setViewMode] = useState<'design' | '3d_raw' | 'drawing'>('design');

  const [activePreset, setActivePreset] = useState<'iso' | 'top' | 'front' | 'right' | 'back' | 'left' | 'bottom'>('iso');

  // Mouse orbit state
  const isDraggingRef = useRef<boolean>(false);
  const prevMousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const p = parameters || {};
  const hasGeometry = Boolean(tool && tool.trim() !== '' && Object.keys(p).length > 0);

  // Dimension extraction with accurate defaults
  const l = Number(p.length_mm) || Number(p.diagonal_x_mm) || Number(p.outer_diameter_mm) || 30;
  const w = Number(p.width_mm) || Number(p.diagonal_y_mm) || l;
  const h = Number(p.height_mm) || Number(p.thickness_mm) || 30;
  const dia = Number(p.diameter_mm) || Number(p.outer_diameter_mm) || (p.radius_mm ? Number(p.radius_mm) * 2 : (p.base_radius_mm ? Number(p.base_radius_mm) * 2 : 40));
  const cylH = Number(p.height_mm) || Number(p.length_mm) || 50;
  const teethCount = Number(p.teeth_count) || (tool.includes('sprocket') ? 14 : 0);
  const boreDia = Number(p.bore_diameter_mm) || (teethCount ? round(dia * 0.25) : 0);
  const holeDia = Number(p.hole_diameter_mm) || 0;

  function round(val: number) {
    return Math.round(val * 10) / 10;
  }

  // Component Types
  const isTurntable = tool.includes('turntable') || lastPrompt.toLowerCase().includes('turntable') || lastPrompt.toLowerCase().includes('turn table') || lastPrompt.toLowerCase().includes('rotary table');
  const isPRBConveyor = !isTurntable && (tool.includes('prb') || tool.includes('conveyor') || lastPrompt.toLowerCase().includes('prb') || lastPrompt.toLowerCase().includes('conveyor bed') || lastPrompt.toLowerCase().includes('roller bed'));
  const isBracket = !isTurntable && !isPRBConveyor && (tool.includes('bracket') || lastPrompt.toLowerCase().includes('bracket') || lastPrompt.toLowerCase().includes('rib') || lastPrompt.toLowerCase().includes('angle'));
  const isValveBody = !isTurntable && !isPRBConveyor && !isBracket && (tool.includes('valve') || tool.includes('spool') || lastPrompt.toLowerCase().includes('valve') || lastPrompt.toLowerCase().includes('like this'));
  const isRoller = !isTurntable && !isPRBConveyor && !isBracket && !isValveBody && (tool.includes('roller') || (tool.includes('cylinder') && cylH >= 100) || lastPrompt.toLowerCase().includes('roller'));
  const isSprocket = !isTurntable && !isPRBConveyor && !isBracket && !isValveBody && (tool.includes('sprocket') || teethCount > 0 || lastPrompt.toLowerCase().includes('sprocket') || lastPrompt.toLowerCase().includes('gear'));
  const isBoxWithHole = !isTurntable && !isPRBConveyor && !isBracket && !isValveBody && (tool.includes('box_with_hole') || holeDia > 0);
  const isCone = !isTurntable && !isPRBConveyor && !isBracket && !isValveBody && tool.includes('cone');
  const isRhombus = !isTurntable && !isPRBConveyor && !isBracket && !isValveBody && (tool.includes('rhombus') || p.diagonal_x_mm);
  const isPyramid = !isTurntable && !isPRBConveyor && !isBracket && !isValveBody && (tool.includes('pyramid') || (p.base_length_mm && !p.length_mm));
  const isCompound = !isTurntable && !isPRBConveyor && !isBracket && !isValveBody && (tool.includes('compound') || p.top_feature || p.features);
  const isCylinder = !isTurntable && !isPRBConveyor && !isBracket && !isValveBody && !isRoller && (tool.includes('cylinder') || (p.diameter_mm && !p.length_mm));

  // Material Spec & Calculation
  let materialName = 'Autodesk Generic Smooth (Aluminum 6061-T6)';
  let componentTitle = '3D Parametric Solid Box';
  let volumeCm3 = round((l * w * h) / 1000);

  if (isTurntable) {
    materialName = 'Structural Steel Tubing (RAL 5005 Blue) & Safety Yellow Guard (RAL 1021)';
    componentTitle = `Powered Rotary Conveyor Turntable Assembly (${p.roller_count || 8} Rollers)`;
    volumeCm3 = round(18500.0);
  } else if (isPRBConveyor) {
    materialName = 'Structural Steel C-Channel (RAL 5005 Powder Coat) & Turned Carbon Rollers';
    componentTitle = `Powered Roller Bed (PRB) Conveyor Assembly (${p.roller_count || 5} Rollers)`;
    volumeCm3 = round(12800.0);
  } else if (isBracket) {
    materialName = 'Cast Aluminum A380 / Ductile Iron';
    componentTitle = 'Ribbed Mounting Angle Bracket';
    volumeCm3 = round(165.4);
  } else if (isSprocket) {
    materialName = 'Machined Phosphor Bronze (CuSn8) / Hardened Tool Steel';
    componentTitle = `ISO 606 Sprocket (${teethCount} Teeth)`;
    volumeCm3 = round((Math.PI * Math.pow(dia / 20, 2) * (h / 10)) * 0.75);
  } else if (isRoller) {
    materialName = 'AISI 304 Stainless Steel & Ground Carbon Pin';
    componentTitle = `Conveyor Roller Assembly (Ø${dia}×${cylH}mm)`;
    volumeCm3 = round(Math.PI * Math.pow(dia / 20, 2) * (cylH / 10));
  } else if (isValveBody) {
    materialName = 'Cast Ductile Iron (EN-GJS-400-15)';
    componentTitle = 'Autodesk Flanged Valve Body Spool';
    volumeCm3 = round(480);
  } else if (isCone) {
    materialName = 'Precision Turned Carbon Steel (AISI 1045)';
    componentTitle = '3D Conical Solid Frustum';
    volumeCm3 = round((Math.PI * Math.pow(dia / 20, 2) * (h / 10)) / 3);
  } else if (isCylinder) {
    materialName = 'Billet Aluminum 6061-T6 (Turned)';
    componentTitle = `3D Solid Cylinder (Ø${dia}×${cylH}mm)`;
    volumeCm3 = round(Math.PI * Math.pow(dia / 20, 2) * (cylH / 10));
  }

  // ViewCube initial orientation matching Autodesk Inventor ISO (Top-Front-Right)
  const [viewCubeRot, setViewCubeRot] = useState<{ x: number; y: number }>({ x: -25, y: 45 });

  // 1. Initialize Three.js WebGL Scene
  useEffect(() => {
    if (!mountRef.current || viewMode === 'drawing') return;

    const width = mountRef.current.clientWidth || window.innerWidth - 420;
    const height = mountRef.current.clientHeight || window.innerHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(viewMode === '3d_raw' ? 0xffffff : 0xf1f5f9);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(40, width / height, 1, 3000);
    camera.position.set(130, 100, 150);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    rendererRef.current = renderer;

    mountRef.current.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, viewMode === '3d_raw' ? 1.2 : 0.9);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, viewMode === '3d_raw' ? 1.0 : 1.4);
    keyLight.position.set(150, 200, 130);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x93c5fd, 0.6);
    fillLight.position.set(-130, -80, -130);
    scene.add(fillLight);

    const topRimLight = new THREE.DirectionalLight(0xffffff, 0.5);
    topRimLight.position.set(0, 250, 0);
    scene.add(topRimLight);

    if (viewMode !== '3d_raw') {
      const grid = new THREE.GridHelper(300, 30, 0x64748b, 0xcbd5e1);
      grid.position.y = -35;
      scene.add(grid);
    }

    const modelGroup = new THREE.Group();
    scene.add(modelGroup);
    modelGroupRef.current = modelGroup;

    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!mountRef.current || !rendererRef.current || !cameraRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      cameraRef.current.aspect = w / h;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [viewMode]);

  // 2. Build Solid Meshes and Dimension Callouts in 3D Space
  useEffect(() => {
    if (!modelGroupRef.current || viewMode === 'drawing') return;

    while (modelGroupRef.current.children.length > 0) {
      const obj = modelGroupRef.current.children[0];
      modelGroupRef.current.remove(obj);
    }

    if (!hasGeometry) return;

    const isRaw = viewMode === '3d_raw';

    const addCadMesh = (mesh: THREE.Mesh, edgeColor: number = 0x0f172a) => {
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      modelGroupRef.current?.add(mesh);

      const edges = new THREE.EdgesGeometry(mesh.geometry, 18);
      const line = new THREE.LineSegments(
        edges,
        new THREE.LineBasicMaterial({ color: edgeColor, linewidth: isRaw ? 2.0 : 1.5 })
      );
      mesh.add(line);
    };

    const add3DDimensionCallout = (
      p1: THREE.Vector3,
      p2: THREE.Vector3,
      label: string,
      offset: THREE.Vector3 = new THREE.Vector3(0, 0, 0)
    ) => {
      if (!isRaw) return;

      const group = new THREE.Group();
      const start = p1.clone().add(offset);
      const end = p2.clone().add(offset);

      const extMat = new THREE.LineBasicMaterial({ color: 0x64748b, linewidth: 1 });
      const ext1 = new THREE.Line(new THREE.BufferGeometry().setFromPoints([p1, start]), extMat);
      const ext2 = new THREE.Line(new THREE.BufferGeometry().setFromPoints([p2, end]), extMat);
      group.add(ext1);
      group.add(ext2);

      const dimMat = new THREE.LineBasicMaterial({ color: 0x0f172a, linewidth: 1.5 });
      const dimLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints([start, end]), dimMat);
      group.add(dimLine);

      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 80;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 2;
        ctx.fillRect(10, 10, 236, 60);
        ctx.strokeRect(10, 10, 236, 60);

        ctx.fillStyle = '#0f172a';
        ctx.font = 'bold 36px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(label, 128, 40);
      }

      const texture = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({ map: texture, depthTest: false });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.scale.set(16, 5, 1);
      const midPoint = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
      sprite.position.copy(midPoint).add(new THREE.Vector3(0, 3, 0));
      group.add(sprite);

      modelGroupRef.current?.add(group);
    };

    const baseMat = isRaw
      ? new THREE.MeshBasicMaterial({ color: 0xffffff })
      : new THREE.MeshStandardMaterial({ color: 0xd8e1e8, metalness: 0.65, roughness: 0.28 });

    const sprocketMat = isRaw
      ? new THREE.MeshBasicMaterial({ color: 0xffffff })
      : new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.78, roughness: 0.32 });

    const boreMat = isRaw
      ? new THREE.MeshBasicMaterial({ color: 0xffffff })
      : new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.92, roughness: 0.2 });

    // 000. POWERED ROTARY CONVEYOR TURNTABLE (1:1 with User Turntable Screenshot)
    if (isTurntable) {
      const ttGroup = new THREE.Group();

      const blueFrameMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0x1d4ed8, metalness: 0.45, roughness: 0.35 }); // RAL 5005 Blue

      const yellowGuardMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0xeab308, metalness: 0.25, roughness: 0.4 }); // Warning Safety Yellow

      const rollerSteelMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.85, roughness: 0.2 }); // Ground Precision Steel

      const slewMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.9, roughness: 0.2 }); // Dark Slew Ring

      const footMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.8, roughness: 0.3 }); // Zinc Foot Pad

      const motorMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.75, roughness: 0.3 }); // Drive Motor

      const frameSize = 100; // 100mm scaled (1000mm full scale)
      const totalH = 55;

      // 1. Lower Stationary Base Frame (Square Tubular Base & 4 Corner Legs)
      // Bottom 4 perimeter square tubes
      const bTubeXGeo = new THREE.BoxGeometry(frameSize, 5, 5);
      const bTubeZGeo = new THREE.BoxGeometry(5, 5, frameSize - 10);

      const botTube1 = new THREE.Mesh(bTubeXGeo, blueFrameMat);
      botTube1.position.set(0, -totalH / 2 + 5, -frameSize / 2 + 2.5);
      ttGroup.add(botTube1);

      const botTube2 = new THREE.Mesh(bTubeXGeo, blueFrameMat);
      botTube2.position.set(0, -totalH / 2 + 5, frameSize / 2 - 2.5);
      ttGroup.add(botTube2);

      const botTube3 = new THREE.Mesh(bTubeZGeo, blueFrameMat);
      botTube3.position.set(-frameSize / 2 + 2.5, -totalH / 2 + 5, 0);
      ttGroup.add(botTube3);

      const botTube4 = new THREE.Mesh(bTubeZGeo, blueFrameMat);
      botTube4.position.set(frameSize / 2 - 2.5, -totalH / 2 + 5, 0);
      ttGroup.add(botTube4);

      // Mid Cross Member on base
      const midCross = new THREE.Mesh(new THREE.BoxGeometry(frameSize - 10, 5, 5), blueFrameMat);
      midCross.position.set(0, -totalH / 2 + 5, 0);
      ttGroup.add(midCross);

      // 4 Vertical Corner Legs with Gussets & Leveling Feet
      const legGeo = new THREE.BoxGeometry(6, 22, 6);
      const footGeo = new THREE.BoxGeometry(14, 2, 14);
      const footTabGeo = new THREE.BoxGeometry(20, 1.5, 8);

      const legPositions = [
        { x: -frameSize / 2 + 3, z: -frameSize / 2 + 3 },
        { x: frameSize / 2 - 3, z: -frameSize / 2 + 3 },
        { x: -frameSize / 2 + 3, z: frameSize / 2 - 3 },
        { x: frameSize / 2 - 3, z: frameSize / 2 - 3 }
      ];

      legPositions.forEach((pos) => {
        const leg = new THREE.Mesh(legGeo, blueFrameMat);
        leg.position.set(pos.x, -totalH / 2 + 16, pos.z);
        ttGroup.add(leg);

        // Foot Pad & Anchoring Tab
        const foot = new THREE.Mesh(footGeo, footMat);
        foot.position.set(pos.x, -totalH / 2 + 1, pos.z);
        ttGroup.add(foot);

        const footTab = new THREE.Mesh(footTabGeo, footMat);
        footTab.position.set(pos.x, -totalH / 2 + 1, pos.z);
        ttGroup.add(footTab);

        // Corner Gusset Plate
        const gussetGeo = new THREE.BoxGeometry(8, 8, 2);
        const gusset = new THREE.Mesh(gussetGeo, blueFrameMat);
        gusset.position.set(pos.x + (pos.x > 0 ? -4 : 4), -totalH / 2 + 10, pos.z);
        ttGroup.add(gusset);
      });

      // Upper Stationary Frame Ring Plate
      const statRing = new THREE.Mesh(new THREE.CylinderGeometry(28, 28, 4, 32), blueFrameMat);
      statRing.position.set(0, -totalH / 2 + 28, 0);
      ttGroup.add(statRing);

      // 2. Central Slewing Ring Bearing (Motorized Rotary Swivel)
      const slewBearing = new THREE.Mesh(new THREE.CylinderGeometry(24, 24, 6, 32), slewMat);
      slewBearing.position.set(0, -totalH / 2 + 33, 0);
      ttGroup.add(slewBearing);

      // 3. Rotating Upper Carriage Assembly (Mounted on top of slew bearing)
      const topCarriage = new THREE.Group();
      topCarriage.position.set(0, -totalH / 2 + 38, 0);

      // Upper blue carriage cross frame
      const topBeam1 = new THREE.Mesh(new THREE.BoxGeometry(frameSize, 6, 6), blueFrameMat);
      topBeam1.position.set(0, 0, -frameSize / 2 + 3);
      topCarriage.add(topBeam1);

      const topBeam2 = new THREE.Mesh(new THREE.BoxGeometry(frameSize, 6, 6), blueFrameMat);
      topBeam2.position.set(0, 0, frameSize / 2 - 3);
      topCarriage.add(topBeam2);

      // Two side C-channels with roller mounting notches
      const sideC1 = new THREE.Mesh(new THREE.BoxGeometry(6, 12, frameSize), blueFrameMat);
      sideC1.position.set(-frameSize / 2 + 3, 5, 0);
      topCarriage.add(sideC1);

      const sideC2 = new THREE.Mesh(new THREE.BoxGeometry(6, 12, frameSize), blueFrameMat);
      sideC2.position.set(frameSize / 2 - 3, 5, 0);
      topCarriage.add(sideC2);

      // 4. 8 Parallel Steel Conveyor Rollers
      const rollerCount = 8;
      for (let i = 0; i < rollerCount; i++) {
        const pz = -frameSize / 2 + 10 + i * ((frameSize - 20) / (rollerCount - 1));

        // Steel roller tube
        const rollerGeo = new THREE.CylinderGeometry(3.5, 3.5, frameSize - 14, 24);
        const roller = new THREE.Mesh(rollerGeo, rollerSteelMat);
        roller.rotation.z = Math.PI / 2;
        roller.position.set(0, 10, pz);
        topCarriage.add(roller);

        // Bearing mounts at ends
        const bMount1 = new THREE.Mesh(new THREE.BoxGeometry(5, 5, 5), blueFrameMat);
        bMount1.position.set(-frameSize / 2 + 7, 7, pz);
        topCarriage.add(bMount1);

        const bMount2 = new THREE.Mesh(new THREE.BoxGeometry(5, 5, 5), blueFrameMat);
        bMount2.position.set(frameSize / 2 - 7, 7, pz);
        topCarriage.add(bMount2);
      }

      // 5. Safety Warning Yellow Chain/Drive Guard Plate (as shown on top-left in screenshot)
      const guardGeo = new THREE.BoxGeometry(16, 4, 55);
      const yellowGuard = new THREE.Mesh(guardGeo, yellowGuardMat);
      yellowGuard.position.set(-frameSize / 2 + 8, 14, -frameSize / 2 + 32);
      topCarriage.add(yellowGuard);

      const guardBevelGeo = new THREE.BoxGeometry(16, 8, 4);
      const guardBevel = new THREE.Mesh(guardBevelGeo, yellowGuardMat);
      guardBevel.position.set(-frameSize / 2 + 8, 12, -frameSize / 2 + 5);
      topCarriage.add(guardBevel);

      // 6. Undermounted Rotary Drive Motor
      const motorGearbox = new THREE.Mesh(new THREE.BoxGeometry(16, 12, 14), motorMat);
      motorGearbox.position.set(frameSize / 2 - 16, -10, frameSize / 2 - 20);
      topCarriage.add(motorGearbox);

      const motorCyl = new THREE.Mesh(new THREE.CylinderGeometry(5.5, 5.5, 18, 20), motorMat);
      motorCyl.rotation.x = Math.PI / 2;
      motorCyl.position.set(frameSize / 2 - 16, -10, frameSize / 2 - 5);
      topCarriage.add(motorCyl);

      ttGroup.add(topCarriage);

      // Contours
      ttGroup.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          const edges = new THREE.EdgesGeometry(child.geometry, 18);
          const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x0f172a, linewidth: isRaw ? 2.0 : 1.5 }));
          child.add(line);
        }
      });

      modelGroupRef.current.add(ttGroup);

      if (isRaw) {
        add3DDimensionCallout(new THREE.Vector3(-frameSize / 2, 10, -frameSize / 2), new THREE.Vector3(frameSize / 2, 10, -frameSize / 2), '1000 mm (Bed Length)', new THREE.Vector3(0, 16, -14));
        add3DDimensionCallout(new THREE.Vector3(frameSize / 2, 10, -frameSize / 2), new THREE.Vector3(frameSize / 2, 10, frameSize / 2), '1000 mm (Width)', new THREE.Vector3(16, 10, 0));
        add3DDimensionCallout(new THREE.Vector3(-frameSize / 2 + 3, -totalH / 2 + 1, -frameSize / 2 + 3), new THREE.Vector3(-frameSize / 2 + 3, 10, -frameSize / 2 + 3), '550 mm (Height)', new THREE.Vector3(-16, 0, 0));
        add3DDimensionCallout(new THREE.Vector3(0, 10, -frameSize / 2 + 10), new THREE.Vector3(0, 10, frameSize / 2 - 10), '8x Ø60mm Rollers (120mm Pitch)', new THREE.Vector3(0, 14, 0));
        add3DDimensionCallout(new THREE.Vector3(-frameSize / 2 + 8, 14, -frameSize / 2 + 32), new THREE.Vector3(-frameSize / 2 + 8, 14, -frameSize / 2 + 60), 'Safety Yellow Guard (RAL 1021)', new THREE.Vector3(-14, 8, 0));
      }
    }
    // 00. POWERED ROLLER BED (PRB) CONVEYOR ASSEMBLY (1:1 with User Screenshot)
    else if (isPRBConveyor) {
      const prbGroup = new THREE.Group();

      const frameMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0x1d4ed8, metalness: 0.45, roughness: 0.35 }); // RAL 5005 Industrial Blue

      const rollerSteelMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.85, roughness: 0.25 }); // Dark Steel Roller Tube

      const collarMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0xf1f5f9, metalness: 0.2, roughness: 0.4 }); // White End Hubs

      const motorMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0x0f766e, metalness: 0.7, roughness: 0.3 }); // Geared Reducer Motor

      const footMat = isRaw
        ? new THREE.MeshBasicMaterial({ color: 0xffffff })
        : new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 }); // Galvanized Foot Plates

      const bedL = 220; // 3D scaled length
      const bedW = 60;  // 3D scaled width
      const legH = 40;  // 3D scaled leg elevation

      // 1. Dual Blue Longitudinal Side Rails (C-Channels)
      const railGeo = new THREE.BoxGeometry(bedL, 10, 4);
      const rail1 = new THREE.Mesh(railGeo, frameMat);
      rail1.position.set(0, 0, -bedW / 2);
      prbGroup.add(rail1);

      const rail2 = new THREE.Mesh(railGeo, frameMat);
      rail2.position.set(0, 0, bedW / 2);
      prbGroup.add(rail2);

      // Top lips on rails
      const lipGeo = new THREE.BoxGeometry(bedL, 2.5, 6);
      const lip1 = new THREE.Mesh(lipGeo, frameMat);
      lip1.position.set(0, 5, -bedW / 2 + 1);
      prbGroup.add(lip1);

      const lip2 = new THREE.Mesh(lipGeo, frameMat);
      lip2.position.set(0, 5, bedW / 2 - 1);
      prbGroup.add(lip2);

      // 2. Cross Tie Members
      const endBarGeo = new THREE.BoxGeometry(4, 8, bedW);
      const endBar1 = new THREE.Mesh(endBarGeo, frameMat);
      endBar1.position.set(-bedL / 2 + 2, -1, 0);
      prbGroup.add(endBar1);

      const endBar2 = new THREE.Mesh(endBarGeo, frameMat);
      endBar2.position.set(bedL / 2 - 2, -1, 0);
      prbGroup.add(endBar2);

      // Center Drive Mounting Bed Plate
      const centerPlateGeo = new THREE.BoxGeometry(32, 4, bedW - 4);
      const centerPlate = new THREE.Mesh(centerPlateGeo, frameMat);
      centerPlate.position.set(0, -6, 0);
      prbGroup.add(centerPlate);

      // 3. Four Support Legs with Leveling Base Feet Plates
      const legGeo = new THREE.BoxGeometry(6, legH, 6);
      const footGeo = new THREE.BoxGeometry(14, 2, 14);

      const legPositions = [
        { x: -bedL / 2 + 30, z: -bedW / 2 },
        { x: -bedL / 2 + 30, z: bedW / 2 },
        { x: bedL / 2 - 30, z: -bedW / 2 },
        { x: bedL / 2 - 30, z: bedW / 2 }
      ];

      legPositions.forEach((pos) => {
        const leg = new THREE.Mesh(legGeo, frameMat);
        leg.position.set(pos.x, -legH / 2 - 2, pos.z);
        prbGroup.add(leg);

        const foot = new THREE.Mesh(footGeo, footMat);
        foot.position.set(pos.x, -legH - 2, pos.z);
        prbGroup.add(foot);
      });

      // 4. Five Transverse Rollers with White Bearing Retainer Collars
      const rollerCount = 5;
      for (let i = 0; i < rollerCount; i++) {
        const posX = -bedL / 2 + 20 + i * ((bedL - 40) / (rollerCount - 1));

        // Dark Roller Tube
        const rollerTubeGeo = new THREE.CylinderGeometry(4.5, 4.5, bedW - 14, 24);
        const rollerTube = new THREE.Mesh(rollerTubeGeo, rollerSteelMat);
        rollerTube.rotation.x = Math.PI / 2;
        rollerTube.position.set(posX, 2, 0);
        prbGroup.add(rollerTube);

        // White Tapered Bearing End Collars
        const collarGeo = new THREE.CylinderGeometry(5.8, 4.5, 4, 20);
        const collarLeft = new THREE.Mesh(collarGeo, collarMat);
        collarLeft.rotation.x = Math.PI / 2;
        collarLeft.position.set(posX, 2, -bedW / 2 + 6);
        prbGroup.add(collarLeft);

        const collarRight = new THREE.Mesh(collarGeo, collarMat);
        collarRight.rotation.x = -Math.PI / 2;
        collarRight.position.set(posX, 2, bedW / 2 - 6);
        prbGroup.add(collarRight);

        // Center Pin
        const pinGeo = new THREE.CylinderGeometry(2, 2, bedW + 2, 16);
        const pin = new THREE.Mesh(pinGeo, footMat);
        pin.rotation.x = Math.PI / 2;
        pin.position.set(posX, 2, 0);
        prbGroup.add(pin);
      }

      // 5. Center Electric Motor & Reducer Gearbox
      const gearboxGeo = new THREE.BoxGeometry(18, 14, 12);
      const gearbox = new THREE.Mesh(gearboxGeo, motorMat);
      gearbox.position.set(-6, -14, 0);
      prbGroup.add(gearbox);

      const motorGeo = new THREE.CylinderGeometry(5, 5, 16, 24);
      const motor = new THREE.Mesh(motorGeo, motorMat);
      motor.rotation.x = Math.PI / 2;
      motor.position.set(-6, -14, 14);
      prbGroup.add(motor);

      // Contours
      prbGroup.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          const edges = new THREE.EdgesGeometry(child.geometry, 18);
          const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x0f172a, linewidth: isRaw ? 2.0 : 1.5 }));
          child.add(line);
        }
      });

      modelGroupRef.current.add(prbGroup);

      if (isRaw) {
        add3DDimensionCallout(new THREE.Vector3(-bedL / 2, 5, -bedW / 2), new THREE.Vector3(bedL / 2, 5, -bedW / 2), `${p.length_mm || 2000} mm (Length)`, new THREE.Vector3(0, 16, -12));
        add3DDimensionCallout(new THREE.Vector3(bedL / 2, 5, -bedW / 2), new THREE.Vector3(bedL / 2, 5, bedW / 2), `${p.width_mm || 450} mm (Width)`, new THREE.Vector3(14, 10, 0));
        add3DDimensionCallout(new THREE.Vector3(-bedL / 2 + 30, -legH - 2, -bedW / 2), new THREE.Vector3(-bedL / 2 + 30, 0, -bedW / 2), `${p.height_mm || 350} mm (Height)`, new THREE.Vector3(-14, 0, 0));
        add3DDimensionCallout(new THREE.Vector3(0, 2, -bedW / 2 + 6), new THREE.Vector3(0, 2, bedW / 2 - 6), `Ø ${p.roller_diameter_mm || 50} mm Rollers (${rollerCount}x)`, new THREE.Vector3(0, 14, 0));
      }
    }
    // 0. RIBBED MOUNTING ANGLE BRACKET
    else if (isBracket) {
      const bracketGroup = new THREE.Group();

      const baseShape = new THREE.Shape();
      baseShape.moveTo(-35, -45);
      baseShape.lineTo(35, -45);
      baseShape.lineTo(35, 10);
      baseShape.lineTo(20, 35);
      baseShape.lineTo(-20, 35);
      baseShape.lineTo(-35, 10);
      baseShape.closePath();

      const baseGeo = new THREE.ExtrudeGeometry(baseShape, { depth: 10, bevelEnabled: false });
      const baseMesh = new THREE.Mesh(baseGeo, baseMat);
      baseMesh.rotation.x = -Math.PI / 2;
      baseMesh.position.y = -10;
      bracketGroup.add(baseMesh);

      const wallGeo = new THREE.BoxGeometry(70, 55, 12);
      const wallMesh = new THREE.Mesh(wallGeo, baseMat);
      wallMesh.position.set(0, 17.5, -39);
      bracketGroup.add(wallMesh);

      const bossGeo = new THREE.CylinderGeometry(15, 15, 18, 36);
      const bossMesh = new THREE.Mesh(bossGeo, baseMat);
      bossMesh.position.set(0, 45, -39);
      bracketGroup.add(bossMesh);

      const topBoreGeo = new THREE.CylinderGeometry(7.5, 7.5, 22, 28);
      const topBoreMesh = new THREE.Mesh(topBoreGeo, boreMat);
      topBoreMesh.position.set(0, 45, -39);
      bracketGroup.add(topBoreMesh);

      const ribShape = new THREE.Shape();
      ribShape.moveTo(0, 0);
      ribShape.lineTo(0, 45);
      ribShape.lineTo(48, 0);
      ribShape.closePath();

      const ribGeo = new THREE.ExtrudeGeometry(ribShape, { depth: 10, bevelEnabled: false });
      const ribMesh = new THREE.Mesh(ribGeo, baseMat);
      ribMesh.position.set(-5, 0, -33);
      bracketGroup.add(ribMesh);

      const baseHole1 = new THREE.Mesh(new THREE.CylinderGeometry(5, 5, 14, 20), boreMat);
      baseHole1.position.set(-18, -5, 0);
      bracketGroup.add(baseHole1);

      const baseHole2 = new THREE.Mesh(new THREE.CylinderGeometry(5, 5, 14, 20), boreMat);
      baseHole2.position.set(18, -5, 0);
      bracketGroup.add(baseHole2);

      bracketGroup.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          const edges = new THREE.EdgesGeometry(child.geometry, 18);
          const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x0f172a, linewidth: isRaw ? 2.0 : 1.5 }));
          child.add(line);
        }
      });

      modelGroupRef.current.add(bracketGroup);

      if (isRaw) {
        add3DDimensionCallout(new THREE.Vector3(-19, 54, -39), new THREE.Vector3(19, 54, -39), '38', new THREE.Vector3(0, 10, 0));
        add3DDimensionCallout(new THREE.Vector3(35, 45, -45), new THREE.Vector3(35, 45, -33), '19', new THREE.Vector3(12, 0, 0));
        add3DDimensionCallout(new THREE.Vector3(-5, 25, -15), new THREE.Vector3(5, 25, -15), '10', new THREE.Vector3(0, 8, 8));
        add3DDimensionCallout(new THREE.Vector3(-35, -10, -45), new THREE.Vector3(35, -10, -45), '70', new THREE.Vector3(0, 0, -14));
        add3DDimensionCallout(new THREE.Vector3(-35, -10, -45), new THREE.Vector3(-35, 0, -45), '10', new THREE.Vector3(-12, 0, 0));
        add3DDimensionCallout(new THREE.Vector3(-18, 0, 0), new THREE.Vector3(18, 0, 0), '36 (Hole Span)', new THREE.Vector3(0, 10, 0));
        add3DDimensionCallout(new THREE.Vector3(35, 0, -45), new THREE.Vector3(35, 0, 10), '55', new THREE.Vector3(14, 0, 0));
        add3DDimensionCallout(new THREE.Vector3(0, -10, 35), new THREE.Vector3(0, 45, -39), '67', new THREE.Vector3(25, 0, 0));
      }
    }
    // 1. SPROCKET GEAR
    else if (isSprocket) {
      const outerR = Math.min(Math.max(dia / 2, 22), 48);
      const teeth = teethCount || 14;
      const thk = Math.min(Math.max(Number(p.thickness_mm) || 8, 4), 14);
      const boreR = Math.max(outerR * 0.25, 4);

      const discGeo = new THREE.CylinderGeometry(outerR * 0.85, outerR * 0.85, thk, 36);
      const discMesh = new THREE.Mesh(discGeo, sprocketMat);
      addCadMesh(discMesh);

      const hubGeo = new THREE.CylinderGeometry(outerR * 0.42, outerR * 0.42, thk + 4, 28);
      const hubMesh = new THREE.Mesh(hubGeo, sprocketMat);
      addCadMesh(hubMesh);

      const boreGeo = new THREE.CylinderGeometry(boreR, boreR, thk + 6, 24);
      const boreMesh = new THREE.Mesh(boreGeo, boreMat);
      addCadMesh(boreMesh);

      for (let i = 0; i < teeth; i++) {
        const angle = (i / teeth) * Math.PI * 2;
        const toothWidth = (Math.PI * outerR) / (teeth * 1.4);
        const toothHeight = outerR * 0.24;

        const toothGeo = new THREE.BoxGeometry(toothWidth, thk, toothHeight);
        const toothMesh = new THREE.Mesh(toothGeo, sprocketMat);

        const dist = outerR * 0.92;
        toothMesh.position.x = Math.cos(angle) * dist;
        toothMesh.position.z = Math.sin(angle) * dist;
        toothMesh.rotation.y = -angle;

        addCadMesh(toothMesh);
      }

      if (isRaw) {
        add3DDimensionCallout(new THREE.Vector3(-outerR, thk / 2 + 5, 0), new THREE.Vector3(outerR, thk / 2 + 5, 0), `Ø ${dia} mm (OD)`, new THREE.Vector3(0, 10, 0));
        add3DDimensionCallout(new THREE.Vector3(-boreR, -thk / 2 - 5, 0), new THREE.Vector3(boreR, -thk / 2 - 5, 0), `Ø ${boreDia} BORE`, new THREE.Vector3(0, -10, 0));
        add3DDimensionCallout(new THREE.Vector3(outerR, -thk / 2, 0), new THREE.Vector3(outerR, thk / 2, 0), `${thk} mm (Thk)`, new THREE.Vector3(12, 0, 0));
      }
    }
    // 2. CONVEYOR ROLLER
    else if (isRoller) {
      const radius = Math.min(Math.max(dia / 2, 8), 35);
      const length = Math.min(Math.max(cylH / 4, 80), 220);

      const tubeGeo = new THREE.CylinderGeometry(radius, radius, length, 36);
      const tubeMesh = new THREE.Mesh(tubeGeo, baseMat);
      tubeMesh.rotation.z = Math.PI / 2;
      addCadMesh(tubeMesh);

      const leftCapGeo = new THREE.CylinderGeometry(radius + 0.8, radius + 0.8, 4, 36);
      const leftCapMesh = new THREE.Mesh(leftCapGeo, boreMat);
      leftCapMesh.rotation.z = Math.PI / 2;
      leftCapMesh.position.x = -length / 2;
      addCadMesh(leftCapMesh);

      const rightCapGeo = new THREE.CylinderGeometry(radius + 0.8, radius + 0.8, 4, 36);
      const rightCapMesh = new THREE.Mesh(rightCapGeo, boreMat);
      rightCapMesh.rotation.z = Math.PI / 2;
      rightCapMesh.position.x = length / 2;
      addCadMesh(rightCapMesh);

      const shaftRadius = Math.max(radius * 0.28, 4);
      const shaftGeo = new THREE.CylinderGeometry(shaftRadius, shaftRadius, length + 50, 24);
      const shaftMesh = new THREE.Mesh(shaftGeo, boreMat);
      shaftMesh.rotation.z = Math.PI / 2;
      addCadMesh(shaftMesh);

      if (isRaw) {
        add3DDimensionCallout(new THREE.Vector3(-length / 2, radius + 8, 0), new THREE.Vector3(length / 2, radius + 8, 0), `Length ${cylH} mm`, new THREE.Vector3(0, 10, 0));
        add3DDimensionCallout(new THREE.Vector3(0, -radius, 0), new THREE.Vector3(0, radius, 0), `Ø ${dia} mm`, new THREE.Vector3(0, 0, radius + 10));
      }
    }
    // 3. PRISMATIC BOX WITH DRILLED HOLE
    else if (isBoxWithHole) {
      const boxL = Math.min(Math.max(l * 2.5, 20), 75);
      const boxW = Math.min(Math.max(w * 2.5, 20), 75);
      const boxH = Math.min(Math.max(h * 2.5, 20), 75);
      const hDia = Math.min(Math.max((Number(p.hole_diameter_mm) || 2) * 2.5, 4), boxL * 0.8);

      const boxGeo = new THREE.BoxGeometry(boxL, boxH, boxW);
      const boxMesh = new THREE.Mesh(boxGeo, baseMat);
      addCadMesh(boxMesh);

      // Centered Drill Hole Subtractive representation
      const holeGeo = new THREE.CylinderGeometry(hDia / 2, hDia / 2, boxH + 2, 28);
      const holeMesh = new THREE.Mesh(holeGeo, boreMat);
      addCadMesh(holeMesh, 0x2563eb);

      if (isRaw) {
        add3DDimensionCallout(new THREE.Vector3(-boxL / 2, -boxH / 2, boxW / 2), new THREE.Vector3(boxL / 2, -boxH / 2, boxW / 2), `${l} mm (X)`, new THREE.Vector3(0, -10, 10));
        add3DDimensionCallout(new THREE.Vector3(boxL / 2, -boxH / 2, boxW / 2), new THREE.Vector3(boxL / 2, boxH / 2, boxW / 2), `${h} mm (Z)`, new THREE.Vector3(12, 0, 10));
        add3DDimensionCallout(new THREE.Vector3(0, boxH / 2 + 2, 0), new THREE.Vector3(hDia / 2, boxH / 2 + 2, 0), `Ø ${p.hole_diameter_mm || 2} mm Drill`, new THREE.Vector3(0, 8, 8));
      }
    }
    // 4. SPATIAL COMPOUND SHAPES (e.g. 15mm cube on right side of 10mm cube)
    else if (isCompound || p.features) {
      const boxL = Math.min(Math.max(l * 2.5, 20), 75);
      const boxW = Math.min(Math.max(w * 2.5, 20), 75);
      const boxH = Math.min(Math.max(h * 2.5, 20), 75);

      const baseGeo = new THREE.BoxGeometry(boxL, boxH, boxW);
      const baseMesh = new THREE.Mesh(baseGeo, baseMat);
      addCadMesh(baseMesh);

      // Render secondary side/top features
      const features = p.features || (p.top_feature ? [{ ...p.top_feature, relation: 'top' }] : []);
      features.forEach((feat: any) => {
        const fL = Math.min(Math.max((Number(feat.length_mm) || 15) * 2.5, 15), 90);
        const fW = Math.min(Math.max((Number(feat.width_mm) || 15) * 2.5, 15), 90);
        const fH = Math.min(Math.max((Number(feat.height_mm) || 15) * 2.5, 15), 90);
        const offX = (Number(feat.offset_x_mm) || (boxL / 2 + fL / 2)) * (boxL / l);
        const offY = (Number(feat.offset_y_mm) || 0) * (boxW / w);
        const offZ = (Number(feat.offset_z_mm) || (feat.relation === 'top' ? (boxH / 2 + fH / 2) : 0)) * (boxH / h);

        const featGeo = feat.type === 'cylinder'
          ? new THREE.CylinderGeometry(fL / 2, fL / 2, fH, 32)
          : new THREE.BoxGeometry(fL, fH, fW);
        const featMesh = new THREE.Mesh(featGeo, baseMat);
        featMesh.position.set(offX, offZ, offY);
        addCadMesh(featMesh);

        if (isRaw) {
          add3DDimensionCallout(new THREE.Vector3(offX - fL / 2, offZ - fH / 2, offY + fW / 2), new THREE.Vector3(offX + fL / 2, offZ - fH / 2, offY + fW / 2), `${feat.length_mm || 15} mm`, new THREE.Vector3(0, -8, 8));
        }
      });

      if (isRaw) {
        add3DDimensionCallout(new THREE.Vector3(-boxL / 2, -boxH / 2, boxW / 2), new THREE.Vector3(boxL / 2, -boxH / 2, boxW / 2), `${l} mm (Base)`, new THREE.Vector3(0, -10, 10));
      }
    }
    // 5. STANDARD PRISMATIC SOLID BOX
    else {
      const boxL = Math.min(Math.max(l * 2.5, 20), 75);
      const boxW = Math.min(Math.max(w * 2.5, 20), 75);
      const boxH = Math.min(Math.max(h * 2.5, 20), 75);

      const boxGeo = new THREE.BoxGeometry(boxL, boxH, boxW);
      const boxMesh = new THREE.Mesh(boxGeo, baseMat);
      addCadMesh(boxMesh);

      if (isRaw) {
        add3DDimensionCallout(new THREE.Vector3(-boxL / 2, -boxH / 2, boxW / 2), new THREE.Vector3(boxL / 2, -boxH / 2, boxW / 2), `${l} mm (X)`, new THREE.Vector3(0, -10, 10));
        add3DDimensionCallout(new THREE.Vector3(boxL / 2, -boxH / 2, boxW / 2), new THREE.Vector3(boxL / 2, boxH / 2, boxW / 2), `${h} mm (Z)`, new THREE.Vector3(12, 0, 10));
        add3DDimensionCallout(new THREE.Vector3(boxL / 2, boxH / 2, -boxW / 2), new THREE.Vector3(boxL / 2, boxH / 2, boxW / 2), `${w} mm (Y)`, new THREE.Vector3(12, 10, 0));
      }
    }
  }, [tool, parameters, lastPrompt, isBracket, isRoller, isSprocket, isBoxWithHole, isCone, isRhombus, isCompound, isCylinder, viewMode]);

  // Mouse Interaction Handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    isDraggingRef.current = true;
    prevMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current || !modelGroupRef.current) return;
    const deltaX = e.clientX - prevMousePosRef.current.x;
    const deltaY = e.clientY - prevMousePosRef.current.y;

    modelGroupRef.current.rotation.y += deltaX * 0.01;
    modelGroupRef.current.rotation.x += deltaY * 0.01;

    setViewCubeRot({
      x: (modelGroupRef.current.rotation.x * 180) / Math.PI - 25,
      y: (modelGroupRef.current.rotation.y * 180) / Math.PI + 45
    });

    prevMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const handleWheel = (e: React.WheelEvent) => {
    if (!cameraRef.current) return;
    cameraRef.current.position.multiplyScalar(e.deltaY > 0 ? 1.08 : 0.92);
  };

  const setCameraPreset = (preset: 'iso' | 'top' | 'front' | 'right' | 'back' | 'left' | 'bottom') => {
    if (!cameraRef.current || !modelGroupRef.current) return;
    setActivePreset(preset);
    modelGroupRef.current.rotation.set(0, 0, 0);

    if (preset === 'iso') {
      cameraRef.current.position.set(130, 100, 150);
      setViewCubeRot({ x: -25, y: 45 });
    } else if (preset === 'top') {
      cameraRef.current.position.set(0, 220, 0);
      setViewCubeRot({ x: -90, y: 0 });
    } else if (preset === 'front') {
      cameraRef.current.position.set(0, 0, 220);
      setViewCubeRot({ x: 0, y: 0 });
    } else if (preset === 'right') {
      cameraRef.current.position.set(220, 0, 0);
      setViewCubeRot({ x: 0, y: -90 });
    } else if (preset === 'back') {
      cameraRef.current.position.set(0, 0, -220);
      setViewCubeRot({ x: 0, y: 180 });
    } else if (preset === 'left') {
      cameraRef.current.position.set(-220, 0, 0);
      setViewCubeRot({ x: 0, y: 90 });
    } else if (preset === 'bottom') {
      cameraRef.current.position.set(0, -220, 0);
      setViewCubeRot({ x: 90, y: 0 });
    }
    cameraRef.current.lookAt(0, 0, 0);
  };

  return (
    <div className="flex-1 h-screen w-full bg-[#f8fafc] flex flex-col relative select-none overflow-hidden font-sans">
      {/* Top Navigation & 3-Way Mode Switcher Header Bar */}
      <div className="h-14 border-b border-slate-200 px-6 flex items-center justify-between bg-white/95 backdrop-blur-md z-20 shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-sm shadow-emerald-500/50" />
          <span className="text-xs font-bold text-slate-800 tracking-wider font-mono uppercase flex items-center gap-2">
            <span>Autodesk Inventor 2026</span>
            <span className="text-slate-400">/</span>
            <span className="text-blue-600 font-bold">
              {viewMode === 'design'
                ? '3D Solid Model (Design)'
                : viewMode === '3d_raw'
                ? '3D Raw Drawing (Rotatable Dimensions)'
                : '2D Technical Blueprint (Sheet)'}
            </span>
          </span>
        </div>

        {/* 3-WAY SEGMENTED CONTROL: Design | 3D Raw | Drawing */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-inner">
          <button
            onClick={() => setViewMode('design')}
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
              viewMode === 'design'
                ? 'bg-white text-blue-700 shadow-sm border border-slate-200/80 font-extrabold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Design</span>
          </button>

          <button
            onClick={() => setViewMode('3d_raw')}
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
              viewMode === '3d_raw'
                ? 'bg-white text-blue-700 shadow-sm border border-slate-200/80 font-extrabold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Ruler className="w-3.5 h-3.5" />
            <span>3D Raw</span>
          </button>

          <button
            onClick={() => setViewMode('drawing')}
            className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
              viewMode === 'drawing'
                ? 'bg-white text-blue-700 shadow-sm border border-slate-200/80 font-extrabold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <PenTool className="w-3.5 h-3.5" />
            <span>Drawing</span>
          </button>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          {viewMode === 'drawing' && (
            <button
              onClick={() => window.print()}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-bold rounded-lg shadow-xs transition-all font-mono"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Sheet</span>
            </button>
          )}

          <a
            href={`http://192.168.11.86:8005/api/export/step?length=${l}&width=${w}&height=${h}`}
            download
            className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg shadow-sm transition-all font-mono"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export .STEP</span>
          </a>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 3D WEBGL VIEWPORT (Active for both 'design' and '3d_raw' modes)            */}
      {/* ========================================================================= */}
      {viewMode !== 'drawing' && (
        <div
          ref={mountRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onWheel={handleWheel}
          className={`flex-1 w-full h-full relative cursor-grab active:cursor-grabbing overflow-hidden ${
            viewMode === '3d_raw' ? 'bg-white' : 'bg-gradient-to-b from-[#f8fafc] via-[#f1f5f9] to-[#e2e8f0]'
          }`}
        >
          {/* Blank Screen State when no drawing active */}
          {!hasGeometry && (
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none select-none z-20">
              <div className="bg-slate-900/85 backdrop-blur-md border border-slate-800/90 rounded-2xl p-8 max-w-md text-center shadow-2xl">
                <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto mb-4">
                  <Box className="w-7 h-7 text-amber-400 animate-pulse" />
                </div>
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-widest font-mono">
                  CAD Workspace Blank
                </h3>
                <p className="text-xs text-slate-400 mt-2.5 leading-relaxed font-sans">
                  No active drawing on screen. Enter an engineering prompt below to construct and view 3D parametric geometry.
                </p>
                <div className="mt-5 pt-3.5 border-t border-slate-800/80 flex items-center justify-center space-x-2 text-[11px] text-slate-500 font-mono">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span>Autodesk Inventor Adapter: Standby</span>
                </div>
              </div>
            </div>
          )}

          {/* TOP-LEFT: Engineering Specifications Card */}
          {hasGeometry && (
            <div className="absolute top-6 left-6 z-30 pointer-events-auto bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-xl p-4 shadow-xl max-w-sm w-80 text-xs font-sans text-slate-800 animate-fadeIn">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-2.5">
                <div className="flex items-center space-x-2">
                  <Box className="w-4 h-4 text-blue-600" />
                  <span className="font-bold text-slate-900 tracking-tight text-xs font-mono">{componentTitle}</span>
                </div>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {viewMode === '3d_raw' ? '3D RAW' : '3D SOLID'}
                </span>
              </div>

              <div className="space-y-2 font-mono text-[11px]">
                <div className="bg-slate-50/80 rounded-lg p-2.5 border border-slate-100 space-y-1.5">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Model Dimensions</div>
                  {isBracket ? (
                    <>
                      <div className="flex justify-between text-slate-700"><span>Width × Length:</span><strong className="text-slate-900">70 × 80 mm</strong></div>
                      <div className="flex justify-between text-slate-700"><span>Wall Height (Z):</span><strong className="text-slate-900">55 mm</strong></div>
                      <div className="flex justify-between text-slate-700"><span>Rib Thickness:</span><strong className="text-slate-900">10 mm</strong></div>
                      <div className="flex justify-between text-slate-700"><span>Cylinder Bore:</span><strong className="text-blue-600">Ø 15 mm</strong></div>
                    </>
                  ) : isSprocket ? (
                    <>
                      <div className="flex justify-between text-slate-700"><span>Tip Diameter (OD):</span><strong className="text-slate-900">Ø {dia} mm</strong></div>
                      <div className="flex justify-between text-slate-700"><span>Teeth Count:</span><strong className="text-blue-600">{teethCount} Teeth</strong></div>
                      <div className="flex justify-between text-slate-700"><span>Shaft Bore:</span><strong className="text-slate-900">Ø {boreDia} mm</strong></div>
                      <div className="flex justify-between text-slate-700"><span>Face Thickness:</span><strong className="text-slate-900">{h || 8} mm</strong></div>
                    </>
                  ) : (
                    <>
                      <div className="flex justify-between text-slate-700"><span>Length (X):</span><strong className="text-slate-900">{l} mm</strong></div>
                      <div className="flex justify-between text-slate-700"><span>Width (Y):</span><strong className="text-slate-900">{w} mm</strong></div>
                      <div className="flex justify-between text-slate-700"><span>Height (Z):</span><strong className="text-slate-900">{h} mm</strong></div>
                    </>
                  )}
                </div>

                <div className="bg-slate-50/80 rounded-lg p-2.5 border border-slate-100 space-y-1 text-[10px]">
                  <div className="text-slate-700 font-sans font-medium text-[11px] text-slate-900">{materialName}</div>
                  <div className="flex justify-between pt-1 border-t border-slate-200/50 text-slate-500">
                    <span>Est. Volume:</span><span className="font-bold text-slate-800 font-mono">{volumeCm3} cm³</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Autodesk Inventor Interactive 3D ViewCube with Home Icon POSITIONED BELOW (Top-Right) */}
          <div className="absolute top-6 right-6 z-30 pointer-events-auto flex flex-col items-center space-y-2.5">
            {/* ViewCube Body */}
            <div
              className="w-16 h-16 relative"
              style={{
                perspective: '400px',
                perspectiveOrigin: '50% 50%'
              }}
            >
              <div
                className="w-full h-full relative transition-transform duration-150 ease-out"
                style={{
                  transformStyle: 'preserve-3d',
                  transform: `rotateX(${viewCubeRot.x}deg) rotateY(${viewCubeRot.y}deg)`
                }}
              >
                <button onClick={() => setCameraPreset('top')} className={`absolute inset-0 bg-[#e2e8f0] hover:bg-blue-600 hover:text-white border border-slate-400 font-mono font-bold text-[9px] flex items-center justify-center shadow-xs ${activePreset === 'top' ? 'bg-blue-600 text-white' : 'text-slate-800'}`} style={{ transform: 'rotateX(90deg) translateZ(32px)' }}>TOP</button>
                <button onClick={() => setCameraPreset('front')} className={`absolute inset-0 bg-[#f8fafc] hover:bg-blue-600 hover:text-white border border-slate-400 font-mono font-bold text-[9px] flex items-center justify-center shadow-xs ${activePreset === 'front' ? 'bg-blue-600 text-white' : 'text-slate-800'}`} style={{ transform: 'translateZ(32px)' }}>FRONT</button>
                <button onClick={() => setCameraPreset('right')} className={`absolute inset-0 bg-[#cbd5e1] hover:bg-blue-600 hover:text-white border border-slate-400 font-mono font-bold text-[9px] flex items-center justify-center shadow-xs ${activePreset === 'right' ? 'bg-blue-600 text-white' : 'text-slate-800'}`} style={{ transform: 'rotateY(90deg) translateZ(32px)' }}>RIGHT</button>
                <button onClick={() => setCameraPreset('back')} className="absolute inset-0 bg-[#cbd5e1] hover:bg-blue-600 hover:text-white text-slate-800 border border-slate-400 font-mono font-bold text-[9px] flex items-center justify-center shadow-xs" style={{ transform: 'rotateY(180deg) translateZ(32px)' }}>BACK</button>
                <button onClick={() => setCameraPreset('left')} className="absolute inset-0 bg-[#f8fafc] hover:bg-blue-600 hover:text-white text-slate-800 border border-slate-400 font-mono font-bold text-[9px] flex items-center justify-center shadow-xs" style={{ transform: 'rotateY(-90deg) translateZ(32px)' }}>LEFT</button>
                <button onClick={() => setCameraPreset('bottom')} className="absolute inset-0 bg-[#94a3b8] hover:bg-blue-600 hover:text-white text-slate-900 border border-slate-400 font-mono font-bold text-[9px] flex items-center justify-center shadow-xs" style={{ transform: 'rotateX(-90deg) translateZ(32px)' }}>BOTTOM</button>
              </div>
            </div>

            {/* Home Button placed cleanly BELOW the ViewCube with authentic Home Icon */}
            <button
              onClick={() => setCameraPreset('iso')}
              className="w-7 h-7 rounded-lg bg-white/95 hover:bg-blue-600 hover:text-white border border-slate-300 text-slate-700 flex items-center justify-center shadow-md transition-all hover:scale-105"
              title="Home View (Isometric)"
            >
              <Home className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Coordinate Triad */}
          <div className="absolute bottom-6 left-6 z-30 pointer-events-none select-none">
            {(() => {
              const radX = (viewCubeRot.x * Math.PI) / 180;
              const radY = (viewCubeRot.y * Math.PI) / 180;
              const cx = 50, cy = 60, L = 36;
              const pX = { x: cx + L * Math.cos(radY), y: cy - L * Math.sin(radX) * Math.sin(radY) };
              const pY = { x: cx, y: cy - L * Math.cos(radX) };
              const pZ = { x: cx - L * Math.sin(radY), y: cy - L * Math.sin(radX) * Math.cos(radY) };
              const getArrow = (fx: number, fy: number, tx: number, ty: number) => {
                const a = Math.atan2(ty - fy, tx - fx);
                return `${tx},${ty} ${tx - 8 * Math.cos(a - Math.PI / 6)},${ty - 8 * Math.sin(a - Math.PI / 6)} ${tx - 8 * Math.cos(a + Math.PI / 6)},${ty - 8 * Math.sin(a + Math.PI / 6)}`;
              };
              return (
                <svg width="110" height="110" viewBox="0 0 110 110">
                  <line x1={cx} y1={cy} x2={pX.x} y2={pX.y} stroke="#dc2626" strokeWidth="2.5" strokeLinecap="round" />
                  <polygon points={getArrow(cx, cy, pX.x, pX.y)} fill="#dc2626" />
                  <text x={pX.x + 6} y={pX.y + 4} fill="#dc2626" fontSize="12" fontWeight="bold">X</text>
                  <line x1={cx} y1={cy} x2={pZ.x} y2={pZ.y} stroke="#2563eb" strokeWidth="2.5" strokeLinecap="round" />
                  <polygon points={getArrow(cx, cy, pZ.x, pZ.y)} fill="#2563eb" />
                  <text x={pZ.x + 6} y={pZ.y + 4} fill="#2563eb" fontSize="12" fontWeight="bold">Z</text>
                  <line x1={cx} y1={cy} x2={pY.x} y2={pY.y} stroke="#16a34a" strokeWidth="2.5" strokeLinecap="round" />
                  <polygon points={getArrow(cx, cy, pY.x, pY.y)} fill="#16a34a" />
                  <text x={pY.x - 4} y={pY.y - 6} fill="#16a34a" fontSize="12" fontWeight="bold">Y</text>
                  <circle cx={cx} cy={cy} r="2.5" fill="#334155" />
                </svg>
              );
            })()}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 2D TECHNICAL BLUEPRINT DRAWING SHEET (Active for 'drawing' mode)           */}
      {/* ========================================================================= */}
      {viewMode === 'drawing' && (
        <div className="flex-1 w-full h-full relative overflow-auto bg-[#e5e7eb] flex items-center justify-center p-8">
          <div className="w-[880px] h-[620px] bg-white border-2 border-slate-800 shadow-2xl relative p-6 flex flex-col justify-between select-text print:w-full print:h-full print:shadow-none">
            
            <div className="absolute top-1 left-1/4 text-[9px] font-mono text-slate-400">1</div>
            <div className="absolute top-1 left-1/2 text-[9px] font-mono text-slate-400">2</div>
            <div className="absolute top-1 left-3/4 text-[9px] font-mono text-slate-400">3</div>
            <div className="absolute left-1 top-1/3 text-[9px] font-mono text-slate-400">A</div>
            <div className="absolute left-1 top-2/3 text-[9px] font-mono text-slate-400">B</div>

            <div className="absolute inset-3 border border-slate-800 pointer-events-none" />

            <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 pb-1 border-b border-slate-200">
              <span className="font-bold text-slate-800 tracking-wider uppercase">AUTODESK INVENTOR 2026 — TECHNICAL DRAWING SHEET</span>
              <span>STANDARD: ISO 128 / ASME Y14.5M</span>
            </div>

            <div className="flex-1 w-full flex items-center justify-center relative my-2">
              {isTurntable ? (
                <svg viewBox="0 0 640 420" className="w-[580px] h-[380px]">
                  <defs>
                    <marker id="dimArrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                    <marker id="dimArrowStart" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                  </defs>

                  {/* Base Frame 1000x1000 */}
                  <rect x="140" y="100" width="280" height="280" fill="#f8fafc" stroke="#1d4ed8" strokeWidth="2.5" />
                  
                  {/* Slew Bearing Ring */}
                  <circle cx="280" cy="240" r="95" fill="none" stroke="#334155" strokeWidth="2" strokeDasharray="6,3" />
                  <circle cx="280" cy="240" r="75" fill="#e2e8f0" stroke="#0f172a" strokeWidth="1.5" />
                  <circle cx="280" cy="240" r="20" fill="#94a3b8" stroke="#0f172a" strokeWidth="1" />

                  {/* 4 Corner Legs */}
                  <rect x="135" y="95" width="16" height="16" fill="#1d4ed8" stroke="#0f172a" strokeWidth="1.5" />
                  <rect x="409" y="95" width="16" height="16" fill="#1d4ed8" stroke="#0f172a" strokeWidth="1.5" />
                  <rect x="135" y="369" width="16" height="16" fill="#1d4ed8" stroke="#0f172a" strokeWidth="1.5" />
                  <rect x="409" y="369" width="16" height="16" fill="#1d4ed8" stroke="#0f172a" strokeWidth="1.5" />

                  {/* 8 Rollers */}
                  {[125, 158, 191, 224, 257, 290, 323, 355].map((ry, idx) => (
                    <g key={idx}>
                      <rect x="148" y={ry - 5} width="264" height="10" rx="3" fill="#cbd5e1" stroke="#0f172a" strokeWidth="1.2" />
                      <line x1="140" y1={ry} x2="420" y2={ry} stroke="#64748b" strokeWidth="0.8" strokeDasharray="4,2" />
                    </g>
                  ))}

                  {/* Warning Yellow Safety Chain Guard */}
                  <polygon points="140,100 240,100 240,135 140,155" fill="#facc15" stroke="#ca8a04" strokeWidth="2" />
                  <text x="148" y="122" fill="#854d0e" fontSize="9" fontWeight="bold" fontFamily="monospace">SAFETY GUARD</text>

                  {/* Slewing Motor */}
                  <rect x="360" y="300" width="50" height="35" rx="3" fill="#475569" stroke="#0f172a" strokeWidth="1.5" />
                  <text x="365" y="322" fill="#f8fafc" fontSize="8" fontWeight="bold" fontFamily="monospace">0.55kW</text>

                  {/* Dimension Lines */}
                  {/* Bed Width 1000mm */}
                  <line x1="140" y1="75" x2="140" y2="95" stroke="#64748b" strokeWidth="0.9" />
                  <line x1="420" y1="75" x2="420" y2="95" stroke="#64748b" strokeWidth="0.9" />
                  <line x1="145" y1="80" x2="415" y2="80" stroke="#0f172a" strokeWidth="1.2" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="245" y="74" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">1000 mm (Width)</text>

                  {/* Bed Length 1000mm */}
                  <line x1="425" y1="100" x2="455" y2="100" stroke="#64748b" strokeWidth="0.9" />
                  <line x1="425" y1="380" x2="455" y2="380" stroke="#64748b" strokeWidth="0.9" />
                  <line x1="450" y1="105" x2="450" y2="375" stroke="#0f172a" strokeWidth="1.2" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="458" y="245" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">1000 mm</text>

                  {/* Slew Bearing Callout */}
                  <line x1="280" y1="240" x2="190" y2="320" stroke="#0f172a" strokeWidth="1.2" markerStart="url(#dimArrowStart)" />
                  <text x="180" y="340" fill="#0f172a" fontSize="10" fontWeight="bold" fontFamily="monospace">Ø450 mm Slew Ring</text>

                  <text x="40" y="45" fill="#1d4ed8" fontSize="13" fontWeight="bold" fontFamily="monospace">POWERED ROTARY CONVEYOR TURNTABLE ASSEMBLY</text>
                  <text x="40" y="62" fill="#475569" fontSize="10" fontFamily="monospace">8x Ø60mm ROLLERS • MOTORIZED 90°/180°/360° SLEWING RING • RAL 1021 YELLOW GUARD</text>
                </svg>
              ) : isPRBConveyor ? (
                <svg viewBox="0 0 640 420" className="w-[580px] h-[380px]">
                  <defs>
                    <marker id="dimArrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                    <marker id="dimArrowStart" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                  </defs>

                  <rect x="60" y="160" width="520" height="20" fill="#dbeafe" stroke="#1d4ed8" strokeWidth="2" />
                  <rect x="60" y="240" width="520" height="20" fill="#dbeafe" stroke="#1d4ed8" strokeWidth="2" />

                  <line x1="60" y1="160" x2="60" y2="260" stroke="#1d4ed8" strokeWidth="3" />
                  <line x1="580" y1="160" x2="580" y2="260" stroke="#1d4ed8" strokeWidth="3" />
                  <rect x="290" y="170" width="60" height="80" fill="#e2e8f0" stroke="#0f172a" strokeWidth="1.5" />

                  <line x1="120" y1="260" x2="120" y2="340" stroke="#1d4ed8" strokeWidth="4" />
                  <line x1="105" y1="340" x2="135" y2="340" stroke="#0f172a" strokeWidth="3" />
                  
                  <line x1="520" y1="260" x2="520" y2="340" stroke="#1d4ed8" strokeWidth="4" />
                  <line x1="505" y1="340" x2="535" y2="340" stroke="#0f172a" strokeWidth="3" />

                  {[90, 195, 320, 445, 550].map((rx, idx) => (
                    <g key={idx}>
                      <rect x={rx - 6} y="165" width="12" height="90" rx="3" fill="#334155" stroke="#0f172a" strokeWidth="1.5" />
                      <circle cx={rx} cy="165" r="5" fill="#f8fafc" stroke="#0f172a" strokeWidth="1" />
                      <circle cx={rx} cy="255" r="5" fill="#f8fafc" stroke="#0f172a" strokeWidth="1" />
                      <line x1={rx} y1="150" x2={rx} y2="270" stroke="#64748b" strokeWidth="0.8" strokeDasharray="6,2,2,2" />
                    </g>
                  ))}

                  <rect x="300" y="250" width="40" height="35" rx="4" fill="#0f766e" stroke="#0f172a" strokeWidth="1.8" />
                  <circle cx="320" cy="267" r="10" fill="#134e4a" stroke="#0f172a" strokeWidth="1.5" />
                  <text x="350" y="272" fill="#0f766e" fontSize="10" fontWeight="bold" fontFamily="monospace">0.75kW Reducer</text>

                  <line x1="60" y1="130" x2="60" y2="155" stroke="#64748b" strokeWidth="0.9" />
                  <line x1="580" y1="130" x2="580" y2="155" stroke="#64748b" strokeWidth="0.9" />
                  <line x1="65" y1="135" x2="575" y2="135" stroke="#0f172a" strokeWidth="1.2" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="280" y="128" fill="#0f172a" fontSize="12" fontWeight="bold" fontFamily="monospace">2000 mm (Bed Length)</text>

                  <line x1="585" y1="160" x2="615" y2="160" stroke="#64748b" strokeWidth="0.9" />
                  <line x1="585" y1="260" x2="615" y2="260" stroke="#64748b" strokeWidth="0.9" />
                  <line x1="610" y1="165" x2="610" y2="255" stroke="#0f172a" strokeWidth="1.2" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="618" y="215" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">450 mm</text>

                  <line x1="45" y1="260" x2="45" y2="340" stroke="#0f172a" strokeWidth="1.2" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="10" y="305" fill="#0f172a" fontSize="10" fontWeight="bold" fontFamily="monospace">350 mm</text>

                  <text x="60" y="75" fill="#1d4ed8" fontSize="13" fontWeight="bold" fontFamily="monospace">POWERED ROLLER BED (PRB) CONVEYOR ASSEMBLY</text>
                  <text x="60" y="93" fill="#475569" fontSize="11" fontFamily="monospace">5x Ø50mm ROLLERS • RAL 5005 BLUE STRUCTURAL C-CHANNEL</text>
                </svg>
              ) : isBracket ? (
                <svg viewBox="0 0 620 440" className="w-[560px] h-[390px]">
                  <defs>
                    <marker id="dimArrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                    <marker id="dimArrowStart" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                  </defs>

                  <line x1="120" y1="280" x2="120" y2="330" stroke="#94a3b8" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="120" y1="330" x2="260" y2="400" stroke="#94a3b8" strokeWidth="1" strokeDasharray="4,4" />

                  <path d="M 120 280 L 260 350 L 440 330 L 530 250 L 480 180 L 370 180 L 370 130 L 330 110 L 250 80 L 230 40 L 190 40 L 170 80 L 140 100 L 140 150 L 120 160 Z" fill="none" stroke="#0f172a" strokeWidth="2.2" strokeLinejoin="round" />

                  <path d="M 120 280 L 120 295 L 260 365 L 440 345 L 530 265 L 530 250" fill="none" stroke="#0f172a" strokeWidth="2" />
                  <line x1="260" y1="350" x2="260" y2="365" stroke="#0f172a" strokeWidth="1.8" />
                  <line x1="440" y1="330" x2="440" y2="345" stroke="#0f172a" strokeWidth="1.8" />

                  <path d="M 170 80 L 170 120 L 230 120 L 230 40" fill="none" stroke="#0f172a" strokeWidth="2" />
                  <path d="M 190 40 A 25 14 0 0 1 230 40" fill="none" stroke="#0f172a" strokeWidth="2" />
                  <ellipse cx="210" cy="80" rx="25" ry="14" fill="none" stroke="#0f172a" strokeWidth="2" />
                  
                  <ellipse cx="210" cy="80" rx="14" ry="8" fill="none" stroke="#0f172a" strokeWidth="1.8" />
                  <line x1="190" y1="80" x2="230" y2="80" stroke="#64748b" strokeWidth="0.8" strokeDasharray="6,2,2,2" />
                  <line x1="210" y1="68" x2="210" y2="92" stroke="#64748b" strokeWidth="0.8" strokeDasharray="6,2,2,2" />

                  <path d="M 230 120 L 255 133 L 415 305 L 395 315 L 230 145 Z" fill="none" stroke="#0f172a" strokeWidth="2.2" strokeLinejoin="round" />
                  <line x1="230" y1="120" x2="230" y2="145" stroke="#0f172a" strokeWidth="2" />

                  <ellipse cx="270" cy="275" rx="12" ry="7" fill="none" stroke="#0f172a" strokeWidth="1.8" />
                  <line x1="252" y1="275" x2="288" y2="275" stroke="#64748b" strokeWidth="0.8" strokeDasharray="6,2,2,2" />
                  <line x1="270" y1="264" x2="270" y2="286" stroke="#64748b" strokeWidth="0.8" strokeDasharray="6,2,2,2" />

                  <ellipse cx="430" cy="240" rx="12" ry="7" fill="none" stroke="#0f172a" strokeWidth="1.8" />
                  <line x1="412" y1="240" x2="448" y2="240" stroke="#64748b" strokeWidth="0.8" strokeDasharray="6,2,2,2" />
                  <line x1="430" y1="229" x2="430" y2="251" stroke="#64748b" strokeWidth="0.8" strokeDasharray="6,2,2,2" />

                  <line x1="170" y1="80" x2="170" y2="105" stroke="#475569" strokeWidth="0.9" />
                  <line x1="250" y1="80" x2="250" y2="105" stroke="#475569" strokeWidth="0.9" />
                  <line x1="170" y1="102" x2="250" y2="102" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="204" y="98" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">38</text>

                  <line x1="330" y1="110" x2="360" y2="80" stroke="#475569" strokeWidth="0.9" />
                  <line x1="370" y1="130" x2="400" y2="100" stroke="#475569" strokeWidth="0.9" />
                  <line x1="358" y1="82" x2="398" y2="102" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="372" y="86" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">19</text>

                  <line x1="255" y1="133" x2="305" y2="175" stroke="#475569" strokeWidth="0.9" />
                  <line x1="230" y1="145" x2="280" y2="187" stroke="#475569" strokeWidth="0.9" />
                  <line x1="282" y1="185" x2="303" y2="173" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="282" y="196" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">10</text>

                  <line x1="170" y1="210" x2="270" y2="275" stroke="#475569" strokeWidth="0.9" strokeDasharray="3,3" />
                  <line x1="190" y1="225" x2="265" y2="272" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="220" y="240" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">31</text>

                  <line x1="270" y1="285" x2="415" y2="315" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="335" y="295" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">64</text>

                  <line x1="120" y1="280" x2="70" y2="315" stroke="#475569" strokeWidth="0.9" />
                  <line x1="120" y1="365" x2="70" y2="400" stroke="#475569" strokeWidth="0.9" />
                  <line x1="75" y1="318" x2="75" y2="395" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="50" y="360" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">46</text>

                  <line x1="120" y1="280" x2="95" y2="280" stroke="#475569" strokeWidth="0.9" />
                  <line x1="120" y1="295" x2="95" y2="295" stroke="#475569" strokeWidth="0.9" />
                  <line x1="100" y1="280" x2="100" y2="295" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="80" y="291" fill="#0f172a" fontSize="10" fontWeight="bold" fontFamily="monospace">10</text>

                  <line x1="270" y1="275" x2="235" y2="330" stroke="#0f172a" strokeWidth="1.1" />
                  <line x1="235" y1="330" x2="200" y2="330" stroke="#0f172a" strokeWidth="1.1" />
                  <text x="205" y="325" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">Ø10</text>

                  <line x1="140" y1="150" x2="100" y2="140" stroke="#0f172a" strokeWidth="1.1" />
                  <line x1="100" y1="140" x2="75" y2="140" stroke="#0f172a" strokeWidth="1.1" />
                  <text x="80" y="135" fill="#0f172a" fontSize="10" fontWeight="bold" fontFamily="monospace">2x R6</text>

                  <line x1="440" y1="330" x2="520" y2="270" stroke="#475569" strokeWidth="0.9" />
                  <line x1="370" y1="180" x2="450" y2="120" stroke="#475569" strokeWidth="0.9" />
                  <line x1="510" y1="265" x2="445" y2="125" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="480" y="195" fill="#0f172a" fontSize="11" fontWeight="bold" fontFamily="monospace">67</text>
                </svg>
              ) : isSprocket ? (
                <svg viewBox="0 0 600 400" className="w-[540px] h-[360px]">
                  <defs>
                    <marker id="dimArrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                    <marker id="dimArrowStart" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                  </defs>
                  
                  <circle cx="280" cy="180" r="110" fill="none" stroke="#0f172a" strokeWidth="2.5" />
                  <circle cx="280" cy="180" r="55" fill="none" stroke="#0f172a" strokeWidth="1.8" />
                  <circle cx="280" cy="180" r="28" fill="none" stroke="#0f172a" strokeWidth="2.2" />

                  <line x1="130" y1="180" x2="430" y2="180" stroke="#64748b" strokeWidth="0.9" strokeDasharray="8,3,2,3" />
                  <line x1="280" y1="30" x2="280" y2="330" stroke="#64748b" strokeWidth="0.9" strokeDasharray="8,3,2,3" />

                  {Array.from({ length: teethCount || 14 }).map((_, i) => {
                    const angle = (i / (teethCount || 14)) * Math.PI * 2;
                    const rInner = 110;
                    const rOuter = 135;
                    const x1 = 280 + Math.cos(angle - 0.12) * rInner;
                    const y1 = 180 + Math.sin(angle - 0.12) * rInner;
                    const x2 = 280 + Math.cos(angle) * rOuter;
                    const y2 = 180 + Math.sin(angle) * rOuter;
                    const x3 = 280 + Math.cos(angle + 0.12) * rInner;
                    const y3 = 180 + Math.sin(angle + 0.12) * rInner;
                    return <polygon key={i} points={`${x1},${y1} ${x2},${y2} ${x3},${y3}`} fill="none" stroke="#0f172a" strokeWidth="2" />;
                  })}

                  <line x1="280" y1="45" x2="460" y2="45" stroke="#475569" strokeWidth="0.9" />
                  <line x1="280" y1="315" x2="460" y2="315" stroke="#475569" strokeWidth="0.9" />
                  <line x1="450" y1="48" x2="450" y2="312" stroke="#0f172a" strokeWidth="1.2" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="458" y="185" fill="#0f172a" fontSize="12" fontWeight="bold" fontFamily="monospace">Ø {dia} mm (OD)</text>

                  <line x1="280" y1="180" x2="360" y2="120" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" />
                  <line x1="360" y1="120" x2="420" y2="120" stroke="#0f172a" strokeWidth="1.1" />
                  <text x="365" y="114" fill="#0f172a" fontSize="12" fontWeight="bold" fontFamily="monospace">Ø {boreDia} BORE</text>

                  <text x="50" y="80" fill="#0f172a" fontSize="13" fontWeight="bold" fontFamily="monospace">ISO 606 DRIVE SPROCKET</text>
                  <text x="50" y="100" fill="#2563eb" fontSize="12" fontWeight="bold" fontFamily="monospace">Z = {teethCount || 14} TEETH</text>
                  <text x="50" y="118" fill="#475569" fontSize="11" fontFamily="monospace">PITCH (P) = 12.7 mm</text>
                  <text x="50" y="136" fill="#475569" fontSize="11" fontFamily="monospace">FACE THK (B1) = {h || 8} mm</text>
                </svg>
              ) : (
                <svg viewBox="0 0 600 400" className="w-[540px] h-[360px]">
                  <defs>
                    <marker id="dimArrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                    <marker id="dimArrowStart" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><polygon points="0 2, 8 4, 0 6" fill="#0f172a" /></marker>
                  </defs>

                  <path d="M 180 180 L 320 250 L 460 180 L 320 110 Z" fill="none" stroke="#0f172a" strokeWidth="2.2" />
                  <path d="M 180 180 L 180 270 L 320 340 L 320 250" fill="none" stroke="#0f172a" strokeWidth="2.2" />
                  <path d="M 320 340 L 460 270 L 460 180" fill="none" stroke="#0f172a" strokeWidth="2.2" />

                  <line x1="180" y1="270" x2="320" y2="200" stroke="#94a3b8" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="320" y1="200" x2="460" y2="270" stroke="#94a3b8" strokeWidth="1" strokeDasharray="4,4" />
                  <line x1="320" y1="200" x2="320" y2="110" stroke="#94a3b8" strokeWidth="1" strokeDasharray="4,4" />

                  <line x1="180" y1="280" x2="150" y2="295" stroke="#64748b" strokeWidth="0.8" />
                  <line x1="320" y1="350" x2="290" y2="365" stroke="#64748b" strokeWidth="0.8" />
                  <line x1="160" y1="290" x2="300" y2="360" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="215" y="340" fill="#0f172a" fontSize="12" fontWeight="bold" fontFamily="monospace">{l} mm (X)</text>

                  <line x1="470" y1="180" x2="500" y2="180" stroke="#64748b" strokeWidth="0.8" />
                  <line x1="470" y1="270" x2="500" y2="270" stroke="#64748b" strokeWidth="0.8" />
                  <line x1="490" y1="183" x2="490" y2="267" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="500" y="230" fill="#0f172a" fontSize="12" fontWeight="bold" fontFamily="monospace">{h} mm (Z)</text>

                  <line x1="460" y1="170" x2="480" y2="155" stroke="#64748b" strokeWidth="0.8" />
                  <line x1="320" y1="100" x2="340" y2="85" stroke="#64748b" strokeWidth="0.8" />
                  <line x1="470" y1="160" x2="330" y2="90" stroke="#0f172a" strokeWidth="1.1" markerStart="url(#dimArrowStart)" markerEnd="url(#dimArrow)" />
                  <text x="400" y="115" fill="#0f172a" fontSize="12" fontWeight="bold" fontFamily="monospace">{w} mm (Y)</text>
                </svg>
              )}
            </div>

            <div className="border border-slate-800 grid grid-cols-4 text-[10px] font-mono divide-x divide-slate-800 bg-slate-50/70">
              <div className="p-2 space-y-0.5">
                <div className="text-slate-500 text-[8px] uppercase">Organization</div>
                <div className="font-bold text-slate-900">ATS ENGINEERING AI</div>
                <div className="text-slate-600 text-[9px]">Autodesk Platform Services</div>
              </div>
              <div className="p-2 space-y-0.5">
                <div className="text-slate-500 text-[8px] uppercase">Component Title</div>
                <div className="font-bold text-slate-900 truncate">{componentTitle}</div>
                <div className="text-slate-600 text-[9px]">TOLERANCE: ISO 2768-m</div>
              </div>
              <div className="p-2 space-y-0.5">
                <div className="text-slate-500 text-[8px] uppercase">Material & Finish</div>
                <div className="font-bold text-slate-900 truncate">{materialName}</div>
                <div className="text-slate-600 text-[9px]">SCALE: 1:1 • UNITS: MM</div>
              </div>
              <div className="p-2 space-y-0.5 bg-blue-50/50">
                <div className="text-blue-600 text-[8px] uppercase font-bold">Drawing Status</div>
                <div className="font-bold text-emerald-700">RELEASED (INVENTOR)</div>
                <div className="text-slate-500 text-[9px]">DWG-2026-0818</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
