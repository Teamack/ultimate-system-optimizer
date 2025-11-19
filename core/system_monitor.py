"""Non-blocking system monitor with efficient resource usage."""

import threading
import queue
import time
from collections import deque
from typing import Dict, Any, Optional
import psutil


class SystemMonitor:
    """Background system monitor that doesn't block the GUI."""

    def __init__(self, update_interval: float = 2.0):
        """Initialize system monitor.

        Args:
            update_interval: Seconds between updates (default 2.0)
        """
        self.update_interval = update_interval
        self.data_queue = queue.Queue(maxsize=100)
        self.running = threading.Event()
        self.monitor_thread: Optional[threading.Thread] = None

        # Cache static information (doesn't change)
        self.cache = {
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'total_memory': psutil.virtual_memory().total,
            'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'boot_time': psutil.boot_time(),
        }

        # Limited history for graphs (last 60 data points)
        self.cpu_history = deque(maxlen=60)
        self.mem_history = deque(maxlen=60)
        self.disk_history = deque(maxlen=60)
        self.net_history = deque(maxlen=60)

    def start_monitoring(self):
        """Start background monitoring thread."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return  # Already running

        self.running.set()
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,  # Auto-cleanup on exit
            name="SystemMonitor"
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Gracefully stop monitoring."""
        self.running.clear()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

    def _monitor_loop(self):
        """Background thread - never blocks GUI."""
        while self.running.is_set():
            try:
                # Collect metrics efficiently
                metrics = self._collect_metrics()

                # Update history
                self.cpu_history.append(metrics['cpu_percent'])
                self.mem_history.append(metrics['memory_percent'])
                self.disk_history.append(metrics['disk_percent'])

                # Non-blocking queue put
                try:
                    self.data_queue.put_nowait(metrics)
                except queue.Full:
                    # Drop old data if queue full
                    try:
                        self.data_queue.get_nowait()
                        self.data_queue.put_nowait(metrics)
                    except queue.Empty:
                        pass

                # Sleep to prevent excessive CPU usage
                self.running.wait(self.update_interval)

            except Exception as e:
                print(f"Monitor error: {e}")
                self.running.wait(1.0)

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

        # Memory
        mem = psutil.virtual_memory()

        # Disk
        disk = psutil.disk_usage('/')

        # Network
        net = psutil.net_io_counters()

        # Process count
        process_count = len(psutil.pids())

        return {
            'timestamp': time.time(),
            'cpu_percent': round(cpu_percent, 1),
            'cpu_per_core': [round(c, 1) for c in cpu_per_core],
            'memory_percent': round(mem.percent, 1),
            'memory_used_gb': round(mem.used / (1024**3), 2),
            'memory_available_gb': round(mem.available / (1024**3), 2),
            'disk_percent': round(disk.percent, 1),
            'disk_used_gb': round(disk.used / (1024**3), 2),
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'net_sent_mb': round(net.bytes_sent / (1024**2), 2),
            'net_recv_mb': round(net.bytes_recv / (1024**2), 2),
            'process_count': process_count,
        }

    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """Get latest metrics from queue (non-blocking).

        Returns:
            Latest metrics dict or None if queue is empty
        """
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None

    def get_cached_info(self) -> Dict[str, Any]:
        """Get cached static system information.

        Returns:
            Dictionary of static system info
        """
        return self.cache.copy()

    def get_history(self) -> Dict[str, deque]:
        """Get historical data for graphs.

        Returns:
            Dictionary containing history deques
        """
        return {
            'cpu': self.cpu_history,
            'memory': self.mem_history,
            'disk': self.disk_history,
            'network': self.net_history,
        }
