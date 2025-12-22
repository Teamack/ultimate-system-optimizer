import os
import shutil
import datetime

class SystemOptimizer:
    def __init__(self, backup_dir='backup'):
        self.backup_dir = backup_dir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def backup_system(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'system_backup_{timestamp}')
        os.makedirs(backup_path)
        # Simulate backing up system files
        print(f"Backing up system to {backup_path}")

    def restore_system(self, backup_name):
        backup_path = os.path.join(self.backup_dir, backup_name)
        if os.path.exists(backup_path):
            # Simulate restoring system files
            print(f"Restoring system from {backup_path}")
        else:
            print(f"Backup {backup_name} not found")

    def clean_system(self):
        # Simulate cleaning system files
        print("Cleaning system files")

    def optimize_system(self):
        self.backup_system()
        self.clean_system()
        print("System optimized")

if __name__ == "__main__":
    optimizer = SystemOptimizer()
    optimizer.optimize_system()
