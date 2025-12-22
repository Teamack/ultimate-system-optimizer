import os
import shutil
import datetime

class TimeMachine:
    def __init__(self, backup_dir='backup'):
        self.backup_dir = backup_dir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'backup_{timestamp}')
        os.makedirs(backup_path)
        # Simulate creating a backup
        print(f"Creating backup at {backup_path}")

    def list_backups(self):
        backups = os.listdir(self.backup_dir)
        print("Available backups:")
        for backup in backups:
            print(backup)

    def restore_backup(self, backup_name):
        backup_path = os.path.join(self.backup_dir, backup_name)
        if os.path.exists(backup_path):
            # Simulate restoring from backup
            print(f"Restoring from backup {backup_path}")
        else:
            print(f"Backup {backup_name} not found")

if __name__ == "__main__":
    tm = TimeMachine()
    tm.create_backup()
    tm.list_backups()
    # Example restore
    # tm.restore_backup('backup_20231010120000')
