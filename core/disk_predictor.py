"""Feature #6: Predictive Disk Space Manager

Predicts when you'll run out of disk space and identifies growing folders.
"""

import os
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, asdict
import psutil


@dataclass
class DiskSpaceSnapshot:
    """Snapshot of disk usage at a point in time."""
    timestamp: float
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float


class PredictiveDiskManager:
    """Forecasts disk space issues before they occur.

    Feature #6: Predictive Disk Space Manager
    """

    def __init__(self, history_file: Optional[str] = None):
        """Initialize predictive disk manager.

        Args:
            history_file: Path to save historical data (None = use default)
        """
        if history_file is None:
            home = Path.home()
            config_dir = home / '.ultimate_system_optimizer'
            config_dir.mkdir(exist_ok=True)
            self.history_file = config_dir / 'disk_history.json'
        else:
            self.history_file = Path(history_file)

        # Keep last 90 days of data
        self.history: deque = deque(maxlen=90)
        self._load_history()

    def _load_history(self):
        """Load historical disk data from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    for snapshot in data:
                        self.history.append(DiskSpaceSnapshot(**snapshot))
            except Exception as e:
                print(f"Error loading disk history: {e}")

    def _save_history(self):
        """Save historical disk data to file."""
        try:
            with open(self.history_file, 'w') as f:
                data = [asdict(snapshot) for snapshot in self.history]
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving disk history: {e}")

    def record_snapshot(self, drive: str = '/'):
        """Record current disk usage snapshot.

        Args:
            drive: Drive to monitor (default: root)
        """
        try:
            disk = psutil.disk_usage(drive)

            snapshot = DiskSpaceSnapshot(
                timestamp=time.time(),
                total_gb=round(disk.total / (1024**3), 2),
                used_gb=round(disk.used / (1024**3), 2),
                free_gb=round(disk.free / (1024**3), 2),
                percent_used=round(disk.percent, 1)
            )

            self.history.append(snapshot)
            self._save_history()

        except Exception as e:
            print(f"Error recording disk snapshot: {e}")

    def predict_space_exhaustion(self, drive: str = '/') -> Dict[str, any]:
        """Predict when disk will be full based on growth trends.

        Args:
            drive: Drive to analyze

        Returns:
            Dictionary with prediction results
        """
        # Record current snapshot first
        self.record_snapshot(drive)

        if len(self.history) < 2:
            return {
                'prediction_available': False,
                'reason': 'Insufficient historical data (need at least 2 days)',
                'days_of_data': len(self.history)
            }

        # Calculate daily growth rate
        growth_rate = self._calculate_growth_rate()

        if growth_rate <= 0:
            return {
                'prediction_available': True,
                'disk_growing': False,
                'growth_rate_gb_per_day': round(growth_rate, 3),
                'message': 'Disk usage is stable or decreasing'
            }

        # Get current free space
        current_snapshot = self.history[-1]
        current_free = current_snapshot.free_gb

        # Calculate days until full
        if growth_rate > 0:
            days_until_full = current_free / growth_rate
        else:
            days_until_full = float('inf')

        # Identify fastest growing folders
        growing_folders = self._identify_growing_folders(drive)

        return {
            'prediction_available': True,
            'disk_growing': True,
            'days_until_full': round(days_until_full, 1),
            'growth_rate_gb_per_day': round(growth_rate, 3),
            'current_free_gb': current_free,
            'current_used_percent': current_snapshot.percent_used,
            'fastest_growing_folders': growing_folders,
            'warning_level': self._get_warning_level(days_until_full),
            'recommendation': self._get_recommendation(days_until_full, growing_folders)
        }

    def _calculate_growth_rate(self) -> float:
        """Calculate daily disk growth rate.

        Returns:
            Growth rate in GB per day
        """
        if len(self.history) < 2:
            return 0.0

        # Use linear regression for more accurate prediction
        # For simplicity, we'll use the difference between first and last snapshots

        first_snapshot = self.history[0]
        last_snapshot = self.history[-1]

        time_diff_days = (last_snapshot.timestamp - first_snapshot.timestamp) / (24 * 3600)

        if time_diff_days <= 0:
            return 0.0

        space_diff_gb = last_snapshot.used_gb - first_snapshot.used_gb

        growth_rate = space_diff_gb / time_diff_days

        return growth_rate

    def _identify_growing_folders(self, drive: str) -> List[Dict[str, any]]:
        """Identify folders that are consuming the most space.

        Args:
            drive: Drive to analyze

        Returns:
            List of folder information dicts
        """
        folders = []

        try:
            # Common locations that tend to grow
            if os.name == 'nt':  # Windows
                check_paths = [
                    os.path.join(os.getenv('USERPROFILE', ''), 'Downloads'),
                    os.path.join(os.getenv('USERPROFILE', ''), 'Documents'),
                    os.path.join(os.getenv('USERPROFILE', ''), 'Videos'),
                    os.path.join(os.getenv('LOCALAPPDATA', ''), 'Temp'),
                    'C:\\Windows\\Temp',
                ]
            else:  # Linux/Mac
                home = os.path.expanduser('~')
                check_paths = [
                    os.path.join(home, 'Downloads'),
                    os.path.join(home, 'Documents'),
                    os.path.join(home, '.cache'),
                    '/tmp',
                ]

            for path in check_paths:
                if os.path.exists(path):
                    try:
                        size_gb = self._get_directory_size(path) / (1024**3)
                        if size_gb > 1.0:  # Only report folders > 1GB
                            folders.append({
                                'path': path,
                                'size_gb': round(size_gb, 2),
                                'can_cleanup': self._is_safe_to_cleanup(path)
                            })
                    except (PermissionError, OSError):
                        continue

        except Exception as e:
            print(f"Error identifying growing folders: {e}")

        # Sort by size descending
        folders.sort(key=lambda x: x['size_gb'], reverse=True)

        return folders[:5]  # Top 5 largest folders

    def _get_directory_size(self, path: str) -> int:
        """Get total size of directory in bytes.

        Args:
            path: Directory path

        Returns:
            Size in bytes
        """
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    # Limit recursion depth to avoid slowness
                    try:
                        total += sum(f.stat().st_size for f in Path(entry.path).rglob('*') if f.is_file())
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass

        return total

    def _is_safe_to_cleanup(self, path: str) -> bool:
        """Determine if a folder is safe to clean up.

        Args:
            path: Folder path

        Returns:
            True if safe to cleanup
        """
        safe_cleanup_folders = [
            'temp', 'tmp', 'cache', 'downloads'
        ]

        path_lower = path.lower()
        return any(safe_folder in path_lower for safe_folder in safe_cleanup_folders)

    def _get_warning_level(self, days_until_full: float) -> str:
        """Get warning level based on days until full.

        Args:
            days_until_full: Predicted days until disk is full

        Returns:
            Warning level string
        """
        if days_until_full < 7:
            return 'CRITICAL'
        elif days_until_full < 30:
            return 'WARNING'
        elif days_until_full < 90:
            return 'INFO'
        else:
            return 'OK'

    def _get_recommendation(self, days_until_full: float, growing_folders: List[Dict]) -> str:
        """Get recommendation based on prediction.

        Args:
            days_until_full: Days until full
            growing_folders: List of growing folders

        Returns:
            Recommendation string
        """
        if days_until_full < 7:
            return f"URGENT: Disk will be full in {int(days_until_full)} days! Clean up large files immediately."

        elif days_until_full < 30:
            suggestions = []
            if growing_folders:
                largest = growing_folders[0]
                suggestions.append(f"Review {largest['path']} ({largest['size_gb']}GB)")

            return f"Disk will be full in {int(days_until_full)} days. " + " ".join(suggestions)

        elif days_until_full < 90:
            return f"Disk space is adequate for {int(days_until_full)} days. Monitor usage regularly."

        else:
            return "Disk space is healthy. No immediate action needed."

    def get_historical_trend(self) -> List[Tuple[float, float]]:
        """Get historical disk usage trend for graphing.

        Returns:
            List of (timestamp, used_gb) tuples
        """
        return [(s.timestamp, s.used_gb) for s in self.history]
