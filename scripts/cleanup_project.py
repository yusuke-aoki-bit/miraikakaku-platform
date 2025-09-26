#!/usr/bin/env python3
"""
Project Cleanup Script
Removes duplicate files, old backups, and organizes the project structure
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Set
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = "/mnt/c/Users/yuuku/cursor/miraikakaku"

class ProjectCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.removed_files = []
        self.moved_files = []

    def clean_duplicate_files(self):
        """Remove duplicate and backup files"""
        logger.info("🧹 Cleaning duplicate and backup files...")

        # Patterns to remove
        patterns_to_remove = [
            "*.backup",
            "*.old",
            "*.temp",
            "*.tmp",
            "*_backup_*",
            "*_old_*",
            "Dockerfile.old",
            "package-lock.json.backup"
        ]

        removed_count = 0
        for pattern in patterns_to_remove:
            files = list(self.project_root.rglob(pattern))
            for file_path in files:
                try:
                    file_path.unlink()
                    self.removed_files.append(str(file_path))
                    removed_count += 1
                    logger.info(f"   Removed: {file_path}")
                except Exception as e:
                    logger.error(f"   Failed to remove {file_path}: {e}")

        logger.info(f"✅ Removed {removed_count} duplicate/backup files")

    def clean_excessive_python_scripts(self):
        """Clean up excessive automatically generated Python scripts"""
        logger.info("🐍 Cleaning excessive Python scripts...")

        # Scripts to keep (essential ones)
        essential_scripts = {
            'system_health_check.py',
            'check_data_status.py',
            'config/secrets_manager.py',
            'shared/database/connection_pool.py',
            'cleanup_project.py'
        }

        # Find Python scripts in root directory
        python_files = list(self.project_root.glob("*.py"))

        # Archive directory for removed scripts
        archive_dir = self.project_root / "archived_scripts"
        archive_dir.mkdir(exist_ok=True)

        moved_count = 0
        for py_file in python_files:
            relative_path = py_file.relative_to(self.project_root)

            # Skip essential scripts
            if str(relative_path) in essential_scripts:
                continue

            # Skip if it's a main entry point
            if py_file.name in ['main.py', 'app.py', '__init__.py']:
                continue

            # Move to archive
            try:
                archive_path = archive_dir / py_file.name
                if not archive_path.exists():
                    shutil.move(str(py_file), str(archive_path))
                    self.moved_files.append(f"{py_file} -> {archive_path}")
                    moved_count += 1
                    logger.info(f"   Archived: {py_file.name}")
                else:
                    # If archive already exists, remove the duplicate
                    py_file.unlink()
                    self.removed_files.append(str(py_file))
                    moved_count += 1
                    logger.info(f"   Removed duplicate: {py_file.name}")
            except Exception as e:
                logger.error(f"   Failed to archive {py_file}: {e}")

        logger.info(f"✅ Archived/removed {moved_count} Python scripts")

    def clean_log_files(self):
        """Clean up old log files"""
        logger.info("📄 Cleaning old log files...")

        log_patterns = ["*.log", "*.log.*"]
        removed_count = 0

        for pattern in log_patterns:
            log_files = list(self.project_root.rglob(pattern))
            for log_file in log_files:
                try:
                    # Keep recent logs (less than 7 days old)
                    if log_file.stat().st_mtime < (time.time() - 7 * 24 * 3600):
                        log_file.unlink()
                        self.removed_files.append(str(log_file))
                        removed_count += 1
                        logger.info(f"   Removed old log: {log_file}")
                except Exception as e:
                    logger.error(f"   Failed to remove {log_file}: {e}")

        logger.info(f"✅ Removed {removed_count} old log files")

    def clean_quality_reports(self):
        """Clean up duplicate quality reports"""
        logger.info("📊 Cleaning quality reports...")

        quality_reports = list(self.project_root.glob("quality_report_*.md"))
        if len(quality_reports) > 3:
            # Sort by modification time and keep only the 3 most recent
            quality_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            reports_to_remove = quality_reports[3:]

            for report in reports_to_remove:
                try:
                    report.unlink()
                    self.removed_files.append(str(report))
                    logger.info(f"   Removed old report: {report.name}")
                except Exception as e:
                    logger.error(f"   Failed to remove {report}: {e}")

        logger.info(f"✅ Cleaned up quality reports (kept 3 most recent)")

    def organize_documentation(self):
        """Organize documentation files"""
        logger.info("📚 Organizing documentation...")

        docs_dir = self.project_root / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Documentation files to move
        doc_patterns = [
            "*.md",
            "ARCHITECTURE*",
            "DEPLOYMENT*",
            "OPERATIONS*",
            "SECURITY*",
            "PHASE_*"
        ]

        moved_count = 0
        for pattern in doc_patterns:
            doc_files = list(self.project_root.glob(pattern))
            for doc_file in doc_files:
                # Skip README.md in root
                if doc_file.name == "README.md" and doc_file.parent == self.project_root:
                    continue

                try:
                    dest_path = docs_dir / doc_file.name
                    if not dest_path.exists():
                        shutil.move(str(doc_file), str(dest_path))
                        self.moved_files.append(f"{doc_file} -> {dest_path}")
                        moved_count += 1
                        logger.info(f"   Moved to docs: {doc_file.name}")
                except Exception as e:
                    logger.error(f"   Failed to move {doc_file}: {e}")

        logger.info(f"✅ Organized {moved_count} documentation files")

    def clean_dockerfile_duplicates(self):
        """Clean up duplicate Dockerfiles"""
        logger.info("🐳 Cleaning Dockerfile duplicates...")

        # Find all Dockerfiles
        dockerfiles = []
        for dockerfile in self.project_root.rglob("Dockerfile*"):
            if not dockerfile.is_file():
                continue
            dockerfiles.append(dockerfile)

        # Group by directory
        dockerfile_groups = {}
        for dockerfile in dockerfiles:
            parent = dockerfile.parent
            if parent not in dockerfile_groups:
                dockerfile_groups[parent] = []
            dockerfile_groups[parent].append(dockerfile)

        removed_count = 0
        for directory, files in dockerfile_groups.items():
            if len(files) > 2:  # Keep main Dockerfile and one backup max
                # Sort by name, keep Dockerfile and one other
                files.sort(key=lambda x: (x.name != "Dockerfile", x.name))
                files_to_remove = files[2:]  # Remove excess

                for dockerfile in files_to_remove:
                    try:
                        dockerfile.unlink()
                        self.removed_files.append(str(dockerfile))
                        removed_count += 1
                        logger.info(f"   Removed excess Dockerfile: {dockerfile}")
                    except Exception as e:
                        logger.error(f"   Failed to remove {dockerfile}: {e}")

        logger.info(f"✅ Cleaned up {removed_count} excess Dockerfiles")

    def generate_cleanup_report(self):
        """Generate a report of cleanup actions"""
        report = {
            'cleanup_date': datetime.now().isoformat(),
            'summary': {
                'files_removed': len(self.removed_files),
                'files_moved': len(self.moved_files)
            },
            'removed_files': self.removed_files,
            'moved_files': self.moved_files
        }

        report_path = self.project_root / "cleanup_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📋 Cleanup report saved to: {report_path}")
        return report

    def run_full_cleanup(self):
        """Run complete cleanup process"""
        logger.info("🚀 Starting full project cleanup...")

        try:
            self.clean_duplicate_files()
            self.clean_excessive_python_scripts()
            self.clean_log_files()
            self.clean_quality_reports()
            self.organize_documentation()
            self.clean_dockerfile_duplicates()

            report = self.generate_cleanup_report()

            logger.info("✨ Project cleanup completed successfully!")
            logger.info(f"   Files removed: {report['summary']['files_removed']}")
            logger.info(f"   Files moved: {report['summary']['files_moved']}")

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            raise

if __name__ == "__main__":
    import time
    from datetime import datetime

    cleaner = ProjectCleaner(PROJECT_ROOT)
    cleaner.run_full_cleanup()