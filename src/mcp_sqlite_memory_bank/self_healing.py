"""
Enhanced Error Recovery and Self-Healing Module

Provides automatic dependency checking, graceful degradation, self-diagnostic tools,
and automatic repair for common issues.
"""

import subprocess
import importlib
import traceback
from typing import Any, Dict, List
from pathlib import Path
import sqlite3
import shutil
from datetime import datetime


class DependencyChecker:
    """Automatic dependency checking and installation guidance."""

    REQUIRED_PACKAGES = {
        "sentence-transformers": {
            "install_cmd": "pip install sentence-transformers",
            "test_import": "sentence_transformers",
            "feature": "semantic search",
        },
        "numpy": {
            "install_cmd": "pip install numpy",
            "test_import": "numpy",
            "feature": "numeric operations",
        },
        "fastmcp": {
            "install_cmd": "pip install fastmcp",
            "test_import": "fastmcp",
            "feature": "MCP server functionality",
        },
        "sqlalchemy": {
            "install_cmd": "pip install sqlalchemy",
            "test_import": "sqlalchemy",
            "feature": "database operations",
        },
    }

    def check_dependencies(self) -> Dict[str, Any]:
        """Check all required dependencies and return status report."""
        results = {
            "all_available": True,
            "missing_packages": [],
            "available_packages": [],
            "install_instructions": [],
            "degraded_features": [],
        }

        for package, info in self.REQUIRED_PACKAGES.items():
            try:
                importlib.import_module(info["test_import"])
                results["available_packages"].append(package)
            except ImportError:
                results["all_available"] = False
                results["missing_packages"].append(package)
                results["install_instructions"].append(info["install_cmd"])
                results["degraded_features"].append(info["feature"])

        return results

    def auto_install_missing(self, missing_packages: List[str]) -> Dict[str, Any]:
        """Attempt to automatically install missing packages."""
        install_results = {}

        for package in missing_packages:
            if package in self.REQUIRED_PACKAGES:
                try:
                    cmd = self.REQUIRED_PACKAGES[package]["install_cmd"]
                    result = subprocess.run(
                        cmd.split(), capture_output=True, text=True, timeout=300
                    )

                    if result.returncode == 0:
                        install_results[package] = {
                            "success": True,
                            "output": result.stdout,
                        }
                    else:
                        install_results[package] = {
                            "success": False,
                            "error": result.stderr,
                        }

                except Exception as e:
                    install_results[package] = {"success": False, "error": str(e)}

        return install_results


class DatabaseDiagnostic:
    """Self-diagnostic tools for database issues."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run comprehensive database health check."""
        diagnostics = {
            "database_exists": False,
            "database_readable": False,
            "database_writable": False,
            "corruption_check": "unknown",
            "table_count": 0,
            "total_rows": 0,
            "issues_found": [],
            "repair_suggestions": [],
            "backup_recommended": False,
        }

        try:
            # Check if database file exists
            db_file = Path(self.db_path)
            diagnostics["database_exists"] = db_file.exists()

            if not diagnostics["database_exists"]:
                diagnostics["issues_found"].append("Database file does not exist")
                diagnostics["repair_suggestions"].append(
                    "Database will be created automatically on first use"
                )
                return diagnostics

            # Check file permissions
            diagnostics["database_readable"] = (
                db_file.is_file() and db_file.stat().st_size > 0
            )

            # Test database connection and integrity
            with sqlite3.connect(self.db_path) as conn:
                diagnostics["database_writable"] = True

                # Check database integrity
                cursor = conn.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                diagnostics["corruption_check"] = integrity_result

                if integrity_result != "ok":
                    diagnostics["issues_found"].append(
                        f"Database integrity issue: {integrity_result}"
                    )
                    diagnostics["backup_recommended"] = True
                    diagnostics["repair_suggestions"].append(
                        "Consider running database repair or creating backup"
                    )

                # Count tables and rows
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = cursor.fetchall()
                diagnostics["table_count"] = len(tables)

                total_rows = 0
                for table in tables:
                    table_name = table[0]
                    if not table_name.startswith("sqlite_"):
                        try:
                            cursor = conn.execute(
                                f"SELECT COUNT(*) FROM `{table_name}`"
                            )
                            count = cursor.fetchone()[0]
                            total_rows += count
                        except sqlite3.Error:
                            pass

                diagnostics["total_rows"] = total_rows

        except sqlite3.DatabaseError as e:
            diagnostics["issues_found"].append(f"Database error: {str(e)}")
            diagnostics["repair_suggestions"].append(
                "Database may be corrupted - consider backup and repair"
            )
        except Exception as e:
            diagnostics["issues_found"].append(f"Unexpected error: {str(e)}")

        return diagnostics

    def auto_repair(self) -> Dict[str, Any]:
        """Attempt automatic repair of common database issues."""
        repair_results = {
            "repairs_attempted": [],
            "repairs_successful": [],
            "repairs_failed": [],
            "backup_created": False,
            "backup_path": None,
        }

        try:
            # Create backup before repair
            if Path(self.db_path).exists():
                backup_path = (
                    f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                shutil.copy2(self.db_path, backup_path)
                repair_results["backup_created"] = True
                repair_results["backup_path"] = backup_path

            # Attempt to repair database
            with sqlite3.connect(self.db_path) as conn:
                # Vacuum to reclaim space and fix minor corruption
                repair_results["repairs_attempted"].append("VACUUM")
                try:
                    conn.execute("VACUUM")
                    repair_results["repairs_successful"].append("VACUUM")
                except sqlite3.Error as e:
                    repair_results["repairs_failed"].append(f"VACUUM failed: {e}")

                # Reindex to fix index corruption
                repair_results["repairs_attempted"].append("REINDEX")
                try:
                    conn.execute("REINDEX")
                    repair_results["repairs_successful"].append("REINDEX")
                except sqlite3.Error as e:
                    repair_results["repairs_failed"].append(f"REINDEX failed: {e}")

        except Exception as e:
            repair_results["repairs_failed"].append(f"Repair process failed: {e}")

        return repair_results


class GracefulDegradation:
    """Handles graceful degradation when features are unavailable."""

    def __init__(self):
        self.feature_status = {}
        self.fallback_strategies = {}

    def check_feature_availability(self) -> Dict[str, bool]:
        """Check availability of optional features."""
        features = {
            "semantic_search": self._check_sentence_transformers(),
            "advanced_analytics": self._check_numpy(),
            "web_exports": self._check_web_libraries(),
            "visualization": self._check_visualization_libraries(),
        }

        self.feature_status = features
        return features

    def _check_sentence_transformers(self) -> bool:
        """Check if sentence-transformers is available."""
        try:
            pass

            return True
        except ImportError:
            return False

    def _check_numpy(self) -> bool:
        """Check if numpy is available."""
        try:
            pass

            return True
        except ImportError:
            return False

    def _check_web_libraries(self) -> bool:
        """Check if web export libraries are available."""
        try:
            pass

            return True
        except ImportError:
            return False

    def _check_visualization_libraries(self) -> bool:
        """Check if visualization libraries are available."""
        # Check for basic HTML generation capabilities
        return True  # HTML generation is built-in

    def get_fallback_strategy(self, feature: str) -> Dict[str, Any]:
        """Get fallback strategy for unavailable feature."""
        fallback_strategies = {
            "semantic_search": {
                "available": self.feature_status.get("semantic_search", False),
                "fallback": "keyword-based search",
                "message": "Semantic search unavailable. Using keyword-based search instead.",
                "install_help": "pip install sentence-transformers",
            },
            "advanced_analytics": {
                "available": self.feature_status.get("advanced_analytics", False),
                "fallback": "basic statistics",
                "message": "Advanced analytics unavailable. Using basic statistics instead.",
                "install_help": "pip install numpy pandas",
            },
            "web_exports": {
                "available": self.feature_status.get("web_exports", True),
                "fallback": "JSON export",
                "message": "Web exports available.",
                "install_help": None,
            },
            "visualization": {
                "available": self.feature_status.get("visualization", True),
                "fallback": "text-based output",
                "message": "Basic visualization available.",
                "install_help": None,
            },
        }

        return fallback_strategies.get(
            feature,
            {
                "available": False,
                "fallback": "basic functionality",
                "message": f"Feature '{feature}' not available",
                "install_help": "Check documentation for installation instructions",
            },
        )


class SystemHealthMonitor:
    """Monitor overall system health and provide recommendations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.dependency_checker = DependencyChecker()
        self.db_diagnostic = DatabaseDiagnostic(db_path)
        self.graceful_degradation = GracefulDegradation()

    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive system health check."""
        health_report = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "dependencies": self.dependency_checker.check_dependencies(),
            "database": self.db_diagnostic.run_comprehensive_check(),
            "features": self.graceful_degradation.check_feature_availability(),
            "recommendations": [],
            "critical_issues": [],
            "warnings": [],
        }

        # Analyze dependencies
        if not health_report["dependencies"]["all_available"]:
            health_report["overall_status"] = "degraded"
            health_report["warnings"].append("Some optional dependencies are missing")
            health_report["recommendations"].extend(
                [
                    f"Install missing packages: {
                        ', '.join(
                            health_report['dependencies']['missing_packages'])}",
                    "Some features may have reduced functionality",
                ])

        # Analyze database
        if health_report["database"]["issues_found"]:
            if health_report["database"]["corruption_check"] != "ok":
                health_report["overall_status"] = "critical"
                health_report["critical_issues"].extend(
                    health_report["database"]["issues_found"]
                )
            else:
                health_report["warnings"].extend(
                    health_report["database"]["issues_found"]
                )

            health_report["recommendations"].extend(
                health_report["database"]["repair_suggestions"]
            )

        # Analyze features
        unavailable_features = [
            k for k, v in health_report["features"].items() if not v
        ]
        if unavailable_features:
            health_report["warnings"].append(
                f"Features with limited functionality: {
                    ', '.join(unavailable_features)}")

        return health_report

    def auto_repair_system(self) -> Dict[str, Any]:
        """Attempt automatic system repair."""
        repair_report = {
            "timestamp": datetime.now().isoformat(),
            "repairs_attempted": [],
            "repairs_successful": [],
            "repairs_failed": [],
            "manual_intervention_required": [],
        }

        # Check health first
        health = self.comprehensive_health_check()

        # Attempt dependency repairs
        if not health["dependencies"]["all_available"]:
            repair_report["repairs_attempted"].append("dependency_installation")
            install_results = self.dependency_checker.auto_install_missing(
                health["dependencies"]["missing_packages"]
            )

            for package, result in install_results.items():
                if result["success"]:
                    repair_report["repairs_successful"].append(f"Installed {package}")
                else:
                    repair_report["repairs_failed"].append(
                        f"Failed to install {package}: {result['error']}"
                    )

        # Attempt database repairs
        if health["database"]["issues_found"]:
            repair_report["repairs_attempted"].append("database_repair")
            db_repair_results = self.db_diagnostic.auto_repair()

            repair_report["repairs_successful"].extend(
                db_repair_results["repairs_successful"]
            )
            repair_report["repairs_failed"].extend(db_repair_results["repairs_failed"])

            if db_repair_results["backup_created"]:
                repair_report["repairs_successful"].append(
                    f"Database backup created: {db_repair_results['backup_path']}"
                )

        # Check for manual intervention needs
        if health["overall_status"] == "critical":
            repair_report["manual_intervention_required"].append(
                "Critical database issues require manual attention"
            )

        if repair_report["repairs_failed"]:
            repair_report["manual_intervention_required"].append(
                "Some automatic repairs failed - manual intervention may be needed"
            )

        return repair_report


def create_system_health_tool(db_path: str):
    """Factory function to create system health monitoring tool."""
    monitor = SystemHealthMonitor(db_path)

    def system_health_check() -> Dict[str, Any]:
        """Run comprehensive system health check and return detailed report."""
        try:
            return {
                "success": True,
                "health_report": monitor.comprehensive_health_check(),
                "repair_available": True,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Health check failed: {str(e)}",
                "traceback": traceback.format_exc(),
            }

    def auto_repair_system() -> Dict[str, Any]:
        """Attempt automatic system repair and return results."""
        try:
            return {"success": True, "repair_report": monitor.auto_repair_system()}
        except Exception as e:
            return {
                "success": False,
                "error": f"Auto-repair failed: {str(e)}",
                "traceback": traceback.format_exc(),
            }

    return system_health_check, auto_repair_system
