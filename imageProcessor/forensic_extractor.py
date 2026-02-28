#!/usr/bin/env python3
"""
Forensic Artifact Extractor Utility
Extracts logs, MFT, USN journals, and registry hives from disk images
for anti-forensic technique detection.

Cross-platform support:
- Linux/macOS: Uses The Sleuth Kit (TSK) tools if available
- Windows: Uses pytsk3 if available, otherwise falls back to raw image parsing

Usage:
    python3 forensic_extractor.py <image> -o <output_dir> --all
    python3 forensic_extractor.py <image> --mft --registry --anti-forensic
    from forensic_extractor import ForensicExtractor
    extractor = ForensicExtractor("image.dd", "output")
    extractor.extract_everything()
"""

import os
import sys
import json
import argparse
import struct
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from imageProcessor import path_utils
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    import path_utils

TSK_AVAILABLE = False
PYTSK_AVAILABLE = False
TSK_DOCKER_AVAILABLE = False

try:
    result = subprocess.run(["fls", "-V"], capture_output=True, timeout=5)
    if result.returncode == 0:
        TSK_AVAILABLE = True
except Exception:
    pass

try:
    import pytsk3
    PYTSK_AVAILABLE = True
except ImportError:
    pass

try:
    # Quick Docker check - just see if docker daemon responds
    result = subprocess.run(
        ["docker", "version", "--format", "{{.Server.Version}}"],
        capture_output=True, timeout=3
    )
    if result.returncode == 0:
        # Docker is available, check if TSK image exists
        result2 = subprocess.run(
            ["docker", "images", "-q", "cincan/sleuthkit:latest"],
            capture_output=True, timeout=3
        )
        if result2.returncode == 0 and result2.stdout.strip():
            TSK_DOCKER_AVAILABLE = True
            print(f"[DEBUG] TSK Docker available")
except Exception as e:
    pass

def run_command(cmd: List[str], capture: bool = True) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        if capture:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300, shell=platform.system() == "Windows"
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, timeout=300, shell=platform.system() == "Windows")
            return result.returncode, "", ""
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


class PytskExtractor:
    """Cross-platform extractor using pytsk3."""
    
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.img = None
        self.fs = None
        self._open_image()
    
    def _open_image(self):
        """Open the disk image using pytsk3."""
        try:
            self.img = pytsk3.Img_Open(self.image_path)
        except Exception as e:
            raise Exception(f"Failed to open image: {e}")
    
    def get_partition_layout(self) -> List[Dict]:
        """Get partition layout using pytsk3."""
        partitions = []
        try:
            if hasattr(self.img, 'partition') or hasattr(self.img, 'tsk_part'):
                part_iter = self.img.tsk_part
                part_num = 0
                for part in part_iter:
                    if hasattr(part, 'start') and hasattr(part, 'len'):
                        start_sector = part.start
                        num_sectors = part.len
                        if start_sector > 0:
                            partitions.append({
                                "slot": f"{part_num}:",
                                "partition_num": part_num,
                                "start": str(start_sector),
                                "start_int": start_sector,
                                "end": str(start_sector + num_sectors),
                                "length": str(num_sectors),
                                "desc": part.desc or "Unknown"
                            })
                            part_num += 1
        except Exception as e:
            partitions.append({
                "slot": "0:",
                "partition_num": 0,
                "start": "0",
                "start_int": 0,
                "end": str(self.img.get_size() // 512),
                "length": str(self.img.get_size() // 512),
                "desc": "Whole disk (fallback)"
            })
        return partitions
    
    def get_partition_offset(self, partition_idx: int) -> int:
        """Get sector offset for a partition by index."""
        partitions = self.get_partition_layout()
        if partition_idx < len(partitions):
            return partitions[partition_idx].get("start_int", 0)
        return 0
    
    def list_files(self, partition_idx: int = 0, path: str = "/") -> List[str]:
        """List files in a directory."""
        offset = self.get_partition_offset(partition_idx)
        files = []
        try:
            fs = pytsk3.FS_Open(self.img, offset * 512)
            dir_obj = fs.open_dir(path)
            for entry in dir_obj:
                files.append(f"{entry.name.name}")
        except Exception as e:
            pass
        return files


class RawImageExtractor:
    """Fallback raw image parser for when TSK and pytsk3 are unavailable."""
    
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.file_size = os.path.getsize(image_path)
    
    def get_partition_layout(self) -> List[Dict]:
        """Detect partitions from MBR, GPT, and detect hidden/encrypted."""
        partitions = []
        
        is_e01 = self._is_e01_file()
        
        if is_e01:
            partitions = self._parse_e01_partitions()
            if not partitions:
                partitions = [{
                    "slot": "0:",
                    "partition_num": 0,
                    "start": "0",
                    "start_int": 0,
                    "end": str(self.file_size // 512),
                    "length": str(self.file_size // 512),
                    "desc": "E01 Container (raw disk image inside)",
                    "is_e01": True,
                    "note": "EnCase Evidence File - raw image embedded"
                }]
        else:
            partitions = self._parse_mbr()
        
        # If MBR has only GPT protective partition (0xEE), try GPT
        if partitions and len(partitions) == 1:
            # Check if it's a GPT protective partition
            if partitions[0].get('raw_type') == '0xee' or 'GPT' in partitions[0].get('desc', ''):
                print("[DEBUG] GPT protective partition detected, trying GPT parsing...")
                gpt_partitions = self._parse_gpt()
                if gpt_partitions:
                    partitions = gpt_partitions
        
        if not partitions or len(partitions) <= 1:
            gpt_partitions = self._parse_gpt()
            if gpt_partitions:
                partitions = gpt_partitions
        
        if not partitions:
            total_sectors = self.file_size // 512
            partitions.append({
                "slot": "0:",
                "partition_num": 0,
                "start": "0",
                "start_int": 0,
                "end": str(total_sectors),
                "length": str(total_sectors),
                "desc": "Whole disk (unpartitioned)"
            })
        
        partitions = self._detect_hidden_encrypted(partitions)
        
        return partitions
    
    def _is_e01_file(self) -> bool:
        """Check if file is EnCase Evidence File."""
        ext = Path(self.image_path).suffix.lower()
        if ext in ['.e01', '.e02', '.e03', '.ewf']:
            return True
            
        try:
            with open(self.image_path, 'rb') as f:
                header = f.read(64)
                if header[:4] == b'EVFY' or header[:4] == b'EVDF':
                    return True
                if b'EnCase' in header or b'EWF' in header:
                    return True
        except:
            pass
        return False
    
    def _parse_e01_partitions(self) -> List[Dict]:
        """Try to extract partitions from E01 (looks for raw disk inside)."""
        partitions = []
        try:
            with open(self.image_path, 'rb') as f:
                f.seek(0)
                # Read more data to search for embedded partition table
                data = f.read(16 * 1024 * 1024)  # Search first 16MB
                
                # Look for MBR signature (0x55AA at offset 0x1FE from sector start)
                # Search for pattern where 0xAA is followed by potential MBR data
                mbr_pos = -1
                for i in range(len(data) - 512):
                    if data[i] == 0x55 and i + 1 < len(data) and data[i+1] == 0xaa:
                        # Check if this looks like a valid MBR (at sector boundary)
                        # and has partition entries after it
                        if i % 512 == 0x1FE or i % 512 == 510:
                            mbr_pos = i - (i % 512)  # Go back to sector start
                            if mbr_pos >= 0 and mbr_pos < len(data) - 512:
                                # Verify it's a valid MBR by checking partition entries exist
                                if data[mbr_pos + 0x1BE:mbr_pos + 0x1EE] != b'\\x00' * 32:
                                    print(f"[DEBUG] Found potential MBR at offset {mbr_pos}")
                                    break
                
                if mbr_pos >= 0:
                    partitions = self._parse_mbr_at_offset(mbr_pos)
                    for p in partitions:
                        p["source"] = "E01 embedded MBR"
                        p["is_e01"] = True
                
                if not partitions:
                    gpt_sig = data.find(b'EFI PART')
                    if gpt_sig > 0:
                        partitions = self._parse_gpt_at_offset(gpt_sig)
                        for p in partitions:
                            p["source"] = "E01 embedded GPT"
                            p["is_e01"] = True
                            
        except Exception as e:
            print(f"[DEBUG] E01 partition parse error: {e}")
        return partitions
    
    def _parse_mbr_at_offset(self, offset: int) -> List[Dict]:
        """Parse MBR at specific offset."""
        partitions = []
        try:
            with open(self.image_path, 'rb') as f:
                # MBR signature is at offset 0x1FE (510) from start of sector
                f.seek(offset + 0x1FE)
                signature = f.read(2)
                print(f"[DEBUG] MBR signature at offset {offset + 0x1FE}: {signature.hex()}")
                if signature != b'\x55\xaa':
                    print(f"[DEBUG] Invalid MBR signature, got {signature}")
                    return partitions
                
                # Partition table starts at offset 0x1BE (446)
                f.seek(offset + 0x1BE)
                for i in range(4):
                    part_entry = f.read(16)
                    print(f"[DEBUG] Partition {i}: {part_entry.hex()}")
                    
                    # Check partition type - 0 means empty entry
                    part_type = part_entry[4]
                    if part_type == 0:
                        continue
                    
                    boot_indicator = part_entry[0]
                    start_sector = struct.unpack('<I', part_entry[8:12])[0]
                    num_sectors = struct.unpack('<I', part_entry[12:16])[0]
                    
                    print(f"[DEBUG] Partition {i}: type={hex(part_type)}, start={start_sector}, size={num_sectors}")
                    
                    # Accept partition if it has valid size or is a known partition type
                    if start_sector > 0 and num_sectors > 0:
                        is_hidden = (boot_indicator & 0x80) != 0
                        partitions.append({
                            "slot": f"{i}:",
                            "partition_num": i,
                            "start": str(start_sector),
                            "start_int": start_sector,
                            "start_sector": start_sector,
                            "end": str(start_sector + num_sectors),
                            "size_sectors": num_sectors,
                            "length": str(num_sectors),
                            "desc": self._get_partition_type(part_type),
                            "description": self._get_partition_type(part_type),
                            "fs": "NTFS" if part_type in [0x07, 0x17] else ("FAT" if part_type in [0x01, 0x04, 0x06, 0x0B, 0x0C, 0x0E] else "Unknown"),
                            "raw_type": hex(part_type),
                            "is_hidden": is_hidden,
                            "bootable": (boot_indicator & 0x80) != 0
                        })
        except Exception:
            pass
        return partitions
    
    def _get_partition_type(self, type_byte: int) -> str:
        """Get partition type description."""
        types = {
            0x01: "FAT12", 0x04: "FAT16", 0x05: "Extended",
            0x06: "FAT16B", 0x07: "NTFS/HPFS", 0x0B: "FAT32",
            0x0C: "FAT32X", 0x0E: "FAT16X", 0x0F: "ExtendedX",
            0x11: "Hidden FAT12", 0x14: "Hidden FAT16", 0x16: "Hidden FAT16B",
            0x17: "Hidden NTFS", 0x1B: "Hidden FAT32", 0x1C: "Hidden FAT32X",
            0x1E: "Hidden FAT16X", 0x27: "Windows RE", 0x82: "Linux Swap",
            0x83: "Linux", 0x85: "Linux Extended", 0x8E: "Linux LVM",
            0xA0: "Hibernation", 0xA5: "FreeBSD", 0xA6: "OpenBSD",
            0xA8: "MacOS X", 0xAB: "MacOS X Boot", 0xAF: "MacOS X HFS+",
            0xEB: "BeOS", 0xEE: "GPT Protective", 0xEF: "EFI System",
            0xFD: "Linux RAID"
        }
        return types.get(type_byte, f"Type 0x{type_byte:02X}")
    
    def _detect_hidden_encrypted(self, partitions: List[Dict]) -> List[Dict]:
        """Detect hidden and encrypted partitions."""
        for part in partitions:
            part_type = part.get("raw_type", "")
            desc = part.get("desc", "").lower()
            
            part["is_encrypted"] = False
            part["is_hidden"] = part.get("is_hidden", False)
            part["encryption_type"] = None
            
            if part_type in ["0xee", "0xef"]:
                part["is_gpt_protective"] = True
                
            if "bitlocker" in desc or "encrypted" in desc:
                part["is_encrypted"] = True
                part["encryption_type"] = "BitLocker"
                
            if any(h in desc for h in ["hidden", "recovery", "diagnostic"]):
                part["is_hidden"] = True
                
            if "0x17" == part_type or "0x27" in part_type:
                part["is_hidden"] = True
                
        return partitions
    
    def _parse_mbr(self) -> List[Dict]:
        """Parse MBR partition table."""
        return self._parse_mbr_at_offset(0)
    
    def _parse_gpt_at_offset(self, offset: int) -> List[Dict]:
        """Parse GPT at specific offset."""
        partitions = []
        try:
            with open(self.image_path, 'rb') as f:
                # GPT header is at LBA 1 (offset 512 from start)
                f.seek(offset + 512)
                header = f.read(92)
                if header[:8] != b'EFI PART':
                    return partitions
                
                # GPT header fields (offset from start of GPT header)
                # Offset 80-83: Number of partition entries
                # Offset 84-87: Size of partition entry  
                # Offset 72-79: Starting LBA of partition array
                part_entries = struct.unpack('<I', header[80:84])[0]  # Number of entries
                part_entry_size = struct.unpack('<I', header[84:88])[0]  # Size of each entry
                part_start_lba = struct.unpack('<Q', header[72:80])[0]  # LBA of partition table
                
                if part_entries == 0 or part_entry_size == 0 or part_start_lba == 0:
                    return partitions
                
                part_start = offset + part_start_lba * 512
                f.seek(part_start)
                
                for i in range(min(part_entries, 128)):
                    entry = f.read(part_entry_size)
                    if len(entry) < part_entry_size:
                        break
                    
                    part_type = entry[:16]
                    if all(b == 0 for b in part_type):
                        continue
                    
                    start_lba = struct.unpack('<Q', entry[32:40])[0]
                    end_lba = struct.unpack('<Q', entry[40:48])[0]
                    name = entry[56:128].decode('utf-16-le', errors='ignore').strip('\x00 ')
                    
                    if start_lba > 0 and end_lba > start_lba:
                        size_sectors = end_lba - start_lba + 1
                        partitions.append({
                            "slot": f"GPT {i}",
                            "partition_num": i,
                            "start": str(start_lba),
                            "start_int": start_lba,
                            "start_sector": start_lba,
                            "end_sector": end_lba,
                            "end": str(end_lba),
                            "size_sectors": size_sectors,
                            "length": str(size_sectors),
                            "desc": name or f"GPT Partition {i}",
                            "description": name or f"GPT Partition {i}",
                            "is_gpt": True,
                            "fs": "NTFS" if "NTFS" in name or "Basic" in name else "Unknown"
                        })
        except Exception as e:
            print(f"[DEBUG] GPT parse error: {e}")
        return partitions
    
    def _parse_gpt(self) -> List[Dict]:
        """Parse GPT partition table."""
        return self._parse_gpt_at_offset(0)
    
    def detect_filesystem(self, offset_sectors: int = 0) -> Optional[str]:
        """Detect filesystem type at given offset."""
        try:
            with open(self.image_path, 'rb') as f:
                f.seek(offset_sectors * 512 + 0x03)
                boot_sector = f.read(512)
                
                if boot_sector[3:11] == b'NTFS    ':
                    return "ntfs"
                
                if boot_sector[0x52:0x5A] == b'FAT32   ' or boot_sector[0x36:0x3E] == b'FAT32   ':
                    return "fat32"
                
                if boot_sector[0x36:0x3E] == b'FAT16   ' or boot_sector[0x28:0x30] == b'FAT16   ':
                    return "fat16"
                
                if boot_sector[0x28:0x3D] == b'FAT12   ' or boot_sector[0x36:0x3D] == b'FAT12   ':
                    return "fat12"
                
                if boot_sector[0x38:0x3C] == b'FAT    ':
                    return "fat"
                
                if boot_sector[0x38:0x3C] == b'FAT    ':
                    return "fat"
                
                ext2_magic = struct.unpack('<H', boot_sector[0x38:0x3A])[0]
                if ext2_magic == 0xEF53:
                    return "ext2"
                
        except Exception:
            pass
        return None
    
    def get_partition_offset(self, partition_idx: int) -> int:
        """Get sector offset for a partition by index."""
        partitions = self.get_partition_layout()
        if partition_idx < len(partitions):
            return partitions[partition_idx].get("start_int", 0)
        return 0
    
    def read_sectors(self, start_sector: int, num_sectors: int) -> bytes:
        """Read raw sectors from the image."""
        with open(self.image_path, 'rb') as f:
            f.seek(start_sector * 512)
            return f.read(num_sectors * 512)
    
    def list_files_basic(self, partition_idx: int = 0) -> List[str]:
        """Basic file listing for supported filesystems."""
        offset = self.get_partition_offset(partition_idx) * 512
        fs_type = self.detect_filesystem(offset // 512)
        
        files = []
        try:
            if fs_type == "ntfs":
                files = self._list_ntfs_files(offset)
            elif fs_type in ["fat12", "fat16", "fat32", "fat"]:
                files = self._list_fat_files(offset, fs_type)
        except Exception:
            pass
        return files
    
    def _list_ntfs_files(self, offset: int) -> List[str]:
        """Basic NTFS file listing from MFT."""
        files = []
        try:
            with open(self.image_path, 'rb') as f:
                mft_offset = offset + (0x30 * 512)
                f.seek(mft_offset)
                mft_entry = f.read(1024)
                
                if mft_entry[0:4] == b'FILE':
                    seq_num = struct.unpack('<H', mft_entry[0x10:0x12])[0]
                    if seq_num > 0:
                        files.append(f"MFT Record at offset {mft_offset} (seq: {seq_num})")
        except Exception:
            pass
        return files
    
    def _list_fat_files(self, offset: int, fs_type: str) -> List[str]:
        """Basic FAT file listing."""
        files = []
        try:
            with open(self.image_path, 'rb') as f:
                f.seek(offset)
                boot_sector = f.read(512)
                
                bytes_per_sector = struct.unpack('<H', boot_sector[0x0B:0x0D])[0]
                sectors_per_cluster = boot_sector[0x0D]
                reserved_sectors = struct.unpack('<H', boot_sector[0x0E:0x10])[0]
                num_fats = boot_sector[0x10]
                sectors_per_fat = struct.unpack('<I', boot_sector[0x24:0x28])[0] if fs_type == "fat32" else struct.unpack('<H', boot_sector[0x16:0x18])[0]
                
                root_dir_sector = reserved_sectors + (sectors_per_fat * num_fats)
                root_dir_offset = offset + (root_dir_sector * bytes_per_sector)
                
                f.seek(root_dir_offset)
                for _ in range(256):
                    entry = f.read(32)
                    if entry[0] == 0:
                        break
                    if entry[0] == 0xE5:
                        continue
                    if entry[11] & 0x08:
                        continue
                    
                    name = entry[:11].decode('ascii', errors='ignore').strip()
                    if name:
                        files.append(name)
        except Exception:
            pass
        return files

    def find_mft_entry_by_name(self, partition_offset: int, parent_mft_ref: int, target_name: str) -> Optional[int]:
        """Find MFT entry by filename within a parent directory."""
        try:
            with open(self.image_path, 'rb') as f:
                offset = partition_offset * 512
                
                f.seek(offset + (parent_mft_ref * 1024))
                mft_data = f.read(1024)
                
                if mft_data[:4] != b'FILE':
                    return None
                
                fixup_offset = struct.unpack('<H', mft_data[4:6])[0]
                attrs_offset = struct.unpack('<H', mft_data[20:22])[0]
                
                if attrs_offset < 48 or attrs_offset >= 1024:
                    return None
                
                pos = attrs_offset
                while pos < len(mft_data) - 48:
                    attr_type = struct.unpack('<I', mft_data[pos:pos+4])[0]
                    attr_len = struct.unpack('<I', mft_data[pos+4:pos+8])[0]
                    
                    if attr_len == 0:
                        break
                    
                    if attr_type == 0x90:
                        fname_offset = struct.unpack('<H', mft_data[pos+66:pos+68])[0]
                        fname_len = struct.unpack('<H', mft_data[pos+68:pos+70])[0]
                        
                        if fname_offset > pos and fname_offset + fname_len * 2 <= pos + attr_len:
                            fname_data = mft_data[fname_offset:fname_offset + fname_len * 2]
                            fname = fname_data.decode('utf-16-le', errors='ignore').strip('\x00')
                            
                            if fname.lower() == target_name.lower():
                                seq_num = struct.unpack('<H', mft_data[0x10:0x12])[0]
                                return struct.unpack('<I', mft_data[0x34:0x38])[0] & 0xFFFFFFFF
                    
                    pos += attr_len
                    
        except Exception:
            pass
        return None

    def read_usn_journal_data(self, partition_offset: int, mft_ref: int) -> Dict:
        """Read USN journal data from $J stream."""
        result = {
            "found": False,
            "entries": [],
            "max_size": 0,
            "allocated_size": 0,
            "next_usn": 0,
            "oldest_usn": 0,
        }
        
        try:
            with open(self.image_path, 'rb') as f:
                offset = partition_offset * 1024 + (mft_ref * 1024)
                f.seek(offset)
                mft_data = f.read(2048)
                
                if mft_data[:4] != b'FILE':
                    return result
                
                attrs_offset = struct.unpack('<H', mft_data[20:22])[0]
                
                pos = attrs_offset
                while pos < len(mft_data) - 64:
                    attr_type = struct.unpack('<I', mft_data[pos:pos+4])[0]
                    attr_len = struct.unpack('<I', mft_data[pos+4:pos+8])[0]
                    
                    if attr_len == 0:
                        break
                    
                    if attr_type == 0x80:
                        is_resident = mft_data[pos+8]
                        if is_resident == 0:
                            data_size = struct.unpack('<Q', mft_data[pos+16:pos+24])[0]
                            result["allocated_size"] = data_size
                            
                            data_run_start = pos + 32
                            if data_run_start < len(mft_data) - 8:
                                first_run = mft_data[data_run_start:data_run_start+8]
                                run_length = struct.unpack('<I', first_run[:4])[0]
                                run_offset = struct.unpack('<I', first_run[4:8])[0]
                                
                                if run_length > 0:
                                    journal_offset = partition_offset * 512 + (offset & 0xFFFFFE00) + run_offset
                                    f.seek(journal_offset)
                                    journal_header = f.read(64)
                                    
                                    if len(journal_header) >= 40:
                                        result["found"] = True
                                        result["max_size"] = struct.unpack('<Q', journal_header[8:16])[0]
                                        result["next_usn"] = struct.unpack('<Q', journal_header[16:24])[0]
                                        result["oldest_usn"] = struct.unpack('<Q', journal_header[24:32])[0]
                    
                    pos += attr_len
                    
        except Exception as e:
            result["error"] = str(e)
        
        return result

    def extract_usn_journal(self, partition_offset: int = 0) -> List[Dict]:
        """Extract USN journal entries from $Extend/$UsnJrnl."""
        usn_records = []
        try:
            with open(self.image_path, 'rb') as f:
                offset = partition_offset * 512
                
                usn_records.append({
                    "location": "Searching for $UsnJrnl in $Extend directory",
                    "method": "MFT analysis"
                })
                
                f.seek(offset + 0x30 * 1024)
                mft_data = f.read(1024)
                
                if mft_data[:4] != b'FILE':
                    usn_records.append({"error": "MFT header not found at entry 0x30"})
                    return usn_records
                
                extend_ref = None
                attrs_offset = struct.unpack('<H', mft_data[20:22])[0]
                
                if attrs_offset > 48 and attrs_offset < 1024:
                    pos = attrs_offset
                    while pos < len(mft_data) - 64:
                        attr_type = struct.unpack('<I', mft_data[pos:pos+4])[0]
                        attr_len = struct.unpack('<I', mft_data[pos+4:pos+8])[0]
                        
                        if attr_len == 0:
                            break
                        
                        if attr_type == 0x90:
                            fname_offset = struct.unpack('<H', mft_data[pos+66:pos+68])[0]
                            fname_len = struct.unpack('<H', mft_data[pos+68:pos+70])[0]
                            
                            if fname_offset > pos:
                                fname_data = mft_data[fname_offset:fname_offset + min(fname_len * 2, 64)]
                                fname = fname_data.decode('utf-16-le', errors='ignore').strip('\x00')
                                
                                if fname == "$Extend":
                                    parent_seq = struct.unpack('<H', mft_data[0x10:0x12])[0]
                                    extend_ref = struct.unpack('<I', mft_data[0x34:0x38])[0] & 0xFFFF
                                    usn_records.append({
                                        "found": "$Extend directory",
                                        "mft_reference": hex(extend_ref),
                                        "sequence": parent_seq
                                    })
                        
                        pos += attr_len
                
                if extend_ref:
                    usn_ref = self.find_mft_entry_by_name(partition_offset, extend_ref, "$UsnJrnl")
                    if usn_ref:
                        usn_records.append({
                            "status": "FOUND",
                            "file": "$UsnJrnl",
                            "mft_reference": hex(usn_ref),
                            "note": "USN journal MFT entry found"
                        })
                        
                        journal_data = self.read_usn_journal_data(partition_offset, usn_ref)
                        if journal_data.get("found"):
                            usn_records.append({
                                "status": "USN_JOURNAL_DATA_FOUND",
                                "max_size": journal_data.get("max_size", 0),
                                "allocated_size": journal_data.get("allocated_size", 0),
                                "next_usn": journal_data.get("next_usn", 0),
                                "oldest_usn": journal_data.get("oldest_usn", 0),
                                "entry_count": len(journal_data.get("entries", []))
                            })
                    else:
                        usn_records.append({
                            "status": "NOT_FOUND",
                            "note": "$UsnJrnl entry not found in $Extend directory",
                            "possible_reasons": [
                                "Journal may have been deleted/cleared",
                                "USN journaling not enabled",
                                "MFT entry outside scanned range"
                            ]
                        })
                else:
                    usn_records.append({
                        "status": "EXTEND_NOT_FOUND",
                        "note": "Could not locate $Extend directory"
                    })
                
                return usn_records
                
        except Exception as e:
            usn_records.append({"error": str(e)})
        
        return usn_records

    def parse_mft_entries(self, partition_offset: int = 0, max_entries: int = 100) -> List[Dict]:
        """Parse MFT (Master File Table) entries to extract file metadata."""
        mft_entries = []
        try:
            with open(self.image_path, 'rb') as f:
                offset = partition_offset * 512
                
                for i in range(max_entries):
                    mft_offset = offset + (i * 1024)
                    f.seek(mft_offset)
                    
                    header = f.read(48)
                    if len(header) < 48:
                        break
                    
                    if header[:4] != b'FILE':
                        break
                    
                    seq_num = struct.unpack('<H', header[0x10:0x12])[0]
                    link_count = struct.unpack('<H', header[0x12:0x14])[0]
                    
                    alloc_size = struct.unpack('<Q', header[0x28:0x30])[0]
                    real_size = struct.unpack('<Q', header[0x30:0x38])[0]
                    
                    if seq_num == 0:
                        continue
                    
                    timestamps = {}
                    try:
                        fixup_offset = struct.unpack('<H', header[0x04:0x06])[0]
                        if fixup_offset > 0:
                            f.seek(mft_offset + 512 - 2)
                            fixup_value = f.read(2)
                            f.seek(mft_offset + fixup_offset)
                            f.read(2)
                            for _ in range(3):
                                attr_type = struct.unpack('<I', f.read(4))[0]
                                attr_len = struct.unpack('<H', f.read(2))[0]
                                if attr_type == 0x10:
                                    pass
                                elif attr_type == 0x30:
                                    f.seek(mft_offset + fixup_offset + 24)
                                    created = struct.unpack('<Q', f.read(8))[0]
                                    modified = struct.unpack('<Q', f.read(8))[0]
                                    accessed = struct.unpack('<Q', f.read(8))[0]
                                    changed = struct.unpack('<Q', f.read(8))[0]
                                    
                                    timestamps = {
                                        "created": self._filetime_to_datetime(created) if created else None,
                                        "modified": self._filetime_to_datetime(modified) if modified else None,
                                        "accessed": self._filetime_to_datetime(accessed) if accessed else None,
                                        "changed": self._filetime_to_datetime(changed) if changed else None,
                                    }
                                    break
                                if attr_len == 0:
                                    break
                                f.seek(mft_offset + fixup_offset + attr_len - 4)
                    except Exception:
                        pass
                    
                    mft_entries.append({
                        "entry": i,
                        "sequence": seq_num,
                        "links": link_count,
                        "allocated_size": alloc_size,
                        "real_size": real_size,
                        "timestamps": timestamps
                    })
        except Exception:
            pass
        return mft_entries

    def _filetime_to_datetime(self, filetime: int) -> str:
        """Convert Windows FILETIME to ISO datetime string."""
        try:
            if filetime == 0:
                return "None"
            import datetime
            return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime // 10)
        except Exception:
            return "Invalid"

    def analyze_timestamp_consistency(self, partition_offset: int = 0) -> Dict:
        """Analyze consistency between MFT timestamps and USN journal."""
        from datetime import datetime
        
        result = {
            "partition_offset": partition_offset,
            "analyzed_at": str(datetime.now()),
            "total_mft_entries": 0,
            "total_usn_records": 0,
            "inconsistencies": [],
            "redundancy": [],
            "summary": ""
        }
        
        try:
            mft_entries = self.parse_mft_entries(partition_offset, max_entries=50)
            result["total_mft_entries"] = len(mft_entries)
            
            usn_records = self.extract_usn_journal(partition_offset)
            result["total_usn_records"] = len(usn_records)
            
            for entry in mft_entries:
                ts = entry.get("timestamps", {})
                created = ts.get("created")
                modified = ts.get("modified")
                changed = ts.get("changed")
                
                if created and modified and changed:
                    if changed < modified:
                        result["inconsistencies"].append({
                            "type": "modified_after_changed",
                            "entry": entry["entry"],
                            "message": f"MFT Entry {entry['entry']}: Changed time ({changed}) is before Modified time ({modified})",
                            "severity": "high"
                        })
                    
                    if created > modified:
                        result["inconsistencies"].append({
                            "type": "created_after_modified",
                            "entry": entry["entry"],
                            "message": f"MFT Entry {entry['entry']}: Created time ({created}) is after Modified time ({modified})",
                            "severity": "medium"
                        })
                
                if entry["real_size"] == 0 and entry["allocated_size"] > 0:
                    result["redundancy"].append({
                        "type": "allocated_not_used",
                        "entry": entry["entry"],
                        "message": f"MFT Entry {entry['entry']}: Allocated {entry['allocated_size']} bytes but real size is 0"
                    })
                
                if entry["link_count"] > 1:
                    result["redundancy"].append({
                        "type": "hardlinks",
                        "entry": entry["entry"],
                        "message": f"MFT Entry {entry['entry']}: Has {entry['link_count']} hard links (same data in multiple locations)"
                    })
            
            high_severity = sum(1 for i in result["inconsistencies"] if i["severity"] == "high")
            medium_severity = sum(1 for i in result["inconsistencies"] if i["severity"] == "medium")
            
            result["summary"] = (
                f"Found {len(mft_entries)} MFT entries, {len(usn_records)} USN records. "
                f"Detected {len(result['inconsistencies'])} timestamp inconsistencies "
                f"({high_severity} high, {medium_severity} medium) "
                f"and {len(result['redundancy'])} potential redundancies."
            )
            
        except Exception as e:
            result["summary"] = f"Analysis failed: {str(e)}"
        
        return result


class ForensicExtractor:
    def __init__(self, image_path: str, output_dir: str):
        self.image_path = image_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.image_type = self._detect_image_type()
        self.backend = self._init_backend()
        self.partitions = self.get_partition_layout()

    def _detect_image_type(self) -> str:
        """Detect image type from file extension."""
        ext = Path(self.image_path).suffix.lower()
        if ext in [".e01", ".ewf"]:
            return "ewf"
        return "raw"

    def _init_backend(self):
        """Initialize the appropriate backend based on availability."""
        if TSK_AVAILABLE:
            print("[*] Using The Sleuth Kit (TSK) backend")
            return "tsk"
        
        if PYTSK_AVAILABLE:
            print("[*] Using pytsk3 backend")
            try:
                return PytskExtractor(self.image_path)
            except Exception as e:
                print(f"[!] pytsk3 failed: {e}")
        
        if TSK_DOCKER_AVAILABLE:
            print("[*] Using TSK Docker backend")
            try:
                from imageProcessor.tsk_docker import TSKDocker
                
                # Validate and resolve the image path
                is_valid, error_msg = path_utils.validate_image_path(self.image_path)
                if not is_valid:
                    print(f"[!] {error_msg}")
                    print("[*] Falling back to raw image backend")
                    return RawImageExtractor(self.image_path)
                
                # Get absolute path for backend operations
                abs_image_path = path_utils.get_image_for_backend(self.image_path)
                logger.info(f"Using absolute image path: {abs_image_path}")
                
                # Ensure image is in evidence directory for Docker
                image_name, evidence_path = path_utils.ensure_image_in_evidence(self.image_path)
                logger.info(f"Image copied to evidence: {evidence_path}")
                
                tsk_docker = TSKDocker()
                # Store the image name for later use
                tsk_docker._image_name = image_name
                return tsk_docker
            except Exception as e:
                print(f"[!] TSK Docker failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("[*] Using raw image fallback backend")
        return RawImageExtractor(self.image_path)

    def run_command(self, cmd: List[str], capture: bool = True) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        return run_command(cmd, capture)

    def get_partition_offset(self, partition_idx: int) -> int:
        """Get sector offset for a partition by index."""
        if partition_idx < len(self.partitions):
            part = self.partitions[partition_idx]
            start = part.get("start_int", part.get("start_sector", 0))
            return start
        return 0

    def get_partition_offset_bytes(self, partition_idx: int) -> int:
        """Get byte offset for a partition by index."""
        return self.get_partition_offset(partition_idx) * 512

    def get_fls_cmd_base(self, sector_offset: int) -> List[str]:
        """Build base fls command with correct image type."""
        cmd = ["fls"]
        if self.image_type == "ewf":
            cmd.extend(["-i", "ewf"])
        cmd.extend(["-o", str(sector_offset)])
        return cmd

    def get_partition_layout(self) -> List[Dict]:
        """Get partition layout using available backend."""
        if self.backend == "tsk":
            pass  # Use local TSK commands below
        elif hasattr(self.backend, 'get_partition_layout'):
            # Use the image name stored in the backend (for Docker)
            if hasattr(self.backend, 'image_name') and self.backend.image_name:
                logger.info(f"Getting partition layout for: {self.backend.image_name}")
                return self.backend.get_partition_layout(self.backend.image_name)
            elif hasattr(self.backend, 'evidence_dir'):
                # Fallback: try to get from path
                image_name = Path(self.image_path).name
                return self.backend.get_partition_layout(image_name)
            return self.backend.get_partition_layout()
        
        cmd = ["mmls"]
        if self.image_type == "ewf":
            cmd.extend(["-i", "ewf"])
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)
        partitions = []

        if code == 0 and stdout:
            lines = stdout.strip().split("\n")
            for line in lines[3:]:
                parts = line.split()
                if len(parts) >= 4:
                    slot = parts[0]

                    if slot.startswith("000:") or "-------" in slot:
                        continue

                    is_partition = False
                    part_num = 0

                    if ":" in slot:
                        slot_parts = slot.split(":")
                        if len(slot_parts) == 2 and slot_parts[0].isdigit():
                            part_num = (
                                int(slot_parts[1]) if slot_parts[1].isdigit() else 0
                            )
                            is_partition = True
                    elif slot.replace("-", "").isdigit():
                        is_partition = True

                    if is_partition:
                        try:
                            start_sector = int(parts[2])
                            desc = (
                                " ".join(parts[5:])
                                if len(parts) > 5
                                else " ".join(parts[4:])
                                if len(parts) > 4
                                else ""
                            )
                            desc_lower = desc.lower()

                            skip_patterns = [
                                "unallocated",
                                "meta",
                                "header",
                                "table",
                                "gpt ",
                                "safety",
                            ]

                            if start_sector > 0 and not any(
                                p in desc_lower for p in skip_patterns
                            ):
                                partitions.append(
                                    {
                                        "slot": parts[0],
                                        "partition_num": part_num,
                                        "start": parts[2],
                                        "start_int": start_sector,
                                        "end": parts[3],
                                        "length": parts[4],
                                        "desc": desc,
                                    }
                                )
                        except (ValueError, IndexError):
                            pass
        
        if not partitions:
            partitions.append({
                "slot": "0:",
                "partition_num": 0,
                "start": "0",
                "start_int": 0,
                "end": str(os.path.getsize(self.image_path) // 512),
                "length": str(os.path.getsize(self.image_path) // 512),
                "desc": "Whole disk (fallback)"
            })
        return partitions

    def detect_filesystem(self, offset: int = 0) -> Optional[str]:
        """Detect filesystem type at given offset."""
        cmd = self.get_fls_cmd_base(offset)
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)
        if code == 0 and stdout:
            return "auto"

        for fs in ["ntfs", "fat", "ext2", "ext3", "ext4", "hfs", "apfs"]:
            cmd = self.get_fls_cmd_base(offset)
            cmd.extend(["-f", fs])
            cmd.append(self.image_path)

            code, stdout, stderr = self.run_command(cmd)
            if code == 0:
                return fs
        return "ntfs"

    def extract_mft(self, partition_num: int = 0) -> bool:
        """Extract and parse MFT records from partition."""
        output_file = self.output_dir / f"mft_partition_{partition_num}.txt"
        offset = self.get_partition_offset(partition_num)
        fs_type = self.detect_filesystem(offset)

        cmd = self.get_fls_cmd_base(offset)
        if fs_type and fs_type != "auto":
            cmd.extend(["-f", fs_type])
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)

        if code == 0 and stdout:
            with open(output_file, "w") as f:
                f.write(f"MFT Listing for Partition {partition_num}\n")
                f.write(f"Image: {self.image_path}\n")
                f.write(f"Offset: {offset} bytes\n")
                f.write(f"Filesystem: {fs_type}\n")
                f.write("=" * 80 + "\n\n")
                f.write(stdout)
            return True
        elif stderr:
            with open(output_file, "w") as f:
                f.write(f"MFT Listing for Partition {partition_num}\n")
                f.write(f"Error: {stderr}\n")
        return False

    def extract_usn_journal(self, partition_num: int = 0) -> bool:
        """Extract USN journal from NTFS partition."""
        output_file = self.output_dir / f"usn_journal_partition_{partition_num}.txt"
        offset = self.get_partition_offset(partition_num)
        fs_type = self.detect_filesystem(offset)

        cmd = self.get_fls_cmd_base(offset)
        cmd.append("-r")
        if fs_type and fs_type != "auto":
            cmd.extend(["-f", fs_type])
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)

        usn_files = []
        if code == 0 and stdout:
            for line in stdout.split("\n"):
                if "$UsnJrnl" in line or "usn" in line.lower():
                    usn_files.append(line)

        raw_usn_data = []
        usn_found = False
        
        # Try raw MFT extraction first
        raw_usn_data = []
        usn_found = False
        
        if hasattr(self.backend, 'extract_usn_journal') and callable(getattr(self.backend, 'extract_usn_journal', None)):
            try:
                backend_result = self.backend.extract_usn_journal(offset)
                # Handle both list (PyTSK) and dict (TSKDocker) return types
                if isinstance(backend_result, dict):
                    if backend_result.get("found") or backend_result.get("usn_journal_found"):
                        usn_found = True
                    raw_usn_data.append(backend_result)
                elif isinstance(backend_result, list):
                    raw_usn_data = backend_result
                    for entry in backend_result:
                        if isinstance(entry, dict):
                            if entry.get("status") == "FOUND" or entry.get("status") == "USN_JOURNAL_DATA_FOUND":
                                usn_found = True
            except Exception as e:
                raw_usn_data.append({"error": str(e)})
        
        # Try TSK Docker if raw extraction failed - use already initialized backend if available
        if not usn_found:
            print(f"[DEBUG] Raw USN failed, trying TSK Docker for partition {partition_num}...")
            try:
                # Check if we already have TSK Docker backend initialized
                if hasattr(self.backend, 'image_name') and self.backend.image_name:
                    print(f"[DEBUG] Using existing TSK Docker backend with image: {self.backend.image_name}")
                    # Get the TSKDocker instance and call extract_usn_journal directly
                    image_name = self.backend.image_name
                    # offset is already a sector offset from get_partition_offset
                    sector_offset = offset
                    
                    # Call the method directly on the backend
                    tsk_result = self.backend.extract_usn_journal(image_name, sector_offset)
                else:
                    # Fallback: try to import and use the function directly
                    from imageProcessor.tsk_docker import extract_usn_with_tsk
                    print(f"[DEBUG] Calling TSK Docker with image: {self.image_path}, offset: {offset // 512}")
                    tsk_result = extract_usn_with_tsk(self.image_path, offset // 512)
                
                print(f"[DEBUG] TSK Docker result: {tsk_result.get('usn_journal_found')}, error: {tsk_result.get('error')}")
                
                if tsk_result.get("usn_journal_found"):
                    usn_found = True
                    raw_usn_data.append({
                        "method": "docker_tsk",
                        "usn_inode": tsk_result.get("usn_inode"),
                        "usn_file": tsk_result.get("usn_file"),
                        "status": "FOUND_VIA_DOCKER"
                    })
                if tsk_result.get("partitions"):
                    raw_usn_data.append({"tsk_partitions": tsk_result.get("partitions")})
                if tsk_result.get("error"):
                    raw_usn_data.append({"tsk_error": tsk_result.get("error")})
            except Exception as e:
                print(f"[DEBUG] TSK Docker exception: {e}")
                import traceback
                traceback.print_exc()

        with open(output_file, "w") as f:
            # Get partition details
            part = self.partitions[partition_num] if partition_num < len(self.partitions) else {}
            part_size = part.get('size_sectors', 0) * 512  # Convert to bytes
            part_start = part.get('start_sector', offset // 512)
            part_desc = part.get('description', 'Unknown')
            part_fs = part.get('fs', fs_type or 'Unknown')
            
            f.write(f"USN Journal Analysis for Partition {partition_num}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"IMAGE INFORMATION:\n")
            f.write(f"  Image File: {self.image_path}\n")
            f.write(f"  Backend: {type(self.backend).__name__}\n\n")
            f.write(f"PARTITION INFORMATION:\n")
            f.write(f"  Partition Number: {partition_num}\n")
            f.write(f"  Partition Slot: {part.get('slot', 'N/A')}\n")
            f.write(f"  Start Sector: {part_start}\n")
            f.write(f"  Byte Offset: {part_start * 512}\n")
            f.write(f"  Size: {part_size:,} bytes ({part_size / (1024**3):.2f} GB)\n")
            f.write(f"  Filesystem: {part_fs}\n")
            f.write(f"  Description: {part_desc}\n\n")
            f.write(f"ANALYSIS:\n")
            f.write(f"  Sector Offset Used: {offset} sectors\n")
            f.write(f"  Byte Offset: {offset * 512:,} bytes\n")
            f.write(f"  Filesystem Detected: {fs_type}\n")
            f.write(f"\n{'='*80}\n\n")
            
            if usn_files:
                f.write("USN Journal Entries Found (via TSK):\n")
                f.write("\n".join(usn_files))
                f.write("\n\n")
            
            if raw_usn_data:
                f.write("USN Journal MFT Analysis:\n")
                f.write("-" * 40 + "\n")
                for entry in raw_usn_data:
                    if isinstance(entry, dict):
                        for key, value in entry.items():
                            f.write(f"  {key}: {value}\n")
                    else:
                        f.write(f"  {entry}\n")
                f.write("\n")
            
            if usn_found:
                f.write("\n[RESULT] USN JOURNAL DETECTED\n")
                for entry in raw_usn_data:
                    if isinstance(entry, dict):
                        if entry.get("usn_data_size"):
                            f.write(f"  USN Journal Size: {entry.get('usn_data_size'):,} bytes\n")
                        if entry.get("status") == "USN_JOURNAL_DATA_FOUND":
                            f.write(f"  Max Size: {entry.get('max_size', 0)} bytes\n")
                            f.write(f"  Allocated Size: {entry.get('allocated_size', 0)} bytes\n")
                            f.write(f"  Next USN: {entry.get('next_usn', 0)}\n")
                            f.write(f"  Oldest USN: {entry.get('oldest_usn', 0)}\n")
                        if entry.get("method") == "docker_tsk":
                            f.write(f"  Method: {entry.get('method')}\n")
                            f.write(f"  USN Inode: {entry.get('usn_inode')}\n")
                            if entry.get("usn_file"):
                                f.write(f"  USN File: {entry.get('usn_file')}\n")
            elif usn_files:
                f.write("\n[RESULT] USN JOURNAL FOUND (via TSK)\n")
            else:
                f.write("\n[RESULT] USN JOURNAL NOT FOUND OR NOT ACCESSIBLE\n")
                f.write("This could mean:\n")
                f.write("  - USN journal was cleared/deleted\n")
                f.write("  - USN journaling is not enabled on this volume\n")
                f.write("  - The journal is located outside the analyzed MFT range\n")
            
            if code != 0 and not usn_files:
                f.write("\n\nNote: TSK tools not available. Using raw MFT analysis.\n")
                f.write(f"TSK Error: {stderr[:500]}\n")
                
            f.write("\n" + "=" * 80 + "\n")
            f.write("Full file listing for reference:\n")
            f.write("=" * 40 + "\n")
            f.write(stdout[:100000])
        
        return usn_found

    def extract_registry_hives(self, partition_num: int = 0) -> bool:
        """Extract Windows registry hives from NTFS partition."""
        output_file = self.output_dir / f"registry_partition_{partition_num}.txt"
        offset = self.get_partition_offset(partition_num)
        fs_type = self.detect_filesystem(offset)

        cmd = ["fls", "-o", str(offset), "-r"]
        if fs_type and fs_type != "auto":
            cmd.extend(["-f", fs_type])
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)

        registry_patterns = [
            "System32/config/SAM",
            "System32/config/SECURITY",
            "System32/config/SOFTWARE",
            "System32/config/SYSTEM",
            "System32/config/DEFAULT",
            "NTUSER.DAT",
            "USRCLASS.DAT",
        ]

        registry_hives = []
        if code == 0 and stdout:
            for line in stdout.split("\n"):
                line_lower = line.lower()
                for pattern in registry_patterns:
                    if pattern.lower() in line_lower:
                        registry_hives.append(line)
                        break

        with open(output_file, "w") as f:
            f.write(f"Registry Hives for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write(f"Offset: {offset} bytes\n")
            f.write(f"Filesystem: {fs_type}\n")
            f.write("=" * 80 + "\n\n")
            if registry_hives:
                f.write("Registry Hives Found:\n")
                f.write("\n".join(registry_hives))
            else:
                f.write("No registry hives found in standard locations.\n")
                if code == 0 and stdout:
                    f.write("\nSearching full output for .DAT/.LOG files...\n")
                    for line in stdout.split("\n"):
                        if ".DAT" in line or ".LOG" in line:
                            f.write(line + "\n")
        return True

    def extract_logs(self, partition_num: int = 0) -> bool:
        """Extract Windows event logs and other log files."""
        output_file = self.output_dir / f"logs_partition_{partition_num}.txt"
        offset = self.get_partition_offset(partition_num)
        fs_type = self.detect_filesystem(offset)

        cmd = ["fls", "-o", str(offset), "-r"]
        if fs_type and fs_type != "auto":
            cmd.extend(["-f", fs_type])
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)

        log_patterns = [".evtx", ".log", "/Logs", "/Temp", "/Debug", "/Tracing"]

        log_files = []
        if code == 0 and stdout:
            for line in stdout.split("\n"):
                for pattern in log_patterns:
                    if pattern.lower() in line.lower():
                        log_files.append(line)
                        break

        with open(output_file, "w") as f:
            f.write(f"Log Files for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write(f"Offset: {offset} bytes\n")
            f.write(f"Filesystem: {fs_type}\n")
            f.write("=" * 80 + "\n\n")
            if log_files:
                f.write("Log Files Found:\n")
                f.write("\n".join(log_files))
            else:
                f.write("No explicit log files found.\n")
        return True

    def extract_timeline(self, partition_num: int = 0) -> bool:
        """Extract complete timeline for anti-forensic analysis."""
        output_file = self.output_dir / f"timeline_partition_{partition_num}.txt"
        offset = self.get_partition_offset(partition_num)
        fs_type = self.detect_filesystem(offset)

        cmd = ["fls", "-o", str(offset), "-r", "-l"]
        if fs_type and fs_type != "auto":
            cmd.extend(["-f", fs_type])
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)

        with open(output_file, "w") as f:
            f.write(f"Full Timeline for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write(f"Offset: {offset} bytes\n")
            f.write(f"Filesystem: {fs_type}\n")
            f.write("=" * 80 + "\n\n")
            if code == 0 and stdout:
                f.write(stdout)
            else:
                f.write(f"Error: {stderr}\n")
        return True

    def detect_shadow_copies(self, partition_num: int = 0) -> bool:
        """Detect shadow copies (anti-forensic technique)."""
        output_file = self.output_dir / f"shadow_copies_partition_{partition_num}.txt"
        offset = self.get_partition_offset(partition_num)
        fs_type = self.detect_filesystem(offset)

        cmd = ["fls", "-o", str(offset), "-r"]
        if fs_type and fs_type != "auto":
            cmd.extend(["-f", fs_type])
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)

        shadow_indicators = []
        keywords = [
            "shadow",
            "vss",
            "snapshot",
            "$Extend",
            "$Volume",
            "System Volume Information",
        ]

        if code == 0 and stdout:
            for line in stdout.split("\n"):
                for kw in keywords:
                    if kw.lower() in line.lower():
                        shadow_indicators.append(line)
                        break

        with open(output_file, "w") as f:
            f.write(f"Shadow Copy / VSS Indicators for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write(f"Offset: {offset} bytes\n")
            f.write(f"Filesystem: {fs_type}\n")
            f.write("=" * 80 + "\n\n")
            if shadow_indicators:
                f.write("Potential Shadow Copy / VSS Related Files:\n")
                f.write("\n".join(shadow_indicators))
            else:
                f.write("No shadow copy indicators found.\n")
        return True

    def detect_hidden_structures(self, partition_num: int = 0) -> bool:
        """Detect hidden files and alternate data streams."""
        output_file = (
            self.output_dir / f"hidden_structures_partition_{partition_num}.txt"
        )
        offset = self.get_partition_offset(partition_num)
        fs_type = self.detect_filesystem(offset)

        cmd = ["fls", "-o", str(offset), "-r", "-p"]
        if fs_type and fs_type != "auto":
            cmd.extend(["-f", fs_type])
        cmd.append(self.image_path)

        code, stdout, stderr = self.run_command(cmd)

        hidden_items = []
        if code == 0 and stdout:
            for line in stdout.split("\n"):
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) > 2:
                        hidden_items.append(line)

        with open(output_file, "w") as f:
            f.write(f"Hidden Structures / ADS for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write(f"Offset: {offset} bytes\n")
            f.write(f"Filesystem: {fs_type}\n")
            f.write("=" * 80 + "\n\n")
            if hidden_items:
                f.write("Potential Alternate Data Streams / Hidden Data:\n")
                f.write("\n".join(hidden_items))
            else:
                f.write("No hidden structures/ADS found.\n")
        return True

    def extract_timeline(self, partition_num: int = 0) -> bool:
        """Extract complete timeline for anti-forensic analysis."""
        output_file = self.output_dir / f"timeline_partition_{partition_num}.txt"
        offset = self.get_partition_offset(partition_num)

        cmd = ["fls", "-o", str(offset), "-r", "-l", self.image_path]
        code, stdout, stderr = self.run_command(cmd)

        with open(output_file, "w") as f:
            f.write(f"Full Timeline for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write(f"Offset: {offset} bytes\n")
            f.write("=" * 80 + "\n\n")
            if code == 0 and stdout:
                f.write(stdout)
            else:
                f.write(f"Error: {stderr}\n")
        return True

    def detect_shadow_copies(self, partition_num: int = 0) -> bool:
        """Detect shadow copies (anti-forensic technique)."""
        output_file = self.output_dir / f"shadow_copies_partition_{partition_num}.txt"
        offset = self.get_partition_offset(partition_num)

        cmd = ["fls", "-o", str(offset), "-r", self.image_path]
        code, stdout, stderr = self.run_command(cmd)

        shadow_indicators = []
        keywords = [
            "shadow",
            "vss",
            "snapshot",
            "$Extend",
            "$Volume",
            "System Volume Information",
        ]

        if code == 0 and stdout:
            for line in stdout.split("\n"):
                for kw in keywords:
                    if kw.lower() in line.lower():
                        shadow_indicators.append(line)
                        break

        with open(output_file, "w") as f:
            f.write(f"Shadow Copy / VSS Indicators for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write("=" * 80 + "\n\n")
            if shadow_indicators:
                f.write("Potential Shadow Copy / VSS Related Files:\n")
                f.write("\n".join(shadow_indicators))
            else:
                f.write("No shadow copy indicators found.\n")
        return True

    def detect_hidden_structures(self, partition_num: int = 0) -> bool:
        """Detect hidden files, alternate data streams, and hidden volumes."""
        output_file = (
            self.output_dir / f"hidden_structures_partition_{partition_num}.txt"
        )
        
        with open(output_file, "w") as f:
            f.write(f"Hidden Structures Analysis for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write("=" * 80 + "\n\n")
            
            # Get partition info
            if partition_num < len(self.partitions):
                part = self.partitions[partition_num]
                size_sectors = part.get('size_sectors', int(part.get('length', 0)))
                f.write(f"Partition Slot: {part.get('slot', 'N/A')}\n")
                f.write(f"Partition Size: {size_sectors * 512:,} bytes ({size_sectors * 512 / (1024**3):.2f} GB)\n")
                f.write(f"Filesystem: {part.get('fs', 'N/A')}\n\n")
            
            # Part 1: Alternate Data Streams detection
            f.write("-" * 80 + "\n")
            f.write("ALTERNATE DATA STREAMS / HIDDEN FILES\n")
            f.write("-" * 80 + "\n\n")
            
            offset = self.get_partition_offset(partition_num)
            cmd_result = None
            
            # Try TSK first, fallback to basic
            if hasattr(self.backend, 'fls'):
                try:
                    cmd_result = self.backend.fls(self.image_name or Path(self.image_path).name, offset, "/")
                except:
                    pass
            
            if not cmd_result:
                cmd = ["fls", "-o", str(offset), "-r", "-p", self.image_path]
                code, stdout, stderr = self.run_command(cmd)
                cmd_result = stdout if code == 0 else ""
            
            hidden_items = []
            if cmd_result and isinstance(cmd_result, str):
                for line in cmd_result.split("\n"):
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) > 2:
                            hidden_items.append(line)
            
            if hidden_items:
                f.write("Potential Alternate Data Streams / Hidden Data:\n")
                f.write("\n".join(hidden_items[:100]))  # Limit output
            else:
                f.write("No alternate data streams found.\n")
            
            # Part 2: Hidden Volume Detection
            f.write("\n" + "=" * 80 + "\n")
            f.write("HIDDEN VOLUME / HIDDEN OS DETECTION\n")
            f.write("=" * 80 + "\n\n")
            
            try:
                from imageProcessor.hidden_volume_detector import detect_hidden_volumes
                
                # Prepare partition info
                partition_info = {
                    "slot": self.partitions[partition_num].get("slot", ""),
                    "start_sector": self.partitions[partition_num].get("start_sector", 0),
                    "size_sectors": self.partitions[partition_num].get("size_sectors", 0)
                }
                
                results = detect_hidden_volumes(self.image_path, [partition_info])
                
                if results:
                    result = results[0]
                    
                    f.write(f"Hidden Volume Detected: {result.get('hidden_volume_detected', False)}\n")
                    f.write(f"Confidence: {result.get('confidence', 0) * 100:.1f}%\n")
                    f.write(f"Detection Method: {result.get('detection_method', 'N/A')}\n\n")
                    
                    details = result.get('details', '')
                    if details:
                        f.write(f"Details: {details}\n\n")
                    
                    # Entropy analysis
                    entropy = result.get('entropy_analysis', {})
                    if entropy:
                        f.write(f"Entropy Analysis:\n")
                        f.write(f"  Regions Scanned: {entropy.get('total_regions_scanned', 0)}\n")
                        f.write(f"  Encrypted Regions: {entropy.get('encrypted_regions', 0)}\n")
                        f.write(f"  Encrypted Percentage: {entropy.get('encrypted_percentage', 0):.1f}%\n")
                        f.write(f"  High Entropy Regions (>7.9): {entropy.get('high_entropy_regions', 0)}\n\n")
                    
                    # OS artifacts
                    os_art = result.get('os_artifacts', {})
                    if os_art:
                        f.write(f"OS Artifact Analysis:\n")
                        f.write(f"  Artifacts Found: {os_art.get('count', 0)}\n")
                        f.write(f"  Has Hidden OS Indicators: {os_art.get('has_hidden_os_indicators', False)}\n")
                        
                        artifacts = os_art.get('artifacts_found', [])
                        if artifacts:
                            f.write(f"\n  Detected Artifacts:\n")
                            for art in artifacts[:10]:
                                f.write(f"    - {art.get('artifact', 'Unknown')} at offset {art.get('offset', 0)}\n")
                else:
                    f.write("No hidden volume analysis results.\n")
                    
            except Exception as e:
                f.write(f"Hidden volume detection error: {str(e)}\n")
                import traceback
                traceback.print_exc(file=f)
            
            f.write("\n" + "=" * 80 + "\n")
            
        return True

    def detect_timestomping(self, partition_num: int = 0) -> bool:
        """Detect timestamp manipulation (anti-forensic)."""
        output_file = (
            self.output_dir / f"timestomp_indicators_partition_{partition_num}.txt"
        )
        offset = self.get_partition_offset(partition_num)

        cmd = ["fls", "-o", str(offset), "-r", "-l", self.image_path]
        code, stdout, stderr = self.run_command(cmd)

        with open(output_file, "w") as f:
            f.write(f"Timestamp Analysis for Partition {partition_num}\n")
            f.write(f"Image: {self.image_path}\n")
            f.write("=" * 80 + "\n\n")
            if code == 0 and stdout:
                f.write("Full file listing with timestamps:\n")
                f.write("Format: mode uid gid size date time name\n\n")
                f.write(stdout)
            else:
                f.write(f"Error: {stderr}\n")
        return True

    def extract_all_artifacts(self, partition_num: int = 0) -> Dict[str, bool]:
        """Extract all artifact types for a specific partition."""
        results = {}
        results["mft"] = self.extract_mft(partition_num)
        results["usn"] = self.extract_usn_journal(partition_num)
        results["registry"] = self.extract_registry_hives(partition_num)
        results["logs"] = self.extract_logs(partition_num)
        results["timeline"] = self.extract_timeline(partition_num)
        results["shadow_copies"] = self.detect_shadow_copies(partition_num)
        results["hidden_structures"] = self.detect_hidden_structures(partition_num)
        results["timestomp"] = self.detect_timestomping(partition_num)
        return results

    def extract_everything(self) -> Dict[str, Any]:
        """Extract all artifacts from all partitions and return summary."""
        summary = {
            "image": self.image_path,
            "partitions": [],
            "extracted_files": {
                "mft": [],
                "usn_journals": [],
                "registry": [],
                "logs": [],
                "timelines": [],
                "shadow_copies": [],
                "hidden_structures": [],
                "timestomp": [],
                "timestamp_analysis": [],
            },
            "status": {},
        }

        for part in self.partitions:
            summary["partitions"].append(
                {"slot": part["slot"], "start": part["start"], "desc": part["desc"]}
            )

        for i in range(len(self.partitions)):
            results = self.extract_all_artifacts(i)
            summary["status"][f"partition_{i}"] = results

            summary["extracted_files"]["mft"].append(f"mft_partition_{i}.txt")
            summary["extracted_files"]["usn_journals"].append(
                f"usn_journal_partition_{i}.txt"
            )
            summary["extracted_files"]["registry"].append(f"registry_partition_{i}.txt")
            summary["extracted_files"]["logs"].append(f"logs_partition_{i}.txt")
            summary["extracted_files"]["timelines"].append(
                f"timeline_partition_{i}.txt"
            )
            summary["extracted_files"]["shadow_copies"].append(
                f"shadow_copies_partition_{i}.txt"
            )
            summary["extracted_files"]["hidden_structures"].append(
                f"hidden_structures_partition_{i}.txt"
            )
            summary["extracted_files"]["timestomp"].append(
                f"timestomp_indicators_partition_{i}.txt"
            )
            
            offset = self.get_partition_offset(i)
            try:
                from imageProcessor.agents.timestamp_agent import analyze as timestamp_analyze
                ts_analysis = timestamp_analyze(self.image_path, offset)
            except Exception as e:
                ts_analysis = {"error": str(e)}
            ts_file = self.output_dir / f"timestamp_analysis_partition_{i}.json"
            with open(ts_file, "w") as f:
                json.dump(ts_analysis, f, indent=2)
            summary["extracted_files"]["timestamp_analysis"].append(
                f"timestamp_analysis_partition_{i}.json"
            )

        summary_file = self.output_dir / "extraction_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return summary


def main():
    parser = argparse.ArgumentParser(
        description="Forensic Artifact Extractor - Extract logs, MFT, USN journals, and registry hives",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.dd -o output --all
  %(prog)s image.E01 -o output --mft --registry
  %(prog)s image.dd --anti-forensic
  
Library usage:
  from forensic_extractor import ForensicExtractor
  extractor = ForensicExtractor("image.dd", "output")
  result = extractor.extract_everything()
        """,
    )
    parser.add_argument("image", help="Path to disk image file")
    parser.add_argument(
        "-o",
        "--output",
        default="forensic_output",
        help="Output directory (default: forensic_output)",
    )
    parser.add_argument(
        "-p",
        "--partition",
        type=int,
        default=-1,
        help="Specific partition number (default: all)",
    )
    parser.add_argument("--mft", action="store_true", help="Extract MFT only")
    parser.add_argument("--usn", action="store_true", help="Extract USN journals only")
    parser.add_argument(
        "--registry", action="store_true", help="Extract registry hives only"
    )
    parser.add_argument("--logs", action="store_true", help="Extract logs only")
    parser.add_argument("--timeline", action="store_true", help="Extract timeline only")
    parser.add_argument(
        "--anti-forensic", action="store_true", help="Run anti-forensic detection only"
    )
    parser.add_argument("--all", action="store_true", help="Extract everything")

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)

    extractor = ForensicExtractor(args.image, args.output)

    print(f"Processing image: {args.image}")
    print(f"Output directory: {args.output}")
    print(f"Found {len(extractor.partitions)} partitions")

    if args.all:
        print("Extracting all artifacts...")
        summary = extractor.extract_everything()
        print(
            f"Extraction complete. Summary: {len(summary['extracted_files']['mft'])} MFT, "
            f"{len(summary['extracted_files']['registry'])} registry files"
        )
        print(f"Summary saved to {args.output}/extraction_summary.json")

    elif args.anti_forensic:
        print("Running anti-forensic detection...")
        for i in range(len(extractor.partitions)):
            extractor.detect_shadow_copies(i)
            extractor.detect_hidden_structures(i)
            extractor.detect_timestomping(i)
        print("Anti-forensic detection complete.")

    else:
        target_partitions = (
            [args.partition]
            if args.partition >= 0
            else range(len(extractor.partitions))
        )

        if args.mft:
            for i in target_partitions:
                extractor.extract_mft(i)
        if args.usn:
            for i in target_partitions:
                extractor.extract_usn_journal(i)
        if args.registry:
            for i in target_partitions:
                extractor.extract_registry_hives(i)
        if args.logs:
            for i in target_partitions:
                extractor.extract_logs(i)
        if args.timeline:
            for i in target_partitions:
                extractor.extract_timeline(i)

        if not any([args.mft, args.usn, args.registry, args.logs, args.timeline]):
            print("No extraction option specified. Use --all for full extraction.")
            print("Use -h for help.")


if __name__ == "__main__":
    main()
