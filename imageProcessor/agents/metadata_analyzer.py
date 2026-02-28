#!/usr/bin/env python3
"""
File Metadata Timestamp Analyzer
Compares file system timestamps with internal metadata timestamps.
Detects timestomping by comparing:
- MFT/filesystem timestamps
- Document properties (Office)
- EXIF data (images)
- PDF metadata
- PE compile timestamps
"""

import os
import sys
import struct
import datetime
import zipfile
import json
import io
from pathlib import Path
from typing import Dict, List, Optional, Any
from xml.etree import ElementTree as ET


def filetime_to_datetime(filetime: int) -> Optional[datetime.datetime]:
    if filetime == 0:
        return None
    try:
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime // 10)
    except Exception:
        return None


def filetime_to_iso(filetime: int) -> Optional[str]:
    dt = filetime_to_datetime(filetime)
    return dt.isoformat() if dt else None


def get_filesystem_timestamps(file_path: str) -> Dict[str, Any]:
    """Get file system timestamps."""
    try:
        stat = os.stat(file_path)
        return {
            "accessed": datetime.datetime.fromtimestamp(stat.st_atime).isoformat(),
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }
    except Exception:
        return {}


def parse_office_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from Office Open XML files (.docx, .xlsx, .pptx)."""
    metadata = {"type": "office", "found": False}
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            core_xml = None
            app_xml = None
            
            try:
                core_xml = zf.read('docProps/core.xml')
            except KeyError:
                pass
            
            try:
                app_xml = zf.read('docProps/app.xml')
            except KeyError:
                pass
            
            if core_xml:
                root = ET.fromstring(core_xml)
                ns = {'dc': 'http://purl.org/dc/elements/1.1/', 'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'}
                ns_cp = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                ns_dc = "http://purl.org/dc/elements/1.1/"
                ns_dcterms = "http://purl.org/dc/terms/"

                created = root.find(f'{{{ns_dcterms}}}created')
                modified = root.find(f'{{{ns_dcterms}}}modified')
                creator = root.find(f'{{{ns_dc}}}creator')
                modified_by = root.find(f'{{{ns_cp}}}lastModifiedBy')
                
                metadata["created"] = created.text if created is not None else None
                metadata["modified"] = modified.text if modified is not None else None
                metadata["creator"] = creator.text if creator is not None else None
                metadata["last_modified_by"] = modified_by.text if modified_by is not None else None
                metadata["found"] = True
                
            if app_xml:
                root = ET.fromstring(app_xml)
                ns = {'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes', 'xp': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                
                company = root.find('.//Company', ns)
                manager = root.find('.//Manager', ns)
                
                metadata["company"] = company.text if company is not None else None
                metadata["manager"] = manager.text if manager is not None else None
                
    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata


def parse_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from PDF files."""
    metadata = {"type": "pdf", "found": False}
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read(100000)
            
            author_match = b'/Author '
            creator_match = b'/Creator '
            producer_match = b'/Producer '
            creation_match = b'/CreationDate '
            mod_match = b'/ModDate '
            
            def extract_string(data, marker):
                idx = data.find(marker)
                if idx == -1:
                    return None
                start = idx + len(marker)
                end = start
                while end < len(data) and data[end:end+1] in b'()/<>0123456789abcdefABCDEF':
                    end += 1
                try:
                    return data[start:end].decode('utf-8', errors='ignore').strip('() ')
                except:
                    return None
            
            author = extract_string(content, author_match)
            creator = extract_string(content, creator_match)
            producer = extract_string(content, producer_match)
            created = extract_string(content, creation_match)
            modified = extract_string(content, mod_match)
            
            if author or creator or producer:
                metadata["found"] = True
                metadata["author"] = author
                metadata["creator"] = creator
                metadata["producer"] = producer
                metadata["created"] = created
                metadata["modified"] = modified
                
    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata


def parse_exif_metadata(file_path: str) -> Dict[str, Any]:
    """Extract EXIF data from images (JPEG, PNG)."""
    metadata = {"type": "image", "found": False}
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read(100000)
            
            if data[:2] == b'\xFF\xD8':
                metadata["format"] = "JPEG"
                
                i = 2
                while i < len(data) - 10:
                    if data[i] != 0xFF:
                        break
                    
                    marker = data[i+1]
                    
                    if marker == 0xD8 or marker == 0xD9:
                        i += 1
                        continue
                    
                    if marker == 0xE1:
                        exif_len = struct.unpack('>H', data[i+2:i+4])[0]
                        exif_data = data[i+4:i+2+exif_len]
                        
                        if exif_data[:4] == b'Exif':
                            metadata["found"] = True
                            
                            tiff_data = exif_data[6:]
                            little_endian = tiff_data[0:2] == b'II'
                            
                            ifds = []
                            offset = struct.unpack(little_endian and '<I' or '>I', tiff_data[4:8])[0]
                            
                            while offset > 0 and offset < len(tiff_data) - 2:
                                num_tags = struct.unpack(little_endian and '<H' or '>H', tiff_data[offset:offset+2])[0]
                                offset += 2
                                
                                for _ in range(min(num_tags, 20)):
                                    if offset + 12 > len(tiff_data):
                                        break
                                    tag = struct.unpack(little_endian and '<H' or '>H', tiff_data[offset:offset+2])[0]
                                    offset += 2
                                    
                                    if tag == 0x0132:
                                        val = tiff_data[offset+8:offset+12]
                                        if len(val) == 9:
                                            try:
                                                dt = datetime.datetime.strptime(val.decode('ascii'), '%Y:%m%d')
                                                metadata["datetime_original"] = dt.isoformat()
                                            except:
                                                pass
                                    elif tag == 0x0131:
                                        val = tiff_data[offset+8:offset+20]
                                        if len(val) >= 8:
                                            metadata["software"] = val.split(b'\x00')[0].decode('ascii', errors='ignore')
                                            
                                    offset += 10
                                break
                        break
                    
                    elif marker == 0xDB:
                        break
                    else:
                        length = struct.unpack('>H', data[i+2:i+4])[0]
                        i += 2 + length
                        
            elif data[:8] == b'\x89PNG\r\n\x1a\n':
                metadata["format"] = "PNG"
                
                i = 8
                while i < len(data) - 12:
                    chunk_len = struct.unpack('>I', data[i:i+4])[0]
                    chunk_type = data[i+4:i+8]
                    
                    if chunk_type == b'tEXt' or chunk_type == b'iTXt':
                        metadata["found"] = True
                        
                    if chunk_type == b'IEND':
                        break
                    
                    i += 12 + chunk_len
                    
    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata


def parse_pe_metadata(file_path: str) -> Dict[str, Any]:
    """Extract timestamps from PE executables."""
    metadata = {"type": "pe", "found": False}
    
    try:
        with open(file_path, 'rb') as f:
            dos_header = f.read(64)
            
            if dos_header[:2] != b'MZ':
                return metadata
            
            pe_offset = struct.unpack('<I', dos_header[60:64])[0]
            
            f.seek(pe_offset)
            pe_sig = f.read(4)
            
            if pe_sig != b'PE\x00\x00':
                return metadata
            
            file_header = f.read(20)
            
            time_date_stamp = struct.unpack('<I', file_header[4:8])[0]
            
            if time_date_stamp > 0:
                metadata["compile_timestamp"] = datetime.datetime.fromtimestamp(time_date_stamp).isoformat()
                metadata["compile_timestamp_raw"] = time_date_stamp
                metadata["found"] = True
            
            optional_header_size = struct.unpack('<H', file_header[16:18])[0]
            
            if optional_header_size >= 64:
                optional_header = f.read(optional_header_size)
                
                if optional_header[:2] == b'PE':
                    magic = struct.unpack('<H', optional_header[16:18])[0]
                    
                    if magic == 0x10b:
                        resource_offset = struct.unpack('<I', optional_header[96:100])[0]
                    elif magic == 0x20b:
                        resource_offset = struct.unpack('<I', optional_header[112:116])[0]
                    else:
                        resource_offset = 0
                        
    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata


def parse_archive_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from ZIP archives."""
    metadata = {"type": "archive", "found": False}
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            info = zf.infolist()
            
            if info:
                metadata["found"] = True
                metadata["files"] = len(info)
                
                timestamps = []
                for zinfo in info[:10]:
                    if zinfo.date_time:
                        try:
                            dt = datetime.datetime(*zinfo.date_time)
                            timestamps.append(dt.isoformat())
                        except:
                            pass
                
                metadata["entries"] = timestamps
                
    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata


def extract_file_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata based on file type."""
    ext = Path(file_path).suffix.lower()
    
    if ext in ['.docx', '.xlsx', '.pptx', '.vsdx', '.docm', '.xlsm', '.pptm']:
        return parse_office_metadata(file_path)
    elif ext == '.pdf':
        return parse_pdf_metadata(file_path)
    elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic']:
        return parse_exif_metadata(file_path)
    elif ext in ['.exe', '.dll']:
        return parse_pe_metadata(file_path)
    elif ext in ['.zip', '.jar']:
        return parse_archive_metadata(file_path)
    else:
        return {"type": "unknown", "found": False}


def compare_timestamps(fs_timestamps: Dict, metadata: Dict) -> List[Dict]:
    """Compare filesystem timestamps with metadata timestamps."""
    inconsistencies = []
    
    if not metadata.get("found"):
        return inconsistencies
    
    fs_modified = fs_timestamps.get("modified")
    fs_created = fs_timestamps.get("created")
    
    meta_created = metadata.get("created")
    meta_modified = metadata.get("modified")
    
    if meta_created:
        try:
            if 'T' in meta_created:
                meta_dt = datetime.datetime.fromisoformat(meta_created.replace('Z', '+00:00'))
            else:
                meta_dt = datetime.datetime.strptime(meta_created, '%Y-%m-%dT%H:%M:%S')
            
            if fs_created:
                fs_dt = datetime.datetime.fromisoformat(fs_created)
                
                diff = abs((meta_dt - fs_dt).total_seconds())
                
                if diff > 86400:
                    inconsistencies.append({
                        "type": "created_mismatch",
                        "severity": "high",
                        "message": "Document created date differs from file system",
                        "description": f"Metadata created: {meta_created}, FS created: {fs_created} (diff: {diff/86400:.1f} days)",
                    })
                    
        except Exception:
            pass
    
    if meta_modified:
        try:
            if 'T' in meta_modified:
                meta_dt = datetime.datetime.fromisoformat(meta_modified.replace('Z', '+00:00'))
            else:
                meta_dt = datetime.datetime.strptime(meta_modified, '%Y-%m-%dT%H:%M:%S')
            
            if fs_modified:
                fs_dt = datetime.datetime.fromisoformat(fs_modified)
                
                diff = abs((meta_dt - fs_dt).total_seconds())
                
                if diff > 86400:
                    inconsistencies.append({
                        "type": "modified_mismatch",
                        "severity": "high",
                        "message": "Document modified date differs from file system",
                        "description": f"Metadata modified: {meta_modified}, FS modified: {fs_modified} (diff: {diff/86400:.1f} days)",
                    })
                    
        except Exception:
            pass
    
    if metadata.get("type") == "pe" and metadata.get("compile_timestamp"):
        compile_ts = metadata.get("compile_timestamp")
        
        if fs_created:
            try:
                fs_dt = datetime.datetime.fromisoformat(fs_created)
                compile_dt = datetime.datetime.fromisoformat(compile_ts)
                
                diff = abs((compile_dt - fs_dt).total_seconds())
                
                if diff > 86400:
                    inconsistencies.append({
                        "type": "compile_mismatch",
                        "severity": "high",
                        "message": "PE compile timestamp differs from file system",
                        "description": f"Compile timestamp: {compile_ts}, FS created: {fs_created}",
                    })
            except Exception:
                pass
    
    return inconsistencies


def analyze_directory_metadata(directory: str, max_files: int = 100) -> Dict[str, Any]:
    """Analyze all files in a directory for metadata timestamp inconsistencies."""
    results = {
        "directory": directory,
        "files_analyzed": 0,
        "files_with_metadata": 0,
        "inconsistencies": [],
        "summary": "",
    }
    
    try:
        files = list(Path(directory).rglob('*'))
        files = [f for f in files if f.is_file()][:max_files]
        
        for file_path in files:
            if file_path.is_file():
                try:
                    fs_ts = get_filesystem_timestamps(str(file_path))
                    metadata = extract_file_metadata(str(file_path))
                    
                    results["files_analyzed"] += 1
                    
                    if metadata.get("found"):
                        results["files_with_metadata"] += 1
                        
                        incs = compare_timestamps(fs_ts, metadata)
                        
                        for inc in incs:
                            inc["file"] = str(file_path.name)
                            inc["full_path"] = str(file_path)
                            results["inconsistencies"].append(inc)
                            
                except Exception:
                    pass
                    
    except Exception as e:
        results["error"] = str(e)
    
    high_count = sum(1 for i in results["inconsistencies"] if i.get("severity") == "high")
    medium_count = sum(1 for i in results["inconsistencies"] if i.get("severity") == "medium")
    
    results["summary"] = (
        f"Analyzed {results['files_analyzed']} files. "
        f"{results['files_with_metadata']} with extractable metadata. "
        f"Found {len(results['inconsistencies'])} timestamp inconsistencies "
        f"({high_count} high, {medium_count} medium)."
    )
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="File Metadata Timestamp Analyzer")
    parser.add_argument("path", help="File or directory to analyze")
    parser.add_argument("--max-files", type=int, default=100, help="Max files to analyze")
    args = parser.parse_args()
    
    if os.path.isdir(args.path):
        results = analyze_directory_metadata(args.path, args.max_files)
    else:
        fs_ts = get_filesystem_timestamps(args.path)
        metadata = extract_file_metadata(args.path)
        incs = compare_timestamps(fs_ts, metadata)
        
        results = {
            "file": args.path,
            "filesystem_timestamps": fs_ts,
            "metadata": metadata,
            "inconsistencies": incs,
        }
    
    print(json.dumps(results, indent=2, default=str))
