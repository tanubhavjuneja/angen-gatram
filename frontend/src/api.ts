const API_BASE = 'http://127.0.0.1:8000/forensics';

export interface ForensicHealthResponse {
  status: string;
  pipeline_available: boolean;
  docker_available?: boolean;
  docker_message?: string;
}

export interface ForensicStartResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface ForensicStatusResponse {
  task_id: string;
  status: string;
  progress: number;
  stage: string;
  message: string;
  output_dir?: string;
  error?: string;
}

export interface ForensicFinding {
  technique: string;
  severity: string;
  evidence: string;
  explanation: string;
  recommendation: string;
  confidence: number;
}

export interface DataWipeIndicator {
  type: string;
  severity: string;
  description: string;
  evidence: string;
  confidence: number;
  file_path?: string;
  offset?: number;
}

export interface DataWipeAnalysis {
  wipe_detected: boolean;
  confidence: number;
  indicators: DataWipeIndicator[];
  summary: string;
  details?: any;
}

export interface HiddenVolumeAnalysis {
  wipe_detected?: boolean;
  summary: string;
  partitions?: any[];
}

export interface IntegratedAnalysis {
  partition_results?: any[];
  summary?: {
    total_partitions?: number;
    total_files_analyzed?: number;
    suspicious_files?: number;
    critical_count?: number;
    high_count?: number;
    medium_count?: number;
    low_count?: number;
  };
  critical_findings?: any[];
  high_findings?: any[];
  medium_findings?: any[];
}

export interface ForensicResultsResponse {
  task_id: string;
  status: string;
  output_dir: string;
  findings: ForensicFinding[];
  summary: string;
  risk_level: string;
  recommendations: string[];
  timestamp: string;
  timestamp_analysis?: any;
  metadata_analysis?: any;
  integrated_analysis?: IntegratedAnalysis;
  data_wipe_analysis?: DataWipeAnalysis;
  hidden_volume_analysis?: HiddenVolumeAnalysis;
  partitions?: PartitionInfo[];
  report_files?: { txt?: string; html?: string };
  model: string;
  analysis_time_seconds: number;
}

export interface PartitionInfo {
  slot: string;
  start: string;
  desc: string;
  is_hidden?: boolean;
  is_encrypted?: boolean;
  encryption_type?: string;
}

export interface FileItem {
  name: string;
  path: string;
  is_dir: boolean;
  is_file: boolean;
  size: number;
}

export interface BrowseResponse {
  path: string;
  items: FileItem[];
}

export interface DriveResponse {
  drives: string[];
}

export interface SelectImageResponse {
  valid: boolean;
  path?: string;
  name?: string;
  size?: number;
  format?: string;
  error?: string;
}

export async function getDrives(): Promise<DriveResponse> {
  const response = await fetch(`${API_BASE}/drives`);
  if (!response.ok) throw new Error('Failed to get drives');
  return response.json();
}

export async function browseDirectory(path: string): Promise<BrowseResponse> {
  const response = await fetch(`${API_BASE}/browse?path=${encodeURIComponent(path)}`);
  if (!response.ok) throw new Error('Failed to browse directory');
  return response.json();
}

export async function selectImage(path: string): Promise<SelectImageResponse> {
  const response = await fetch(`${API_BASE}/select-image?path=${encodeURIComponent(path)}`);
  if (!response.ok) throw new Error('Failed to validate image');
  return response.json();
}

export async function getForensicHealth(): Promise<ForensicHealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (response.ok) {
    return response.json();
  }
  return { status: 'unavailable', pipeline_available: false };
}

export async function startForensicAnalysis(imagePath: string): Promise<ForensicStartResponse> {
  const response = await fetch(`${API_BASE}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_path: imagePath }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `Failed to start analysis: ${response.statusText}`);
  }

  return response.json();
}

export async function getForensicStatus(taskId: string): Promise<ForensicStatusResponse> {
  const response = await fetch(`${API_BASE}/status/${taskId}`);

  if (!response.ok) {
    throw new Error(`Failed to get status: ${response.statusText}`);
  }

  return response.json();
}

export async function getForensicResults(taskId: string): Promise<ForensicResultsResponse> {
  const response = await fetch(`${API_BASE}/results/${taskId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `Failed to get results: ${response.statusText}`);
  }

  return response.json();
}

export async function downloadForensicPdf(taskId: string): Promise<void> {
  let response = await fetch(`${API_BASE}/report/${taskId}?format=html`);
  
  if (!response.ok) {
    response = await fetch(`${API_BASE}/pdf/${taskId}`);
  }

  if (!response.ok) {
    const errorText = await response.text();
    if (errorText.includes('not found') || response.status === 404) {
      throw new Error('No report available. Analysis may still be processing or failed.');
    }
    throw new Error(errorText || `Failed to download report: ${response.statusText}`);
  }

  const contentType = response.headers.get('content-type') || 'text/plain';
  const extension = contentType.includes('html') ? 'html' : 'txt';
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `forensic_report_${taskId}.${extension}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function downloadReportFile(taskId: string, format: string): Promise<void> {
  const response = await fetch(`${API_BASE}/report/${taskId}?format=${format}`);
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Failed to download ${format} report: ${response.statusText}`);
  }

  const contentType = response.headers.get('content-type') || 'text/plain';
  let extension = format;
  if (contentType.includes('html')) extension = 'html';
  else if (contentType.includes('json')) extension = 'json';
  else if (contentType.includes('csv')) extension = 'csv';
  else if (contentType.includes('text')) extension = 'txt';
  
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `forensic_report_${taskId}.${extension}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
