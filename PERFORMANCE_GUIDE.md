# Performance Optimization Guide
## Ultimate System Optimizer - Zero-Lag Architecture

This guide ensures the application runs smoothly without causing system lag or UI freezing.

---

## 🎯 Critical Performance Issues to Avoid

### ❌ **Common Mistakes That Cause Lag**

1. **Blocking the GUI Thread**
   - Running system scans on the main tkinter thread
   - Performing I/O operations without threading
   - Heavy computations in event handlers

2. **Excessive Polling**
   - Updating UI too frequently (< 500ms intervals)
   - Repeatedly calling expensive psutil functions
   - Not caching static system information

3. **Memory Leaks**
   - Not properly closing file handles
   - Accumulating graph data indefinitely
   - Creating new thread objects without cleanup

4. **Inefficient Data Structures**
   - Using lists for large datasets instead of deques
   - Not limiting log history
   - Storing raw data instead of aggregated metrics

---

## ✅ **Optimized Architecture**

### **1. Multi-Threaded Design**

```python
import threading
import queue
from collections import deque
import psutil
import tkinter as tk
from tkinter import ttk

class SystemMonitor:
    """Non-blocking system monitor with efficient resource usage"""

    def __init__(self, update_interval=2.0):
        self.update_interval = update_interval
        self.data_queue = queue.Queue(maxsize=100)  # Limit queue size
        self.running = threading.Event()
        self.monitor_thread = None

        # Cache for expensive operations
        self.cache = {
            'cpu_count': psutil.cpu_count(),
            'total_memory': psutil.virtual_memory().total,
            'disk_partitions': psutil.disk_partitions()
        }

        # Limited history for graphs (last 60 data points)
        self.cpu_history = deque(maxlen=60)
        self.mem_history = deque(maxlen=60)

    def start_monitoring(self):
        """Start background monitoring thread"""
        self.running.set()
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True  # Auto-cleanup on exit
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Gracefully stop monitoring"""
        self.running.clear()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

    def _monitor_loop(self):
        """Background thread - never blocks GUI"""
        while self.running.is_set():
            try:
                # Collect metrics efficiently
                metrics = {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_io': psutil.disk_io_counters(),
                    'net_io': psutil.net_io_counters()
                }

                # Non-blocking queue put
                try:
                    self.data_queue.put_nowait(metrics)
                except queue.Full:
                    # Drop old data if queue full
                    try:
                        self.data_queue.get_nowait()
                        self.data_queue.put_nowait(metrics)
                    except:
                        pass

                # Sleep to prevent excessive CPU usage
                self.running.wait(self.update_interval)

            except Exception as e:
                print(f"Monitor error: {e}")
                self.running.wait(1.0)
```

---

### **2. Efficient GUI Updates**

```python
class PerformanceMonitorGUI:
    """Lag-free GUI with throttled updates"""

    def __init__(self, root):
        self.root = root
        self.monitor = SystemMonitor(update_interval=2.0)

        # Update throttling
        self.last_update = 0
        self.min_update_interval = 500  # ms - prevents too frequent updates

        # Use after() for non-blocking updates
        self.update_job = None

        self.setup_gui()
        self.monitor.start_monitoring()
        self.schedule_update()

    def schedule_update(self):
        """Schedule next GUI update without blocking"""
        self.update_job = self.root.after(500, self.update_gui)

    def update_gui(self):
        """Update GUI from queue - runs on main thread"""
        import time
        current_time = time.time() * 1000

        # Throttle updates
        if current_time - self.last_update < self.min_update_interval:
            self.schedule_update()
            return

        # Process all available data (batch updates)
        updates_processed = 0
        latest_metrics = None

        while updates_processed < 10:  # Limit per update cycle
            try:
                latest_metrics = self.monitor.data_queue.get_nowait()
                updates_processed += 1
            except queue.Empty:
                break

        # Only update if we have new data
        if latest_metrics:
            self.update_displays(latest_metrics)
            self.last_update = current_time

        # Schedule next update
        self.schedule_update()

    def update_displays(self, metrics):
        """Fast display update with minimal overhead"""
        # Update labels (fast)
        self.cpu_label.config(text=f"{metrics['cpu_percent']:.1f}%")
        self.mem_label.config(text=f"{metrics['memory_percent']:.1f}%")

        # Update graphs (limit complexity)
        self.update_graph(self.cpu_canvas, self.monitor.cpu_history,
                         metrics['cpu_percent'])

    def update_graph(self, canvas, history, new_value):
        """Efficient graph drawing"""
        history.append(new_value)

        # Clear and redraw efficiently
        canvas.delete("all")

        if len(history) < 2:
            return

        # Calculate dimensions
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Draw line graph (faster than bars)
        points = []
        step = width / len(history)
        max_val = max(history) if history else 100

        for i, val in enumerate(history):
            x = i * step
            y = height - (val / max_val * height * 0.9)
            points.extend([x, y])

        if len(points) >= 4:
            canvas.create_line(points, fill="#4CAF50", width=2)
```

---

### **3. Efficient System Optimization**

```python
import os
import shutil
import concurrent.futures
from pathlib import Path

class SystemOptimizer:
    """Non-blocking, efficient system optimization"""

    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def optimize_async(self, cleanup_settings):
        """Run optimization in background without freezing GUI"""
        future = self.executor.submit(self._run_optimization, cleanup_settings)
        return future

    def _run_optimization(self, settings):
        """Actual optimization work - runs in thread pool"""
        results = {
            'files_deleted': 0,
            'space_freed': 0,
            'errors': []
        }

        tasks = []

        if settings.get('cleanup_temp_files'):
            tasks.append(('temp', self._cleanup_temp_files))

        if settings.get('memory_cleanup'):
            tasks.append(('memory', self._optimize_memory))

        if settings.get('optimize_registry') and os.name == 'nt':
            tasks.append(('registry', self._optimize_registry))

        total_tasks = len(tasks)

        for i, (name, task_func) in enumerate(tasks):
            try:
                # Report progress
                if self.progress_callback:
                    progress = int((i / total_tasks) * 100)
                    self.progress_callback(progress, f"Running {name}...")

                # Run task
                task_result = task_func()
                results['files_deleted'] += task_result.get('files', 0)
                results['space_freed'] += task_result.get('bytes', 0)

            except Exception as e:
                results['errors'].append(f"{name}: {str(e)}")

        return results

    def _cleanup_temp_files(self):
        """Efficient temp file cleanup with batching"""
        import tempfile

        temp_dirs = [
            tempfile.gettempdir(),
            os.path.expanduser("~/.cache") if os.name != 'nt' else None,
            os.path.join(os.getenv('LOCALAPPDATA', ''), 'Temp') if os.name == 'nt' else None
        ]

        files_deleted = 0
        bytes_freed = 0

        for temp_dir in filter(None, temp_dirs):
            if not os.path.exists(temp_dir):
                continue

            # Use os.scandir for efficiency (faster than os.walk)
            try:
                with os.scandir(temp_dir) as entries:
                    for entry in entries:
                        try:
                            # Check file age before deletion
                            if entry.is_file() and self._is_safe_to_delete(entry):
                                size = entry.stat().st_size
                                os.remove(entry.path)
                                files_deleted += 1
                                bytes_freed += size

                                # Yield control periodically
                                if files_deleted % 100 == 0:
                                    import time
                                    time.sleep(0.01)  # Prevent CPU hogging

                        except (PermissionError, OSError):
                            continue  # Skip files we can't delete
            except (PermissionError, OSError):
                continue

        return {'files': files_deleted, 'bytes': bytes_freed}

    def _is_safe_to_delete(self, entry):
        """Check if file is safe to delete"""
        import time

        # Only delete files older than 7 days
        current_time = time.time()
        file_age = current_time - entry.stat().st_mtime

        return file_age > (7 * 24 * 3600)  # 7 days in seconds

    def _optimize_memory(self):
        """Memory optimization"""
        import gc

        # Force garbage collection
        gc.collect()

        # Platform-specific memory optimization
        if os.name == 'nt':
            # Windows: Clear standby list (requires admin)
            try:
                import ctypes
                ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
            except:
                pass

        return {'files': 0, 'bytes': 0}

    def _optimize_registry(self):
        """Safe registry optimization (Windows only)"""
        # Placeholder - implement safe registry cleaning
        return {'files': 0, 'bytes': 0}
```

---

### **4. Memory Management Best Practices**

```python
class MemoryEfficientLogger:
    """Log viewer that doesn't consume unlimited memory"""

    def __init__(self, max_lines=1000):
        self.max_lines = max_lines
        self.log_buffer = deque(maxlen=max_lines)

    def add_log(self, message):
        """Add log entry with automatic cleanup"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_buffer.append(f"[{timestamp}] {message}")

    def get_logs(self):
        """Get all logs as string"""
        return "\n".join(self.log_buffer)


class ResourceManager:
    """Context manager for safe resource handling"""

    def __init__(self):
        self.resources = []

    def register(self, resource):
        """Register resource for cleanup"""
        self.resources.append(resource)

    def cleanup(self):
        """Clean up all registered resources"""
        for resource in self.resources:
            try:
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'stop'):
                    resource.stop()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
            except:
                pass
        self.resources.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
```

---

### **5. Startup Optimization**

```python
class LazyImports:
    """Delay heavy imports until needed"""

    def __init__(self):
        self._modules = {}

    def get_platform_utils(self):
        """Import platform-specific utils only when needed"""
        if 'platform_utils' not in self._modules:
            import platform
            if platform.system() == 'Windows':
                import winreg
                self._modules['platform_utils'] = winreg
            # Similar for Linux/macOS
        return self._modules['platform_utils']


def fast_startup():
    """Optimize application startup time"""

    # 1. Show splash screen immediately
    splash = create_splash_screen()

    # 2. Load configuration (fast)
    config = load_config()

    # 3. Initialize GUI (fast - defer heavy operations)
    root = tk.Tk()
    app = PerformanceMonitorGUI(root)

    # 4. Close splash
    splash.destroy()

    # 5. Start background initialization
    threading.Thread(target=delayed_initialization, daemon=True).start()

    # 6. Start main loop
    root.mainloop()


def delayed_initialization():
    """Load heavy components after UI is shown"""
    import time
    time.sleep(0.5)  # Let GUI render first

    # Now load heavy modules
    initialize_optimization_engine()
    load_system_information()
    start_background_services()
```

---

## 🚀 **Performance Benchmarks to Target**

### **Responsiveness**
- GUI updates: < 16ms (60 FPS)
- Button clicks: Respond within 100ms
- System scan: Show progress every 500ms
- Startup time: < 2 seconds

### **Resource Usage**
- Idle CPU: < 1%
- Active monitoring: < 5% CPU
- Memory footprint: < 50MB
- Update interval: 1-2 seconds (configurable)

### **Optimization Speed**
- Temp file scan: Process 1000 files/second
- Progress updates: Every 1000 files or 500ms
- Memory cleanup: < 1 second
- Total optimization: 30-120 seconds depending on system

---

## 📊 **Monitoring Performance**

```python
import cProfile
import time
from functools import wraps

def profile_performance(func):
    """Decorator to profile function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start

        if duration > 0.1:  # Log slow operations
            print(f"⚠️  {func.__name__} took {duration:.3f}s")

        return result
    return wrapper


class PerformanceMonitor:
    """Monitor application performance"""

    def __init__(self):
        self.metrics = {
            'gui_updates': deque(maxlen=100),
            'optimization_times': deque(maxlen=10)
        }

    def record_gui_update(self, duration):
        """Track GUI update performance"""
        self.metrics['gui_updates'].append(duration)

        # Warn if GUI updates are slow
        avg_time = sum(self.metrics['gui_updates']) / len(self.metrics['gui_updates'])
        if avg_time > 0.05:  # 50ms = too slow
            print(f"⚠️  GUI updates averaging {avg_time*1000:.1f}ms - consider reducing update frequency")
```

---

## ✅ **Implementation Checklist**

### **Before Writing Code**
- [ ] Design thread architecture
- [ ] Plan data flow (background → queue → GUI)
- [ ] Define update intervals
- [ ] Plan resource cleanup strategy

### **During Development**
- [ ] Use threading for all I/O operations
- [ ] Implement progress callbacks
- [ ] Add try-except for all system operations
- [ ] Limit data structure sizes (use maxlen)
- [ ] Use daemon threads for background work
- [ ] Test on low-end hardware

### **Performance Testing**
- [ ] Profile with cProfile
- [ ] Monitor memory with memory_profiler
- [ ] Test with 10,000+ temp files
- [ ] Test on systems with 2GB RAM
- [ ] Measure startup time
- [ ] Test all operations on different OS

---

## 🎯 **Quick Wins for Performance**

1. **Use `psutil` efficiently** - Cache static info, batch calls
2. **Thread all I/O** - Never block the GUI thread
3. **Limit history** - Use `deque(maxlen=N)` for all time series
4. **Batch GUI updates** - Update every 500ms, not every data point
5. **Use `os.scandir()`** - 2-3x faster than `os.walk()`
6. **Implement progress** - User perception of speed matters
7. **Clean up resources** - Use context managers and daemon threads
8. **Profile regularly** - Find bottlenecks early

---

## 🔧 **Configuration for Different Systems**

```python
import psutil

def get_optimal_config():
    """Adjust performance based on system capabilities"""

    total_ram = psutil.virtual_memory().total / (1024**3)  # GB
    cpu_count = psutil.cpu_count()

    if total_ram < 4:
        # Low-end system
        return {
            'update_interval': 3.0,
            'max_history': 30,
            'thread_pool_size': 2,
            'enable_graphs': False  # Graphs are expensive
        }
    elif total_ram < 8:
        # Medium system
        return {
            'update_interval': 2.0,
            'max_history': 60,
            'thread_pool_size': 4,
            'enable_graphs': True
        }
    else:
        # High-end system
        return {
            'update_interval': 1.0,
            'max_history': 120,
            'thread_pool_size': 8,
            'enable_graphs': True
        }
```

---

## 🎓 **Key Principles**

1. **Never block the main thread** - Use threading/asyncio
2. **Cache expensive operations** - Don't re-query static data
3. **Limit unbounded growth** - Use maxlen on all collections
4. **Throttle updates** - More updates ≠ better UX
5. **Clean up resources** - Close files, stop threads, clear caches
6. **Profile before optimizing** - Measure, don't guess
7. **Test on target hardware** - Low-end systems reveal issues

---

**Implementation Priority:**
1. ✅ Multi-threaded monitoring (critical)
2. ✅ Non-blocking GUI updates (critical)
3. ✅ Limited history buffers (critical)
4. ✅ Progress callbacks (user experience)
5. ✅ Resource cleanup (stability)
6. ✅ Performance profiling (optimization)

This architecture will ensure smooth, lag-free operation even on modest hardware.
