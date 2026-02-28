#!/usr/bin/env python3
"""
Docker-based TSK wrapper for forensic analysis.
Uses Docker container with The Sleuth Kit tools.
"""

import os
import sys
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

DOCKER_DIR = Path(__file__).parent.parent / "docker" / "tsk"
CONTAINER_NAME = "tsk-forensics"


def docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def ensure_container_running() -> bool:
    """Ensure the TSK container is built and running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10
        )
        
        if CONTAINER_NAME not in result.stdout:
            print(f"[*] Building and starting TSK container...")
            subprocess.run(["docker-compose", "up", "-d"], cwd=str(DOCKER_DIR), check=True, timeout=300)
            return True
        return True
    except Exception as e:
        print(f"[!] Docker error: {e}")
        return False


def run_tsk_command(cmd: List[str], image_path: str, timeout: int = 300) -> Tuple[int, str, str]:
    """Run a TSK command inside the Docker container."""
    if not docker_available():
        return -1, "", "Docker not available"
    
    if not ensure_container_running():
        return -1, "", "Failed to start TSK container"
    
    try:
        docker_cmd = [
            "docker", "exec", CONTAINER_NAME,
            "mmls", "-i", "ewf", f"/forensics/images/{Path(image_path).name}"
        ]
        
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def get_partition_layout_docker(image_path: str) -> List[Dict]:
    """Get partition layout using mmls inside Docker."""
    if not docker_available():
        return [{"slot": "0:", "partition_num": 0, "start_int": 0, "desc": "Whole disk (Docker not available)"}]
    
    try:
        docker_cmd = [
            "docker", "exec", CONTAINER_NAME,
            "mmls", "-i", "ewf", f"/forensics/images/{Path(image_path).name}"
        ]
        
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"[DEBUG] mmls failed: {result.stderr}")
            return [{"slot": "0:", "partition_num": 0, "start_int": 0, "desc": "Whole disk"}]
        
        partitions = []
        lines = result.stdout.strip().split("\n")
        for line in lines[3:]:
            parts = line.split()
            if len(parts) >= 4:
                slot = parts[0]
                if slot.startswith("-------") or ":" not in slot:
                    continue
                try:
                    start = int(parts[2])
                    length = int(parts[3])
                    desc = " ".join(parts[5:]) if len(parts) > 5 else ""
                    partitions.append({
                        "slot": slot,
                        "start_int": start,
                        "length": length,
                        "desc": desc
                    })
                except (ValueError, IndexError):
                    continue
        
        if not partitions:
            partitions = [{"slot": "0:", "partition_num": 0, "start_int": 0, "desc": "Whole disk"}]
        
        return partitions
        
    except Exception as e:
        print(f"[DEBUG] Docker error: {e}")
        return [{"slot": "0:", "partition_num": 0, "start_int": 0, "desc": f"Error: {e}"}]


def extract_mft_docker(image_path: str, partition_offset: int = 0, max_records: int = 2000) -> Dict[int, Dict]:
    """Extract MFT entries using icat inside Docker."""
    mft_data = {}
    
    if not docker_available():
        return mft_data
    
    try:
        for mft_num in range(max_records):
            inode = f"{mft_num}-0"
            
            docker_cmd = [
                "docker", "exec", CONTAINER_NAME,
                "icat", "-i", "ewf", "-o", str(partition_offset),
                f"/forensics/images/{Path(image_path).name}", inode
            ]
            
            result = subprocess.run(docker_cmd, capture_output=True, timeout=30)
            
            if result.returncode != 0 or len(result.stdout) < 1024:
                continue
            
            try:
                record = result.stdout[:1024]
                
                if record[0:4] != b"FILE":
                    continue
                
                import struct
                
                attrs_offset = struct.unpack("<H", record[20:22])[0]
                if attrs_offset >= 1024:
                    continue
                
                attr_data = record[attrs_offset:]
                pos = 0
                
                while pos < len(attr_data) - 48:
                    attr_id = struct.unpack("<I", attr_data[pos:pos+4])[0]
                    attr_len = struct.unpack("<I", attr_data[pos+4:pos+8])[0]
                    
                    if attr_len == 0 or attr_len > 65536:
                        break
                    
                    if attr_id == 0x10 and len(attr_data) >= pos + 48:
                        created = struct.unpack("<Q", attr_data[pos+16:pos+24])[0]
                        modified = struct.unpack("<Q", attr_data[pos+24:pos+32])[0]
                        changed = struct.unpack("<Q", attr_data[pos+32:pos+40])[0]
                        accessed = struct.unpack("<Q", attr_data[pos+40:pos+48])[0]
                        
                        mft_data[mft_num] = {
                            "created_raw": created,
                            "modified_raw": modified,
                            "changed_raw": changed,
                            "accessed_raw": accessed,
                            "created": filetime_to_datetime(created),
                            "modified": filetime_to_datetime(modified),
                            "changed": filetime_to_datetime(changed),
                            "accessed": filetime_to_datetime(accessed),
                        }
                        break
                    
                    pos += attr_len
                    
            except Exception:
                continue
    
    except Exception as e:
        print(f"[DEBUG] Error extracting MFT: {e}")
    
    return mft_data


def filetime_to_datetime(filetime: int) -> Optional[str]:
    """Convert Windows FILETIME to ISO datetime string."""
    if filetime == 0:
        return None
    try:
        import datetime
        dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime // 10)
        return dt.isoformat()
    except Exception:
        return None


def analyze_timestamp_integrity_docker(image_path: str, partition_offset: int = 0) -> Dict[str, Any]:
    """Main entry point for Docker-based timestamp analysis."""
    import datetime
    
    result = {
        "partition_offset": partition_offset,
        "analyzed_at": datetime.datetime.now().isoformat(),
        "filesystem": "ntfs",
        "total_mft_entries": 0,
        "usn_journal_status": {},
        "inconsistencies": [],
        "summary": "",
        "docker_used": True,
    }
    
    if not docker_available():
        result["error"] = "Docker not available. Please install Docker."
        result["summary"] = "Error: Docker required for disk image analysis."
        return result
    
    print(f"[DEBUG] Using Docker-based TSK for analysis")
    
    partitions = get_partition_layout_docker(image_path)
    print(f"[DEBUG] Found {len(partitions)} partitions: {partitions}")
    
    if partition_offset == 0 and partitions:
        partition_offset = partitions[0].get("start_int", 0)
    
    mft_data = extract_mft_docker(image_path, partition_offset)
    result["total_mft_entries"] = len(mft_data)
    print(f"[DEBUG] Extracted {len(mft_data)} MFT entries")
    
    import datetime
    current_filetime = int((datetime.datetime.now() - datetime.datetime(1601, 1, 1)).total_seconds() * 10_000_000)
    
    for mft_entry_num, mft_entry in mft_data.items():
        mft_modified_raw = mft_entry.get("modified_raw", 0)
        mft_created_raw = mft_entry.get("created_raw", 0)
        
        if mft_created_raw > current_filetime:
            result["inconsistencies"].append({
                "type": "future_timestamp",
                "severity": "high",
                "message": "MFT Created timestamp is in the future",
                "description": f"Entry {mft_entry_num}",
            })
        
        if mft_created_raw == 0 or mft_modified_raw == 0:
            result["inconsistencies"].append({
                "type": "zero_timestamp",
                "severity": "medium",
                "message": "Zero timestamp detected",
                "description": f"Entry {mft_entry_num}",
            })
    
    high_severity = sum(1 for i in result["inconsistencies"] if i.get("severity") == "high")
    
    result["summary"] = f"Timestamp Analysis: {len(mft_data)} MFT entries. {len(result['inconsistencies'])} inconsistencies ({high_severity} high)."
    
    return result


def copy_image_to_docker(image_path: str) -> bool:
    """Copy disk image to Docker volume."""
    if not docker_available():
        return False
    
    images_dir = DOCKER_DIR / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    dest = images_dir / Path(image_path).name
    
    if not dest.exists():
        print(f"[*] Copying {image_path} to Docker volume...")
        try:
            shutil.copy2(image_path, dest)
            return True
        except Exception as e:
            print(f"[!] Failed to copy image: {e}")
            return False
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Docker-based TSK Timestamp Analyzer")
    parser.add_argument("image", help="Path to disk image")
    parser.add_argument("--copy", action="store_true", help="Copy image to Docker volume first")
    args = parser.parse_args()
    
    if args.copy:
        copy_image_to_docker(args.image)
    
    result = analyze_timestamp_integrity_docker(args.image)
    print(json.dumps(result, indent=2))
