"""Feature #14: Context-Aware Resource Allocation

Automatically detects what you're doing and optimizes accordingly.
"""

import psutil
import platform
from typing import Optional, Dict, List
from enum import Enum


class ContextType(Enum):
    """Types of user contexts."""
    GAMING = "gaming"
    WORK = "work"
    CREATIVE = "creative"
    IDLE = "idle"
    UNKNOWN = "unknown"


class ContextAwareManager:
    """Dynamically allocates resources based on user activity.

    Feature #14: Context-Aware Resource Allocation
    """

    # Known game executables (expandable list)
    GAMING_PROCESSES = {
        # Popular games
        'csgo.exe', 'valorant.exe', 'league of legends.exe', 'fortnite.exe',
        'minecraft.exe', 'dota2.exe', 'overwatch.exe', 'apex.exe',
        'gta5.exe', 'rdr2.exe', 'cyberpunk2077.exe', 'witcher3.exe',
        # Game launchers
        'steam.exe', 'epicgameslauncher.exe', 'origin.exe', 'uplay.exe',
        # Linux games
        'steam', 'lutris', 'wine', 'proton'
    }

    # Creative/professional software
    CREATIVE_PROCESSES = {
        'photoshop.exe', 'illustrator.exe', 'premiere.exe', 'aftereffects.exe',
        'davinci resolve.exe', 'blender.exe', '3dsmax.exe', 'maya.exe',
        'unity.exe', 'unrealengine.exe', 'obs64.exe', 'obs.exe',
        'gimp', 'kdenlive', 'inkscape', 'krita'
    }

    # Work/productivity apps
    WORK_PROCESSES = {
        'excel.exe', 'word.exe', 'powerpoint.exe', 'outlook.exe',
        'teams.exe', 'slack.exe', 'zoom.exe', 'chrome.exe', 'firefox.exe',
        'code.exe', 'pycharm.exe', 'intellij.exe', 'visual studio.exe',
        'libreoffice', 'thunderbird'
    }

    def __init__(self):
        """Initialize context-aware manager."""
        self.current_context = ContextType.UNKNOWN
        self.foreground_process: Optional[str] = None
        self.system = platform.system()

    def detect_context(self) -> ContextType:
        """Detect current user context based on running applications.

        Returns:
            Detected context type
        """
        try:
            # Get all running processes
            processes = [p.name().lower() for p in psutil.process_iter(['name'])]

            # Check for gaming
            if any(game in processes for game in self.GAMING_PROCESSES):
                self.current_context = ContextType.GAMING
                return ContextType.GAMING

            # Check for creative apps
            if any(app in processes for app in self.CREATIVE_PROCESSES):
                self.current_context = ContextType.CREATIVE
                return ContextType.CREATIVE

            # Check for work apps
            if any(app in processes for app in self.WORK_PROCESSES):
                self.current_context = ContextType.WORK
                return ContextType.WORK

            # Check CPU usage to detect idle
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 10:
                self.current_context = ContextType.IDLE
                return ContextType.IDLE

            self.current_context = ContextType.UNKNOWN
            return ContextType.UNKNOWN

        except Exception as e:
            print(f"Error detecting context: {e}")
            return ContextType.UNKNOWN

    def get_foreground_process(self) -> Optional[str]:
        """Get the currently active foreground process.

        Returns:
            Process name or None
        """
        # This is platform-specific and requires additional libraries
        # For now, return None (can be enhanced later)
        return None

    def optimize_for_context(self, context: Optional[ContextType] = None) -> Dict[str, bool]:
        """Apply optimizations based on detected context.

        Args:
            context: Context to optimize for (None = auto-detect)

        Returns:
            Dictionary of applied optimizations
        """
        if context is None:
            context = self.detect_context()

        results = {}

        if context == ContextType.GAMING:
            results.update(self._apply_gaming_profile())
        elif context == ContextType.CREATIVE:
            results.update(self._apply_creative_profile())
        elif context == ContextType.WORK:
            results.update(self._apply_work_profile())
        elif context == ContextType.IDLE:
            results.update(self._apply_idle_profile())

        return results

    def _apply_gaming_profile(self) -> Dict[str, bool]:
        """Apply gaming optimizations.

        - Max CPU/GPU to game
        - Disable Windows updates
        - Stop non-essential services
        - High priority to game process
        """
        results = {
            'profile': 'gaming',
            'power_plan': False,
            'services_stopped': False,
            'priority_adjusted': False
        }

        # Set high performance power plan (Windows)
        if self.system == 'Windows':
            try:
                import subprocess
                subprocess.run(
                    ['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'],
                    check=False, capture_output=True
                )
                results['power_plan'] = True
            except:
                pass

        # Note: Stopping services and adjusting priorities requires admin rights
        # and should be done carefully. For now, we just detect and report.

        return results

    def _apply_creative_profile(self) -> Dict[str, bool]:
        """Apply creative/productivity optimizations.

        - Max cores to creative apps
        - Reduce background processes
        - Balanced power plan
        """
        results = {
            'profile': 'creative',
            'power_plan': False,
            'ram_optimized': False
        }

        # Set balanced power plan
        if self.system == 'Windows':
            try:
                import subprocess
                subprocess.run(
                    ['powercfg', '/setactive', '381b4222-f694-41f0-9685-ff5bb260df2e'],
                    check=False, capture_output=True
                )
                results['power_plan'] = True
            except:
                pass

        return results

    def _apply_work_profile(self) -> Dict[str, bool]:
        """Apply work optimizations.

        - Optimize browser performance
        - Balanced resources
        """
        return {
            'profile': 'work',
            'browser_optimized': False,
            'balanced': True
        }

    def _apply_idle_profile(self) -> Dict[str, bool]:
        """Apply idle optimizations.

        - Allow background tasks
        - Run maintenance
        - Power saving mode
        """
        results = {
            'profile': 'idle',
            'power_saving': False,
            'maintenance_allowed': True
        }

        # Set power saver plan
        if self.system == 'Windows':
            try:
                import subprocess
                subprocess.run(
                    ['powercfg', '/setactive', 'a1841308-3541-4fab-bc81-f71556f20b4a'],
                    check=False, capture_output=True
                )
                results['power_saving'] = True
            except:
                pass

        return results

    def get_optimization_suggestions(self, context: Optional[ContextType] = None) -> List[str]:
        """Get optimization suggestions for current context.

        Args:
            context: Context to get suggestions for (None = auto-detect)

        Returns:
            List of suggestion strings
        """
        if context is None:
            context = self.detect_context()

        suggestions = []

        if context == ContextType.GAMING:
            suggestions = [
                "Close unnecessary background applications",
                "Enable high-performance power plan",
                "Disable Windows updates temporarily",
                "Close browser tabs to free RAM",
                "Stop antivirus real-time scanning during gameplay"
            ]
        elif context == ContextType.CREATIVE:
            suggestions = [
                "Close unused browser tabs",
                "Allocate more RAM to creative applications",
                "Clear application cache for Adobe apps",
                "Disable non-essential startup programs"
            ]
        elif context == ContextType.WORK:
            suggestions = [
                "Organize browser tabs to reduce memory usage",
                "Close unused applications",
                "Clear browser cache for faster performance"
            ]
        elif context == ContextType.IDLE:
            suggestions = [
                "Good time to run deep system cleanup",
                "Schedule automatic optimization",
                "Run disk defragmentation (HDD only)",
                "Update applications and system"
            ]

        return suggestions
