export interface Agent {
  id: string;
  workstation_ip: string;
  hostname?: string;
  application_name: string;
  application_version?: string;
  status: 'READY' | 'BUSY' | 'OFFLINE';
  is_active: boolean;
  last_heartbeat: string;
}

export interface ExecutionStep {
  id: string;
  step: string;
  label: string;
  detail: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  timestamp?: string;
}

export type PipelineStage = 'idle' | 'planning' | 'generating' | 'kernel' | 'validating' | 'exporting' | 'completed' | 'failed';

export interface BoundingBoxInfo {
  min_x: number;
  max_x: number;
  min_y: number;
  max_y: number;
  min_z: number;
  max_z: number;
  size_x: number;
  size_y: number;
  size_z: number;
}

export interface CADValidationReport {
  is_valid: boolean;
  is_solid: boolean;
  volume_mm3: number;
  surface_area_mm2?: number;
  bounding_box: BoundingBoxInfo;
  face_count: number;
  edge_count: number;
  vertex_count: number;
  brep_check_status: boolean;
  step_import_verified: boolean;
  step_path: string;
  stl_path?: string;
  glb_path?: string;
  message: string;
  warnings?: string[];
}

export interface CADFeatureItem {
  id: string;
  name: string;
  type: string;
  parameters: Record<string, any>;
  icon?: string;
}

export interface CADVersion {
  id: string;
  versionNumber: string; // e.g. "v001"
  prompt: string;
  timestamp: number;
  tool: string;
  shapeType: string;
  parameters: Record<string, any>;
  validation?: CADValidationReport;
  features: CADFeatureItem[];
  pythonScript?: string;
  planJson?: Record<string, any>;
  stepUrl?: string;
  stlUrl?: string;
  glbUrl?: string;
}

export interface CADProject {
  id: string;
  name: string;
  created_at: number;
  current_version: string;
  versions: CADVersion[];
  units: 'mm' | 'cm' | 'inch';
}

export type DisplayMode = 'solid' | 'wireframe' | 'edges' | 'xray' | 'drawing';
export type CameraPreset = 'iso' | 'top' | 'bottom' | 'front' | 'back' | 'left' | 'right';
export type ThemeMode = 'dark' | 'light' | 'system';

export interface SelectedGeometryInfo {
  type: 'face' | 'edge' | 'solid';
  id: string | number;
  normal?: [number, number, number];
  area_mm2?: number;
  length_mm?: number;
  center?: [number, number, number];
}

export interface CadJobResult {
  jobId: string;
  tool: string;
  parameters: Record<string, any>;
  workstationIp: string;
  status: string;
  message: string;
  data?: Record<string, any>;
  executionTimeMs?: number;
  validation?: CADValidationReport;
  stepUrl?: string;
  stlUrl?: string;
}
