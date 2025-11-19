"""System optimization engine with transparent operations."""

import os
import shutil
import tempfile
import gc
import platform
import time
from pathlib import Path
from typing import Dict, List, Callable, Optional, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass


@dataclass
class OptimizationAction:
    """Represents a single optimization action for transparency."""
    category: str
    description: str
    file_path: Optional[str] = None
    file_size: int = 0
    safe_to_delete: bool = True
    reason: str = ""


class SystemOptimizer:
    """Non-blocking, transparent system optimization engine.

    Implements:
    - Feature #15: One-Click Boost
    - Feature #25: Transparent Optimization
    """

    def __init__(self, progress_callback: Optional[Callable] = None):
        """Initialize optimizer.

        Args:
            progress_callback: Function to call with (percent, message) for progress updates
        """
        self.progress_callback = progress_callback
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.pending_actions: List[OptimizationAction] = []
        self.completed_actions: List[OptimizationAction] = []

    def analyze_system(self) -> Dict[str, Any]:
        """Analyze system and return what can be optimized.

        This is Feature #25: Transparent Optimization
        Shows exactly what will be cleaned BEFORE doing it.

        Returns:
            Dictionary containing analysis results and pending actions
        """
        self.pending_actions = []

        # Analyze temp files
        temp_actions = self._analyze_temp_files()
        self.pending_actions.extend(temp_actions)

        # Analyze memory
        mem_actions = self._analyze_memory()
        self.pending_actions.extend(mem_actions)

        # Analyze cache
        cache_actions = self._analyze_cache()
        self.pending_actions.extend(cache_actions)

        # Calculate totals
        total_files = len([a for a in self.pending_actions if a.file_path])
        total_size = sum(a.file_size for a in self.pending_actions)

        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024**2), 2),
            'actions': self.pending_actions,
            'categories': self._group_by_category()
        }

    def _analyze_temp_files(self) -> List[OptimizationAction]:
        """Analyze temporary files that can be cleaned."""
        actions = []

        # Get temp directory
        temp_dir = tempfile.gettempdir()

        try:
            # Use os.scandir for efficiency (2-3x faster than os.walk)
            with os.scandir(temp_dir) as entries:
                for entry in entries:
                    try:
                        if entry.is_file():
                            # Check file age
                            stat = entry.stat()
                            age_days = (time.time() - stat.st_mtime) / (24 * 3600)

                            if age_days > 7:  # Only files older than 7 days
                                actions.append(OptimizationAction(
                                    category='Temporary Files',
                                    description=f'Delete old temp file: {entry.name}',
                                    file_path=entry.path,
                                    file_size=stat.st_size,
                                    safe_to_delete=True,
                                    reason=f'File is {int(age_days)} days old'
                                ))
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass

        # Platform-specific temp locations
        if platform.system() == 'Windows':
            # Windows temp folders
            win_temp_paths = [
                os.path.join(os.getenv('LOCALAPPDATA', ''), 'Temp'),
                'C:\\Windows\\Temp',
            ]
            for temp_path in win_temp_paths:
                if os.path.exists(temp_path):
                    actions.extend(self._scan_directory_for_old_files(
                        temp_path, 'Windows Temp Files', 7
                    ))

        elif platform.system() == 'Linux':
            # Linux cache/temp
            linux_cache = os.path.expanduser('~/.cache')
            if os.path.exists(linux_cache):
                actions.extend(self._scan_directory_for_old_files(
                    linux_cache, 'Linux Cache', 7
                ))

        return actions[:100]  # Limit to 100 files for analysis

    def _analyze_memory(self) -> List[OptimizationAction]:
        """Analyze memory optimization opportunities."""
        import psutil

        actions = []
        mem = psutil.virtual_memory()

        if mem.percent > 70:  # Memory usage above 70%
            actions.append(OptimizationAction(
                category='Memory Optimization',
                description='Clear system cache and free unused RAM',
                safe_to_delete=True,
                reason=f'Memory usage at {mem.percent}%'
            ))

        return actions

    def _analyze_cache(self) -> List[OptimizationAction]:
        """Analyze cache that can be cleared."""
        actions = []

        # Browser caches (if we can access them safely)
        if platform.system() == 'Windows':
            # Chrome cache
            chrome_cache = os.path.join(
                os.getenv('LOCALAPPDATA', ''),
                'Google', 'Chrome', 'User Data', 'Default', 'Cache'
            )
            if os.path.exists(chrome_cache):
                try:
                    size = sum(f.stat().st_size for f in Path(chrome_cache).rglob('*') if f.is_file())
                    if size > 100 * 1024 * 1024:  # > 100MB
                        actions.append(OptimizationAction(
                            category='Browser Cache',
                            description='Clear Chrome cache',
                            file_path=chrome_cache,
                            file_size=size,
                            safe_to_delete=True,
                            reason=f'Cache size: {round(size/(1024**2), 1)}MB'
                        ))
                except:
                    pass

        return actions

    def _scan_directory_for_old_files(self, directory: str, category: str, age_days: int) -> List[OptimizationAction]:
        """Scan directory for old files."""
        actions = []

        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        if entry.is_file():
                            stat = entry.stat()
                            age = (time.time() - stat.st_mtime) / (24 * 3600)

                            if age > age_days:
                                actions.append(OptimizationAction(
                                    category=category,
                                    description=f'Delete: {entry.name}',
                                    file_path=entry.path,
                                    file_size=stat.st_size,
                                    safe_to_delete=True,
                                    reason=f'{int(age)} days old'
                                ))
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass

        return actions[:50]  # Limit per directory

    def _group_by_category(self) -> Dict[str, Dict[str, Any]]:
        """Group actions by category for display."""
        categories = {}

        for action in self.pending_actions:
            if action.category not in categories:
                categories[action.category] = {
                    'count': 0,
                    'total_size': 0,
                    'actions': []
                }

            categories[action.category]['count'] += 1
            categories[action.category]['total_size'] += action.file_size
            categories[action.category]['actions'].append(action)

        return categories

    def optimize_async(self, selected_categories: Optional[List[str]] = None) -> Any:
        """Run optimization asynchronously.

        This is Feature #15: One-Click Boost

        Args:
            selected_categories: List of categories to optimize (None = all)

        Returns:
            Future object that can be used to check status
        """
        future = self.executor.submit(self._run_optimization, selected_categories)
        return future

    def _run_optimization(self, selected_categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Actually perform the optimization."""
        results = {
            'files_deleted': 0,
            'space_freed': 0,
            'errors': [],
            'actions_completed': []
        }

        # Filter actions by selected categories
        if selected_categories:
            actions_to_run = [a for a in self.pending_actions if a.category in selected_categories]
        else:
            actions_to_run = self.pending_actions

        total_actions = len(actions_to_run)

        for i, action in enumerate(actions_to_run):
            try:
                # Report progress
                if self.progress_callback:
                    progress = int((i / total_actions) * 100)
                    self.progress_callback(progress, f"Processing: {action.category}")

                # Execute action
                if action.category == 'Memory Optimization':
                    self._optimize_memory()
                elif action.file_path and os.path.exists(action.file_path):
                    # Delete file
                    try:
                        os.remove(action.file_path)
                        results['files_deleted'] += 1
                        results['space_freed'] += action.file_size
                        results['actions_completed'].append(action)
                    except (PermissionError, OSError) as e:
                        results['errors'].append(f"Cannot delete {action.file_path}: {e}")

            except Exception as e:
                results['errors'].append(f"{action.category}: {str(e)}")

        # Final progress
        if self.progress_callback:
            self.progress_callback(100, "Optimization complete!")

        results['space_freed_mb'] = round(results['space_freed'] / (1024**2), 2)
        return results

    def _optimize_memory(self):
        """Optimize system memory."""
        # Force garbage collection
        gc.collect()

        # Platform-specific memory optimization
        if platform.system() == 'Windows':
            try:
                import ctypes
                # Clear working set
                ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
            except:
                pass

    def one_click_boost(self) -> Any:
        """Feature #15: One-Click Boost

        Immediately optimize system without user having to select categories.

        Returns:
            Future object for the optimization task
        """
        # First analyze
        self.analyze_system()

        # Then optimize everything
        return self.optimize_async()
