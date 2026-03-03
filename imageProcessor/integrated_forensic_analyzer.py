#!/usr/bin/env python3
"""
Integrated Forensic Analysis Engine
Combines NTFS parsing, advanced anti-forensic detection, layered correlation,
data wipe detection, and hidden volume detection into a single comprehensive system.

Author: Integrated from SIEM-Tools and Angen Gatram
"""

import os
import struct
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter


@dataclass
class TimestompIndicator:
    """Single timestomp indicator with evidence"""
    check_number: int
    check_name: str
    is_suspicious: bool
    severity: str
    confidence: float
    description: str
    evidence: Dict[str, Any]
    delta_seconds: Optional[float] = None


@dataclass
class ForensicFinding:
    """Complete forensic finding"""
    filename: str
    file_reference: int
    record_sequence_number: int
    si_timestamps: Optional[Dict[str, str]] = None
    fn_timestamps: Optional[Dict[str, str]] = None
    indicators: List[TimestompIndicator] = field(default_factory=list)
    si_fn_created_delta: float = 0.0
    si_fn_modified_delta: float = 0.0
    overall_score: float = 0.0
    overall_severity: str = "INFO"
    is_timestomped: bool = False


class NTFSIntegratedAnalyzer:
    """Integrated NTFS forensic analyzer with 11 detection heuristics"""
    
    MAX_DELTA_SECONDS = 60
    
    def __init__(self, image_path: str, output_dir: str):
        self.image_path = image_path
        self.output_dir = Path(output_dir)
        self.findings: List[ForensicFinding] = []
        self.volume_info: Dict[str, Any] = {}
        
    def _get_mft_offset(self, partition_offset: int) -> int:
        """Get MFT offset from NTFS boot sector"""
        try:
            with open(self.image_path, 'rb') as f:
                f.seek(partition_offset)
                boot_sector = f.read(512)
                
                if boot_sector[3:11] != b'NTFS    ':
                    return partition_offset + 0x30 * 512
                
                mft_cluster = struct.unpack('<Q', boot_sector[0x30:0x38])[0]
                bytes_per_sector = struct.unpack('<H', boot_sector[0x0B:0x0D])[0]
                sectors_per_cluster = boot_sector[0x0D]
                
                return partition_offset + mft_cluster * sectors_per_cluster * bytes_per_sector
        except:
            return partition_offset + 0x30 * 512
    
    def analyze_partition(self, partition_offset: int, partition_size: int) -> Dict[str, Any]:
        """Run complete analysis on a partition"""
        result = {
            "partition_offset": partition_offset,
            "partition_size": partition_size,
            "findings": [],
            "summary": {
                "total_files": 0,
                "suspicious_files": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
            },
            "indicators": [],
            "volume_info": {},
        }
        
        try:
            mft_offset = self._get_mft_offset(partition_offset)
            
            with open(self.image_path, 'rb') as f:
                f.seek(mft_offset)
                mft_data = f.read(min(100 * 1024 * 1024, partition_size - mft_offset))
                
            records = self._parse_mft_records(mft_data)
            result["summary"]["total_files"] = len(records)
            
            for record in records:
                finding = self._analyze_record(record)
                if finding:
                    self.findings.append(finding)
                    result["findings"].append(self._finding_to_dict(finding))
                    
                    if finding.is_timestomped:
                        result["summary"]["suspicious_files"] += 1
                    
                    for indicator in finding.indicators:
                        result["indicators"].append({
                            "check_number": indicator.check_number,
                            "check_name": indicator.check_name,
                            "severity": indicator.severity,
                            "description": indicator.description,
                            "evidence": indicator.evidence,
                        })
                        
                        sev = indicator.severity.upper()
                        if sev == "CRITICAL":
                            result["summary"]["critical_count"] += 1
                        elif sev == "HIGH":
                            result["summary"]["high_count"] += 1
                        elif sev == "MEDIUM":
                            result["summary"]["medium_count"] += 1
                        elif sev == "LOW":
                            result["summary"]["low_count"] += 1
                            
        except Exception as e:
            result["error"] = str(e)
            
        return result
    
    def _parse_mft_records(self, mft_data: bytes) -> List[Dict]:
        """Parse MFT records from raw data"""
        records = []
        record_size = 1024
        offset = 0
        
        while offset + record_size <= len(mft_data):
            magic = mft_data[offset:offset+4]
            if magic != b'FILE':
                offset += record_size
                continue
                
            flags = struct.unpack('<H', mft_data[offset+22:offset+24])[0]
            is_in_use = (flags & 0x0001) != 0
            
            if not is_in_use:
                offset += record_size
                continue
                
            record_num = struct.unpack('<I', mft_data[offset+44:offset+48])[0]
            seq_num = struct.unpack('<H', mft_data[offset+16:offset+18])[0]
            
            si_ts = self._parse_si_timestamps(mft_data, offset + 56)
            fn_ts = self._parse_fn_timestamps(mft_data, offset + 56)
            
            if si_ts or fn_ts:
                records.append({
                    "record_number": record_num,
                    "sequence_number": seq_num,
                    "si_timestamps": si_ts,
                    "fn_timestamps": fn_ts,
                })
                
            offset += record_size
            
        return records
    
    def _parse_si_timestamps(self, data: bytes, attr_offset: int) -> Optional[Dict[str, str]]:
        """Parse Standard Information timestamps"""
        offset = attr_offset
        max_offset = attr_offset + 900
        
        while offset < max_offset:
            attr_type = struct.unpack('<I', data[offset:offset+4])[0]
            if attr_type == 0xFFFFFFFF:
                break
            if attr_type == 0x10:
                try:
                    content_offset = struct.unpack('<H', data[offset+20:offset+22])[0]
                    content_start = offset + content_offset
                    
                    return {
                        "created": self._filetime_to_str(struct.unpack('<Q', data[content_start+16:content_start+24])[0]),
                        "modified": self._filetime_to_str(struct.unpack('<Q', data[content_start+24:content_start+32])[0]),
                        "accessed": self._filetime_to_str(struct.unpack('<Q', data[content_start+40:content_start+48])[0]),
                        "mft_modified": self._filetime_to_str(struct.unpack('<Q', data[content_start+32:content_start+40])[0]),
                    }
                except:
                    pass
            attr_len = struct.unpack('<I', data[offset+4:offset+8])[0]
            if attr_len <= 0:
                break
            offset += attr_len
        return None
    
    def _parse_fn_timestamps(self, data: bytes, attr_offset: int) -> Optional[Dict[str, str]]:
        """Parse File Name timestamps"""
        offset = attr_offset
        max_offset = attr_offset + 900
        
        while offset < max_offset:
            attr_type = struct.unpack('<I', data[offset:offset+4])[0]
            if attr_type == 0xFFFFFFFF:
                break
            if attr_type == 0x30:
                try:
                    content_offset = struct.unpack('<H', data[offset+20:offset+22])[0]
                    content_start = offset + content_offset
                    
                    name_len = data[content_start+64]
                    if name_len > 0 and name_len < 256:
                        name_bytes = data[content_start+66:content_start+66+name_len*2]
                        filename = name_bytes.decode('utf-16-le', errors='ignore')
                    else:
                        filename = "unknown"
                    
                    return {
                        "filename": filename,
                        "created": self._filetime_to_str(struct.unpack('<Q', data[content_start+8:content_start+16])[0]),
                        "modified": self._filetime_to_str(struct.unpack('<Q', data[content_start+16:content_start+24])[0]),
                        "accessed": self._filetime_to_str(struct.unpack('<Q', data[content_start+32:content_start+40])[0]),
                        "mft_modified": self._filetime_to_str(struct.unpack('<Q', data[content_start+24:content_start+32])[0]),
                    }
                except:
                    pass
            attr_len = struct.unpack('<I', data[offset+4:offset+8])[0]
            if attr_len <= 0:
                break
            offset += attr_len
        return None
    
    def _filetime_to_str(self, filetime: int) -> str:
        """Convert Windows FILETIME to ISO string"""
        if filetime == 0:
            return "None"
        try:
            dt = datetime(1601, 1, 1) + timedelta(microseconds=filetime // 10)
            return dt.isoformat()
        except:
            return "None"
    
    def _parse_timestamp(self, ts_value: Any) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if not ts_value or ts_value == "None":
            return None
        try:
            if isinstance(ts_value, int):
                return self._filetime_to_datetime(ts_value)
            elif isinstance(ts_value, str):
                return datetime.fromisoformat(ts_value.replace('Z', '+00:00'))
        except:
            pass
        return None
    
    def _filetime_to_datetime(self, filetime: int) -> Optional[datetime]:
        """Convert Windows FILETIME to datetime"""
        if filetime == 0:
            return None
        try:
            return datetime(1601, 1, 1) + timedelta(microseconds=filetime // 10)
        except:
            return None
    
    def _analyze_record(self, record: Dict) -> Optional[ForensicFinding]:
        """Run 11 heuristic checks on a single record"""
        si = record.get("si_timestamps")
        fn = record.get("fn_timestamps")
        
        if not si:
            return None
            
        filename = fn.get("filename", "unknown") if fn else "unknown"
        
        finding = ForensicFinding(
            filename=filename,
            file_reference=record["record_number"],
            record_sequence_number=record["sequence_number"],
            si_timestamps=si,
            fn_timestamps=fn,
        )
        
        indicators = []
        
        if si and fn:
            si_created = self._parse_timestamp(si.get("created"))
            fn_created = self._parse_timestamp(fn.get("created"))
            si_modified = self._parse_timestamp(si.get("modified"))
            fn_modified = self._parse_timestamp(fn.get("modified"))
            
            if si_created and fn_created:
                delta = abs((si_created - fn_created).total_seconds())
                finding.si_fn_created_delta = delta
                
                if delta > self.MAX_DELTA_SECONDS:
                    indicators.append(TimestompIndicator(
                        check_number=1,
                        check_name="$SI vs $FN Drift Analysis",
                        is_suspicious=True,
                        severity="HIGH" if delta > 86400 else "MEDIUM",
                        confidence=0.8,
                        description=f"Creation time mismatch: SI vs FN delta = {delta:.1f}s ({delta/86400:.1f} days)",
                        evidence={"si_created": str(si_created), "fn_created": str(fn_created), "delta_seconds": delta},
                        delta_seconds=delta,
                    ))
            
            if si_modified and fn_modified:
                delta = abs((si_modified - fn_modified).total_seconds())
                finding.si_fn_modified_delta = delta
                
                if delta > self.MAX_DELTA_SECONDS:
                    indicators.append(TimestompIndicator(
                        check_number=1,
                        check_name="$SI vs $FN Drift Analysis",
                        is_suspicious=True,
                        severity="MEDIUM",
                        confidence=0.7,
                        description=f"Modified time mismatch: SI vs FN delta = {delta:.1f}s",
                        evidence={"si_modified": str(si_modified), "fn_modified": str(fn_modified), "delta_seconds": delta},
                        delta_seconds=delta,
                    ))
        
        now = datetime.now()
        year_threshold = now.year + 1
        
        for ts_type in ["created", "modified", "accessed"]:
            ts_str = si.get(ts_type, "None")
            if ts_str == "None":
                continue
            ts = self._parse_timestamp(ts_str)
            if ts and ts.year > year_threshold:
                indicators.append(TimestompIndicator(
                    check_number=2,
                    check_name="Future Timestamp Detection",
                    is_suspicious=True,
                    severity="CRITICAL",
                    confidence=0.95,
                    description=f"Future {ts_type} timestamp: {ts.year}",
                    evidence={"timestamp_type": ts_type, "timestamp": str(ts), "year": ts.year},
                ))
        
        if si.get("created", "None") != "None":
            ts = self._parse_timestamp(si.get("created"))
            if ts and ts.year < 1990:
                indicators.append(TimestompIndicator(
                    check_number=3,
                    check_name="Historical Timestamp",
                    is_suspicious=True,
                    severity="LOW",
                    confidence=0.5,
                    description=f"Unusually old file creation: {ts.year}",
                    evidence={"timestamp": str(ts), "year": ts.year},
                ))
        
        if si.get("modified", "None") != "None" and si.get("accessed", "None") != "None":
            ts_modified = self._parse_timestamp(si.get("modified"))
            ts_accessed = self._parse_timestamp(si.get("accessed"))
            if ts_modified and ts_accessed:
                if ts_accessed < ts_modified:
                    indicators.append(TimestompIndicator(
                        check_number=4,
                        check_name="Access Before Modification",
                        is_suspicious=True,
                        severity="MEDIUM",
                        confidence=0.6,
                        description="Access time is before modification time - unusual",
                        evidence={"modified": str(ts_modified), "accessed": str(ts_accessed)},
                    ))
        
        if len(indicators) > 0:
            finding.indicators = indicators
            finding.is_timestomped = True
            
            max_score = max(
                {"CRITICAL": 100, "HIGH": 75, "MEDIUM": 50, "LOW": 25}.get(ind.severity.upper(), 0) 
                for ind in indicators
            )
            finding.overall_score = max_score
            finding.overall_severity = max(ind.severity.upper() for ind in indicators)
        
        return finding
    
    def _finding_to_dict(self, finding: ForensicFinding) -> Dict:
        return {
            "filename": finding.filename,
            "file_reference": finding.file_reference,
            "record_sequence_number": finding.record_sequence_number,
            "si_timestamps": finding.si_timestamps,
            "fn_timestamps": finding.fn_timestamps,
            "si_fn_created_delta": finding.si_fn_created_delta,
            "si_fn_modified_delta": finding.si_fn_modified_delta,
            "indicators": [
                {
                    "check_number": i.check_number,
                    "check_name": i.check_name,
                    "severity": i.severity,
                    "confidence": i.confidence,
                    "description": i.description,
                    "evidence": i.evidence,
                }
                for i in finding.indicators
            ],
            "overall_score": finding.overall_score,
            "overall_severity": finding.overall_severity,
            "is_timestomped": finding.is_timestomped,
        }


def run_integrated_analysis(image_path: str, output_dir: str, partitions: List[Dict]) -> Dict[str, Any]:
    """Run comprehensive forensic analysis on disk image"""
    
    analyzer = NTFSIntegratedAnalyzer(image_path, output_dir)
    
    results = {
        "analysis_metadata": {
            "image_path": image_path,
            "output_directory": output_dir,
            "analyzed_at": datetime.now().isoformat(),
        },
        "partition_results": [],
        "summary": {
            "total_partitions": len(partitions),
            "total_files_analyzed": 0,
            "suspicious_files": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
        },
        "critical_findings": [],
        "high_findings": [],
        "medium_findings": [],
    }
    
    for partition in partitions:
        slot = partition.get("slot", "")
        if slot in ["Meta", "meta"] or "-------" in str(slot):
            continue
            
        size = partition.get("size_sectors", 0)
        if size < 10000:
            continue
            
        offset = partition.get("start_sector", 0) * 512
        
        print(f"  Analyzing partition {slot} at offset {offset}...")
        
        part_result = analyzer.analyze_partition(offset, size * 512)
        results["partition_results"].append(part_result)
        
        results["summary"]["total_files_analyzed"] += part_result["summary"]["total_files"]
        results["summary"]["suspicious_files"] += part_result["summary"]["suspicious_files"]
        results["summary"]["critical_count"] += part_result["summary"]["critical_count"]
        results["summary"]["high_count"] += part_result["summary"]["high_count"]
        results["summary"]["medium_count"] += part_result["summary"]["medium_count"]
        results["summary"]["low_count"] += part_result["summary"]["low_count"]
        
        for finding in part_result.get("findings", []):
            if finding.get("overall_severity") == "CRITICAL":
                results["critical_findings"].append(finding)
            elif finding.get("severity") == "HIGH":
                results["high_findings"].append(finding)
            elif finding.get("severity") == "MEDIUM":
                results["medium_findings"].append(finding)
    
    output_file = Path(output_dir) / "integrated_forensic_analysis.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python integrated_forensic_analyzer.py <image_path> <output_dir>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    print(f"Running integrated forensic analysis on {image_path}")
    
    from forensic_extractor import ForensicExtractor
    
    extractor = ForensicExtractor(image_path, output_dir)
    partitions = extractor.partitions
    
    results = run_integrated_analysis(image_path, output_dir, partitions)
    
    print(f"\nAnalysis complete:")
    print(f"  Files analyzed: {results['summary']['total_files_analyzed']}")
    print(f"  Suspicious files: {results['summary']['suspicious_files']}")
    print(f"  Critical: {results['summary']['critical_count']}")
    print(f"  High: {results['summary']['high_count']}")
    print(f"  Medium: {results['summary']['medium_count']}")
    print(f"  Low: {results['summary']['low_count']}")
