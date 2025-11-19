"""Main application window for Ultimate System Optimizer."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from config import ConfigManager
from core import (
    SystemMonitor,
    SystemOptimizer,
    ResourceManager,
    ContextAwareManager,
    PredictiveDiskManager
)


class MainApplication:
    """Main application window with tabbed interface."""

    def __init__(self, config: Optional[ConfigManager] = None):
        """Initialize main application.

        Args:
            config: Configuration manager (None = create new)
        """
        self.config = config or ConfigManager()

        # Initialize core components
        self.monitor = SystemMonitor(
            update_interval=self.config.get('monitoring_interval', 2.0)
        )
        self.optimizer = SystemOptimizer()
        self.context_manager = ContextAwareManager()
        self.disk_predictor = PredictiveDiskManager()
        self.resource_manager = ResourceManager()

        # Register resources for cleanup
        self.resource_manager.register(self.monitor)

        # Create main window
        self.root = tk.Tk()
        self.root.title("Ultimate System Optimizer - AI-Powered System Management")
        self.root.geometry("900x700")

        # Set minimum size
        self.root.minsize(800, 600)

        # Create UI
        self._create_ui()

        # Start monitoring
        self.monitor.start_monitoring()

        # Schedule GUI updates
        self._schedule_update()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_ui(self):
        """Create main user interface."""
        # Create menu bar
        self._create_menu()

        # Create top status bar
        self._create_status_bar()

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self._create_dashboard_tab()
        self._create_optimizer_tab()
        self._create_monitoring_tab()
        self._create_context_tab()
        self._create_disk_predictor_tab()
        self._create_settings_tab()

    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self._on_closing)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="One-Click Boost", command=self._one_click_boost)
        tools_menu.add_separator()
        tools_menu.add_command(label="Analyze System", command=self._analyze_system)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_status_bar(self):
        """Create top status bar with key metrics."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        # CPU status
        ttk.Label(status_frame, text="CPU:").grid(row=0, column=0, padx=5)
        self.cpu_status_label = ttk.Label(status_frame, text="0%", font=('Arial', 10, 'bold'))
        self.cpu_status_label.grid(row=0, column=1, padx=5)

        # Memory status
        ttk.Label(status_frame, text="Memory:").grid(row=0, column=2, padx=5)
        self.mem_status_label = ttk.Label(status_frame, text="0%", font=('Arial', 10, 'bold'))
        self.mem_status_label.grid(row=0, column=3, padx=5)

        # Disk status
        ttk.Label(status_frame, text="Disk:").grid(row=0, column=4, padx=5)
        self.disk_status_label = ttk.Label(status_frame, text="0%", font=('Arial', 10, 'bold'))
        self.disk_status_label.grid(row=0, column=5, padx=5)

        # Context status
        ttk.Label(status_frame, text="Context:").grid(row=0, column=6, padx=5)
        self.context_status_label = ttk.Label(status_frame, text="Unknown", font=('Arial', 10))
        self.context_status_label.grid(row=0, column=7, padx=5)

    def _create_dashboard_tab(self):
        """Create dashboard tab with overview."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dashboard")

        # Welcome message
        welcome_frame = ttk.LabelFrame(tab, text="Welcome", padding=10)
        welcome_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            welcome_frame,
            text="Ultimate System Optimizer",
            font=('Arial', 16, 'bold')
        ).pack()

        ttk.Label(
            welcome_frame,
            text="AI-Powered Predictive System Management",
            font=('Arial', 10)
        ).pack()

        # Quick Actions
        quick_frame = ttk.LabelFrame(tab, text="Quick Actions", padding=10)
        quick_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Feature #15: One-Click Boost Button
        boost_btn = ttk.Button(
            quick_frame,
            text="⚡ ONE-CLICK BOOST",
            command=self._one_click_boost,
            style='Accent.TButton'
        )
        boost_btn.pack(pady=20)

        ttk.Label(
            quick_frame,
            text="Instantly optimize your system with one click",
            font=('Arial', 9)
        ).pack()

        # System info
        info_frame = ttk.LabelFrame(tab, text="System Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        cached_info = self.monitor.get_cached_info()

        info_text = f"""
CPU Cores: {cached_info['cpu_count_logical']} logical ({cached_info['cpu_count']} physical)
Total Memory: {cached_info['total_memory_gb']} GB
        """
        ttk.Label(info_frame, text=info_text.strip()).pack()

    def _create_optimizer_tab(self):
        """Create optimizer tab for Features #15 and #25."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Optimizer")

        # Instructions
        instr_frame = ttk.LabelFrame(tab, text="Transparent Optimization", padding=10)
        instr_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            instr_frame,
            text="Feature #25: See exactly what will be optimized before any changes are made."
        ).pack()

        # Analysis results
        self.analysis_frame = ttk.LabelFrame(tab, text="Analysis Results", padding=10)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.analysis_text = tk.Text(self.analysis_frame, height=15, width=80)
        self.analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.analysis_frame, command=self.analysis_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.analysis_text.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            btn_frame,
            text="Analyze System",
            command=self._analyze_system
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Run Optimization",
            command=self._run_optimization
        ).pack(side=tk.LEFT, padx=5)

    def _create_monitoring_tab(self):
        """Create monitoring tab with real-time graphs."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Performance Monitor")

        # CPU Monitor
        cpu_frame = ttk.LabelFrame(tab, text="CPU Usage", padding=10)
        cpu_frame.pack(fill=tk.X, padx=10, pady=5)

        self.cpu_canvas = tk.Canvas(cpu_frame, height=100, bg='white')
        self.cpu_canvas.pack(fill=tk.X)

        self.cpu_monitor_label = ttk.Label(cpu_frame, text="CPU: 0%", font=('Arial', 12))
        self.cpu_monitor_label.pack()

        # Memory Monitor
        mem_frame = ttk.LabelFrame(tab, text="Memory Usage", padding=10)
        mem_frame.pack(fill=tk.X, padx=10, pady=5)

        self.mem_canvas = tk.Canvas(mem_frame, height=100, bg='white')
        self.mem_canvas.pack(fill=tk.X)

        self.mem_monitor_label = ttk.Label(mem_frame, text="Memory: 0%", font=('Arial', 12))
        self.mem_monitor_label.pack()

        # Disk Monitor
        disk_frame = ttk.LabelFrame(tab, text="Disk Usage", padding=10)
        disk_frame.pack(fill=tk.X, padx=10, pady=5)

        self.disk_monitor_label = ttk.Label(disk_frame, text="Disk: 0%", font=('Arial', 12))
        self.disk_monitor_label.pack()

    def _create_context_tab(self):
        """Create tab for Feature #14: Context-Aware Resource Allocation."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Context-Aware")

        # Info
        info_frame = ttk.LabelFrame(tab, text="Feature #14: Context-Aware Optimization", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            info_frame,
            text="Automatically detects what you're doing (gaming, work, creative) and optimizes accordingly."
        ).pack()

        # Current context
        context_frame = ttk.LabelFrame(tab, text="Current Context", padding=10)
        context_frame.pack(fill=tk.X, padx=10, pady=10)

        self.context_label = ttk.Label(
            context_frame,
            text="Detecting...",
            font=('Arial', 14, 'bold')
        )
        self.context_label.pack(pady=10)

        # Suggestions
        suggestions_frame = ttk.LabelFrame(tab, text="Optimization Suggestions", padding=10)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.suggestions_text = tk.Text(suggestions_frame, height=10, width=80)
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)

        # Button
        ttk.Button(
            tab,
            text="Apply Context Optimizations",
            command=self._apply_context_optimizations
        ).pack(pady=10)

    def _create_disk_predictor_tab(self):
        """Create tab for Feature #6: Predictive Disk Space Manager."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Disk Predictor")

        # Info
        info_frame = ttk.LabelFrame(tab, text="Feature #6: Predictive Disk Space Manager", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            info_frame,
            text="Predicts when you'll run out of disk space based on usage trends."
        ).pack()

        # Prediction results
        pred_frame = ttk.LabelFrame(tab, text="Prediction Results", padding=10)
        pred_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.prediction_text = tk.Text(pred_frame, height=15, width=80)
        self.prediction_text.pack(fill=tk.BOTH, expand=True)

        # Button
        ttk.Button(
            tab,
            text="Run Prediction Analysis",
            command=self._predict_disk_space
        ).pack(pady=10)

    def _create_settings_tab(self):
        """Create settings tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")

        settings_frame = ttk.LabelFrame(tab, text="Configuration", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Monitoring interval
        ttk.Label(settings_frame, text="Monitoring Interval (seconds):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.DoubleVar(value=self.config.get('monitoring_interval', 2.0))
        ttk.Spinbox(
            settings_frame,
            from_=1.0,
            to=10.0,
            increment=0.5,
            textvariable=self.interval_var,
            width=10
        ).grid(row=0, column=1, sticky=tk.W, pady=5)

        # Context-aware enable
        self.context_aware_var = tk.BooleanVar(value=self.config.get('enable_context_aware', True))
        ttk.Checkbutton(
            settings_frame,
            text="Enable Context-Aware Optimization",
            variable=self.context_aware_var
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Save button
        ttk.Button(
            settings_frame,
            text="Save Settings",
            command=self._save_settings
        ).grid(row=10, column=0, columnspan=2, pady=20)

    def _schedule_update(self):
        """Schedule GUI updates (non-blocking)."""
        self._update_gui()
        self.root.after(500, self._schedule_update)  # Update every 500ms

    def _update_gui(self):
        """Update GUI with latest metrics."""
        # Get latest metrics
        metrics = self.monitor.get_latest_metrics()

        if metrics:
            # Update status bar
            self.cpu_status_label.config(text=f"{metrics['cpu_percent']}%")
            self.mem_status_label.config(text=f"{metrics['memory_percent']}%")
            self.disk_status_label.config(text=f"{metrics['disk_percent']}%")

            # Update monitoring tab
            self.cpu_monitor_label.config(text=f"CPU: {metrics['cpu_percent']}%")
            self.mem_monitor_label.config(text=f"Memory: {metrics['memory_percent']}% ({metrics['memory_used_gb']}GB / {self.monitor.cache['total_memory_gb']}GB)")
            self.disk_monitor_label.config(text=f"Disk: {metrics['disk_percent']}% ({metrics['disk_free_gb']}GB free)")

            # Update graphs
            self._update_graphs()

        # Update context
        if self.config.get('enable_context_aware', True):
            context = self.context_manager.detect_context()
            self.context_status_label.config(text=context.value.capitalize())

    def _update_graphs(self):
        """Update performance graphs."""
        history = self.monitor.get_history()

        # Update CPU graph
        self._draw_graph(self.cpu_canvas, history['cpu'])

        # Update memory graph
        self._draw_graph(self.mem_canvas, history['memory'])

    def _draw_graph(self, canvas, history):
        """Draw line graph on canvas."""
        canvas.delete("all")

        if len(history) < 2:
            return

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Draw line graph
        points = []
        step = width / len(history)
        max_val = max(history) if max(history) > 0 else 100

        for i, val in enumerate(history):
            x = i * step
            y = height - (val / max_val * height * 0.9)
            points.extend([x, y])

        if len(points) >= 4:
            canvas.create_line(points, fill="#4CAF50", width=2, smooth=True)

    def _one_click_boost(self):
        """Feature #15: One-Click Boost."""
        if messagebox.askyesno("One-Click Boost", "Run quick system optimization?"):
            # Analyze first
            self.optimizer.analyze_system()

            # Show progress
            progress = tk.Toplevel(self.root)
            progress.title("Optimizing...")
            progress.geometry("400x150")

            ttk.Label(progress, text="Running One-Click Boost...", font=('Arial', 12)).pack(pady=20)
            progress_label = ttk.Label(progress, text="Starting...")
            progress_label.pack(pady=10)

            def update_progress(percent, message):
                progress_label.config(text=message)
                progress.update()

            self.optimizer.progress_callback = update_progress

            # Run optimization in background
            future = self.optimizer.one_click_boost()

            # Wait for completion (in real app, this should be non-blocking)
            try:
                result = future.result(timeout=60)
                progress.destroy()

                messagebox.showinfo(
                    "Optimization Complete",
                    f"Files deleted: {result['files_deleted']}\n"
                    f"Space freed: {result['space_freed_mb']:.2f} MB\n"
                    f"Errors: {len(result['errors'])}"
                )
            except Exception as e:
                progress.destroy()
                messagebox.showerror("Error", f"Optimization failed: {e}")

    def _analyze_system(self):
        """Analyze system and show results (Feature #25)."""
        analysis = self.optimizer.analyze_system()

        # Display results
        self.analysis_text.delete(1.0, tk.END)

        self.analysis_text.insert(tk.END, "=== TRANSPARENT OPTIMIZATION ANALYSIS ===\n\n")
        self.analysis_text.insert(tk.END, f"Total Files: {analysis['total_files']}\n")
        self.analysis_text.insert(tk.END, f"Total Size: {analysis['total_size_mb']:.2f} MB\n\n")

        self.analysis_text.insert(tk.END, "=== CATEGORIES ===\n\n")

        for category, info in analysis['categories'].items():
            self.analysis_text.insert(tk.END, f"{category}:\n")
            self.analysis_text.insert(tk.END, f"  Files: {info['count']}\n")
            self.analysis_text.insert(tk.END, f"  Size: {info['total_size']/(1024**2):.2f} MB\n\n")

        messagebox.showinfo("Analysis Complete", f"Found {analysis['total_files']} files to clean ({analysis['total_size_mb']:.2f} MB)")

    def _run_optimization(self):
        """Run optimization based on analysis."""
        if messagebox.askyesno("Run Optimization", "Proceed with optimization?"):
            future = self.optimizer.optimize_async()

            try:
                result = future.result(timeout=60)
                messagebox.showinfo(
                    "Optimization Complete",
                    f"Files deleted: {result['files_deleted']}\n"
                    f"Space freed: {result['space_freed_mb']:.2f} MB"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Optimization failed: {e}")

    def _apply_context_optimizations(self):
        """Apply context-aware optimizations."""
        context = self.context_manager.detect_context()

        self.context_label.config(text=f"Context: {context.value.capitalize()}")

        result = self.context_manager.optimize_for_context(context)
        suggestions = self.context_manager.get_optimization_suggestions(context)

        # Display suggestions
        self.suggestions_text.delete(1.0, tk.END)
        self.suggestions_text.insert(tk.END, f"=== OPTIMIZATIONS FOR {context.value.upper()} MODE ===\n\n")

        for key, value in result.items():
            self.suggestions_text.insert(tk.END, f"{key}: {value}\n")

        self.suggestions_text.insert(tk.END, "\n=== SUGGESTIONS ===\n\n")

        for i, suggestion in enumerate(suggestions, 1):
            self.suggestions_text.insert(tk.END, f"{i}. {suggestion}\n")

        messagebox.showinfo("Context Optimization", f"Applied {context.value} mode optimizations")

    def _predict_disk_space(self):
        """Run disk space prediction."""
        prediction = self.disk_predictor.predict_space_exhaustion()

        self.prediction_text.delete(1.0, tk.END)

        self.prediction_text.insert(tk.END, "=== DISK SPACE PREDICTION ===\n\n")

        if not prediction['prediction_available']:
            self.prediction_text.insert(tk.END, f"Reason: {prediction['reason']}\n")
            self.prediction_text.insert(tk.END, f"Days of data: {prediction['days_of_data']}\n")
        else:
            if prediction['disk_growing']:
                self.prediction_text.insert(tk.END, f"Days until full: {prediction['days_until_full']:.1f}\n")
                self.prediction_text.insert(tk.END, f"Growth rate: {prediction['growth_rate_gb_per_day']:.3f} GB/day\n")
                self.prediction_text.insert(tk.END, f"Current free: {prediction['current_free_gb']:.2f} GB\n")
                self.prediction_text.insert(tk.END, f"Warning level: {prediction['warning_level']}\n\n")

                self.prediction_text.insert(tk.END, f"Recommendation: {prediction['recommendation']}\n\n")

                if prediction.get('fastest_growing_folders'):
                    self.prediction_text.insert(tk.END, "=== FASTEST GROWING FOLDERS ===\n\n")
                    for folder in prediction['fastest_growing_folders']:
                        self.prediction_text.insert(tk.END, f"{folder['path']}: {folder['size_gb']:.2f} GB\n")
            else:
                self.prediction_text.insert(tk.END, prediction['message'])

        messagebox.showinfo("Prediction Complete", "Disk space analysis complete")

    def _save_settings(self):
        """Save settings to configuration."""
        self.config.set('monitoring_interval', self.interval_var.get())
        self.config.set('enable_context_aware', self.context_aware_var.get())

        messagebox.showinfo("Settings Saved", "Configuration has been saved")

        # Restart monitoring with new interval
        self.monitor.stop_monitoring()
        self.monitor.update_interval = self.interval_var.get()
        self.monitor.start_monitoring()

    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Ultimate System Optimizer",
            "Ultimate System Optimizer v1.0\n\n"
            "AI-Powered Predictive System Management\n\n"
            "Features:\n"
            "• Feature #15: One-Click Boost\n"
            "• Feature #25: Transparent Optimization\n"
            "• Feature #14: Context-Aware Resource Allocation\n"
            "• Feature #6: Predictive Disk Space Manager\n\n"
            "Built with Python and tkinter"
        )

    def _on_closing(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Stop monitoring
            self.monitor.stop_monitoring()

            # Cleanup resources
            self.resource_manager.cleanup()

            # Close window
            self.root.destroy()

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
