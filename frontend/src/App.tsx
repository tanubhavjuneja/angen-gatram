import { useState, useEffect, useRef } from 'react';
import {
  HardDrive,
  FileSearch,
  AlertTriangle,
  Shield,
  Clock,
  Download,
  Loader2,
  CheckCircle,
  XCircle,
  RefreshCw,
  Activity,
  Target,
  Lightbulb,
  FolderOpen,
  Upload,
} from 'lucide-react';
import {
  getForensicHealth,
  startForensicAnalysis,
  getForensicStatus,
  getForensicResults,
  downloadReportFile,
  getDrives,
  browseDirectory,
  selectImage,
  ForensicHealthResponse,
  ForensicResultsResponse,
} from './api';

function App() {
  const [health, setHealth] = useState<ForensicHealthResponse | null>(null);
  const [imagePath, setImagePath] = useState('');
  const [loading, setLoading] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('');
  const [message, setMessage] = useState('');
  const [results, setResults] = useState<ForensicResultsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  
  // File browser state
  const [showFileBrowser, setShowFileBrowser] = useState(false);
  const [drives, setDrives] = useState<string[]>([]);
  const [currentPath, setCurrentPath] = useState('C:/');
  const [browseItems, setBrowseItems] = useState<any[]>([]);
  const [browseLoading, setBrowseLoading] = useState(false);

  const openFileBrowser = async () => {
    setShowFileBrowser(true);
    setBrowseLoading(true);
    try {
      const driveData = await getDrives();
      setDrives(driveData.drives);
      if (driveData.drives.length > 0) {
        setCurrentPath(driveData.drives[0]);
        const browseData = await browseDirectory(driveData.drives[0]);
        setBrowseItems(browseData.items);
      }
    } catch (err) {
      console.error('Failed to load drives:', err);
    }
    setBrowseLoading(false);
  };

  const navigateTo = async (path: string) => {
    setBrowseLoading(true);
    setCurrentPath(path);
    try {
      const data = await browseDirectory(path);
      setBrowseItems(data.items);
    } catch (err) {
      console.error('Failed to browse:', err);
    }
    setBrowseLoading(false);
  };

  const selectFile = async (item: any) => {
    if (item.is_dir) {
      await navigateTo(item.path);
    } else {
      const result = await selectImage(item.path);
      if (result.valid && result.path) {
        setImagePath(result.path);
        setShowFileBrowser(false);
      } else {
        setError(result.error || 'Invalid file selected');
      }
    }
  };

  const goUp = () => {
    const parts = currentPath.replace(/\\/g, '/').split('/').filter(Boolean);
    if (parts.length > 1) {
      parts.pop();
      const newPath = parts.join('/');
      navigateTo(newPath.length === 1 ? newPath + ':/' : newPath + '/');
    }
  };

  useEffect(() => {
    checkHealth();
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const checkHealth = async () => {
    try {
      const h = await getForensicHealth();
      setHealth(h);
    } catch {
      setHealth({ status: 'unavailable', pipeline_available: false });
    }
  };

  const startAnalysis = async () => {
    if (!imagePath.trim()) return;

    setLoading(true);
    setError(null);
    setMessage('Starting forensic analysis...');

    try {
      const response = await startForensicAnalysis(imagePath.trim());
      setTaskId(response.task_id);
      setMessage('Analysis queued...');

      pollRef.current = setInterval(async () => {
        try {
          const status = await getForensicStatus(response.task_id);
          setProgress(status.progress);
          setStage(status.stage);
          setMessage(status.message);

          if (status.status === 'completed') {
            if (pollRef.current) {
              clearInterval(pollRef.current);
              pollRef.current = null;
            }
            const resultsData = await getForensicResults(response.task_id);
            setResults(resultsData);
            setLoading(false);
          } else if (status.status === 'failed') {
            if (pollRef.current) {
              clearInterval(pollRef.current);
              pollRef.current = null;
            }
            setError(status.error || 'Analysis failed');
            setLoading(false);
          }
        } catch (err) {
          console.error('Error polling status:', err);
        }
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start analysis');
      setLoading(false);
    }
  };

  const reset = () => {
    setImagePath('');
    setTaskId(null);
    setProgress(0);
    setStage('');
    setMessage('');
    setResults(null);
    setError(null);
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  const handleDownloadPdf = async () => {
    if (!taskId) return;
    try {
      await downloadReportFile(taskId, 'html');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download HTML');
    }
  };

  const handleDownloadTxt = async () => {
    if (!taskId) return;
    try {
      await downloadReportFile(taskId, 'txt');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download TXT');
    }
  };

  const handleDownloadJson = async () => {
    if (!taskId) return;
    try {
      await downloadReportFile(taskId, 'json');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download JSON');
    }
  };

  const handleDownloadCsv = async () => {
    if (!taskId) return;
    try {
      await downloadReportFile(taskId, 'csv');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download CSV');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL': return { bg: '#fee2e2', text: '#dc2626', border: '#ef4444' };
      case 'HIGH': return { bg: '#ffedd5', text: '#ea580c', border: '#f97316' };
      case 'MEDIUM': return { bg: '#fef9c3', text: '#ca8a04', border: '#eab308' };
      case 'LOW': return { bg: '#dcfce7', text: '#16a34a', border: '#22c55e' };
      default: return { bg: '#f3f4f6', text: '#6b7280', border: '#9ca3af' };
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'critical': return { bg: '#dc2626', text: 'white' };
      case 'high': return { bg: '#ea580c', text: 'white' };
      case 'medium': return { bg: '#ca8a04', text: 'white' };
      case 'low': return { bg: '#16a34a', text: 'white' };
      default: return { bg: '#6b7280', text: 'white' };
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <HardDrive size={32} />
            <h1>Forensic Disk Analyzer</h1>
          </div>
          <div className="status-badge">
            {health?.pipeline_available ? (
              <span className="badge success"><Shield size={14} /> Ready</span>
            ) : (
              <span className="badge error"><XCircle size={14} /> Unavailable</span>
            )}
          </div>
        </div>
      </header>

      <main className="main">
        {!results ? (
          <div className="upload-section">
            <div className="card">
              <div className="card-header">
                <FileSearch size={28} />
                <h2>Disk Image Analysis</h2>
              </div>
              <p className="description">
                Analyze disk images (.E01, .DD, .RAW, .IMG) for anti-forensic techniques
                including timestomping, shadow copy deletion, ADS, and more.
              </p>

              <div className="input-group">
                <FolderOpen size={20} />
                <input
                  type="text"
                  placeholder="Enter path to disk image file..."
                  value={imagePath}
                  onChange={(e) => setImagePath(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !loading && startAnalysis()}
                  disabled={loading}
                />
                <button
                  type="button"
                  className="btn-icon"
                  onClick={openFileBrowser}
                  disabled={loading}
                  title="Browse for file"
                >
                  <Upload size={18} />
                </button>
              </div>

              <button
                className="btn primary"
                onClick={startAnalysis}
                disabled={loading || !imagePath.trim() || !health?.pipeline_available}
              >
                {loading ? <Loader2 className="spin" size={20} /> : <FileSearch size={20} />}
                {loading ? 'Analyzing...' : 'Start Analysis'}
              </button>

              {loading && (
                <div className="progress-section">
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${progress}%` }} />
                  </div>
                  <div className="progress-info">
                    <span className="stage">{stage}</span>
                    <span className="percent">{progress}%</span>
                  </div>
                  <p className="message">{message}</p>
                </div>
              )}

              {error && (
                <div className="error-message">
                  <AlertTriangle size={20} />
                  {error}
                </div>
              )}

              {showFileBrowser && (
                <div className="file-browser-overlay">
                  <div className="file-browser-modal">
                    <div className="browser-header">
                      <h3>Select Disk Image</h3>
                      <button className="btn-close" onClick={() => setShowFileBrowser(false)}>×</button>
                    </div>
                    
                    <div className="browser-drives">
                      {drives.map(drive => (
                        <button
                          key={drive}
                          className={`drive-btn ${currentPath.startsWith(drive) ? 'active' : ''}`}
                          onClick={() => navigateTo(drive)}
                        >
                          {drive}
                        </button>
                      ))}
                    </div>

                    <div className="browser-path">
                      <button onClick={goUp} disabled={!currentPath.match(/^[A-Z]:\\/)}>↑ Up</button>
                      <span>{currentPath}</span>
                    </div>

                    <div className="browser-content">
                      {browseLoading ? (
                        <div className="browser-loading"><Loader2 className="spin" /> Loading...</div>
                      ) : (
                        <div className="browser-items">
                          {browseItems.slice(0, 100).map(item => (
                            <div
                              key={item.path}
                              className={`browser-item ${item.is_dir ? 'folder' : 'file'}`}
                              onClick={() => selectFile(item)}
                            >
                              {item.is_dir ? '📁' : '📄'} {item.name}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="browser-help">
                      Click on folders to navigate, files to select. Supported: .dd, .raw, .img, .e01
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="results-section">
            <div className="results-header">
              <div className="header-info">
                <Shield size={32} className="shield-icon" />
                <div>
                  <h2>Analysis Complete</h2>
                  <p className="meta">
                    <Clock size={14} /> {new Date(results.timestamp).toLocaleString()} |
                    Model: {results.model} |
                    Time: {results.analysis_time_seconds.toFixed(1)}s
                  </p>
                </div>
              </div>
              <div className="header-actions">
                <button className="btn btn-primary" onClick={handleDownloadPdf}>
                  <Download size={18} /> HTML Report
                </button>
                <button className="btn" onClick={handleDownloadTxt}>
                  <Download size={18} /> TXT
                </button>
                <button className="btn" onClick={handleDownloadJson}>
                  <Download size={18} /> JSON
                </button>
                <button className="btn" onClick={handleDownloadCsv}>
                  <Download size={18} /> CSV
                </button>
                <button className="btn btn-secondary" onClick={reset}>
                  <RefreshCw size={18} /> New Analysis
                </button>
              </div>
            </div>

            <div className="risk-banner" style={{ backgroundColor: getRiskBadge(results.risk_level).bg }}>
              <Activity size={24} style={{ color: getRiskBadge(results.risk_level).text }} />
              <span style={{ color: getRiskBadge(results.risk_level).text }}>
                Risk Level: {results.risk_level}
              </span>
            </div>

            <div className="card summary-card">
              <h3><Target size={20} /> Summary</h3>
              <p>{results.summary}</p>
            </div>

            {results.timestamp_analysis && Object.keys(results.timestamp_analysis).length > 0 && (
              <div className="card timestamp-card">
                <h3><Clock size={20} /> Timestamp Integrity Analysis</h3>
                
                {Object.entries(results.timestamp_analysis).map(([partition, data]: [string, any]) => (
                  <div key={partition} className="timestamp-partition">
                    <h4>{partition.replace('_', ' ').toUpperCase()}</h4>
                    
                    {data.usn_journal_status && (
                      <div className="usn-status">
                        <span className={`status-badge ${data.usn_journal_status.found ? 'found' : 'missing'}`}>
                          {data.usn_journal_status.found ? 'USN Journal Found' : 'USN Journal Missing'}
                        </span>
                        {data.usn_journal_status.error && (
                          <p className="usn-error">{data.usn_journal_status.error}</p>
                        )}
                      </div>
                    )}
                    
                    {data.time_gaps && data.time_gaps.length > 0 && (
                      <div className="time-gaps-section">
                        <h5>Time Gaps in USN Journal</h5>
                        {data.time_gaps.map((gap: any, idx: number) => (
                          <div key={idx} className="time-gap-item">
                            <span className="gap-seconds">{gap.gap_seconds}s</span>
                            <span className="gap-hours">({gap.gap_hours} hours, {gap.gap_days} days)</span>
                            <p className="gap-range">
                              {gap.from_timestamp} → {gap.to_timestamp}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {data.inconsistencies && data.inconsistencies.length > 0 ? (
                      <div className="inconsistencies-list">
                        <h5>Timestamp Inconsistencies ({data.inconsistencies.length})</h5>
                        {data.inconsistencies.map((inc: any, idx: number) => (
                          <div 
                            key={idx} 
                            className="inconsistency-item"
                            style={{
                              borderLeftColor: inc.severity === 'high' ? '#ef4444' : inc.severity === 'medium' ? '#eab308' : '#6b7280',
                            }}
                          >
                            <span className={`severity-badge ${inc.severity}`}>
                              {inc.severity?.toUpperCase()}
                            </span>
                            <span className="inc-type">{inc.type}</span>
                            <p className="inc-message">{inc.message}</p>
                            {inc.description && <p className="inc-desc">{inc.description}</p>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="no-issues">No timestamp inconsistencies detected</p>
                    )}
                    
                    <p className="partition-summary">
                      {data.total_mft_entries} MFT entries, {data.total_usn_records} USN records analyzed
                    </p>
                  </div>
                ))}
                
                <details className="raw-data-toggle">
                  <summary>View Raw Data</summary>
                  <pre style={{whiteSpace: 'pre-wrap', color: '#9ca3af', fontSize: '12px'}}>
{JSON.stringify(results.timestamp_analysis, null, 2)}
                  </pre>
                </details>
              </div>
            )}

            <div className="findings-grid">
              {results.findings.map((finding, idx) => (
                <div
                  key={idx}
                  className="card finding-card"
                  style={{
                    borderColor: getSeverityColor(finding.severity).border,
                    backgroundColor: getSeverityColor(finding.severity).bg,
                  }}
                >
                  <div className="finding-header">
                    <span
                      className="severity-badge"
                      style={{
                        backgroundColor: getSeverityColor(finding.severity).text,
                        color: 'white',
                      }}
                    >
                      {finding.severity}
                    </span>
                    <span className="confidence">
                      {Math.round(finding.confidence * 100)}% confidence
                    </span>
                  </div>
                  <h4>{finding.technique}</h4>
                  <p className="evidence"><strong>Evidence:</strong> {finding.evidence}</p>
                  <p className="explanation">{finding.explanation}</p>
                  <p className="recommendation">
                    <Lightbulb size={14} />
                    <strong>Recommendation:</strong> {finding.recommendation}
                  </p>
                </div>
              ))}
              {results.findings.length === 0 && (
                <div className="card no-findings">
                  <CheckCircle size={48} />
                  <h3>No Anti-Forest Indicators Found</h3>
                  <p>The analysis did not find evidence of anti-forensic techniques in this image.</p>
                </div>
              )}
            </div>

            {results.integrated_analysis && results.integrated_analysis.summary && (
              <div className="card integrated-card">
                <h3><Clock size={20} /> Advanced Timestomp Analysis</h3>
                
                <div className="analysis-stats">
                  <div className="stat-box critical">
                    <span className="stat-number">{results.integrated_analysis.summary.critical_count || 0}</span>
                    <span className="stat-label">Critical</span>
                  </div>
                  <div className="stat-box high">
                    <span className="stat-number">{results.integrated_analysis.summary.high_count || 0}</span>
                    <span className="stat-label">High</span>
                  </div>
                  <div className="stat-box medium">
                    <span className="stat-number">{results.integrated_analysis.summary.medium_count || 0}</span>
                    <span className="stat-label">Medium</span>
                  </div>
                  <div className="stat-box low">
                    <span className="stat-number">{results.integrated_analysis.summary.low_count || 0}</span>
                    <span className="stat-label">Low</span>
                  </div>
                </div>
                
                <p className="analysis-summary">
                  Files Analyzed: {results.integrated_analysis.summary.total_files_analyzed || 0} | 
                  Suspicious: {results.integrated_analysis.summary.suspicious_files || 0}
                </p>
                
                {results.integrated_analysis.critical_findings && results.integrated_analysis.critical_findings.length > 0 && (
                  <div className="findings-list">
                    <h4>Critical Findings ({results.integrated_analysis.critical_findings.length})</h4>
                    {results.integrated_analysis.critical_findings.slice(0, 5).map((finding: any, idx: number) => (
                      <div key={idx} className="finding-item critical">
                        <span className="filename">{finding.filename}</span>
                        <span className="score">Score: {finding.overall_score}</span>
                        {finding.si_fn_created_delta > 0 && (
                          <span className="delta">SI/FN Delta: {finding.si_fn_created_delta.toFixed(0)}s</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Suspicious Timestamp Files List */}
                {results.integrated_analysis && results.integrated_analysis.partition_results && (
                  <div className="suspicious-files-list">
                    <h4>Files with Suspicious Timestamps</h4>
                    {(() => {
                      const suspiciousFiles: any[] = [];
                      results.integrated_analysis.partition_results.forEach((part: any) => {
                        if (part.findings) {
                          part.findings.forEach((f: any) => {
                            if (f.is_timestomped || f.overall_score > 0) {
                              suspiciousFiles.push(f);
                            }
                          });
                        }
                      });
                      if (suspiciousFiles.length === 0) return null;
                      return (
                        <div className="suspicious-table-container">
                          <table className="suspicious-table">
                            <thead>
                              <tr>
                                <th>Filename</th>
                                <th>Severity</th>
                                <th>Score</th>
                                <th>SI/FN Delta</th>
                                <th>SI Created</th>
                                <th>FN Created</th>
                              </tr>
                            </thead>
                            <tbody>
                              {suspiciousFiles.slice(0, 20).map((f: any, idx: number) => (
                                <tr key={idx} className={`severity-${f.overall_severity?.toLowerCase()}`}>
                                  <td className="filename-cell">{f.filename}</td>
                                  <td><span className={`severity-badge ${f.overall_severity?.toLowerCase()}`}>{f.overall_severity}</span></td>
                                  <td>{f.overall_score}</td>
                                  <td>{f.si_fn_created_delta ? f.si_fn_created_delta.toFixed(1) + 's' : '-'}</td>
                                  <td className="timestamp">{f.si_timestamps?.created?.split('T')[0] || '-'}</td>
                                  <td className="timestamp">{f.fn_timestamps?.created?.split('T')[0] || '-'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                          {suspiciousFiles.length > 20 && (
                            <p className="more-files">... and {suspiciousFiles.length - 20} more files</p>
                          )}
                        </div>
                      );
                    })()}
                  </div>
                )}
              </div>
            )}

            <div className="card data-wipe-card">
              <h3><Activity size={20} /> Data Wipe Detection</h3>
              
              {results.data_wipe_analysis && results.data_wipe_analysis.wipe_detected ? (
                <div className="wipe-detected">
                  <div className="wipe-alert">
                    <AlertTriangle size={24} />
                    <span>Data Wiping Detected</span>
                  </div>
                  <p className="wipe-summary">{results.data_wipe_analysis.summary}</p>
                  <p className="wipe-confidence">
                    Confidence: {Math.round((results.data_wipe_analysis.confidence || 0) * 100)}%
                  </p>
                  
                  {results.data_wipe_analysis.details && results.data_wipe_analysis.details.partition_scan && (
                    <div className="wipe-stats">
                      <div className="stat-item">
                        <span className="stat-label">High Entropy Regions:</span>
                        <span className="stat-value">{results.data_wipe_analysis.details.partition_scan.high_entropy_percentage?.toFixed(1)}%</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Zero-Filled Regions:</span>
                        <span className="stat-value">{results.data_wipe_analysis.details.partition_scan.zero_percentage?.toFixed(1)}%</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Wipe Method:</span>
                        <span className="stat-value">{results.data_wipe_analysis.details.partition_scan.method || 'unknown'}</span>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="no-wipe-detected">
                  <CheckCircle size={32} />
                  <p>No evidence of data wiping or file shredding detected</p>
                </div>
              )}
              
              {results.data_wipe_analysis && results.data_wipe_analysis.indicators && results.data_wipe_analysis.indicators.length > 0 && (
                <div className="wipe-indicators">
                  <h4>Indicators ({results.data_wipe_analysis.indicators.length})</h4>
                  {results.data_wipe_analysis.indicators.map((indicator: any, idx: number) => (
                    <div 
                      key={idx} 
                      className="wipe-indicator"
                      style={{
                        borderLeftColor: indicator.severity === 'high' ? '#dc2626' : indicator.severity === 'medium' ? '#eab308' : '#6b7280',
                      }}
                    >
                      <span className={`severity-badge ${indicator.severity}`}>
                        {indicator.severity?.toUpperCase()}
                      </span>
                      <span className="indicator-type">{indicator.type}</span>
                      <p className="indicator-desc">{indicator.description}</p>
                      <p className="indicator-evidence"><strong>Evidence:</strong> {indicator.evidence}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card hidden-volume-card">
              <h3><Shield size={20} /> Hidden Volume / Encrypted Container Detection</h3>
              
              {results.hidden_volume_analysis && results.hidden_volume_analysis.wipe_detected ? (
                <div className="wipe-detected">
                  <div className="wipe-alert">
                    <AlertTriangle size={24} />
                    <span>Hidden Volume/Encrypted Container Detected</span>
                  </div>
                  <p className="wipe-summary">{results.hidden_volume_analysis.summary}</p>
                </div>
              ) : (
                <div className="no-wipe-detected">
                  <CheckCircle size={32} />
                  <p>No hidden volumes or encrypted containers detected</p>
                </div>
              )}
              
              {results.hidden_volume_analysis && results.hidden_volume_analysis.partitions && results.hidden_volume_analysis.partitions.length > 0 && (
                <div className="partition-results">
                  <h4>Partition Analysis</h4>
                  {results.hidden_volume_analysis.partitions.map((partition: any, idx: number) => (
                    <div 
                      key={idx} 
                      className="partition-result"
                      style={{
                        borderLeftColor: partition.hidden_volume_detected ? '#dc2626' : '#22c55e',
                        }}
                      >
                        <span className={`severity-badge ${partition.hidden_volume_detected ? 'high' : 'low'}`}>
                          {partition.hidden_volume_detected ? 'DETECTED' : 'CLEAN'}
                        </span>
                        <span className="partition-slot">{partition.partition_slot || `Partition ${idx + 1}`}</span>
                        <p className="partition-details">
                          {partition.details || partition.detection_method || 'No details'}
                        </p>
                        {partition.confidence > 0 && (
                          <p className="partition-confidence">
                            Confidence: {Math.round(partition.confidence * 100)}%
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
            </div>

            {results.recommendations.length > 0 && (
              <div className="card recommendations-card">
                <h3><Lightbulb size={20} /> Recommendations</h3>
                <ul>
                  {results.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
