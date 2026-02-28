"""Path utilities for forensic image processing."""

from pathlib import Path
from typing import Tuple, Optional


def resolve_image_path(image_path: str) -> Tuple[str, Path, bool]:
    """
    Resolve image path to absolute path and check existence.
    
    Args:
        image_path: Input path (relative, absolute, with spaces, etc.)
        
    Returns:
        Tuple of (original_path, absolute_path, exists)
    """
    original = image_path
    resolved = Path(image_path).expanduser().resolve()
    exists = resolved.exists()
    
    return original, resolved, exists


def get_image_for_display(image_path: str) -> str:
    """
    Get display-friendly version of image path (basename for UI).
    
    Args:
        image_path: Input path
        
    Returns:
        Basename for display purposes
    """
    return Path(image_path).name


def get_image_for_backend(image_path: str) -> str:
    """
    Get the path to use for backend operations (must be absolute).
    
    Args:
        image_path: Input path
        
    Returns:
        Absolute path string for backend operations
    """
    resolved = Path(image_path).expanduser().resolve()
    return str(resolved)


def validate_image_path(image_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that image path exists and is accessible.
    
    Args:
        image_path: Input path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    original, resolved, exists = resolve_image_path(image_path)
    
    if not exists:
        return False, f"Image file not found: {resolved}"
    
    if not resolved.is_file():
        return False, f"Path is not a file: {resolved}"
    
    return True, None


def get_evidence_dir() -> Path:
    """Get the evidence directory for copying images."""
    return Path(__file__).parent.parent / "evidence"


def ensure_image_in_evidence(image_path: str) -> Tuple[str, Path]:
    """
    Ensure image is available in evidence directory.
    Copies if necessary and returns the name to use for backend.
    
    Args:
        image_path: Original image path
        
    Returns:
        Tuple of (image_name_for_backend, evidence_path)
    """
    import shutil
    
    original, resolved, exists = resolve_image_path(image_path)
    
    if not exists:
        raise FileNotFoundError(f"Image not found: {resolved}")
    
    image_name = resolved.name
    evidence_dir = get_evidence_dir()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / image_name
    
    if not evidence_path.exists():
        shutil.copy(resolved, evidence_path)
    
    return image_name, evidence_path
