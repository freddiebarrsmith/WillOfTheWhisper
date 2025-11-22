"""
Performance monitoring and optimization system
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import deque
import psutil
import os


@dataclass
class PerformanceMetric:
    """Represents a performance metric"""
    name: str
    value: float
    timestamp: float
    unit: str = ""
    category: str = "general"


@dataclass
class PerformanceStats:
    """Performance statistics for a component"""
    component_name: str
    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=100))
    error_count: int = 0
    last_error: Optional[str] = None


class PerformanceMonitor:
    """Performance monitoring and optimization system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.stats: Dict[str, PerformanceStats] = {}
        self.metrics: List[PerformanceMetric] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Performance thresholds
        self.thresholds = {
            'audio_recording': 5.0,  # seconds
            'transcription': 10.0,   # seconds
            'text_processing': 1.0,  # seconds
            'system_integration': 2.0,  # seconds
            'memory_usage': 80.0,    # percentage
            'cpu_usage': 90.0,       # percentage
        }
        
        # Optimization settings
        self.optimization_enabled = True
        self.auto_optimize = True
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self) -> None:
        """Start performance monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        self.logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check performance thresholds
                self._check_thresholds()
                
                # Auto-optimize if enabled
                if self.auto_optimize:
                    self._auto_optimize()
                
                # Clean up old metrics
                self._cleanup_metrics()
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                time.sleep(5.0)
    
    def _collect_system_metrics(self) -> None:
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self._add_metric("cpu_usage", cpu_percent, "percent", "system")
            
            # Memory usage
            memory = psutil.virtual_memory()
            self._add_metric("memory_usage", memory.percent, "percent", "system")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self._add_metric("disk_usage", disk.percent, "percent", "system")
            
            # Process-specific metrics
            process = psutil.Process(os.getpid())
            self._add_metric("process_memory", process.memory_info().rss / 1024 / 1024, "MB", "process")
            self._add_metric("process_cpu", process.cpu_percent(), "percent", "process")
            
        except Exception as e:
            self.logger.debug(f"Failed to collect system metrics: {e}")
    
    def _add_metric(self, name: str, value: float, unit: str = "", category: str = "general") -> None:
        """Add a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=time.time(),
            unit=unit,
            category=category
        )
        
        self.metrics.append(metric)
        
        # Keep only recent metrics (last 1000)
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def _check_thresholds(self) -> None:
        """Check performance thresholds and log warnings"""
        for metric_name, threshold in self.thresholds.items():
            recent_metrics = [m for m in self.metrics[-10:] if m.name == metric_name]
            
            if recent_metrics:
                avg_value = sum(m.value for m in recent_metrics) / len(recent_metrics)
                
                if avg_value > threshold:
                    self.logger.warning(
                        f"Performance threshold exceeded: {metric_name} = {avg_value:.2f} "
                        f"(threshold: {threshold})"
                    )
    
    def _auto_optimize(self) -> None:
        """Automatically optimize performance"""
        try:
            # Check if optimization is needed
            recent_cpu = self._get_recent_average("cpu_usage")
            recent_memory = self._get_recent_average("memory_usage")
            
            if recent_cpu > 80 or recent_memory > 80:
                self.logger.info("High resource usage detected, applying optimizations")
                self._apply_optimizations()
                
        except Exception as e:
            self.logger.debug(f"Auto-optimization failed: {e}")
    
    def _get_recent_average(self, metric_name: str, count: int = 5) -> float:
        """Get average of recent metrics"""
        recent_metrics = [m for m in self.metrics[-count:] if m.name == metric_name]
        
        if not recent_metrics:
            return 0.0
        
        return sum(m.value for m in recent_metrics) / len(recent_metrics)
    
    def _apply_optimizations(self) -> None:
        """Apply performance optimizations"""
        try:
            # Clear old metrics to free memory
            if len(self.metrics) > 500:
                self.metrics = self.metrics[-250:]
            
            # Clear old stats
            for stats in self.stats.values():
                if len(stats.recent_times) > 50:
                    stats.recent_times = deque(list(stats.recent_times)[-25:], maxlen=50)
            
            # Force garbage collection
            import gc
            gc.collect()
            
            self.logger.info("Performance optimizations applied")
            
        except Exception as e:
            self.logger.debug(f"Optimization application failed: {e}")
    
    def _cleanup_metrics(self) -> None:
        """Clean up old metrics"""
        current_time = time.time()
        cutoff_time = current_time - 300  # Keep last 5 minutes
        
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
    
    def time_function(self, component_name: str):
        """Decorator to time function execution"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self._record_success(component_name, time.time() - start_time)
                    return result
                except Exception as e:
                    self._record_error(component_name, str(e))
                    raise
            return wrapper
        return decorator
    
    def _record_success(self, component_name: str, execution_time: float) -> None:
        """Record successful operation"""
        if component_name not in self.stats:
            self.stats[component_name] = PerformanceStats(component_name)
        
        stats = self.stats[component_name]
        stats.total_calls += 1
        stats.total_time += execution_time
        stats.min_time = min(stats.min_time, execution_time)
        stats.max_time = max(stats.max_time, execution_time)
        stats.avg_time = stats.total_time / stats.total_calls
        stats.recent_times.append(execution_time)
        
        # Add metric
        self._add_metric(f"{component_name}_time", execution_time, "seconds", "timing")
    
    def _record_error(self, component_name: str, error_message: str) -> None:
        """Record operation error"""
        if component_name not in self.stats:
            self.stats[component_name] = PerformanceStats(component_name)
        
        stats = self.stats[component_name]
        stats.error_count += 1
        stats.last_error = error_message
        
        # Add error metric
        self._add_metric(f"{component_name}_errors", 1, "count", "errors")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        report = {
            "timestamp": time.time(),
            "components": {},
            "system_metrics": {},
            "recommendations": []
        }
        
        # Component statistics
        for name, stats in self.stats.items():
            report["components"][name] = {
                "total_calls": stats.total_calls,
                "avg_time": stats.avg_time,
                "min_time": stats.min_time,
                "max_time": stats.max_time,
                "error_count": stats.error_count,
                "error_rate": stats.error_count / max(stats.total_calls, 1) * 100,
                "last_error": stats.last_error
            }
        
        # System metrics
        recent_metrics = self.metrics[-10:] if self.metrics else []
        for metric in recent_metrics:
            if metric.category == "system":
                report["system_metrics"][metric.name] = {
                    "value": metric.value,
                    "unit": metric.unit
                }
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check component performance
        for name, stats in self.stats.items():
            if stats.avg_time > self.thresholds.get(f"{name}_time", 5.0):
                recommendations.append(f"Consider optimizing {name} (avg: {stats.avg_time:.2f}s)")
            
            if stats.error_count > 0:
                error_rate = stats.error_count / max(stats.total_calls, 1) * 100
                if error_rate > 10:
                    recommendations.append(f"High error rate in {name}: {error_rate:.1f}%")
        
        # Check system metrics
        recent_cpu = self._get_recent_average("cpu_usage")
        if recent_cpu > 80:
            recommendations.append(f"High CPU usage: {recent_cpu:.1f}%")
        
        recent_memory = self._get_recent_average("memory_usage")
        if recent_memory > 80:
            recommendations.append(f"High memory usage: {recent_memory:.1f}%")
        
        # Check transcription performance
        transcription_time = self._get_recent_average("transcription_time")
        if transcription_time > 10:
            recommendations.append(f"Slow transcription: {transcription_time:.2f}s - consider using smaller Whisper model")
        
        return recommendations
    
    def optimize_for_speed(self) -> Dict[str, Any]:
        """Optimize system for speed"""
        optimizations = {
            "applied": [],
            "skipped": [],
            "errors": []
        }
        
        try:
            # Reduce Whisper model size if transcription is slow
            transcription_time = self._get_recent_average("transcription_time")
            if transcription_time > 5.0:
                optimizations["applied"].append("Consider using smaller Whisper model (tiny/base)")
            else:
                optimizations["skipped"].append("Transcription speed is acceptable")
            
            # Reduce audio preprocessing if CPU is high
            cpu_usage = self._get_recent_average("cpu_usage")
            if cpu_usage > 70:
                optimizations["applied"].append("Reduce audio preprocessing complexity")
            else:
                optimizations["skipped"].append("CPU usage is acceptable")
            
            # Clear caches if memory is high
            memory_usage = self._get_recent_average("memory_usage")
            if memory_usage > 75:
                optimizations["applied"].append("Clear caches and old metrics")
                self._apply_optimizations()
            else:
                optimizations["skipped"].append("Memory usage is acceptable")
            
        except Exception as e:
            optimizations["errors"].append(str(e))
        
        return optimizations
    
    def get_component_stats(self, component_name: str) -> Optional[PerformanceStats]:
        """Get statistics for a specific component"""
        return self.stats.get(component_name)
    
    def reset_stats(self, component_name: Optional[str] = None) -> None:
        """Reset statistics for a component or all components"""
        if component_name:
            if component_name in self.stats:
                del self.stats[component_name]
                self.logger.info(f"Reset stats for {component_name}")
        else:
            self.stats.clear()
            self.metrics.clear()
            self.logger.info("Reset all performance statistics")
    
    def export_stats(self, filename: str) -> bool:
        """Export performance statistics to file"""
        try:
            import json
            
            report = self.get_performance_report()
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Performance stats exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export stats: {e}")
            return False
