#!/usr/bin/env python3
"""
TSK Docker Wrapper - Run The Sleuth Kit tools via Docker on Windows
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional


class TSKDocker:
    """Run TSK commands via Docker container."""
    
    DOCKER_IMAGE = "cincan/sleuthkit:latest"
    EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"
    OUTPUT_DIR = Path(__file__).parent.parent / "output"
    
    def __init__(self):
        self.evidence_dir = self.EVIDENCE_DIR
        self.output_dir = self.OUTPUT_DIR
        self.evidence_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.docker_available = self._check_docker()
        self._image_name = None
    
    @property
    def image_name(self) -> str:
        """Get the current image name being used."""
        return self._image_name
    
    @image_name.setter
    def image_name(self, value: str):
        """Set the current image name."""
        self._image_name = value
    
    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    
    def _run_docker_cmd(self, cmd: List[str], volume_mount: str = None) -> tuple:
        """Run a command inside the TSK Docker container."""
        if not self.docker_available:
            return None, "Docker not available"
        
        evidence_path = str(self.evidence_dir).replace("\\", "/")
        output_path = str(self.output_dir).replace("\\", "/")
        
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{evidence_path}:/evidence",
            "-v", f"{output_path}:/output",
            "-w", "/evidence",
            self.DOCKER_IMAGE
        ] + cmd
        
        # Set environment to prevent Git Bash path conversion on Windows
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        
        result = subprocess.run(docker_cmd, capture_output=True, text=True, env=env)
        return result.stdout, result.stderr
    
    def is_available(self) -> bool:
        """Check if TSK via Docker is available."""
        return self.docker_available
    
    def get_partition_layout(self, image_file: str) -> List[Dict]:
        """Get partition layout using mmls."""
        mmls_output = self.mmls(image_file)
        if mmls_output:
            return self._parse_mmls_output(mmls_output)
        return []
    
    def mmls(self, image_file: str) -> Optional[str]:
        """List partitions using mmls."""
        stdout, stderr = self._run_docker_cmd(["mmls", image_file])
        if stdout:
            return stdout
        return None
    
    def fls(self, image_file: str, partition_offset: int = 0, path: str = None) -> Optional[str]:
        """List files using fls."""
        if path is None:
            cmd = ["fls", "-o", str(partition_offset), "-r", image_file]
        elif path.isdigit():
            cmd = ["fls", "-o", str(partition_offset), "-r", image_file, path]
        else:
            cmd = ["fls", "-o", str(partition_offset), "-r", image_file, path]
        stdout, stderr = self._run_docker_cmd(cmd)
        if stdout:
            return stdout
        return None
    
    def icat(self, image_file: str, inode: str, partition_offset: int = 0, output_file: str = None) -> Optional[bytes]:
        """Extract file content using icat."""
        cmd = ["icat", "-o", str(partition_offset), image_file, inode]
        
        if not self.docker_available:
            return None
        
        evidence_path = str(self.evidence_dir).replace("\\", "/")
        output_path = str(self.output_dir).replace("\\", "/")
        
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{evidence_path}:/evidence",
            "-v", f"{output_path}:/output",
            "-w", "/evidence",
            self.DOCKER_IMAGE
        ] + cmd
        
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        
        result = subprocess.run(docker_cmd, capture_output=True, env=env)
        if result.returncode == 0:
            return result.stdout
        return None
    
    def extract_usn_journal(self, image_file: str, partition_offset: int = 0) -> Dict[str, Any]:
        """Extract USN journal using TSK tools."""
        result = {
            "found": False,
            "method": "docker_tsk",
            "partitions": [],
            "usn_journal_found": False,
            "error": None
        }
        
        if not self.docker_available:
            result["error"] = "Docker not available. Install Docker Desktop."
            return result
        
        try:
            # If partition_offset was explicitly provided, use it directly
            if partition_offset > 0:
                ntfs_offset = partition_offset
                result["partitions"].append({
                    "slot": "manual",
                    "start_sector": partition_offset,
                    "description": "Manual offset",
                    "fs": "NTFS"
                })
            else:
                # Get partition list
                mmls_output = self.mmls(image_file)
                if mmls_output:
                    result["partitions"] = self._parse_mmls_output(mmls_output)
                
                # Find NTFS partition
                ntfs_offset = None
                for part in result["partitions"]:
                    fs = part.get("fs", "")
                    desc = part.get("description", "").lower()
                    
                    # Check if it's NTFS - either explicit or implied
                    if fs == "NTFS" or "basic data" in desc or "ntfs" in desc:
                        ntfs_offset = part.get("start_sector")
                        part["fs"] = "NTFS"  # Assume Basic data is NTFS on Windows
                        break
                
                # If no partition found, try fsstat on offset 0 (raw partition image)
                if not result["partitions"] or ntfs_offset is None:
                    fsstat_result = self._run_docker_cmd(["fsstat", "-o", "0", image_file])
                    if fsstat_result[0] and "NTFS" in fsstat_result[0]:
                        ntfs_offset = 0
                        result["partitions"].append({
                            "slot": "raw",
                            "start_sector": 0,
                            "description": "Raw NTFS partition",
                            "fs": "NTFS"
                        })
                
                if ntfs_offset is None:
                    # Try to detect filesystem using fsstat on each partition
                    for part in result["partitions"]:
                        offset = part.get("start_sector")
                        if offset and offset >= 0:
                            fsstat_result = self._run_docker_cmd(["fsstat", "-o", str(offset), image_file])
                            if fsstat_result[0] and "NTFS" in fsstat_result[0]:
                                ntfs_offset = offset
                                part["fs"] = "NTFS"
                                break
                
                if ntfs_offset is None:
                    # Fallback: use first data partition
                    for part in result["partitions"]:
                        if "data partition" in part.get("description", "").lower():
                            ntfs_offset = part.get("start_sector")
                            break
            
            if ntfs_offset is None:
                result["error"] = "No NTFS partition found"
                return result
            
            # Find $UsnJrnl - first get root directory to find $Extend inode
            root_fls = self.fls(image_file, ntfs_offset)
            extend_inode = None
            if root_fls:
                for line in root_fls.split("\n"):
                    if "$Extend" in line:
                        parts = line.split(":")
                        if len(parts) >= 1:
                            inode = parts[0].split()[-1]
                            extend_inode = inode
                            break
            
            if not extend_inode:
                result["error"] = "$Extend directory not found"
                return result
            
            # Get $Extend directory contents
            fls_output = self.fls(image_file, ntfs_offset, extend_inode)
            if fls_output:
                for line in fls_output.split("\n"):
                    if "UsnJrnl" in line:
                        result["usn_journal_found"] = True
                        result["found"] = True
                        
                        # Extract inode
                        parts = line.split(":")
                        if len(parts) >= 2:
                            inode = parts[0].split()[-1]
                            result["usn_inode"] = inode
                            
                            # Extract $J stream
                            j_inode = inode.replace("0-", "0-3-")
                            usn_data = self.icat(image_file, j_inode, ntfs_offset)
                            if usn_data:
                                result["usn_data_size"] = len(usn_data)
                                # Save to file
                                output_path = self.output_dir / "usn_journal.bin"
                                with open(output_path, "wb") as f:
                                    f.write(usn_data)
                                result["usn_file"] = str(output_path)
                        break
            
            if not result["usn_journal_found"]:
                result["error"] = "$UsnJrnl not found in $Extend directory"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _parse_mmls_output(self, output: str) -> List[Dict]:
        """Parse mmls output to extract partition info."""
        partitions = []
        for line in output.split("\n"):
            if not line.strip() or line.startswith("="):
                continue
            if "-------" in line or "Slot" in line or "Start" in line or "Offset" in line or "Units" in line:
                continue
            parts = line.split()
            if len(parts) >= 5:
                try:
                    slot = parts[0]
                    # Skip meta/unallocated entries
                    if slot == "Meta" or slot == "-------" or ":" not in slot:
                        continue
                    start = int(parts[2])
                    end = int(parts[3])
                    size = int(parts[4])
                    desc = " ".join(parts[5:])
                    
                    fs = "Unknown"
                    if "NTFS" in desc:
                        fs = "NTFS"
                    elif "FAT" in desc:
                        fs = "FAT"
                    
                    partitions.append({
                        "slot": parts[1] if len(parts) > 1 else slot,
                        "start_sector": start,
                        "start_int": start,  # For compatibility with ForensicExtractor
                        "end_sector": end,
                        "size_sectors": size,
                        "description": desc,
                        "fs": fs
                    })
                except:
                    continue
        return partitions


def check_tsk_docker() -> bool:
    """Check if TSK Docker is available."""
    tsk = TSKDocker()
    return tsk.is_available()


def extract_usn_with_tsk(image_path: str, partition_offset: int = 0) -> Dict[str, Any]:
    """Extract USN journal using TSK via Docker."""
    tsk = TSKDocker()
    
    # Copy image to evidence directory
    image_name = Path(image_path).name
    evidence_path = tsk.evidence_dir / image_name
    
    if not evidence_path.exists():
        import shutil
        shutil.copy(image_path, evidence_path)
    
    return tsk.extract_usn_journal(image_name, partition_offset)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tsk_docker.py <image_file>")
        print("\nFirst, start the Docker container:")
        print("  docker run -dit --name forensic_tsk -v $(pwd)/evidence:/evidence dfirdudes/the-sleuth-kit:latest")
        sys.exit(1)
    
    image_file = sys.argv[1]
    print(f"[*] Analyzing: {image_file}")
    
    result = extract_usn_with_tsk(image_file)
    print(json.dumps(result, indent=2))
