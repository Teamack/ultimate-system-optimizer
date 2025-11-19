"""Resource management and cleanup."""

from typing import List, Any


class ResourceManager:
    """Context manager for safe resource handling."""

    def __init__(self):
        """Initialize resource manager."""
        self.resources: List[Any] = []

    def register(self, resource: Any):
        """Register resource for cleanup.

        Args:
            resource: Any object with close(), stop(), or cleanup() method
        """
        self.resources.append(resource)

    def cleanup(self):
        """Clean up all registered resources."""
        for resource in self.resources:
            try:
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'stop'):
                    resource.stop()
                elif hasattr(resource, 'stop_monitoring'):
                    resource.stop_monitoring()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
            except Exception as e:
                print(f"Error cleaning up resource: {e}")

        self.resources.clear()

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and cleanup resources."""
        self.cleanup()
        return False
