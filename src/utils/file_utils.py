"""
File Utilities

Helper functions for reading/writing data files during generation process.
Handles JSON, CSV, and other data formats.
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def ensure_directories_exist(*paths: str) -> None:
    """
    Create directories if they don't exist.
    
    Args:
        *paths: Variable number of directory paths to create
    """
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Directory ensured: {path}")


def save_json(data: Any, filepath: str, indent: int = 2) -> None:
    """
    Save data to JSON file with pretty formatting.
    
    Args:
        data: Data to save (dict, list, etc.)
        filepath: Path to save the file
        indent: JSON indentation for readability
    """
    # Ensure parent directory exists
    parent_dir = Path(filepath).parent
    ensure_directories_exist(str(parent_dir))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    
    print(f"💾 Saved JSON data to: {filepath}")


def load_json(filepath: str) -> Any:
    """
    Load data from JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Loaded data structure
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📖 Loaded JSON data from: {filepath}")
    return data


def save_csv(data: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save list of dictionaries to CSV file.
    
    Args:
        data: List of dictionaries to save
        filepath: Path to save the CSV file
    """
    if not data:
        print("⚠️ No data to save to CSV")
        return
    
    # Ensure parent directory exists
    parent_dir = Path(filepath).parent
    ensure_directories_exist(str(parent_dir))
    
    # Get fieldnames from first item
    fieldnames = list(data[0].keys())
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"💾 Saved CSV data to: {filepath}")


def load_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Load CSV file as list of dictionaries.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        List of dictionaries
    """
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    print(f"📖 Loaded CSV data from: {filepath}")
    return data


def backup_data(filepath: str, backup_dir: str = "backups") -> str:
    """
    Create a timestamped backup of a file.
    
    Args:
        filepath: Path to the file to backup
        backup_dir: Directory to store backups
        
    Returns:
        Path to the backup file
    """
    if not Path(filepath).exists():
        print(f"⚠️ File not found for backup: {filepath}")
        return ""
    
    # Create backup directory
    ensure_directories_exist(backup_dir)
    
    # Generate backup filename with timestamp
    original_name = Path(filepath).name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{timestamp}_{original_name}"
    backup_path = Path(backup_dir) / backup_name
    
    # Copy file
    import shutil
    shutil.copy2(filepath, backup_path)
    
    print(f"💾 Backup created: {backup_path}")
    return str(backup_path)


def file_exists(filepath: str) -> bool:
    """
    Check if file exists.
    
    Args:
        filepath: Path to check
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(filepath).exists()


def get_file_size(filepath: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        filepath: Path to the file
        
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    try:
        return Path(filepath).stat().st_size
    except FileNotFoundError:
        return 0


def list_files(directory: str, pattern: str = "*") -> List[str]:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: File pattern (e.g., "*.json", "*.csv")
        
    Returns:
        List of matching file paths
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        return []
    
    files = [str(f) for f in directory_path.glob(pattern) if f.is_file()]
    return sorted(files) 