"""Data Wipe and File Shredding Detection Module

Detects evidence of file shredding, data wiping, and secure deletion tools.
This includes detection of:
- Encrypted/shredded files (high entropy)
- Known shredding tool artifacts
- Free space wiping
- Zero-filled regions
- Random data overwrite patterns
"""

import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class WipeIndicator:
    """Represents a detected data wipe indicator."""
    indicator_type: str
    severity: str
    description: str
    evidence: str
    confidence: float
    file_path: Optional[str] = None
    offset: Optional[int] = None


@dataclass
class DataWipeResult:
    """Result of data wipe detection analysis."""
    wipe_detected: bool
    confidence: float
    indicators: List[WipeIndicator]
    summary: str
    details: Dict[str, Any]


class DataWipeDetector:
    """Detect evidence of data wiping and file shredding."""
    
    HIGH_ENTROPY_THRESHOLD = 7.8
    MODERATE_ENTROPY_THRESHOLD = 7.0
    
    KNOWN_SHRED_TOOLS = [
        "sdelete",
        "cipher", 
        "shred",
        "wipe",
        "eraser",
        "secure-delete",
        "bleachbit",
        "ccleaner",
        "dbAN",
        "file-shredder",
        "veracrypt",
        "truecrypt",
    ]
    
    SHREDDER_REGEX_PATTERNS = [
        r"shred_temp\.dat",
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        r"\.shred$",
        r"wipe\.tmp$",
        r"wipe\d+\.dat$",
    ]
    
    def __init__(self, chunk_size: int = 4096):
        self.chunk_size = chunk_size
    
    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0
        
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        entropy = 0.0
        data_len = len(data)
        
        for count in byte_counts:
            if count == 0:
                continue
            probability = count / data_len
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def analyze_file_entropy(self, file_path: str, sample_size: int = 65536) -> Dict[str, Any]:
        """Analyze entropy of a file to detect encryption/shredding."""
        try:
            file_size = os.path.getsize(file_path)
            
            if file_size == 0:
                return {"entropy": 0.0, "is_high_entropy": False, "size": 0}
            
            with open(file_path, 'rb') as f:
                start_data = f.read(min(sample_size, file_size))
                start_entropy = self.calculate_entropy(start_data)
                
                if file_size > sample_size:
                    f.seek(file_size // 2)
                    middle_data = f.read(min(sample_size // 2, file_size - file_size // 2))
                    middle_entropy = self.calculate_entropy(middle_data)
                else:
                    middle_entropy = start_entropy
                
                if file_size > sample_size:
                    f.seek(max(0, file_size - sample_size))
                    end_data = f.read(sample_size)
                    end_entropy = self.calculate_entropy(end_data)
                else:
                    end_entropy = start_entropy
            
            avg_entropy = (start_entropy + middle_entropy + end_entropy) / 3
            is_high_entropy = avg_entropy > self.HIGH_ENTROPY_THRESHOLD
            
            return {
                "entropy": avg_entropy,
                "start_entropy": start_entropy,
                "middle_entropy": middle_entropy,
                "end_entropy": end_entropy,
                "is_high_entropy": is_high_entropy,
                "size": file_size,
            }
        except Exception as e:
            return {"error": str(e), "entropy": 0.0, "is_high_entropy": False}
    
    def detect_zero_filled_regions(self, file_path: str, sample_size: int = 1024 * 1024) -> Dict[str, Any]:
        """Detect zero-filled regions in a file (common wiping method)."""
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {"zero_regions": 0, "zero_percentage": 0.0}
            
            zero_chunks = 0
            total_chunks = 0
            
            with open(file_path, 'rb') as f:
                for offset in range(0, min(file_size, sample_size), self.chunk_size):
                    f.seek(offset)
                    chunk = f.read(self.chunk_size)
                    if len(chunk) < self.chunk_size:
                        break
                    
                    total_chunks += 1
                    if all(b == 0 for b in chunk):
                        zero_chunks += 1
            
            zero_percentage = (zero_chunks / total_chunks * 100) if total_chunks > 0 else 0
            
            return {
                "zero_regions": zero_chunks,
                "zero_percentage": zero_percentage,
                "is_wiped": zero_percentage > 50,
            }
        except Exception as e:
            return {"error": str(e), "zero_regions": 0, "zero_percentage": 0.0}
    
    def detect_random_pattern(self, file_path: str, sample_size: int = 65536) -> Dict[str, Any]:
        """Detect random data patterns (indicates secure overwrite)."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read(sample_size)
            
            if len(data) < 256:
                return {"is_random": False, "confidence": 0.0}
            
            byte_counts = [0] * 256
            for byte in data:
                byte_counts[byte] += 1
            
            unique_bytes = sum(1 for c in byte_counts if c > 0)
            byte_diversity = unique_bytes / 256
            
            entropy = self.calculate_entropy(data)
            is_random = entropy > 7.5 and byte_diversity > 0.8
            
            return {
                "is_random": is_random,
                "entropy": entropy,
                "byte_diversity": byte_diversity,
                "unique_bytes": unique_bytes,
                "confidence": entropy / 8.0,
            }
        except Exception as e:
            return {"error": str(e), "is_random": False, "confidence": 0.0}
    
    def check_shredder_artifacts(self, directory: str) -> List[WipeIndicator]:
        """Check for file shredder tool artifacts in directory."""
        indicators = []
        
        EXCLUDED_PATTERNS = [
            'analysis.json', 'analysis_', 'preprocessed_', 'report_',
            'timestamp_', 'metadata_', 'antiforensic_', 'hidden_volume_',
            'data_wipe_', 'forensic_', '.json', '.txt', '.csv'
        ]
        
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return indicators
            
            for item in dir_path.rglob("*"):
                if not item.is_file():
                    continue
                
                name = item.name.lower()
                stem = item.stem.lower()
                
                if any(excl in stem for excl in EXCLUDED_PATTERNS):
                    continue
                
                for tool in self.KNOWN_SHRED_TOOLS:
                    if tool in name and len(name) < 50:
                        indicators.append(WipeIndicator(
                            indicator_type="shredder_artifact",
                            severity="high",
                            description=f"Known file shredder tool artifact: {tool}",
                            evidence=f"File: {item.name}",
                            confidence=0.9,
                            file_path=str(item),
                        ))
                        break
                
                for pattern in self.SHREDDER_REGEX_PATTERNS:
                    if re.search(pattern, item.name, re.IGNORECASE):
                        indicators.append(WipeIndicator(
                            indicator_type="shredder_pattern",
                            severity="medium",
                            description="Possible file shredder temporary file pattern",
                            evidence=f"Pattern match: {item.name}",
                            confidence=0.6,
                            file_path=str(item),
                        ))
                        break
                
                try:
                    if item.stat().st_size > 0:
                        entropy_result = self.analyze_file_entropy(str(item))
                        if entropy_result.get("is_high_entropy", False):
                            indicators.append(WipeIndicator(
                                indicator_type="high_entropy_file",
                                severity="medium",
                                description=f"High entropy file ({entropy_result['entropy']:.2f}) - possibly encrypted or shredded",
                                evidence=f"File: {item.name}, Entropy: {entropy_result['entropy']:.2f}",
                                confidence=0.7,
                                file_path=str(item),
                            ))
                except:
                    pass
                    
        except Exception as e:
            pass
        
        return indicators
    
    def detect_wiped_free_space(self, file_path: str, partition_offset: int = 0, 
                                 partition_size: int = None) -> Dict[str, Any]:
        """Analyze disk image for wiped free space patterns."""
        try:
            if partition_size is None:
                partition_size = os.path.getsize(file_path)
            
            sample_size = min(16 * 1024 * 1024, partition_size)
            scan_start = partition_offset + (1024 * 1024)
            
            if scan_start >= partition_size:
                return {"wiped_free_space": False, "evidence": "Cannot scan"}
            
            high_entropy_regions = 0
            zero_regions = 0
            total_regions = 0
            
            with open(file_path, 'rb') as f:
                offset = scan_start
                while offset < scan_start + sample_size:
                    f.seek(offset)
                    chunk = f.read(self.chunk_size)
                    
                    if not chunk or len(chunk) < self.chunk_size:
                        break
                    
                    total_regions += 1
                    entropy = self.calculate_entropy(chunk)
                    
                    if entropy > 7.5:
                        high_entropy_regions += 1
                    elif entropy < 0.5:
                        zero_regions += 1
                    
                    offset += self.chunk_size
            
            if total_regions == 0:
                return {"wiped_free_space": False, "evidence": "No regions scanned"}
            
            high_entropy_pct = high_entropy_regions / total_regions * 100
            zero_pct = zero_regions / total_regions * 100
            
            wiped = high_entropy_pct > 30 or zero_pct > 30
            
            return {
                "wiped_free_space": wiped,
                "high_entropy_percentage": high_entropy_pct,
                "zero_percentage": zero_pct,
                "total_regions": total_regions,
                "method": "random_overwrite" if high_entropy_pct > 30 else "zero_fill" if zero_pct > 30 else "none",
            }
        except Exception as e:
            return {"error": str(e), "wiped_free_space": False}
    
    def analyze_partition(self, image_path: str, partition_info: Dict) -> DataWipeResult:
        """Analyze a partition for data wiping evidence."""
        indicators = []
        
        offset = partition_info.get("start_sector", 0) * 512
        size = partition_info.get("size_sectors", 0) * 512
        
        if offset == 0 or size == 0:
            return DataWipeResult(
                wipe_detected=False,
                confidence=0.0,
                indicators=[],
                summary="Invalid partition",
                details={}
            )
        
        wipe_result = self.detect_wiped_free_space(image_path, offset, size)
        
        if wipe_result.get("wiped_free_space", False):
            indicators.append(WipeIndicator(
                indicator_type="wiped_free_space",
                severity="high",
                description=f"Free space appears to be wiped using {wipe_result.get('method', 'unknown')} method",
                evidence=f"High entropy: {wipe_result.get('high_entropy_percentage', 0):.1f}%, Zero: {wipe_result.get('zero_percentage', 0):.1f}%",
                confidence=0.8,
                offset=offset,
            ))
        
        detected = len(indicators) > 0
        confidence = sum(i.confidence for i in indicators) / len(indicators) if indicators else 0.0
        
        summary = "No data wiping detected"
        if detected:
            methods = [i.indicator_type for i in indicators]
            summary = f"Data wiping indicators found: {', '.join(set(methods))}"
        
        return DataWipeResult(
            wipe_detected=detected,
            confidence=confidence,
            indicators=indicators,
            summary=summary,
            details={"partition_scan": wipe_result}
        )
    
    def analyze_directory(self, directory: str) -> DataWipeResult:
        """Analyze extracted files for data wiping evidence."""
        indicators = []
        
        artifacts = self.check_shredder_artifacts(directory)
        indicators.extend(artifacts)
        
        detected = len(indicators) > 0
        confidence = sum(i.confidence for i in indicators) / len(indicators) if indicators else 0.0
        
        if detected:
            summary = f"Found {len(indicators)} data wiping indicator(s)"
        else:
            summary = "No data wiping detected in extracted files"
        
        return DataWipeResult(
            wipe_detected=detected,
            confidence=confidence,
            indicators=indicators,
            summary=summary,
            details={"files_analyzed": True}
        )


def detect_data_wipe(image_path: str, output_dir: str, partitions: List[Dict] = None) -> Dict[str, Any]:
    """Main function to detect data wiping across partitions and files.
    
    Args:
        image_path: Path to disk image
        output_dir: Directory with extracted artifacts
        partitions: List of partition dictionaries
        
    Returns:
        Dictionary with wipe detection results
    """
    detector = DataWipeDetector()
    
    results = {
        "wipe_detected": False,
        "confidence": 0.0,
        "indicators": [],
        "summary": "No data wiping detected",
        "details": {},
    }
    
    dir_indicators = detector.analyze_directory(output_dir)
    if dir_indicators.wipe_detected:
        results["wipe_detected"] = True
        results["confidence"] = max(results["confidence"], dir_indicators.confidence)
        results["indicators"].extend([
            {
                "type": i.indicator_type,
                "severity": i.severity,
                "description": i.description,
                "evidence": i.evidence,
                "confidence": i.confidence,
                "file_path": i.file_path,
            }
            for i in dir_indicators.indicators
        ])
        results["details"]["directory_analysis"] = dir_indicators.details
    
    if partitions:
        partition_results = []
        for partition in partitions:
            slot = partition.get("slot", "")
            if slot in ["Meta", "meta"] or "-------" in str(slot):
                continue
            
            size = partition.get("size_sectors", 0)
            if size < 10000:
                continue
            
            result = detector.analyze_partition(image_path, partition)
            if result.wipe_detected:
                results["wipe_detected"] = True
                results["confidence"] = max(results["confidence"], result.confidence)
                results["indicators"].extend([
                    {
                        "type": i.indicator_type,
                        "severity": i.severity,
                        "description": i.description,
                        "evidence": i.evidence,
                        "confidence": i.confidence,
                        "offset": i.offset,
                    }
                    for i in result.indicators
                ])
                partition_results.append(result.details)
        
        if partition_results:
            results["details"]["partition_analysis"] = partition_results
    
    if results["wipe_detected"]:
        results["summary"] = f"Data wiping detected with {len(results['indicators'])} indicator(s)"
    else:
        results["summary"] = "No evidence of data wiping or file shredding detected"
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_wipe_detector.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    print(f"[*] Analyzing: {directory}")
    
    detector = DataWipeDetector()
    result = detector.analyze_directory(directory)
    
    print(f"\nWipe Detected: {result.wipe_detected}")
    print(f"Confidence: {result.confidence * 100:.1f}%")
    print(f"Summary: {result.summary}")
    print(f"\nIndicators ({len(result.indicators)}):")
    for indicator in result.indicators:
        print(f"  - [{indicator.severity.upper()}] {indicator.description}")
        print(f"    Evidence: {indicator.evidence}")
