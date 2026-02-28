#!/usr/bin/env python3
"""
Forensic Disk Analyzer - Desktop Application
Single file that runs both backend and PySide6 WebView GUI
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIcon, QAction

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uuid
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
FRONTEND_DIR = SCRIPT_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"
IMAGE_PROCESSOR_DIR = SCRIPT_DIR / "imageProcessor"
FORENSIC_OUTPUT_DIR = SCRIPT_DIR / "forensic_output"

INPUT_DIRS = []
for d in [SCRIPT_DIR, SCRIPT_DIR / "imageProcessor", Path.home() / "Desktop", Path.home() / "Documents", Path.home() / "Downloads"]:
    if d.exists():
        INPUT_DIRS.append(d)

for drive_letter in ["C", "D", "E", "F", "G"]:
    drive = Path(f"{drive_letter}:/")
    if drive.exists():
        INPUT_DIRS.append(drive)

sys.path.insert(0, str(IMAGE_PROCESSOR_DIR))
sys.path.insert(0, str(SCRIPT_DIR))


def resolve_image_path(image_path: str) -> Path:
    import os
    
    if not image_path:
        return Path("")
    
    normalized_path = os.path.normpath(image_path)
    path = Path(normalized_path)
    
    if path.exists():
        return path.resolve()
    
    alt_path = Path(str(path).replace('\\', '/'))
    if alt_path.exists():
        return alt_path.resolve()
    
    return path


app = FastAPI(title="Forensic Disk Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

task_manager = {"tasks": {}, "lock": threading.Lock()}


class ForensicTask:
    def __init__(self, task_id: str, image_path: str):
        self.task_id = task_id
        self.image_path = image_path
        self.status = "pending"
        self.progress = 0
        self.stage = "initialized"
        self.message = "Task created"
        self.output_dir = None
        self.results = None
        self.error = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None


class ForensicStartRequest(BaseModel):
    image_path: str


class ForensicStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    stage: str
    message: str
    output_dir: str | None = None
    error: str | None = None


class ForensicResultsResponse(BaseModel):
    task_id: str
    status: str
    output_dir: str | None = None
    findings: list = []
    summary: str = ""
    risk_level: str = "Unknown"
    recommendations: list = []
    timestamp: str = ""
    model: str = "unknown"
    analysis_time_seconds: float = 0.0
    timestamp_analysis: dict = {}
    metadata_analysis: dict = {}
    partitions: list = []
    report_files: dict = {}


def run_forensic_analysis(task_id: str, image_path: str):
    task = task_manager["tasks"].get(task_id)
    if not task:
        return

    try:
        task.status = "running"
        task.progress = 5
        task.stage = "validation"
        task.message = "Validating image file..."

        image_file = resolve_image_path(image_path)
        
        print(f"[DEBUG] Resolved path: {image_file}, exists: {image_file.exists()}")
        
        if not image_file.exists():
            if Path(image_path).exists():
                image_file = Path(image_path)
            elif Path(str(image_path).replace('/', '\\')).exists():
                image_file = Path(str(image_path).replace('/', '\\'))
        
        if not image_file.exists():
            searched = []
            for base in INPUT_DIRS:
                tried = base / image_path
                searched.append(str(tried))
                if tried.exists():
                    image_file = tried
                    break
            
            if not image_file.exists():
                task.status = "failed"
                task.error = f"Image file not found: {image_path}\nTried: {', '.join(searched[:5])}"
                return

        ext = image_file.suffix.lower() if hasattr(image_file, 'suffix') else Path(image_file).suffix.lower()
        supported_formats = [".e01", ".E01", ".dd", ".raw", ".img", ".ewf", ".aff", ".afm"]
        if ext not in supported_formats:
            task.status = "failed"
            task.error = f"Unsupported image format: {ext}. Supported: {', '.join(supported_formats)}"
            return

        task.progress = 10
        task.stage = "preparation"
        task.message = "Preparing output directory..."

        safe_name = image_file.stem.replace(" ", "_").replace("/", "_").replace("\\", "_")
        output_dir = FORENSIC_OUTPUT_DIR / safe_name
        output_dir.mkdir(parents=True, exist_ok=True)
        task.output_dir = str(output_dir)

        task.progress = 20
        task.stage = "extraction"
        task.message = "Extracting forensic artifacts..."

        from forensic_extractor import ForensicExtractor

        extractor = ForensicExtractor(str(image_file), str(output_dir))
        task.progress = 40
        task.stage = "preprocessing"
        task.message = "Preprocessing artifacts..."

        from ai_preprocessor import ForensicPreprocessor

        preprocessor = ForensicPreprocessor(str(output_dir))
        preprocessed = preprocessor.run_full_preprocessing()

        task.progress = 60
        task.stage = "timestamp_analysis"
        task.message = "Running timestamp integrity analysis..."

        from imageProcessor.agents.timestamp_agent import analyze as timestamp_analyze

        timestamp_analysis = {}
        try:
            extractor = ForensicExtractor(image_path, str(output_dir))
            for i, partition in enumerate(extractor.partitions):
                offset = extractor.get_partition_offset(i)
                ts_result = timestamp_analyze(str(image_file), offset)
                timestamp_analysis[f"partition_{i}"] = ts_result

                ts_file = output_dir / f"timestamp_analysis_partition_{i}.json"
                with open(ts_file, "w") as f:
                    json.dump(ts_result, f, indent=2)
        except Exception as e:
            timestamp_analysis = {"error": str(e)}

        findings = []

        task.progress = 63
        task.stage = "metadata_analysis"
        task.message = "Running metadata timestamp analysis..."

        from imageProcessor.agents.universal_metadata_analyzer import analyze_directory as metadata_analyze

        metadata_analysis = {}
        try:
            metadata_results = metadata_analyze(str(output_dir), max_files=100, threshold_seconds=60)
            metadata_analysis = metadata_results

            metadata_file = output_dir / "metadata_timestamp_analysis.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata_results, f, indent=2, default=str)

            for finding in metadata_results.get("file_results", []):
                for inc in finding.get("inconsistencies", []):
                    findings.append({
                        "technique": f"Metadata Timestomping - {inc.get('type', 'unknown')}",
                        "severity": inc.get("severity", "medium").upper(),
                        "evidence": inc.get("description", ""),
                        "explanation": f"File: {finding.get('file_name', 'unknown')}. Metadata timestamp differs from filesystem timestamp.",
                        "recommendation": "Investigate file for potential timestamp manipulation",
                        "confidence": 0.75,
                    })
        except Exception as e:
            metadata_analysis = {"error": str(e)}

        for partition, ts_data in timestamp_analysis.items():
            if not isinstance(ts_data, dict):
                continue
            for inc in ts_data.get("inconsistencies", []):
                findings.append({
                    "technique": f"Timestamp Inconsistency - {inc.get('type', 'unknown')}",
                    "severity": inc.get("severity", "medium").upper(),
                    "evidence": inc.get("message", ""),
                    "explanation": inc.get("description", "Timestamp inconsistency detected"),
                    "recommendation": "Investigate file for potential timestomping or anti-forensic activity",
                    "confidence": 0.8,
                })

        high_count = sum(1 for f in findings if f["severity"] == "HIGH")
        risk_level = "Critical" if high_count > 3 else "High" if high_count > 0 else "Medium"

        task.progress = 65
        task.stage = "antiforensic"
        task.message = "Running anti-forensic analysis..."

        try:
            from analyze_antiforensic import AntiForensicAnalyzer

            af_analyzer = AntiForensicAnalyzer(str(output_dir))
            antiforensic_results = af_analyzer.analyze()

            af_json_file = output_dir / "antiforensic_analysis.json"
            with open(af_json_file, "w") as f:
                json.dump(antiforensic_results, f, indent=2)

            for finding in antiforensic_results.get("findings", []):
                findings.append({
                    "technique": finding.get("technique", "Anti-forensic activity"),
                    "severity": finding.get("severity", "medium").upper(),
                    "evidence": finding.get("evidence", ""),
                    "explanation": finding.get("description", ""),
                    "recommendation": finding.get("recommendation", ""),
                    "confidence": finding.get("confidence", 0.7),
                })
        except Exception as e:
            pass

        task.results = {
            "findings": findings,
            "summary": f"Analysis complete. Found {len(findings)} potential indicators ({high_count} high severity).",
            "risk_level": risk_level,
            "recommendations": [
                "Review timestamp inconsistencies for evidence of timestomping",
                "Check files with modified-after-changed timestamps",
                "Compare with known baseline timestamps",
                "Review metadata timestamp mismatches for file manipulation evidence",
            ],
            "model": "self-contained-agent",
            "analysis_time_seconds": 0,
            "timestamp_analysis": timestamp_analysis,
            "metadata_analysis": metadata_analysis,
            "partitions": [
                {
                    "slot": p.get("slot", ""),
                    "start_sector": p.get("start_sector", p.get("start_int", p.get("start", ""))),
                    "end_sector": p.get("end_sector", p.get("end", "")),
                    "size_sectors": p.get("size_sectors", 0),
                    "fs": p.get("fs", ""),
                    "description": p.get("description", p.get("desc", "")),
                    "is_hidden": p.get("is_hidden", False),
                    "is_encrypted": p.get("is_encrypted", False),
                    "encryption_type": p.get("encryption_type")
                }
                for p in extractor.partitions
            ] if extractor else [],
        }

        # Generate reports
        try:
            from imageProcessor.forensic_report import generate_report
            image_name = Path(image_file).name
            reports = generate_report(str(output_dir), task.results, image_name)
            task.results["report_files"] = reports
        except Exception as e:
            print(f"[DEBUG] Report generation error: {e}")

        task.progress = 100
        task.stage = "complete"
        task.message = "Analysis complete"
        task.status = "completed"
        task.completed_at = datetime.now().isoformat()

    except Exception as e:
        import traceback

        task.status = "failed"
        task.error = f"Analysis failed: {str(e)}\n{traceback.format_exc()}"


@app.get("/forensics/health")
async def forensics_health():
    docker_available = False
    try:
        import subprocess
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        docker_available = result.returncode == 0
    except:
        pass
    
    return {
        "status": "ok",
        "pipeline_available": True,
        "docker_available": docker_available,
        "docker_message": "Docker available - USN journal extraction enabled" if docker_available else "Docker not found - Install Docker to enable USN journal extraction"
    }


@app.post("/forensics/start", response_model=dict)
async def start_forensic_analysis(request: ForensicStartRequest):
    image_path = request.image_path.strip()
    if not image_path:
        raise HTTPException(status_code=400, detail="Image path is required")

    resolved_path = resolve_image_path(image_path)
    
    if not resolved_path.exists():
        raise HTTPException(status_code=400, detail=f"Image file not found: {image_path}\nSearched in common locations")

    ext = resolved_path.suffix.lower()
    if ext not in [".e01", ".dd", ".raw", ".img"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format: {ext}",
        )

    task_id = str(uuid.uuid4())
    task = ForensicTask(task_id, str(resolved_path))
    task_manager["tasks"][task_id] = task

    thread = threading.Thread(target=run_forensic_analysis, args=(task_id, str(resolved_path)))
    thread.daemon = True
    thread.start()

    return {"task_id": task.task_id, "status": task.status, "message": "Forensic analysis started"}


@app.get("/forensics/status/{task_id}", response_model=ForensicStatusResponse)
async def get_forensic_status(task_id: str):
    task = task_manager["tasks"].get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return ForensicStatusResponse(
        task_id=task.task_id,
        status=task.status,
        progress=task.progress,
        stage=task.stage,
        message=task.message,
        output_dir=task.output_dir,
        error=task.error,
    )


@app.get("/forensics/results/{task_id}", response_model=ForensicResultsResponse)
async def get_forensic_results(task_id: str):
    task = task_manager["tasks"].get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail=f"Analysis not complete: {task.status}")

    return ForensicResultsResponse(
        task_id=task.task_id,
        status=task.status,
        output_dir=task.output_dir or "",
        findings=task.results.get("findings", []) if task.results else [],
        summary=task.results.get("summary", "") if task.results else "",
        risk_level=task.results.get("risk_level", "Unknown") if task.results else "Unknown",
        recommendations=task.results.get("recommendations", []) if task.results else [],
        timestamp=task.completed_at or datetime.now().isoformat(),
        model=task.results.get("model", "unknown") if task.results else "unknown",
        analysis_time_seconds=task.results.get("analysis_time_seconds", 0) if task.results else 0,
        timestamp_analysis=task.results.get("timestamp_analysis", {}) if task.results else {},
        metadata_analysis=task.results.get("metadata_analysis", {}) if task.results else {},
        partitions=task.results.get("partitions", []) if task.results else [],
        report_files=task.results.get("report_files", {}) if task.results else {},
    )


@app.get("/forensics/pdf/{task_id}")
async def download_forensic_pdf(task_id: str):
    task = task_manager["tasks"].get(task_id)
    if not task or not task.output_dir:
        raise HTTPException(status_code=404, detail="Task not found")

    output_dir = Path(task.output_dir)
    pdf_files = list(output_dir.glob("forensic_report_*.pdf"))

    if pdf_files:
        return FileResponse(pdf_files[0], media_type="application/pdf")

    raise HTTPException(status_code=404, detail="PDF report not found")


@app.get("/forensics/drives")
async def get_drives():
    """Get available drives on the system."""
    drives = []
    import string
    for letter in string.ascii_uppercase:
        drive = Path(f"{letter}:/")
        if drive.exists():
            drives.append(letter + ":/")
    return {"drives": drives}


@app.get("/forensics/browse")
async def browse_directory(path: str = "C:/"):
    """Browse directory contents."""
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        items = []
        for item in dir_path.iterdir():
            try:
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "is_file": item.is_file(),
                    "size": item.stat().st_size if item.is_file() else 0,
                })
            except PermissionError:
                continue
        
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return {"path": str(dir_path), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/forensics/select-image")
async def select_image(path: str):
    """Validate and select image file."""
    try:
        file_path = Path(path)
        
        if not file_path.exists():
            return {"valid": False, "error": "File not found"}
        
        if not file_path.is_file():
            return {"valid": False, "error": "Not a file"}
        
        ext = file_path.suffix.lower()
        supported = [".e01", ".dd", ".raw", ".img", ".ewf", ".aff", ".afm"]
        
        if ext not in supported:
            return {"valid": False, "error": f"Unsupported format. Supported: {', '.join(supported)}"}
        
        return {
            "valid": True,
            "path": str(file_path.absolute()),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "format": ext
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


@app.get("/forensics/report/{task_id}")
async def download_report(task_id: str, format: str = "html"):
    """Download forensic report."""
    task = task_manager["tasks"].get(task_id)
    if not task or not task.output_dir:
        raise HTTPException(status_code=404, detail="Task not found")
    
    output_dir = Path(task.output_dir)
    
    if format == "html":
        reports = list(output_dir.glob("forensic_report_*.html"))
        if reports:
            return FileResponse(reports[0], media_type="text/html")
    
    reports = list(output_dir.glob("forensic_report_*.txt"))
    if reports:
        return FileResponse(reports[0], media_type="text/plain")
    
    raise HTTPException(status_code=404, detail="Report not found")


@app.get("/")
async def serve_frontend():
    index_path = DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend not found. Run 'npm run build' in frontend directory."}


@app.get("/assets/{path:path}")
async def serve_assets(path: str):
    asset_path = DIST_DIR / "assets" / path
    if asset_path.exists():
        return FileResponse(asset_path)
    raise HTTPException(status_code=404, detail="Asset not found")


class ForensicAnalyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forensic Disk Analyzer")
        self.setMinimumSize(1200, 800)

        central_widget = QWebEngineView()
        self.setCentralWidget(central_widget)

        self.backend_thread = None
        self.backend_ready = False

        self.start_backend()

        QTimer.singleShot(1000, lambda: self.load_frontend(central_widget))

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(central_widget.reload)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def start_backend(self):
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")

        self.backend_thread = threading.Thread(target=run_server, daemon=True)
        self.backend_thread.start()
        print("[*] Backend started at http://127.0.0.1:8000")

    def load_frontend(self, web_view: QWebEngineView):
        web_view.setUrl(QUrl("http://127.0.0.1:8000/"))
        print("[*] Loading frontend from http://127.0.0.1:8000/")


def main():
    if not DIST_DIR.exists():
        print("[!] Frontend not built. Please run: cd frontend && npm install && npm run build")
        print("[*] Starting anyway - will try dev server...")

    FORENSIC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    app_qt = QApplication(sys.argv)
    window = ForensicAnalyzerWindow()
    window.show()
    sys.exit(app_qt.exec())


if __name__ == "__main__":
    main()
