import os
import hashlib
import re
import shutil
import tempfile
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime
import fnmatch

class FileUtils:
    """
    Universal file utilities for project analysis
    """
    
    @staticmethod
    def get_file_extension(filename):
        """Get file extension with dot"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def get_file_size(filepath):
        """Get file size in human-readable format"""
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @staticmethod
    def get_file_hash(filepath, algorithm='md5'):
        """Calculate file hash"""
        hash_func = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    @staticmethod
    def get_file_info(filepath, base_path=None):
        """Get detailed file information"""
        stat = os.stat(filepath)
        
        info = {
            'name': os.path.basename(filepath),
            'path': filepath,
            'extension': FileUtils.get_file_extension(filepath),
            'size': stat.st_size,
            'size_hr': FileUtils.get_file_size(filepath),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
            'is_dir': os.path.isdir(filepath),
            'is_file': os.path.isfile(filepath),
            'is_symlink': os.path.islink(filepath)
        }
        
        if base_path:
            info['relative_path'] = os.path.relpath(filepath, base_path)
        
        return info
    
    @staticmethod
    def count_lines(filepath):
        """Count lines in text file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    @staticmethod
    def read_file_safely(filepath, max_size_mb=10):
        """Safely read file with size limit"""
        if os.path.getsize(filepath) > max_size_mb * 1024 * 1024:
            return None, f"File exceeds {max_size_mb}MB limit"
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(), None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def extract_archive(archive_path, extract_path=None):
        """Extract various archive formats"""
        if extract_path is None:
            extract_path = tempfile.mkdtemp(prefix='extract_')
        
        os.makedirs(extract_path, exist_ok=True)
        
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        
        elif archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_path)
        
        elif archive_path.endswith('.tar.bz2'):
            with tarfile.open(archive_path, 'r:bz2') as tar_ref:
                tar_ref.extractall(extract_path)
        
        elif archive_path.endswith('.tar'):
            with tarfile.open(archive_path, 'r:') as tar_ref:
                tar_ref.extractall(extract_path)
        
        else:
            raise ValueError(f"Unsupported archive format: {archive_path}")
        
        return extract_path
    
    @staticmethod
    def find_files(directory, pattern='*', recursive=True):
        """Find files matching pattern"""
        matches = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        matches.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(directory):
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.join(directory, filename))
        
        return matches
    
    @staticmethod
    def get_directory_tree(directory, max_depth=3, prefix=''):
        """Get directory tree as string"""
        if max_depth < 0:
            return ''
        
        tree = ''
        items = sorted(os.listdir(directory))
        
        for i, item in enumerate(items):
            path = os.path.join(directory, item)
            is_last = i == len(items) - 1
            
            tree += prefix + ('└── ' if is_last else '├── ') + item + '\n'
            
            if os.path.isdir(path):
                extension = '    ' if is_last else '│   '
                tree += FileUtils.get_directory_tree(path, max_depth - 1, prefix + extension)
        
        return tree
    
    @staticmethod
    def get_file_stats(directory):
        """Get statistics about files in directory"""
        stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'by_extension': {},
            'largest_files': [],
            'newest_files': [],
            'oldest_files': []
        }
        
        files_info = []
        
        for root, dirs, files in os.walk(directory):
            stats['total_dirs'] += len(dirs)
            
            for file in files:
                filepath = os.path.join(root, file)
                file_info = FileUtils.get_file_info(filepath)
                
                stats['total_files'] += 1
                stats['total_size'] += file_info['size']
                
                ext = file_info['extension']
                stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
                
                files_info.append(file_info)
        
        # Sort files by size
        files_by_size = sorted(files_info, key=lambda x: x['size'], reverse=True)
        stats['largest_files'] = files_by_size[:10]
        
        # Sort by modified date
        files_by_date = sorted(files_info, key=lambda x: x['modified'], reverse=True)
        stats['newest_files'] = files_by_date[:10]
        stats['oldest_files'] = files_by_date[-10:] if len(files_by_date) >= 10 else files_by_date
        
        stats['total_size_hr'] = FileUtils.get_file_size.__func__(None, stats['total_size'])
        
        return stats
    
    @staticmethod
    def safe_filename(filename):
        """Make filename safe for filesystem"""
        # Remove invalid characters
        safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove control characters
        safe = ''.join(char for char in safe if ord(char) >= 32)
        # Limit length
        if len(safe) > 255:
            name, ext = os.path.splitext(safe)
            safe = name[:255-len(ext)] + ext
        return safe
    
    @staticmethod
    def ensure_directory(path):
        """Ensure directory exists"""
        os.makedirs(path, exist_ok=True)
        return path
    
    @staticmethod
    def clean_directory(path):
        """Remove all contents of directory"""
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)