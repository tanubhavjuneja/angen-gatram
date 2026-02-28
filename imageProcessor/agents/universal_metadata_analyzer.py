#!/usr/bin/env python3
"""
Universal Metadata Timestamp Analyzer
Compares file system timestamps with internal metadata timestamps to detect timestomping.

Detects timestamp manipulation by comparing:
- MFT/filesystem timestamps (accessed, modified, created)
- Document properties (Office: docProps/core.xml, app.xml)
- EXIF data (images: APP1 marker)
- PDF metadata (/Info dictionary, XMP block)
- PE compile timestamps (exe/dll headers)
- Video/Audio metadata (moov atoms, ID3 tags)
- Archive timestamps (ZIP central directory)
- LNK file timestamps
"""

import os
import sys
import struct
import datetime
import zipfile
import json
import io
import re
import math
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from xml.etree import ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class TimestampAnalysis:
    source: str
    timestamp: Optional[datetime.datetime]
    raw_value: Any
    iso_string: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp and not self.iso_string:
            self.iso_string = self.timestamp.isoformat()


@dataclass
class TimestompDetection:
    file_path: str
    file_type: str
    inconsistency_type: str
    severity: str
    description: str
    filesystem_timestamps: Dict[str, Any] = field(default_factory=dict)
    metadata_timestamps: Dict[str, Any] = field(default_factory=dict)
    time_difference_seconds: float = 0.0
    time_difference_display: str = ""


class FilesystemTimestampExtractor:
    """Extract timestamps from filesystem."""
    
    @staticmethod
    def get_stat_timestamps(file_path: str) -> Dict[str, TimestampAnalysis]:
        """Get filesystem timestamps using os.stat."""
        timestamps = {}
        
        try:
            stat = os.stat(file_path)
            
            timestamps["accessed"] = TimestampAnalysis(
                source="filesystem_stat",
                timestamp=datetime.datetime.fromtimestamp(stat.st_atime),
                raw_value=stat.st_atime
            )
            timestamps["modified"] = TimestampAnalysis(
                source="filesystem_stat", 
                timestamp=datetime.datetime.fromtimestamp(stat.st_mtime),
                raw_value=stat.st_mtime
            )
            timestamps["created"] = TimestampAnalysis(
                source="filesystem_stat",
                timestamp=datetime.datetime.fromtimestamp(stat.st_ctime),
                raw_value=stat.st_ctime
            )
            
        except Exception as e:
            timestamps["error"] = TimestampAnalysis(
                source="filesystem_stat",
                timestamp=None,
                raw_value=str(e)
            )
        
        return timestamps
    
    @staticmethod
    def get_ntfs_timestamps(file_path: str) -> Dict[str, TimestampAnalysis]:
        """Get NTFS-specific timestamps if available."""
        timestamps = {}
        
        try:
            import win32file
            import win32con
            
            handle = win32file.CreateFile(
                file_path,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )
            
            info = win32file.GetFileInformationByHandleEx(handle, 2)
            
            timestamps["creation_time"] = TimestampAnalysis(
                source="ntfs_creation_time",
                timestamp=FilesystemTimestampExtractor._filetime_to_datetime(info['CreationTime']),
                raw_value=info['CreationTime']
            )
            timestamps["last_access_time"] = TimestampAnalysis(
                source="ntfs_last_access",
                timestamp=FilesystemTimestampExtractor._filetime_to_datetime(info['LastAccessTime']),
                raw_value=info['LastAccessTime']
            )
            timestamps["last_write_time"] = TimestampAnalysis(
                source="ntfs_last_write",
                timestamp=FilesystemTimestampExtractor._filetime_to_datetime(info['LastWriteTime']),
                raw_value=info['LastWriteTime']
            )
            
            win32file.CloseHandle(handle)
            
        except ImportError:
            timestamps["note"] = TimestampAnalysis(
                source="ntfs",
                timestamp=None,
                raw_value="win32file not available"
            )
        except Exception:
            pass
        
        return timestamps
    
    @staticmethod
    def _filetime_to_datetime(filetime: int) -> Optional[datetime.datetime]:
        if filetime == 0:
            return None
        try:
            return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime // 10)
        except Exception:
            return None


class OfficeMetadataExtractor:
    """Extract metadata from Microsoft Office files."""
    
    OFFICE_EXTENSIONS = ['.docx', '.xlsx', '.pptx', '.vsdx', '.docm', '.xlsm', '.pptm', '.odt', '.ods', '.odp']
    
    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        """Extract metadata from Office Open XML files."""
        metadata = {
            "file_type": "office",
            "format": "open_xml",
            "found": False,
            "timestamps": {},
            "author_info": {},
            "application_info": {},
            "raw_metadata": {}
        }
        
        ext = Path(file_path).suffix.lower()
        
        if ext == '.docx' or ext == '.docm':
            metadata["office_type"] = "Word"
        elif ext == '.xlsx' or ext == '.xlsm':
            metadata["office_type"] = "Excel"
        elif ext == '.pptx' or ext == '.pptm':
            metadata["office_type"] = "PowerPoint"
        elif ext == '.vsdx':
            metadata["office_type"] = "Visio"
        else:
            metadata["office_type"] = "Office"
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                OfficeMetadataExtractor._parse_core_xml(zf, metadata)
                OfficeMetadataExtractor._parse_app_xml(zf, metadata)
                OfficeMetadataExtractor._parse_custom_xml(zf, metadata)
                
        except zipfile.BadZipFile:
            metadata["error"] = "Not a valid ZIP archive (possibly legacy OLE format)"
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    @staticmethod
    def _parse_core_xml(zf: zipfile.ZipFile, metadata: Dict):
        """Parse core.xml for core properties."""
        try:
            core_xml = zf.read('docProps/core.xml')
            root = ET.fromstring(core_xml)
            
            ns = {
                'dc': 'http://purl.org/dc/elements/1.1/',
                'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                'dcterms': 'http://purl.org/dc/terms/'
            }
            
            timestamp_fields = {
                'dc:created': 'created',
                'cp:lastModifiedBy': 'last_modified_by',
                'dcterms:modified': 'modified',
                'dcterms:created': 'created',
            }
            
            for xpath, key in timestamp_fields.items():
                element = root.find(xpath, ns)
                if element is not None and element.text:
                    ts = OfficeMetadataExtractor._parse_w3cdtf(element.text)
                    if ts:
                        metadata["timestamps"][key] = TimestampAnalysis(
                            source="office_core_xml",
                            timestamp=ts,
                            raw_value=element.text
                        )
                        metadata["found"] = True
            
            for tag in ['dc:creator', 'cp:lastModifiedBy']:
                element = root.find(tag, ns)
                if element is not None and element.text:
                    metadata["author_info"][tag.split(':')[-1]] = element.text
                    metadata["found"] = True
            
            revision = root.find('.//cp:revision', ns)
            if revision is not None and revision.text:
                metadata["author_info"]["revision"] = revision.text
            
            metadata["raw_metadata"]["core_xml"] = ET.tostring(root, encoding='unicode')[:500]
            
        except KeyError:
            pass
        except Exception:
            pass
    
    @staticmethod
    def _parse_app_xml(zf: zipfile.ZipFile, metadata: Dict):
        """Parse app.xml for application properties."""
        try:
            app_xml = zf.read('docProps/app.xml')
            root = ET.fromstring(app_xml)
            
            ns = {'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'}
            
            app_fields = {
                'Application': 'application',
                'AppVersion': 'app_version',
                'Company': 'company',
                'Manager': 'manager',
                'Template': 'template',
                'TotalTime': 'total_edit_time',
                'Pages': 'pages',
                'Words': 'words',
                'Characters': 'characters'
            }
            
            for tag, key in app_fields.items():
                element = root.find(f'.//{tag}')
                if element is not None and element.text:
                    metadata["application_info"][key] = element.text
                    metadata["found"] = True
            
            metadata["raw_metadata"]["app_xml"] = ET.tostring(root, encoding='unicode')[:500]
            
        except KeyError:
            pass
        except Exception:
            pass
    
    @staticmethod
    def _parse_custom_xml(zf: zipfile.ZipFile, metadata: Dict):
        """Parse custom.xml for custom properties."""
        try:
            custom_xml = zf.read('docProps/custom.xml')
            root = ET.fromstring(custom_xml)
            
            properties = {}
            for prop in root.findall('.//property'):
                name = prop.get('name')
                value = prop.text
                if name and value:
                    properties[name] = value
            
            if properties:
                metadata["application_info"]["custom_properties"] = properties
                metadata["found"] = True
                
        except KeyError:
            pass
        except Exception:
            pass
    
    @staticmethod
    def _parse_w3cdtf(date_str: str) -> Optional[datetime.datetime]:
        """Parse W3CDTF date format (ISO 8601)."""
        if not date_str:
            return None
        
        try:
            date_str = date_str.replace('Z', '+00:00')
            if '.' in date_str:
                base, frac = date_str.split('.')
                if '+' in base:
                    base, tz = base.split('+')
                    frac = frac.rstrip('Z+-')
                    frac = frac[:6].ljust(6, '0')
                    date_str = f"{base}.{frac}+{tz}"
            return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            pass
        
        try:
            return datetime.datetime.fromisoformat(date_str)
        except Exception:
            pass
        
        return None


class PDFMetadataExtractor:
    """Extract metadata from PDF files."""
    
    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF files."""
        metadata = {
            "file_type": "pdf",
            "found": False,
            "timestamps": {},
            "author_info": {},
            "production_info": {},
            "raw_metadata": {}
        }
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read(200000)
            
            PDFMetadataExtractor._parse_info_dict(content, metadata)
            PDFMetadataExtractor._parse_xmp_block(content, metadata)
            PDFMetadataExtractor._parse_trailer(content, metadata)
            
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    @staticmethod
    def _parse_info_dict(content: bytes, metadata: Dict):
        """Parse /Info dictionary."""
        info_patterns = {
            b'/Author ': 'author',
            b'/Creator ': 'creator', 
            b'/Producer ': 'producer',
            b'/Title ': 'title',
            b'/Subject ': 'subject',
            b'/Keywords ': 'keywords'
        }
        
        timestamp_patterns = {
            b'/CreationDate ': 'created',
            b'/ModDate ': 'modified'
        }
        
        for pattern, key in {**info_patterns, **timestamp_patterns}.items():
            idx = content.find(pattern)
            if idx != -1:
                start = idx + len(pattern)
                value = PDFMetadataExtractor._extract_pdf_string(content[start:start+100])
                
                if value:
                    if key in ['created', 'modified']:
                        ts = PDFMetadataExtractor._parse_pdf_date(value)
                        if ts:
                            metadata["timestamps"][key] = TimestampAnalysis(
                                source="pdf_info_dict",
                                timestamp=ts,
                                raw_value=value
                            )
                            metadata["found"] = True
                    else:
                        metadata["author_info"][key] = value
                        metadata["found"] = True
    
    @staticmethod
    def _parse_xmp_block(content: bytes, metadata: Dict):
        """Parse XMP metadata block."""
        xmp_start = content.find(b'<x:xmpmeta')
        if xmp_start == -1:
            xmp_start = content.find(b'<rdf:RDF')
        
        if xmp_start != -1:
            xmp_end = content.find(b'</x:xmpmeta>', xmp_start)
            if xmp_end == -1:
                xmp_end = content.find(b'</rdf:RDF>', xmp_start)
            
            if xmp_end != -1:
                xmp_data = content[xmp_start:xmp_end+100].decode('utf-8', errors='ignore')
                metadata["raw_metadata"]["xmp"] = xmp_data[:1000]
                
                xmp_patterns = {
                    'dc:creator': 'creator',
                    'xmp:CreateDate': 'created',
                    'xmp:ModifyDate': 'modified',
                    'xmp:CreatorTool': 'creator_tool',
                    'pdf:Producer': 'producer',
                    'pdf:Creator': 'creator'
                }
                
                for pattern, key in xmp_patterns.items():
                    if pattern in xmp_data:
                        start = xmp_data.find(f'<{pattern}')
                        if start != -1:
                            tag_end = xmp_data.find('>', start)
                            if tag_end != -1:
                                tag_content = xmp_data[start:tag_end]
                                if '>' in tag_content:
                                    value = tag_content.split('>')[1].split('<')[0].strip()
                                    if value and key not in metadata["author_info"]:
                                        ts = PDFMetadataExtractor._parse_pdf_date(value)
                                        if ts and key in ['created', 'modified']:
                                            if key not in metadata["timestamps"]:
                                                metadata["timestamps"][key] = TimestampAnalysis(
                                                    source="pdf_xmp",
                                                    timestamp=ts,
                                                    raw_value=value
                                                )
                                                metadata["found"] = True
                                        elif value:
                                            metadata["author_info"][key] = value
                                            metadata["found"] = True
    
    @staticmethod
    def _parse_trailer(content: bytes, metadata: Dict):
        """Parse PDF trailer for additional info."""
        trailer_idx = content.find(b'trailer')
        if trailer_idx != -1:
            trailer_data = content[trailer_idx:trailer_idx+500].decode('utf-8', errors='ignore')
            metadata["raw_metadata"]["trailer"] = trailer_data[:300]
    
    @staticmethod
    def _extract_pdf_string(data: bytes) -> Optional[str]:
        """Extract string from PDF content."""
        if not data:
            return None
        
        try:
            end_chars = b'()/<>[] \n\r\t'
            end_idx = 0
            for i, b in enumerate(data):
                if b in end_chars:
                    end_idx = i
                    break
            
            result = data[:end_idx].decode('utf-8', errors='ignore').strip()
            result = result.strip('() ')
            return result if result else None
        except Exception:
            return None
    
    @staticmethod
    def _parse_pdf_date(date_str: str) -> Optional[datetime.datetime]:
        """Parse PDF date format (D:YYYYMMDDHHmmSS)."""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        if date_str.startswith('D:'):
            date_str = date_str[2:]
        
        if len(date_str) >= 14:
            try:
                year = int(date_str[0:4])
                month = int(date_str[4:6]) if len(date_str) >= 6 else 1
                day = int(date_str[6:8]) if len(date_str) >= 8 else 1
                hour = int(date_str[8:10]) if len(date_str) >= 10 else 0
                minute = int(date_str[10:12]) if len(date_str) >= 12 else 0
                second = int(date_str[12:14]) if len(date_str) >= 14 else 0
                
                return datetime.datetime(year, month, day, hour, minute, second)
            except Exception:
                pass
        
        try:
            return datetime.datetime.fromisoformat(date_str.replace('Z', ''))
        except Exception:
            pass
        
        try:
            return datetime.datetime.strptime(date_str[:19], '%Y-%m-%dT%H:%M:%S')
        except Exception:
            pass
        
        return None


class ImageMetadataExtractor:
    """Extract EXIF and image metadata."""
    
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef', '.arw']
    
    EXIF_TAGS = {
        0x0132: 'datetime_original',
        0x0131: 'software', 
        0x010F: 'make',
        0x0110: 'model',
        0x0112: 'orientation',
        0x8769: 'exif_ifd',
        0x8825: 'gps_ifd',
        0x9003: 'datetime_digitized',
        0x9004: 'datetime_modified',
        0xA002: 'pixel_x_dimension',
        0xA003: 'pixel_y_dimension',
    }
    
    GPS_TAGS = {
        0x0001: 'latitude_ref',
        0x0002: 'latitude',
        0x0003: 'longitude_ref', 
        0x0004: 'longitude',
        0x0006: 'altitude'
    }
    
    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        """Extract metadata from image files."""
        metadata = {
            "file_type": "image",
            "found": False,
            "format": None,
            "timestamps": {},
            "device_info": {},
            "gps_info": {},
            "editing_history": [],
            "raw_metadata": {}
        }
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read(500000)
            
            if data[:2] == b'\xFF\xD8':
                metadata["format"] = "JPEG"
                ImageMetadataExtractor._parse_jpeg(data, metadata)
            elif data[:8] == b'\x89PNG\r\n\x1a\n':
                metadata["format"] = "PNG"
                ImageMetadataExtractor._parse_png(data, metadata)
            elif data[:4] == b'II\x2a\x00' or data[:4] == b'MM\x00\x2a':
                metadata["format"] = "TIFF"
                ImageMetadataExtractor._parse_tiff(data, metadata)
            elif data[:4] == b'HEIC' or data[:4] == b'heic':
                metadata["format"] = "HEIC"
                ImageMetadataExtractor._parse_heic(data, metadata)
                
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    @staticmethod
    def _parse_jpeg(data: bytes, metadata: Dict):
        """Parse JPEG EXIF data."""
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
                    ImageMetadataExtractor._parse_exif_segment(exif_data[6:], metadata)
                break
            
            elif marker == 0xDB:
                break
            else:
                length = struct.unpack('>H', data[i+2:i+4])[0]
                i += 2 + length
        
        ImageMetadataExtractor._parse_jfif(data, metadata)
    
    @staticmethod
    def _parse_exif_segment(tiff_data: bytes, metadata: Dict):
        """Parse EXIF data from TIFF format."""
        if len(tiff_data) < 8:
            return
        
        little_endian = tiff_data[0:2] == b'II'
        
        try:
            ifd_offset = struct.unpack(little_endian and '<I' or '>I', tiff_data[4:8])[0]
        except:
            return
        
        ImageMetadataExtractor._parse_ifd(tiff_data, ifd_offset, little_endian, metadata)
        
        for tag_id, tag_name in [(0x8769, 'exif_ifd'), (0x8825, 'gps_ifd')]:
            exif_offset = ImageMetadataExtractor._find_tag(tiff_data, ifd_offset, tag_id, little_endian)
            if exif_offset > 0:
                if tag_name == 'gps_ifd':
                    ImageMetadataExtractor._parse_gps_ifd(tiff_data, exif_offset, little_endian, metadata)
    
    @staticmethod
    def _parse_ifd(data: bytes, offset: int, le: bool, metadata: Dict, max_tags: int = 50):
        """Parse IFD (Image File Directory)."""
        if offset >= len(data) - 2:
            return
        
        try:
            num_tags = struct.unpack(le and '<H' or '>H', data[offset:offset+2])[0]
        except:
            return
        
        pos = offset + 2
        
        for _ in range(min(num_tags, max_tags)):
            if pos + 12 > len(data):
                break
            
            try:
                tag = struct.unpack(le and '<H' or '>H', data[pos:pos+2])[0]
                tag_type = struct.unpack(le and '<H' or '>H', data[pos+2:pos+4])[0]
                count = struct.unpack(le and '<I' or '>I', data[pos+4:pos+8])[0]
                value_offset = struct.unpack(le and '<I' or '>I', data[pos+8:pos+12])[0]
            except:
                break
            
            if tag in ImageMetadataExtractor.EXIF_TAGS:
                tag_name = ImageMetadataExtractor.EXIF_TAGS[tag]
                
                if tag in [0x0132, 0x9003, 0x9004]:
                    if value_offset + 20 < len(data):
                        val = data[value_offset:value_offset+20]
                        date_str = val.split(b'\x00')[0].decode('ascii', errors='ignore')
                        if len(date_str) >= 19:
                            try:
                                dt = datetime.datetime.strptime(date_str[:19], '%Y:%m:%d %H:%M:%S')
                                metadata["timestamps"][tag_name] = TimestampAnalysis(
                                    source="exif",
                                    timestamp=dt,
                                    raw_value=date_str
                                )
                            except:
                                pass
                
                elif tag == 0x0131:
                    if value_offset + 40 < len(data):
                        software = data[value_offset:value_offset+40].split(b'\x00')[0].decode('utf-8', errors='ignore')
                        if software:
                            metadata["device_info"]["software"] = software
                
                elif tag == 0x010F:
                    if value_offset + 40 < len(data):
                        make = data[value_offset:value_offset+40].split(b'\x00')[0].decode('utf-8', errors='ignore')
                        if make:
                            metadata["device_info"]["make"] = make
                
                elif tag == 0x0110:
                    if value_offset + 40 < len(data):
                        model = data[value_offset:value_offset+40].split(b'\x00')[0].decode('utf-8', errors='ignore')
                        if model:
                            metadata["device_info"]["model"] = model
                
                elif tag == 0x0112:
                    metadata["device_info"]["orientation"] = count
            
            pos += 12
    
    @staticmethod
    def _parse_gps_ifd(data: bytes, offset: int, le: bool, metadata: Dict):
        """Parse GPS IFD."""
        if offset >= len(data) - 2:
            return
        
        try:
            num_tags = struct.unpack(le and '<H' or '>H', data[offset:offset+2])[0]
        except:
            return
        
        pos = offset + 2
        
        for _ in range(min(num_tags, 20)):
            if pos + 12 > len(data):
                break
            
            try:
                tag = struct.unpack(le and '<H' or '>H', data[pos:pos+2])[0]
                value_offset = struct.unpack(le and '<I' or '>I', data[pos+8:pos+12])[0]
            except:
                break
            
            if tag in ImageMetadataExtractor.GPS_TAGS:
                tag_name = ImageMetadataExtractor.GPS_TAGS[tag]
                if value_offset + 30 < len(data):
                    val = data[value_offset:value_offset+30].split(b'\x00')[0].decode('utf-8', errors='ignore')
                    if val:
                        metadata["gps_info"][tag_name] = val
            
            pos += 12
    
    @staticmethod
    def _find_tag(data: bytes, ifd_offset: int, tag_id: int, le: bool) -> int:
        """Find tag offset in IFD."""
        if ifd_offset >= len(data) - 2:
            return 0
        
        try:
            num_tags = struct.unpack(le and '<H' or '>H', data[ifd_offset:ifd_offset+2])[0]
        except:
            return 0
        
        pos = ifd_offset + 2
        
        for _ in range(min(num_tags, 50)):
            if pos + 12 > len(data):
                break
            
            try:
                tag = struct.unpack(le and '<H' or '>H', data[pos:pos+2])[0]
                value_offset = struct.unpack(le and '<I' or '>I', data[pos+8:pos+12])[0]
            except:
                break
            
            if tag == tag_id:
                return value_offset
            
            pos += 12
        
        return 0
    
    @staticmethod
    def _parse_jfif(data: bytes, metadata: Dict):
        """Parse JFIF segment for additional info."""
        jfif_idx = data.find(b'JFIF')
        if jfif_idx > 2 and data[jfif_idx-3:jfif_idx-2] == b'\xFF':
            metadata["device_info"]["jfif_present"] = True
    
    @staticmethod
    def _parse_png(data: bytes, metadata: Dict):
        """Parse PNG metadata chunks."""
        i = 8
        while i < len(data) - 12:
            try:
                chunk_len = struct.unpack('>I', data[i:i+4])[0]
                chunk_type = data[i+4:i+8]
            except:
                break
            
            if chunk_type in [b'tEXt', b'iTXt', b'zTXt']:
                metadata["found"] = True
                chunk_data = data[i+8:i+8+chunk_len]
                
                if chunk_type == b'tEXt':
                    null_pos = chunk_data.find(b'\x00')
                    if null_pos > 0:
                        key = chunk_data[:null_pos].decode('utf-8', errors='ignore')
                        value = chunk_data[null_pos+1:].decode('utf-8', errors='ignore')
                        
                        if key == 'DateTime':
                            try:
                                dt = datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                                metadata["timestamps"]["datetime_original"] = TimestampAnalysis(
                                    source="png_text_chunk",
                                    timestamp=dt,
                                    raw_value=value
                                )
                            except:
                                pass
                        metadata["device_info"][key] = value
            
            if chunk_type == b'IEND':
                break
            
            i += 12 + chunk_len
    
    @staticmethod
    def _parse_tiff(data: bytes, metadata: Dict):
        """Parse TIFF metadata."""
        if data[:4] == b'II\x2a\x00':
            le = True
        elif data[:4] == b'MM\x00\x2a':
            le = False
        else:
            return
        
        try:
            ifd_offset = struct.unpack(le and '<I' or '>I', data[4:8])[0]
            metadata["found"] = True
            ImageMetadataExtractor._parse_ifd(data, ifd_offset, le, metadata)
        except:
            pass
    
    @staticmethod
    def _parse_heic(data: bytes, metadata: Dict):
        """Parse HEIC/HEIF metadata (basic)."""
        metadata["device_info"]["note"] = "HEIC format - limited metadata extraction without specialized library"
        metadata["found"] = True


class PEMetadataExtractor:
    """Extract timestamps from PE executables."""
    
    PE_EXTENSIONS = ['.exe', '.dll', '.sys', '.ocx', '.scr']
    
    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        """Extract metadata from PE executables."""
        metadata = {
            "file_type": "pe",
            "found": False,
            "format": None,
            "timestamps": {},
            "version_info": {},
            "debug_info": {},
            "resources": {},
            "raw_headers": {}
        }
        
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
            
            metadata["format"] = "PE"
            PEMetadataExtractor._parse_file_header(f, metadata)
            PEMetadataExtractor._parse_optional_header(f, metadata)
            PEMetadataExtractor._parse_section_headers(f, metadata)
            
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    @staticmethod
    def _parse_file_header(f, metadata: Dict):
        """Parse PE file header."""
        file_header = f.read(20)
        
        if len(file_header) < 20:
            return
        
        machine = struct.unpack('<H', file_header[0:2])[0]
        machine_types = {
            0x014c: 'x86',
            0x8664: 'x64',
            0x01c0: 'ARM',
            0xaa64: 'ARM64'
        }
        metadata["version_info"]["machine"] = machine_types.get(machine, f"0x{machine:04x}")
        
        time_date_stamp = struct.unpack('<I', file_header[4:8])[0]
        
        if time_date_stamp > 0:
            try:
                compile_dt = datetime.datetime.fromtimestamp(time_date_stamp)
                metadata["timestamps"]["compile"] = TimestampAnalysis(
                    source="pe_file_header",
                    timestamp=compile_dt,
                    raw_value=time_date_stamp
                )
                metadata["found"] = True
            except:
                pass
        
        metadata["version_info"]["timestamp_raw"] = time_date_stamp
        
        characteristics = struct.unpack('<H', file_header[12:14])[0]
        metadata["version_info"]["characteristics"] = hex(characteristics)
        
        optional_header_size = struct.unpack('<H', file_header[16:18])[0]
        metadata["version_info"]["optional_header_size"] = optional_header_size
    
    @staticmethod
    def _parse_optional_header(f, metadata: Dict):
        """Parse PE optional header."""
        try:
            optional_header_start = f.tell()
            optional_header = f.read(128)
            
            if len(optional_header) < 2:
                return
            
            magic = struct.unpack('<H', optional_header[0:2])[0]
            
            if magic == 0x10b:
                metadata["format"] = "PE32"
            elif magic == 0x20b:
                metadata["format"] = "PE32+"
            else:
                return
            
            linker_version = f"{optional_header[2]}.{optional_header[3]}"
            metadata["version_info"]["linker_version"] = linker_version
            
            code_size = struct.unpack('<I', optional_header[4:8])[0]
            metadata["resources"]["code_size"] = code_size
            
            image_base = struct.unpack('<I' if magic == 0x10b else '<Q', optional_header[24:28] if magic == 0x10b else optional_header[24:32])[0]
            metadata["version_info"]["image_base"] = hex(image_base)
            
            subsystem = struct.unpack('<H', optional_header[36:38])[0]
            subsystems = {1: 'Console', 2: 'GUI', 3: 'OS/2', 5: 'POSIX'}
            metadata["version_info"]["subsystem"] = subsystems.get(subsystem, f"0x{subsystem:04x}")
            
            if magic == 0x10b and len(optional_header) >= 92:
                data_dir_offset = 96
            elif magic == 0x20b and len(optional_header) >= 112:
                data_dir_offset = 112
            else:
                return
            
            if len(optional_header) >= data_dir_offset + 32:
                resource_rva = struct.unpack('<I', optional_header[data_dir_offset+8:data_dir_offset+12])[0]
                resource_size = struct.unpack('<I', optional_header[data_dir_offset+12:data_dir_offset+16])[0]
                
                if resource_rva > 0:
                    metadata["resources"]["resource_rva"] = hex(resource_rva)
                    metadata["resources"]["resource_size"] = resource_size
        
        except Exception:
            pass
    
    @staticmethod
    def _parse_section_headers(f, metadata: Dict):
        """Parse PE section headers for additional timestamps."""
        sections = []
        
        try:
            f.seek(24, 1)
            num_sections = struct.unpack('<H', f.read(2))[0]
            f.seek(16, 1)
            
            for i in range(min(num_sections, 10)):
                section = f.read(40)
                
                if len(section) < 40:
                    break
                
                name = section[:8].rstrip(b'\x00').decode('ascii', errors='ignore')
                virtual_size = struct.unpack('<I', section[8:12])[0]
                virtual_addr = struct.unpack('<I', section[12:16])[0]
                raw_size = struct.unpack('<I', section[16:20])[0]
                raw_offset = struct.unpack('<I', section[20:24])[0]
                characteristics = struct.unpack('<I', section[36:40])[0]
                
                sections.append({
                    "name": name,
                    "virtual_size": virtual_size,
                    "virtual_address": hex(virtual_addr),
                    "raw_size": raw_size,
                    "raw_offset": hex(raw_offset),
                    "characteristics": hex(characteristics)
                })
            
            metadata["resources"]["sections"] = sections
            
        except Exception:
            pass


class VideoAudioMetadataExtractor:
    """Extract metadata from video and audio files."""
    
    VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv', '.flv', '.m4v']
    AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff']
    
    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        """Extract metadata from video/audio files."""
        metadata = {
            "file_type": "media",
            "found": False,
            "format": None,
            "timestamps": {},
            "device_info": {},
            "encoding_info": {},
            "raw_metadata": {}
        }
        
        ext = Path(file_path).suffix.lower()
        
        if ext in VideoAudioMetadataExtractor.VIDEO_EXTENSIONS:
            metadata["media_type"] = "video"
            if ext in ['.mp4', '.mov', '.m4v']:
                VideoAudioMetadataExtractor._parse_mp4_mov(file_path, metadata)
            elif ext == '.mkv':
                VideoAudioMetadataExtractor._parse_mkv(file_path, metadata)
            elif ext == '.avi':
                VideoAudioMetadataExtractor._parse_avi(file_path, metadata)
                
        elif ext in VideoAudioMetadataExtractor.AUDIO_EXTENSIONS:
            metadata["media_type"] = "audio"
            if ext == '.mp3':
                VideoAudioMetadataExtractor._parse_mp3(file_path, metadata)
            elif ext == '.wav':
                VideoAudioMetadataExtractor._parse_wav(file_path, metadata)
            elif ext == '.flac':
                VideoAudioMetadataExtractor._parse_flac(file_path, metadata)
        
        return metadata
    
    @staticmethod
    def _parse_mp4_mov(file_path: str, metadata: Dict):
        """Parse MP4/MOV atoms."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read(100000)
            
            VideoAudioMetadataExtractor._find_moov_atoms(data, metadata)
            
        except Exception:
            pass
    
    @staticmethod
    def _find_moov_atoms(data: bytes, metadata: Dict):
        """Find and parse moov atom containing metadata."""
        pos = 0
        while pos < len(data) - 8:
            try:
                size = struct.unpack('>I', data[pos:pos+4])[0]
                atom_type = data[pos+4:pos+8]
            except:
                break
            
            if size < 8 or size > len(data) - pos:
                pos += 1
                continue
            
            if atom_type == b'moov':
                metadata["found"] = True
                VideoAudioMetadataExtractor._parse_moov_atom(data[pos+8:pos+size], metadata)
                break
            elif atom_type == b'ftyp':
                ftype_data = data[pos+8:pos+min(size, 20)]
                if b'qt' in ftype_data[:4]:
                    metadata["format"] = "QuickTime"
                elif b'mp4' in ftype_data:
                    metadata["format"] = "MP4"
            
            pos += size if size > 0 else 1
    
    @staticmethod
    def _parse_moov_atom(data: bytes, metadata: Dict):
        """Parse moov atom for metadata."""
        pos = 0
        while pos < len(data) - 8:
            try:
                size = struct.unpack('>I', data[pos:pos+4])[0]
                atom_type = data[pos+4:pos+8]
            except:
                break
            
            if size < 8 or size > len(data) - pos:
                pos += 1
                continue
            
            if atom_type == b'udta':
                VideoAudioMetadataExtractor._parse_udta_atom(data[pos+8:pos+size], metadata)
            elif atom_type == b'mvhd':
                if size >= 100:
                    version = data[pos+8]
                    if version == 0:
                        creation = struct.unpack('>I', data[pos+12:pos+16])[0]
                        modification = struct.unpack('>I', data[pos+16:pos+20])[0]
                        
                        if creation > 0:
                            ts = VideoAudioMetadataExtractor._parse_mp4_timestamp(creation)
                            metadata["timestamps"]["created"] = TimestampAnalysis(
                                source="mp4_mvhd",
                                timestamp=ts,
                                raw_value=creation
                            )
                        if modification > 0:
                            ts = VideoAudioMetadataExtractor._parse_mp4_timestamp(modification)
                            metadata["timestamps"]["modified"] = TimestampAnalysis(
                                source="mp4_mvhd",
                                timestamp=ts,
                                raw_value=modification
                            )
            
            pos += size if size > 0 else 1
    
    @staticmethod
    def _parse_udta_atom(data: bytes, metadata: Dict):
        """Parse udta atom for user metadata."""
        pos = 0
        while pos < len(data) - 8:
            try:
                size = struct.unpack('>I', data[pos:pos+4])[0]
                atom_type = data[pos+4:pos+8]
            except:
                break
            
            if size < 8 or size > len(data) - pos:
                pos += 1
                continue
            
            if atom_type == b'meta':
                VideoAudioMetadataExtractor._parse_meta_atom(data[pos+8:pos+size], metadata)
            elif atom_type == b'\xa9cpy' or atom_type == b'cprt':
                metadata["found"] = True
            
            pos += size if size > 0 else 1
    
    @staticmethod
    def _parse_meta_atom(data: bytes, metadata: Dict):
        """Parse meta atom."""
        if len(data) < 4:
            return
        
        if data[:4] == b'hdlr':
            return
        
        content = data[4:] if len(data) > 4 else data
        pos = 0
        
        while pos < len(content) - 8:
            try:
                size = struct.unpack('>I', content[pos:pos+4])[0]
                atom_type = content[pos+4:pos+8]
            except:
                break
            
            if size < 8 or size > len(content) - pos:
                pos += 1
                continue
            
            if atom_type == b'\xa9day' or atom_type == b'day ':
                date_data = content[pos+8:pos+min(size, 20)]
                try:
                    date_str = date_data.decode('utf-8', errors='ignore').strip('\x00 ')
                    if len(date_str) >= 10:
                        try:
                            dt = datetime.datetime.strptime(date_str[:10], '%Y-%m-%d')
                            metadata["timestamps"]["created"] = TimestampAnalysis(
                                source="mp4_meta",
                                timestamp=dt,
                                raw_value=date_str
                            )
                            metadata["found"] = True
                        except:
                            pass
                except:
                    pass
            
            pos += size if size > 0 else 1
    
    @staticmethod
    def _parse_mp4_timestamp(timestamp: int) -> Optional[datetime.datetime]:
        """Convert MP4 timestamp (seconds since 1904)."""
        try:
            return datetime.datetime(1904, 1, 1) + datetime.timedelta(seconds=timestamp)
        except:
            return None
    
    @staticmethod
    def _parse_mkv(file_path: str, metadata: Dict):
        """Parse MKV/WebM container."""
        metadata["format"] = "MKV"
        metadata["device_info"]["note"] = "MKV metadata parsing requires full EBML parsing"
    
    @staticmethod
    def _parse_avi(file_path: str, metadata: Dict):
        """Parse AVI container."""
        try:
            with open(file_path, 'rb') as f:
                f.seek(0)
                header = f.read(48)
            
            if header[:4] == b'RIFF' and header[8:12] == b'AVI ':
                metadata["format"] = "AVI"
                metadata["found"] = True
                
        except:
            pass
    
    @staticmethod
    def _parse_mp3(file_path: str, metadata: Dict):
        """Parse MP3 ID3 tags."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read(50000)
            
            if data[:3] == b'ID3':
                metadata["found"] = True
                VideoAudioMetadataExtractor._parse_id3v2(data, metadata)
            elif data[:2] == b'\xFF\xFB':
                metadata["found"] = True
                metadata["format"] = "MP3 (no ID3)"
                
        except:
            pass
    
    @staticmethod
    def _parse_id3v2(data: bytes, metadata: Dict):
        """Parse ID3v2 tags."""
        if len(data) < 10:
            return
        
        version = data[3]
        flags = data[5]
        size = VideoAudioMetadataExtractor._synchsafe_int(data[6:10])
        
        metadata["format"] = f"ID3v2.{version}"
        pos = 10
        
        frame_ids = {
            'TPE1': 'artist',
            'TPE2': 'album_artist',
            'TALB': 'album',
            'TIT2': 'title',
            'TYER': 'year',
            'TRCK': 'track',
            'TCON': 'genre',
            'COMM': 'comment',
            'TDAT': 'date',
            'TIME': 'time'
        }
        
        while pos < len(data) - 10 and pos < size + 10:
            frame_id = data[pos:pos+4].decode('ascii', errors='ignore')
            
            if frame_id not in frame_ids or frame_id[0] not in 'TCOMM':
                break
            
            frame_size = struct.unpack('>I', b'\x00' + data[pos+5:pos+8])[0] if version >= 3 else VideoAudioMetadataExtractor._synchsafe_int(data[pos+4:pos+8])
            
            if frame_size < 1 or frame_size > 10000:
                break
            
            frame_data = data[pos+10:pos+10+frame_size]
            
            if frame_id in frame_ids:
                try:
                    value = frame_data.decode('utf-8', errors='ignore').strip('\x00 ')
                    if value:
                        if frame_id == 'TYER' or frame_id == 'TDAT':
                            if frame_id == 'TYER':
                                metadata["timestamps"]["year"] = TimestampAnalysis(
                                    source="id3v2",
                                    timestamp=None,
                                    raw_value=value
                                )
                            metadata["encoding_info"][frame_ids[frame_id]] = value
                        else:
                            metadata["encoding_info"][frame_ids[frame_id]] = value
                        metadata["found"] = True
                except:
                    pass
            
            pos += 10 + frame_size
    
    @staticmethod
    def _synchsafe_int(data: bytes) -> int:
        """Parse synchsafe integer."""
        result = 0
        for b in data:
            result = (result << 7) | (b & 0x7F)
        return result
    
    @staticmethod
    def _parse_wav(file_path: str, metadata: Dict):
        """Parse WAV file metadata."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(44)
            
            if header[:4] == b'RIFF' and header[8:12] == b'WAVE':
                metadata["format"] = "WAV"
                metadata["found"] = True
                
                info_chunk = header[12:]
                pos = 0
                while pos < len(info_chunk) - 8:
                    chunk_id = info_chunk[pos:pos+4]
                    chunk_size = struct.unpack('<I', info_chunk[pos+4:pos+8])[0]
                    
                    if chunk_id == b'LIST' and info_chunk[pos+8:pos+12] == b'INFO':
                        info_data = info_chunk[pos+12:pos+12+chunk_size-4]
                        VideoAudioMetadataExtractor._parse_riff_info(info_data, metadata)
                        break
                    
                    pos += 8 + chunk_size
                    
        except:
            pass
    
    @staticmethod
    def _parse_riff_info(data: bytes, metadata: Dict):
        """Parse RIFF INFO chunk."""
        info_tags = {
            b'INAM': 'title',
            b'IART': 'artist',
            b'ICRD': 'date',
            b'ICMT': 'comment',
            b'IGNR': 'genre'
        }
        
        pos = 0
        while pos < len(data) - 8:
            tag = data[pos:pos+4]
            size = struct.unpack('<I', data[pos+4:pos+8])[0]
            
            if tag in info_tags and size > 0:
                value = data[pos+8:pos+8+size].decode('utf-8', errors='ignore').strip('\x00 ')
                if value:
                    metadata["encoding_info"][info_tags[tag]] = value
                    metadata["found"] = True
            
            pos += 8 + size
    
    @staticmethod
    def _parse_flac(file_path: str, metadata: Dict):
        """Parse FLAC metadata."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
            
            if header[:4] == b'fLaC':
                metadata["format"] = "FLAC"
                metadata["found"] = True
                
        except:
            pass


class ArchiveMetadataExtractor:
    """Extract metadata from archive files."""
    
    ARCHIVE_EXTENSIONS = ['.zip', '.jar', '.odt', '.ods', '.odp', '.docx', '.xlsx', '.pptx']
    
    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        """Extract metadata from archive files."""
        metadata = {
            "file_type": "archive",
            "found": False,
            "format": None,
            "timestamps": {},
            "entries": [],
            "summary": {}
        }
        
        ext = Path(file_path).suffix.lower()
        
        if ext == '.zip' or ext == '.jar':
            metadata["format"] = "ZIP"
            ArchiveMetadataExtractor._parse_zip(file_path, metadata)
        elif ext in ['.rar', '.7z']:
            metadata["format"] = ext[1:].upper()
            metadata["device_info"]["note"] = f"{metadata['format']} requires specialized library for full extraction"
        
        return metadata
    
    @staticmethod
    def _parse_zip(file_path: str, metadata: Dict):
        """Parse ZIP archive."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                info_list = zf.infolist()
                
                if info_list:
                    metadata["found"] = True
                    metadata["summary"]["total_files"] = len(info_list)
                    
                    timestamps = []
                    oldest = None
                    newest = None
                    
                    for zinfo in info_list[:50]:
                        if zinfo.date_time and zinfo.date_time[0] > 1970:
                            try:
                                dt = datetime.datetime(*zinfo.date_time)
                                timestamps.append(dt)
                                
                                if oldest is None or dt < oldest:
                                    oldest = dt
                                if newest is None or dt > newest:
                                    newest = dt
                                    
                            except:
                                pass
                    
                    if timestamps:
                        metadata["timestamps"]["oldest_entry"] = TimestampAnalysis(
                            source="zip_central_directory",
                            timestamp=oldest,
                            raw_value=oldest.isoformat()
                        )
                        metadata["timestamps"]["newest_entry"] = TimestampAnalysis(
                            source="zip_central_directory",
                            timestamp=newest,
                            raw_value=newest.isoformat()
                        )
                    
                    archive_comment = zf.comment
                    if archive_comment:
                        metadata["entries"]["comment"] = archive_comment.decode('utf-8', errors='ignore')
                    
        except Exception as e:
            metadata["error"] = str(e)


class LNKMetadataExtractor:
    """Extract metadata from Windows Shortcut files."""
    
    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        """Extract metadata from .lnk files."""
        metadata = {
            "file_type": "lnk",
            "found": False,
            "format": "Windows Shortcut",
            "timestamps": {},
            "target_info": {},
            "tracking_info": {}
        }
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read(1000)
            
            if len(data) < 76:
                return metadata
            
            header_size = struct.unpack('<I', data[4:8])[0]
            if header_size < 76:
                return metadata
            
            flags = struct.unpack('<I', data[20:24])[0]
            
            has_target_id_list = (flags & 0x01) != 0
            has_link_info = (flags & 0x02) != 0
            has_name = (flags & 0x04) != 0
            has_relative_path = (flags & 0x08) != 0
            has_working_dir = (flags & 0x10) != 0
            has_arguments = (flags & 0x20) != 0
            has_icon_location = (flags & 0x40) != 0
            has_unicode_path = (flags & 0x80) != 0
            has_tracker = (flags & 0x200) != 0
            
            offset = 0x4C
            
            if has_target_id_list:
                id_list_size = struct.unpack('<H', data[offset:offset+2])[0]
                offset += 2 + id_list_size
            
            if has_link_info:
                link_info_size = struct.unpack('<I', data[offset:offset+4])[0]
                link_info_start = offset
                
                volume_id_offset = struct.unpack('<I', data[offset+16:offset+20])[0]
                local_base_path_offset = struct.unpack('<I', data[offset+20:offset+24])[0]
                
                if volume_id_offset > 0 and link_info_start + volume_id_offset < len(data):
                    volume_id_start = link_info_start + volume_id_offset
                    volume_label = data[volume_id_start:volume_id_start+30].rstrip(b'\x00').decode('utf-8', errors='ignore')
                    if volume_label:
                        metadata["tracking_info"]["volume_label"] = volume_label
                
                if local_base_path_offset > 0 and link_info_start + local_base_path_offset < len(data):
                    target_path = data[link_info_start + local_base_path_offset:].split(b'\x00')[0].decode('utf-8', errors='ignore')
                    if target_path:
                        metadata["target_info"]["path"] = target_path
                        metadata["found"] = True
                
                offset = link_info_start + link_info_size
            
            if has_relative_path:
                path_len = struct.unpack('<H', data[offset:offset+2])[0]
                if path_len > 0 and path_len < 500:
                    path = data[offset+2:offset+2+path_len*2 if has_unicode_path else path_len].decode('utf-16-le' if has_unicode_path else 'ascii', errors='ignore')
                    metadata["target_info"]["relative_path"] = path
                    metadata["found"] = True
                offset += 2 + path_len * (2 if has_unicode_path else 1)
            
            creation_time = struct.unpack('<Q', data[28:36])[0]
            access_time = struct.unpack('<Q', data[36:44])[0]
            write_time = struct.unpack('<Q', data[44:52])[0]
            
            if creation_time > 0:
                ts = LNKMetadataExtractor._filetime_to_datetime(creation_time)
                if ts:
                    metadata["timestamps"]["created"] = TimestampAnalysis(
                        source="lnk_header",
                        timestamp=ts,
                        raw_value=creation_time
                    )
                    metadata["found"] = True
            
            if access_time > 0:
                ts = LNKMetadataExtractor._filetime_to_datetime(access_time)
                if ts:
                    metadata["timestamps"]["accessed"] = TimestampAnalysis(
                        source="lnk_header",
                        timestamp=ts,
                        raw_value=access_time
                    )
            
            if write_time > 0:
                ts = LNKMetadataExtractor._filetime_to_datetime(write_time)
                if ts:
                    metadata["timestamps"]["modified"] = TimestampAnalysis(
                        source="lnk_header",
                        timestamp=ts,
                        raw_value=write_time
                    )
            
            if has_tracker:
                offset = data.find(b'MachineID', 0, 500)
                if offset > 0 and offset + 50 < len(data):
                    machine = data[offset+10:offset+50].rstrip(b'\x00').decode('ascii', errors='ignore')
                    if machine:
                        metadata["tracking_info"]["machine_id"] = machine
                        metadata["found"] = True
                
                droid_offset = data.find(b'Droid', 0, 500)
                if droid_offset > 0 and droid_offset + 40 < len(data):
                    droid = data[droid_offset+5:droid_offset+40]
                    metadata["tracking_info"]["droid"] = droid.hex()
        
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    @staticmethod
    def _filetime_to_datetime(filetime: int) -> Optional[datetime.datetime]:
        if filetime == 0:
            return None
        try:
            return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=filetime // 10)
        except:
            return None


class TimestampComparator:
    """Compare filesystem timestamps with metadata timestamps."""
    
    THRESHOLD_SECONDS = 60
    
    def __init__(self, threshold_seconds: int = 60):
        self.threshold_seconds = threshold_seconds
    
    def compare(self, fs_timestamps: Dict[str, TimestampAnalysis], 
                metadata: Dict[str, Any]) -> List[TimestompDetection]:
        """Compare filesystem and metadata timestamps."""
        detections = []
        
        if not metadata.get("found"):
            return detections
        
        meta_timestamps = metadata.get("timestamps", {})
        
        for meta_key, meta_ts in meta_timestamps.items():
            if not meta_ts.timestamp:
                continue
            
            for fs_key, fs_ts in fs_timestamps.items():
                if not fs_ts.timestamp:
                    continue
                
                diff = abs((meta_ts.timestamp - fs_ts.timestamp).total_seconds())
                
                if diff > self.threshold_seconds:
                    severity = "high" if diff > 86400 else "medium"
                    
                    detection = TimestompDetection(
                        file_path="",
                        file_type=metadata.get("file_type", "unknown"),
                        inconsistency_type=f"{meta_key}_mismatch",
                        severity=severity,
                        description=f"Metadata {meta_key} differs from filesystem {fs_key} by {self._format_diff(diff)}",
                        filesystem_timestamps={fs_key: fs_ts.iso_string},
                        metadata_timestamps={meta_key: meta_ts.iso_string},
                        time_difference_seconds=diff,
                        time_difference_display=self._format_diff(diff)
                    )
                    detections.append(detection)
        
        if metadata.get("type") == "pe":
            self._check_pe_timestamps(fs_timestamps, metadata, detections)
        
        return detections
    
    def _check_pe_timestamps(self, fs_timestamps: Dict, metadata: Dict, detections: List):
        """Check PE-specific timestamp anomalies."""
        compile_ts = metadata.get("timestamps", {}).get("compile")
        
        if not compile_ts or not compile_ts.timestamp:
            return
        
        for fs_key, fs_ts in fs_timestamps.items():
            if not fs_ts.timestamp:
                continue
            
            diff = (fs_ts.timestamp - compile_ts.timestamp).total_seconds()
            
            if diff < -86400:
                severity = "high"
                detection = TimestompDetection(
                    file_path="",
                    file_type="pe",
                    inconsistency_type="compiled_after_created",
                    severity=severity,
                    description=f"PE compiled {self._format_diff(abs(diff))} AFTER file was created",
                    filesystem_timestamps={fs_key: fs_ts.iso_string},
                    metadata_timestamps={"compile": compile_ts.iso_string},
                    time_difference_seconds=abs(diff),
                    time_difference_display=self._format_diff(abs(diff))
                )
                detections.append(detection)
    
    def _format_diff(self, seconds: float) -> str:
        """Format time difference."""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            return f"{int(seconds/60)} minutes"
        elif seconds < 86400:
            return f"{int(seconds/3600)} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"


class UniversalMetadataAnalyzer:
    """Main analyzer class."""
    
    def __init__(self, threshold_seconds: int = 60):
        self.threshold_seconds = threshold_seconds
        self.comparator = TimestampComparator(threshold_seconds)
        
        self.extractors = {
            'office': OfficeMetadataExtractor(),
            'pdf': PDFMetadataExtractor(),
            'image': ImageMetadataExtractor(),
            'pe': PEMetadataExtractor(),
            'media': VideoAudioMetadataExtractor(),
            'archive': ArchiveMetadataExtractor(),
            'lnk': LNKMetadataExtractor()
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for metadata and timestamp inconsistencies."""
        result = {
            "file_path": file_path,
            "file_name": Path(file_path).name,
            "file_extension": Path(file_path).suffix.lower(),
            "analyzed_at": datetime.datetime.now().isoformat(),
            "filesystem_timestamps": {},
            "metadata": {},
            "inconsistencies": [],
            "analysis_summary": {}
        }
        
        fs_timestamps = FilesystemTimestampExtractor.get_stat_timestamps(file_path)
        for key, ts in fs_timestamps.items():
            if ts.timestamp:
                result["filesystem_timestamps"][key] = ts.iso_string
        
        try:
            result["ntfs_timestamps"] = {}
            ntfs_ts = FilesystemTimestampExtractor.get_ntfs_timestamps(file_path)
            for key, ts in ntfs_ts.items():
                if ts.timestamp:
                    result["ntfs_timestamps"][key] = ts.iso_string
        except:
            pass
        
        ext = Path(file_path).suffix.lower()
        
        if ext in OfficeMetadataExtractor.OFFICE_EXTENSIONS:
            result["metadata"] = OfficeMetadataExtractor.extract(file_path)
        elif ext == '.pdf':
            result["metadata"] = PDFMetadataExtractor.extract(file_path)
        elif ext in ImageMetadataExtractor.IMAGE_EXTENSIONS:
            result["metadata"] = ImageMetadataExtractor.extract(file_path)
        elif ext in PEMetadataExtractor.PE_EXTENSIONS:
            result["metadata"] = PEMetadataExtractor.extract(file_path)
        elif ext in VideoAudioMetadataExtractor.VIDEO_EXTENSIONS or ext in VideoAudioMetadataExtractor.AUDIO_EXTENSIONS:
            result["metadata"] = VideoAudioMetadataExtractor.extract(file_path)
        elif ext in ArchiveMetadataExtractor.ARCHIVE_EXTENSIONS:
            result["metadata"] = ArchiveMetadataExtractor.extract(file_path)
        elif ext == '.lnk':
            result["metadata"] = LNKMetadataExtractor.extract(file_path)
        else:
            result["metadata"] = {"file_type": "unsupported", "found": False}
        
        detections = self.comparator.compare(fs_timestamps, result["metadata"])
        
        for detection in detections:
            detection.file_path = file_path
        
        result["inconsistencies"] = [
            {
                "type": d.inconsistency_type,
                "severity": d.severity,
                "description": d.description,
                "time_difference": d.time_difference_display,
                "filesystem": d.filesystem_timestamps,
                "metadata": d.metadata_timestamps
            }
            for d in detections
        ]
        
        high_count = sum(1 for d in detections if d.severity == "high")
        medium_count = sum(1 for d in detections if d.severity == "medium")
        
        result["analysis_summary"] = {
            "metadata_found": result["metadata"].get("found", False),
            "timestamp_inconsistencies": len(detections),
            "high_severity": high_count,
            "medium_severity": medium_count,
            "has_timestomping": high_count > 0 or medium_count > 0
        }
        
        return result
    
    def analyze_directory(self, directory: str, max_files: int = 100, 
                          extensions: List[str] = None) -> Dict[str, Any]:
        """Analyze all files in a directory."""
        results = {
            "directory": directory,
            "analyzed_at": datetime.datetime.now().isoformat(),
            "files_analyzed": 0,
            "files_with_metadata": 0,
            "files_with_inconsistencies": 0,
            "total_inconsistencies": 0,
            "file_results": [],
            "summary": {}
        }
        
        try:
            path = Path(directory)
            all_files = [f for f in path.rglob('*') if f.is_file()]
            
            if extensions:
                all_files = [f for f in all_files if f.suffix.lower() in extensions]
            
            all_files = all_files[:max_files]
            
            for file_path in all_files:
                try:
                    result = self.analyze_file(str(file_path))
                    results["files_analyzed"] += 1
                    
                    if result["metadata"].get("found"):
                        results["files_with_metadata"] += 1
                    
                    if result["inconsistencies"]:
                        results["files_with_inconsistencies"] += 1
                        results["total_inconsistencies"] += len(result["inconsistencies"])
                        results["file_results"].append(result)
                    
                except Exception as e:
                    pass
                    
        except Exception as e:
            results["error"] = str(e)
        
        high_total = sum(r["analysis_summary"].get("high_severity", 0) for r in results["file_results"])
        medium_total = sum(r["analysis_summary"].get("medium_severity", 0) for r in results["file_results"])
        
        results["summary"] = {
            "total_files": results["files_analyzed"],
            "with_metadata": results["files_with_metadata"],
            "with_inconsistencies": results["files_with_inconsistencies"],
            "total_inconsistencies": results["total_inconsistencies"],
            "high_severity_count": high_total,
            "medium_severity_count": medium_total,
            "timestomping_detected": high_total > 0 or medium_total > 0
        }
        
        return results


def analyze_file(file_path: str, threshold_seconds: int = 60) -> Dict[str, Any]:
    """Main entry point for single file analysis."""
    analyzer = UniversalMetadataAnalyzer(threshold_seconds)
    return analyzer.analyze_file(file_path)


def analyze_directory(directory: str, max_files: int = 100, 
                     threshold_seconds: int = 60) -> Dict[str, Any]:
    """Main entry point for directory analysis."""
    analyzer = UniversalMetadataAnalyzer(threshold_seconds)
    return analyzer.analyze_directory(directory, max_files)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Metadata Timestamp Analyzer")
    parser.add_argument("path", help="File or directory to analyze")
    parser.add_argument("--max-files", type=int, default=100, help="Max files to analyze")
    parser.add_argument("--threshold", type=int, default=60, help="Threshold in seconds for timestamp comparison")
    parser.add_argument("--output", type=str, help="Output JSON file")
    
    args = parser.parse_args()
    
    if os.path.isdir(args.path):
        results = analyze_directory(args.path, args.max_files, args.threshold)
    else:
        results = analyze_file(args.path, args.threshold)
    
    output = json.dumps(results, indent=2, default=str)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)
