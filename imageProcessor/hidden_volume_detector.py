"""Hidden Volume and Hidden OS Detection Module

Detects VeraCrypt/TrueCrypt hidden volumes and hidden OS installations
using entropy analysis and artifact detection.
"""

import math
import struct
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class EntropyRegion:
    """Represents a region with specific entropy characteristics."""
    offset: int
    size: int
    avg_entropy: float
    is_encrypted: bool


@dataclass
class HiddenVolumeResult:
    """Result of hidden volume detection."""
    detected: bool
    confidence: float
    method: str
    estimated_size: Optional[int] = None
    details: str = ""


class HiddenVolumeDetector:
    """Detect hidden volumes and hidden OS installations."""
    
    # VeraCrypt magic bytes and signatures
    VERACRYPT_MAGIC = b'VERA'
    TRUECRYPT_MAGIC = b'TRUE'
    
    # Entropy thresholds
    HIGH_ENTROPY_THRESHOLD = 7.8
    MODERATE_ENTROPY_THRESHOLD = 6.5
    
    # Windows OS artifacts that may leak from hidden OS
    OS_ARTIFACTS = [
        b'Windows',
        b'Program Files',
        b'Users\\',
        b'bootmgr',
        b'\\Windows\\System32\\',
        b'\\Users\\',
        b'NTUSER.DAT',
        b'USRCLASS.DAT',
        b'pagefile.sys',
        b'hiberfil.sys',
    ]
    
    def __init__(self, chunk_size: int = 4096):
        self.chunk_size = chunk_size
    
    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data.
        
        Args:
            data: Bytes to analyze
            
        Returns:
            Entropy value (0-8, where 8 is maximum randomness)
        """
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
    
    def calculate_entropy_regions(self, image_path: str, start_offset: int, 
                                  size: int, step: int = None) -> List[EntropyRegion]:
        """Calculate entropy in sliding windows across a region.
        
        Args:
            image_path: Path to disk image
            start_offset: Starting byte offset
            size: Size to scan in bytes
            step: Step size (defaults to chunk_size // 2)
            
        Returns:
            List of EntropyRegion objects
        """
        if step is None:
            step = self.chunk_size // 2
        
        regions = []
        
        with open(image_path, 'rb') as f:
            offset = start_offset
            while offset < start_offset + size:
                f.seek(offset)
                chunk = f.read(min(self.chunk_size, start_offset + size - offset))
                
                if not chunk:
                    break
                
                entropy = self.calculate_entropy(chunk)
                is_encrypted = entropy > self.HIGH_ENTROPY_THRESHOLD
                
                regions.append(EntropyRegion(
                    offset=offset,
                    size=len(chunk),
                    avg_entropy=entropy,
                    is_encrypted=is_encrypted
                ))
                
                offset += step
        
        return regions
    
    def detect_encrypted_regions(self, image_path: str, partition_offset: int,
                                 partition_size: int) -> Dict[str, Any]:
        """Detect encrypted regions within a partition.
        
        Args:
            image_path: Path to disk image
            partition_offset: Partition start offset in bytes
            partition_size: Partition size in bytes
            
        Returns:
            Dictionary with encrypted region information
        """
        # Skip the first 1MB (likely contains headers)
        scan_start = partition_offset + (1024 * 1024)
        
        # Limit scan size for performance - scan max 64MB
        max_scan = 64 * 1024 * 1024
        scan_size = min(partition_size - (1024 * 1024), max_scan)
        
        regions = self.calculate_entropy_regions(image_path, scan_start, scan_size)
        
        encrypted_bytes = sum(r.size for r in regions if r.is_encrypted)
        total_bytes = sum(r.size for r in regions)
        
        encrypted_regions = [r for r in regions if r.is_encrypted]
        
        # Find clusters of encrypted regions
        clusters = self._find_encrypted_clusters(encrypted_regions)
        
        return {
            "total_regions_scanned": len(regions),
            "encrypted_regions": len(encrypted_regions),
            "encrypted_bytes": encrypted_bytes,
            "total_bytes": total_bytes,
            "encrypted_percentage": (encrypted_bytes / total_bytes * 100) if total_bytes > 0 else 0,
            "clusters": clusters,
            "high_entropy_regions": len([r for r in regions if r.avg_entropy > 7.9])
        }
    
    def _find_encrypted_clusters(self, encrypted_regions: List[EntropyRegion]) -> List[Dict]:
        """Find clusters of adjacent encrypted regions."""
        if not encrypted_regions:
            return []
        
        clusters = []
        current_cluster = {
            "start": encrypted_regions[0].offset,
            "end": encrypted_regions[0].offset + encrypted_regions[0].size,
            "total_size": encrypted_regions[0].size,
            "region_count": 1
        }
        
        for i in range(1, len(encrypted_regions)):
            region = encrypted_regions[i]
            
            # If within 64KB of previous cluster, extend it
            if region.offset - current_cluster["end"] < 65536:
                current_cluster["end"] = region.offset + region.size
                current_cluster["total_size"] += region.size
                current_cluster["region_count"] += 1
            else:
                clusters.append(current_cluster)
                current_cluster = {
                    "start": region.offset,
                    "end": region.offset + region.size,
                    "total_size": region.size,
                    "region_count": 1
                }
        
        clusters.append(current_cluster)
        
        # Filter out small clusters (less than 1MB)
        significant_clusters = [c for c in clusters if c["total_size"] > 1024 * 1024]
        
        return significant_clusters
    
    def detect_hidden_os_artifacts(self, image_path: str, 
                                   partition_offset: int) -> Dict[str, Any]:
        """Detect artifacts from hidden OS in free space.
        
        When a hidden OS is installed within an encrypted volume, 
        artifacts can leak into the outer volume's free space.
        
        Args:
            image_path: Path to disk image
            partition_offset: Partition start offset
            
        Returns:
            Dictionary with detected artifacts
        """
        artifacts_found = []
        
        with open(image_path, 'rb') as f:
            # Search in free/unallocated space - sample 8MB for performance
            search_start = partition_offset + (1024 * 1024)  # Skip first 1MB
            search_size = 8 * 1024 * 1024  # Search 8MB
            
            f.seek(search_start)
            data = f.read(search_size)
            
            for artifact in self.OS_ARTIFACTS:
                if isinstance(artifact, str):
                    artifact = artifact.encode('utf-8')
                
                offset = data.find(artifact)
                if offset != -1:
                    artifacts_found.append({
                        "artifact": artifact.decode('utf-8', errors='replace'),
                        "offset": search_start + offset,
                        "type": "os_artifact"
                    })
        
        return {
            "artifacts_found": artifacts_found,
            "count": len(artifacts_found),
            "has_hidden_os_indicators": len(artifacts_found) > 0
        }
    
    def detect_hidden_volume(self, image_path: str, partition_offset: int,
                            partition_size: int) -> HiddenVolumeResult:
        """Main detection method for hidden volumes.
        
        Args:
            image_path: Path to disk image
            partition_offset: Partition start offset in bytes
            partition_size: Partition size in bytes
            
        Returns:
            HiddenVolumeResult with detection findings
        """
        # Check for encrypted regions
        encrypted_info = self.detect_encrypted_regions(
            image_path, partition_offset, partition_size
        )
        
        # Check for hidden OS artifacts
        os_info = self.detect_hidden_os_artifacts(image_path, partition_offset)
        
        # Determine if hidden volume/OS detected
        confidence = 0.0
        detection_method = "none"
        details = []
        
        # High encryption (95%+) strongly suggests encrypted container without OS
        if encrypted_info["encrypted_percentage"] > 95:
            confidence = 0.9
            detection_method = "high_entropy_encrypted_container"
            details.append(f"Very high encryption detected: {encrypted_info['encrypted_percentage']:.1f}%")
            details.append("Likely VeraCrypt/TrueCrypt encrypted container")
        
        # High encryption with clusters suggests hidden volume
        elif encrypted_info["encrypted_percentage"] > 90:
            if len(encrypted_info["clusters"]) >= 2:
                confidence = 0.75
                detection_method = "entropy_clustering"
                details.append(f"Found {len(encrypted_info['clusters'])} encrypted clusters")
                details.append(f"Total encrypted: {encrypted_info['encrypted_percentage']:.1f}%")
        
        # OS artifacts in free space suggest hidden OS
        # BUT only if there's also high encryption (to avoid false positives)
        if os_info["has_hidden_os_indicators"]:
            # Check if partition appears to be encrypted (high entropy)
            if encrypted_info["encrypted_percentage"] > 70:
                confidence = max(confidence, 0.85)
                detection_method = "os_artifact_detection"
                details.append(f"Found {os_info['count']} OS artifacts in free space")
                details.append(f"High encryption: {encrypted_info['encrypted_percentage']:.1f}%")
                for artifact in os_info["artifacts_found"][:3]:
                    details.append(f"  - {artifact['artifact']}")
            else:
                # Partition doesn't appear encrypted - likely normal Windows
                details.append(f"OS artifacts found but partition not encrypted")
                details.append(f"Encrypted: {encrypted_info['encrypted_percentage']:.1f}% - likely normal Windows install")
        
        detected = confidence > 0.5
        
        return HiddenVolumeResult(
            detected=detected,
            confidence=confidence,
            method=detection_method,
            details="; ".join(details) if details else "No hidden volume detected"
        )
    
    def analyze_partition(self, image_path: str, partition_info: Dict) -> Dict[str, Any]:
        """Analyze a single partition for hidden volumes/OS.
        
        Args:
            image_path: Path to disk image
            partition_info: Partition dictionary with offset and size
            
        Returns:
            Analysis results
        """
        offset = partition_info.get("start_sector", 0) * 512
        size = partition_info.get("size_sectors", 0) * 512
        
        if offset == 0 or size == 0:
            return {"error": "Invalid partition offset or size"}
        
        result = self.detect_hidden_volume(image_path, offset, size)
        
        # Get additional details
        encrypted_info = self.detect_encrypted_regions(image_path, offset, size)
        os_info = self.detect_hidden_os_artifacts(image_path, offset)
        
        return {
            "partition_slot": partition_info.get("slot", "unknown"),
            "hidden_volume_detected": result.detected,
            "confidence": result.confidence,
            "detection_method": result.method,
            "details": result.details,
            "entropy_analysis": encrypted_info,
            "os_artifacts": os_info
        }


def detect_hidden_volumes(image_path: str, partitions: List[Dict]) -> List[Dict]:
    """Detect hidden volumes across all partitions.
    
    Args:
        image_path: Path to disk image
        partitions: List of partition dictionaries
        
    Returns:
        List of detection results for each partition
    """
    detector = HiddenVolumeDetector()
    
    results = []
    
    for partition in partitions:
        # Skip meta/extended partitions
        slot = partition.get("slot", "")
        if slot in ["Meta", "meta"] or "-------" in str(slot):
            continue
        
        # Skip very small partitions
        size = partition.get("size_sectors", 0)
        if size < 10000:  # Less than ~5MB
            continue
        
        result = detector.analyze_partition(image_path, partition)
        results.append(result)
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hidden_volume_detector.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print(f"[*] Analyzing: {image_path}")
    
    # Simple test - just calculate entropy of first 1MB
    detector = HiddenVolumeDetector()
    
    with open(image_path, 'rb') as f:
        data = f.read(1024 * 1024)  # First 1MB
        entropy = detector.calculate_entropy(data)
        
    print(f"[*] First 1MB entropy: {entropy:.4f}")
    
    if entropy > 7.5:
        print("[!] High entropy detected - possible encrypted volume")
