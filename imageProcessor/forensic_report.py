#!/usr/bin/env python3
"""
Forensic Report Generator - Creates PDF reports from forensic analysis results.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class ForensicReportGenerator:
    """Generate forensic analysis reports in multiple formats."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_pdf_report(self, results: Dict[str, Any], image_name: str = "disk_image") -> str:
        """Generate a text/HTML report (simple format)."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"forensic_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("FORENSIC DISK ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Image: {image_name}\n")
            f.write(f"Output Directory: {self.output_dir}\n\n")
            
            # Partition Information
            f.write("-" * 80 + "\n")
            f.write("PARTITION ANALYSIS\n")
            f.write("-" * 80 + "\n\n")
            
            partitions = results.get('partitions', [])
            if partitions:
                for i, part in enumerate(partitions):
                    if part.get('slot') == 'Meta':
                        continue
                    f.write(f"Partition {i}:\n")
                    f.write(f"  Slot: {part.get('slot', 'N/A')}\n")
                    f.write(f"  Start Sector: {part.get('start_sector', part.get('start', 'N/A'))}\n")
                    f.write(f"  End Sector: {part.get('end_sector', part.get('end', 'N/A'))}\n")
                    
                    # Calculate size
                    size_sectors = part.get('size_sectors', 0)
                    if size_sectors:
                        size_bytes = size_sectors * 512
                        f.write(f"  Size: {size_bytes:,} bytes ({size_bytes/(1024**3):.2f} GB)\n")
                    else:
                        f.write(f"  Size: {part.get('size_sectors', 'N/A')} sectors\n")
                    
                    f.write(f"  Filesystem: {part.get('fs', 'N/A')}\n")
                    f.write(f"  Description: {part.get('description', part.get('desc', 'N/A'))}\n")
                    if part.get('is_hidden'):
                        f.write(f"  [!] HIDDEN PARTITION DETECTED\n")
                    if part.get('is_encrypted'):
                        f.write(f"  [!] ENCRYPTED PARTITION: {part.get('encryption_type', 'Unknown')}\n")
                    if part.get('is_gpt'):
                        f.write(f"  Type: GPT\n")
                    f.write("\n")
            else:
                f.write("No partition information available.\n\n")
            
            # Timestamp Analysis
            f.write("-" * 80 + "\n")
            f.write("TIMESTAMP INTEGRITY ANALYSIS\n")
            f.write("-" * 80 + "\n\n")
            
            timestamp_analysis = results.get('timestamp_analysis', {})
            for partition, ts_data in timestamp_analysis.items():
                f.write(f"{partition}:\n")
                
                usn_status = ts_data.get('usn_journal_status', {})
                if usn_status.get('found'):
                    f.write(f"  USN Journal: FOUND\n")
                    f.write(f"    Max Size: {usn_status.get('max_size', 0)} bytes\n")
                    f.write(f"    Next USN: {usn_status.get('next_usn', 0)}\n")
                    f.write(f"    Oldest USN: {usn_status.get('oldest_usn', 0)}\n")
                else:
                    f.write(f"  USN Journal: NOT FOUND\n")
                    f.write(f"    Reason: {usn_status.get('reason', 'Unknown')}\n")
                
                inconsistencies = ts_data.get('inconsistencies', [])
                if inconsistencies:
                    f.write(f"\n  Timestamp Inconsistencies: {len(inconsistencies)}\n")
                    for inc in inconsistencies[:20]:
                        severity = inc.get('severity', 'unknown').upper()
                        f.write(f"    [{severity}] {inc.get('type', 'unknown')}: {inc.get('message', '')}\n")
                else:
                    f.write(f"\n  No timestamp inconsistencies detected.\n")
                f.write("\n")
            
            # Anti-Forensic Findings
            f.write("-" * 80 + "\n")
            f.write("ANTI-FORENSIC DETECTION RESULTS\n")
            f.write("-" * 80 + "\n\n")
            
            antiforensic = results.get('antiforensic_results', {})
            findings = antiforensic.get('findings', [])
            
            if findings:
                for finding in findings:
                    severity = finding.get('severity', 'medium').upper()
                    f.write(f"[{severity}] {finding.get('technique', 'Unknown')}\n")
                    f.write(f"  Evidence: {finding.get('evidence', 'N/A')}\n")
                    f.write(f"  Explanation: {finding.get('explanation', 'N/A')}\n")
                    f.write(f"  Recommendation: {finding.get('recommendation', 'N/A')}\n")
                    f.write(f"  Confidence: {finding.get('confidence', 0) * 100:.0f}%\n\n")
            else:
                f.write("No anti-forensic indicators found.\n\n")
            
            # Risk Assessment
            f.write("-" * 80 + "\n")
            f.write("RISK ASSESSMENT\n")
            f.write("-" * 80 + "\n\n")
            
            f.write(f"Risk Level: {results.get('risk_level', 'Unknown')}\n")
            f.write(f"Summary: {results.get('summary', 'No summary available')}\n\n")
            
            # Recommendations
            recommendations = results.get('recommendations', [])
            if recommendations:
                f.write("Recommendations:\n")
                for rec in recommendations:
                    f.write(f"  - {rec}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        # Also create JSON version
        json_file = self.output_dir / f"forensic_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return str(report_file)
    
    def generate_html_report(self, results: Dict[str, Any], image_name: str = "disk_image") -> str:
        """Generate HTML report."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = self.output_dir / f"forensic_report_{timestamp}.html"
        
        risk_level = results.get('risk_level', 'Unknown')
        risk_colors = {
            'Critical': '#dc2626',
            'High': '#ea580c', 
            'Medium': '#ca8a04',
            'Low': '#16a34a'
        }
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Forensic Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1e293b; border-bottom: 3px solid #38bdf8; padding-bottom: 10px; }}
        h2 {{ color: #334155; margin-top: 30px; }}
        .meta {{ color: #64748b; font-size: 14px; }}
        .risk-banner {{ padding: 15px; border-radius: 6px; color: white; font-weight: bold; margin: 20px 0; }}
        .partition {{ background: #f8fafc; padding: 15px; margin: 10px 0; border-left: 4px solid #38bdf8; }}
        .hidden {{ border-left-color: #ef4444; background: #fef2f2; }}
        .encrypted {{ border-left-color: #f59e0b; background: #fffbeb; }}
        .finding {{ padding: 15px; margin: 10px 0; border-radius: 6px; }}
        .finding.high {{ background: #fef2f2; border-left: 4px solid #ef4444; }}
        .finding.medium {{ background: #fffbeb; border-left: 4px solid #f59e0b; }}
        .finding.low {{ background: #f0fdf4; border-left: 4px solid #22c55e; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-size: 12px; font-weight: bold; }}
        .badge.high {{ background: #ef4444; }}
        .badge.medium {{ background: #f59e0b; }}
        .badge.low {{ background: #22c55e; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Forensic Disk Analysis Report</h1>
        <p class="meta">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Image: {image_name}<br>
            Output: {self.output_dir}
        </p>
        
        <div class="risk-banner" style="background: {risk_colors.get(risk_level, '#6b7280')}">
            Risk Level: {risk_level}
        </div>
        
        <p><strong>Summary:</strong> {results.get('summary', 'No summary available')}</p>
        
        <h2>Partition Analysis</h2>
"""
        
        partitions = results.get('partitions', [])
        if partitions:
            for i, part in enumerate(partitions):
                cls = ""
                warning = ""
                if part.get('is_hidden'):
                    cls = "hidden"
                    warning += " [HIDDEN] "
                if part.get('is_encrypted'):
                    cls = "encrypted"
                    warning += f" [ENCRYPTED: {part.get('encryption_type', 'Unknown')}] "
                    
                html += f"""
        <div class="partition {cls}">
            <strong>Partition {i}</strong>{warning}<br>
            Start: {part.get('start', 'N/A')} sectors | End: {part.get('end', 'N/A')} sectors<br>
            Type: {part.get('desc', 'N/A')}
        </div>
"""
        else:
            html += "<p>No partition information available.</p>"
        
        html += """
        <h2>Timestamp Analysis</h2>
"""
        
        timestamp_analysis = results.get('timestamp_analysis', {})
        for partition, ts_data in timestamp_analysis.items():
            html += f"<h3>{partition}</h3>"
            
            usn_status = ts_data.get('usn_journal_status', {})
            if usn_status.get('found'):
                html += f"<p><strong>USN Journal:</strong> FOUND ({usn_status.get('max_size', 0)} bytes)</p>"
            else:
                html += f"<p><strong>USN Journal:</strong> NOT FOUND<br><em>Reason: {usn_status.get('reason', 'Unknown')}</em></p>"
            
            inconsistencies = ts_data.get('inconsistencies', [])
            if inconsistencies:
                html += f"<p><strong>Inconsistencies:</strong> {len(inconsistencies)}</p><ul>"
                for inc in inconsistencies[:10]:
                    severity = inc.get('severity', 'medium')
                    html += f"<li><span class='badge {severity}'>{severity.upper()}</span> {inc.get('type', 'unknown')}: {inc.get('message', '')}</li>"
                html += "</ul>"
            else:
                html += "<p>No timestamp inconsistencies detected.</p>"
        
        html += """
        <h2>Anti-Forensic Detection</h2>
"""
        
        antiforensic = results.get('antiforensic_results', {})
        findings = antiforensic.get('findings', [])
        
        if findings:
            for finding in findings:
                severity = finding.get('severity', 'medium')
                html += f"""
        <div class="finding {severity}">
            <span class="badge {severity}">{finding.get('severity', 'medium').upper()}</span>
            <strong>{finding.get('technique', 'Unknown')}</strong>
            <p><strong>Evidence:</strong> {finding.get('evidence', 'N/A')}</p>
            <p><strong>Explanation:</strong> {finding.get('explanation', 'N/A')}</p>
            <p><strong>Recommendation:</strong> {finding.get('recommendation', 'N/A')}</p>
        </div>
"""
        else:
            html += "<p>No anti-forensic indicators found.</p>"
        
        html += """
        <h2>Recommendations</h2>
        <ul>
"""
        
        for rec in results.get('recommendations', []):
            html += f"<li>{rec}</li>"
        
        html += """
        </ul>
        
        <hr>
        <p class="meta">End of Report</p>
    </div>
</body>
</html>
"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(html_file)


def generate_report(output_dir: str, results: Dict[str, Any], image_name: str = "disk_image") -> Dict[str, str]:
    """Generate all report formats."""
    generator = ForensicReportGenerator(output_dir)
    
    txt_report = generator.generate_pdf_report(results, image_name)
    html_report = generator.generate_html_report(results, image_name)
    
    return {
        "txt": txt_report,
        "html": html_report
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python forensic_report.py <output_dir> [image_name]")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    image_name = sys.argv[2] if len(sys.argv) > 2 else "disk_image"
    
    results = {}
    summary_file = Path(output_dir) / "extraction_summary.json"
    if summary_file.exists():
        with open(summary_file) as f:
            results = json.load(f)
    
    reports = generate_report(output_dir, results, image_name)
    print(f"Reports generated:")
    print(f"  Text: {reports['txt']}")
    print(f"  HTML: {reports['html']}")
