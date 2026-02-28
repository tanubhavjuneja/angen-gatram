#!/usr/bin/env python3
"""
Timestamp Integrity Agent - Self-contained forensic analyzer
Parses disk images directly without external tools.
"""

import os
import sys
import struct
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


MAX_MFT_RECORDS = 1000


def filetime_to_datetime(filetime: int) -> Optional[str]:
    if filetime == 0:
        return None
    try:
        dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime // 10)
        return dt.isoformat()
    except Exception:
        return None


def filetime_to_datetime_obj(filetime: int) -> Optional[datetime.datetime]:
    if filetime == 0:
        return None
    try:
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime // 10)
    except Exception:
        return None


def get_current_filetime() -> int:
    try:
        delta = datetime.datetime.now() - datetime.datetime(1601, 1, 1)
        return int(delta.total_seconds() * 10_000_000)
    except Exception:
        return 0


def parse_mbr(image_path: str) -> List[Dict]:
    """Parse MBR partition table."""
    partitions = []
    try:
        with open(image_path, "rb") as f:
            f.seek(0x1FE)
            if f.read(2) != b'\x55\xAA':
                return partitions
            
            f.seek(0x1BE)
            for i in range(4):
                part_entry = f.read(16)
                if part_entry[0] == 0:
                    continue
                
                part_type = part_entry[4]
                start_sector = struct.unpack('<I', part_entry[8:12])[0]
                num_sectors = struct.unpack('<I', part_entry[12:16])[0]
                
                if start_sector > 0 and num_sectors > 0:
                    partitions.append({
                        "slot": f"{i}:",
                        "start_int": start_sector,
                        "length": num_sectors,
                        "type": part_type,
                    })
    except Exception as e:
        print(f"[DEBUG] Error parsing MBR: {e}")
    return partitions


def detect_filesystem(image_path: str, partition_offset: int = 0) -> str:
    """Detect filesystem type from boot sector."""
    try:
        with open(image_path, "rb") as f:
            f.seek(partition_offset * 512)
            boot = f.read(512)
            
            if len(boot) < 512:
                return "unknown"
            
            print(f"[DEBUG] Boot sector bytes 3-11: {boot[3:11].hex()} = {boot[3:11]}")
            print(f"[DEBUG] Boot sector bytes 0x36-0x3E: {boot[0x36:0x3E].hex()} = {boot[0x36:0x3E]}")
            
            fs_sig = boot[3:11]
            if fs_sig == b'NTFS    ':
                return "ntfs"
            
            if boot[0x36:0x3E] == b'FAT12   ':
                return "fat12"
            if boot[0x36:0x3E] == b'FAT16   ':
                return "fat16"
            
            if boot[0x52:0x5A] == b'FAT32   ':
                return "fat32"
            
            if b'NTFS' in boot:
                print(f"[DEBUG] Found NTFS at other offset")
                return "ntfs"
            
            return "unknown"
    except Exception as e:
        print(f"[DEBUG] Error detecting filesystem: {e}")
        return "unknown"


def parse_ntfs_mft(image_path: str, partition_offset: int = 0) -> Dict[str, Any]:
    """Parse NTFS MFT directly from disk image."""
    results = {
        "valid_entries": 0,
        "inconsistencies": [],
    }
    
    try:
        with open(image_path, "rb") as f:
            f.seek(partition_offset * 512)
            boot = f.read(512)
            
            if boot[3:11] != b'NTFS    ':
                return results
            
            bytes_per_sector = struct.unpack("<H", boot[11:13])[0]
            sectors_per_cluster = struct.unpack("<B", boot[13:14])[0]
            mft_lcn = struct.unpack("<Q", boot[48:56])[0]
            
            cluster_size = bytes_per_sector * sectors_per_cluster
            mft_start = partition_offset * 512 + mft_lcn * cluster_size
            
            print(f"[DEBUG] MFT at byte offset: {mft_start}")
            
            current_filetime = get_current_filetime()
            
            for i in range(MAX_MFT_RECORDS):
                f.seek(mft_start + i * 1024)
                record = f.read(1024)
                
                if len(record) < 1024 or record[0:4] != b'FILE':
                    continue
                
                attrs_offset = struct.unpack("<H", record[20:22])[0]
                if attrs_offset >= 1024:
                    continue
                
                attr_data = record[attrs_offset:]
                pos = 0
                timestamps = {}
                filename = f"entry_{i}"
                
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
                        
                        timestamps = {
                            "created_raw": created,
                            "modified_raw": modified,
                            "changed_raw": changed,
                            "accessed_raw": accessed,
                        }
                    
                    elif attr_id == 0x30 and len(attr_data) >= pos + 66:
                        fname_len = attr_data[pos + 64]
                        if fname_len > 0 and len(attr_data) >= pos + 66 + fname_len * 2:
                            try:
                                filename = attr_data[pos+66:pos+66+fname_len*2].decode('utf-16-le', errors='ignore').rstrip('\x00')
                            except:
                                pass
                    
                    pos += attr_len
                
                if not timestamps:
                    continue
                
                results["valid_entries"] += 1
                
                created_raw = timestamps.get("created_raw", 0)
                modified_raw = timestamps.get("modified_raw", 0)
                created = filetime_to_datetime_obj(created_raw)
                modified = filetime_to_datetime_obj(modified_raw)
                
                if created_raw > current_filetime:
                    results["inconsistencies"].append({
                        "type": "future_timestamp",
                        "severity": "high",
                        "message": "Created timestamp is in the future",
                        "description": f"File: {filename}",
                    })
                
                if created_raw == 0 or modified_raw == 0:
                    results["inconsistencies"].append({
                        "type": "zero_timestamp",
                        "severity": "medium",
                        "message": "Zero timestamp detected",
                        "description": f"File: {filename}",
                    })
                
                if created and modified and created > modified:
                    results["inconsistencies"].append({
                        "type": "created_after_modified",
                        "severity": "high",
                        "message": "Created AFTER Modified - timestomping",
                        "description": f"File: {filename}",
                    })
                
                if results["valid_entries"] % 100 == 0:
                    print(f"[DEBUG] Processed {results['valid_entries']} MFT entries...")
    
    except Exception as e:
        print(f"[DEBUG] Error parsing MFT: {e}")
    
    return results


def analyze_usn_journal_raw(image_path: str, partition_offset: int = 0) -> Dict[str, Any]:
    """Analyze USN journal from raw MFT data."""
    result = {
        "found": False,
        "reason": "Could not locate USN journal",
        "max_size": 0,
        "allocated_size": 0,
        "next_usn": 0,
        "oldest_usn": 0,
    }
    
    ext = image_path.lower().split('.')[-1]
    if ext in ['e01', 'e02', 'e03', 'ewf']:
        result["reason"] = "E01/EWF files require libewf to decompress. USN analysis not available."
        return result
    
    try:
        with open(image_path, "rb") as f:
            offset = partition_offset * 512
            
            f.seek(offset)
            boot_sector = f.read(512)
            
            has_ntfs = b'NTFS' in boot_sector
            print(f"[DEBUG] Boot sector contains NTFS: {has_ntfs}")
            
            if not has_ntfs:
                result["reason"] = "Not NTFS filesystem"
                return result
            
            mft_ref = struct.unpack('<Q', boot_sector[0x30:0x38])[0]
            mft_start = offset + (mft_ref * 512)
            
            f.seek(mft_start)
            mft_data = f.read(2048)
            
            if mft_data[:4] != b'FILE':
                result["reason"] = f"Invalid MFT header at {mft_ref}"
                return result
            
            root_dir_ref = None
            attrs_offset = struct.unpack('<H', mft_data[20:22])[0]
            
            if attrs_offset > 48 and attrs_offset < 2048:
                pos = attrs_offset
                while pos < len(mft_data) - 64:
                    attr_type = struct.unpack('<I', mft_data[pos:pos+4])[0]
                    attr_len = struct.unpack('<I', mft_data[pos+4:pos+8])[0]
                    
                    if attr_len == 0:
                        break
                    
                    if attr_type == 0x90:
                        fname_offset = struct.unpack('<H', mft_data[pos+66:pos+68])[0]
                        fname_len = struct.unpack('<H', mft_data[pos+68:pos+70])[0]
                        
                        if fname_offset > pos and fname_offset < attr_len:
                            fname_data = mft_data[pos+fname_offset:pos+fname_offset + min(fname_len * 2, 64)]
                            fname = fname_data.decode('utf-16-le', errors='ignore').strip('\x00')
                            
                            if fname == "":
                                root_dir_ref = struct.unpack('<I', mft_data[pos+48:pos+52])[0] & 0xFFFFFFFF
                                break
            
            if not root_dir_ref:
                result["reason"] = "Could not find root directory reference"
                return result
            
            f.seek(offset + (root_dir_ref * 1024))
            root_mft = f.read(2048)
            
            if root_mft[:4] != b'FILE':
                result["reason"] = "Invalid root directory MFT entry"
                return result
            
            extend_ref = None
            root_attrs_offset = struct.unpack('<H', root_mft[20:22])[0]
            
            if root_attrs_offset > 48 and root_attrs_offset < 2048:
                pos = root_attrs_offset
                while pos < len(root_mft) - 64:
                    attr_type = struct.unpack('<I', root_mft[pos:pos+4])[0]
                    attr_len = struct.unpack('<I', root_mft[pos+4:pos+8])[0]
                    
                    if attr_len == 0:
                        break
                    
                    if attr_type == 0x90:
                        fname_offset = struct.unpack('<H', root_mft[pos+66:pos+68])[0]
                        fname_len = struct.unpack('<H', root_mft[pos+68:pos+70])[0]
                        
                        if fname_offset > pos and fname_offset < attr_len:
                            fname_data = root_mft[pos+fname_offset:pos+fname_offset + min(fname_len * 2, 64)]
                            fname = fname_data.decode('utf-16-le', errors='ignore').strip('\x00')
                            
                            if fname == "$Extend":
                                extend_ref = struct.unpack('<I', root_mft[pos+48:pos+52])[0] & 0xFFFFFFFF
                                break
                    
                    pos += attr_len
            
            if not extend_ref:
                result["reason"] = "Could not find $Extend directory in root"
                return result
            
            f.seek(offset + extend_ref * 1024)
            extend_mft = f.read(1024)
            
            if extend_mft[:4] != b'FILE':
                result["reason"] = "Invalid $Extend MFT entry"
                return result
            
            usn_ref = None
            ext_attrs_offset = struct.unpack('<H', extend_mft[20:22])[0]
            
            if ext_attrs_offset > 48 and ext_attrs_offset < 1024:
                pos = ext_attrs_offset
                while pos < len(extend_mft) - 64:
                    attr_type = struct.unpack('<I', extend_mft[pos:pos+4])[0]
                    attr_len = struct.unpack('<I', extend_mft[pos+4:pos+8])[0]
                    
                    if attr_len == 0:
                        break
                    
                    if attr_type == 0x90:
                        fname_offset = struct.unpack('<H', extend_mft[pos+66:pos+68])[0]
                        fname_len = struct.unpack('<H', extend_mft[pos+68:pos+70])[0]
                        
                        if fname_offset > pos:
                            fname_data = extend_mft[fname_offset:fname_offset + min(fname_len * 2, 64)]
                            fname = fname_data.decode('utf-16-le', errors='ignore').strip('\x00')
                            
                            if fname == "$UsnJrnl":
                                usn_ref = struct.unpack('<I', extend_mft[pos+48:pos+52])[0] & 0xFFFFFFFF
                                break
                    
                    pos += attr_len
            
            if not usn_ref:
                result["reason"] = "Could not find $UsnJrnl in $Extend directory"
                return result
            
            f.seek(offset + (usn_ref * 1024))
            usn_mft = f.read(2048)
            
            if usn_mft[:4] != b'FILE':
                result["reason"] = "Invalid $UsnJrnl MFT entry"
                return result
            
            usn_attrs_offset = struct.unpack('<H', usn_mft[20:22])[0]
            
            if usn_attrs_offset > 48:
                pos = usn_attrs_offset
                while pos < len(usn_mft) - 64:
                    attr_type = struct.unpack('<I', usn_mft[pos:pos+4])[0]
                    attr_len = struct.unpack('<I', usn_mft[pos+4:pos+8])[0]
                    
                    if attr_len == 0:
                        break
                    
                    if attr_type == 0x80:
                        is_resident = usn_mft[pos+8]
                        if is_resident == 0:
                            data_size = struct.unpack('<Q', usn_mft[pos+16:pos+24])[0]
                            result["allocated_size"] = data_size
                            
                            data_rva_offset = pos + 32
                            if data_rva_offset + 8 <= len(usn_mft):
                                first_run = usn_mft[data_rva_offset:data_rva_offset+8]
                                run_length = struct.unpack('<I', first_run[:4])[0]
                                run_offset = struct.unpack('<I', first_run[4:8])[0]
                                
                                if run_length > 0:
                                    journal_offset = offset + ((usn_ref * 1024) & 0xFFFFFE00) + run_offset
                                    f.seek(journal_offset)
                                    journal_header = f.read(64)
                                    
                                    if len(journal_header) >= 40:
                                        result["found"] = True
                                        result["max_size"] = struct.unpack('<Q', journal_header[8:16])[0]
                                        result["next_usn"] = struct.unpack('<Q', journal_header[16:24])[0]
                                        result["oldest_usn"] = struct.unpack('<Q', journal_header[24:32])[0]
                                        result["reason"] = "USN journal located and analyzed"
                    
                    pos += attr_len
            
            if not result["found"]:
                result["reason"] = "USN journal found but data not accessible"
                
    except Exception as e:
        result["reason"] = f"Error analyzing USN: {str(e)}"
    
    return result


def analyze_timestamp_integrity(image_path: str, partition_offset: int = 0) -> Dict[str, Any]:
    """Main entry point."""
    result = {
        "partition_offset": partition_offset,
        "analyzed_at": datetime.datetime.now().isoformat(),
        "filesystem": "unknown",
        "total_mft_entries": 0,
        "usn_journal_status": {"found": False, "reason": "No TSK tools available for USN extraction"},
        "inconsistencies": [],
        "summary": "",
    }
    
    print(f"[DEBUG] Analyzing: {image_path}")
    
    partitions = parse_mbr(image_path)
    print(f"[DEBUG] Found {len(partitions)} MBR partitions")
    
    if not partitions:
        partitions = [{"start_int": 0}]
    
    if partition_offset == 0:
        partition_offset = partitions[0].get("start_int", 0)
    
    fs_type = detect_filesystem(image_path, partition_offset)
    print(f"[DEBUG] Filesystem: {fs_type}")
    result["filesystem"] = fs_type
    
    if fs_type == "ntfs":
        print(f"[DEBUG] Parsing NTFS MFT...")
        mft_results = parse_ntfs_mft(image_path, partition_offset)
        result["total_mft_entries"] = mft_results.get("valid_entries", 0)
        result["inconsistencies"] = mft_results.get("inconsistencies", [])
        
        usn_status = analyze_usn_journal_raw(image_path, partition_offset)
        result["usn_journal_status"] = usn_status
        
        if usn_status.get("found"):
            print(f"[DEBUG] USN Journal found: {usn_status.get('max_size', 0)} bytes")
        else:
            print(f"[DEBUG] USN Journal not found: {usn_status.get('reason', 'unknown')}")
        
    elif fs_type in ["fat12", "fat16", "fat32"]:
        result["inconsistencies"].append({
            "type": "fat_filesystem",
            "severity": "info",
            "message": "FAT filesystem - no MFT or USN journal",
            "description": "FAT filesystems do not have MFT or USN journal"
        })
        result["usn_journal_status"] = {
            "found": False,
            "reason": "FAT filesystem - no USN journal exists"
        }
    else:
        result["inconsistencies"].append({
            "type": "unknown_filesystem",
            "severity": "info",
            "message": "Unknown filesystem",
            "description": "Could not identify filesystem type"
        })
    
    high_count = sum(1 for i in result["inconsistencies"] if i.get("severity") == "high")
    medium_count = sum(1 for i in result["inconsistencies"] if i.get("severity") == "medium")
    
    result["summary"] = (
        f"Filesystem: {fs_type.upper()}. "
        f"Analyzed {result['total_mft_entries']} MFT entries. "
        f"Found {len(result['inconsistencies'])} inconsistencies "
        f"({high_count} high, {medium_count} medium)."
    )
    
    return result


def analyze(image_path: str, partition_offset: int = 0) -> Dict[str, Any]:
    return analyze_timestamp_integrity(image_path, partition_offset)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("-o", "--offset", type=int, default=0)
    args = parser.parse_args()
    
    result = analyze(args.image, args.offset)
    print(json.dumps(result, indent=2))
