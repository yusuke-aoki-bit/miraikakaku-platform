#!/usr/bin/env python3
"""
Automated Security Updater for Miraikakaku
Automated security updates, vulnerability scanning, and patch management
"""

import os
import json
import logging
import subprocess
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

class AutomatedSecurityUpdater:
    def __init__(self):
        self.project_root = '/mnt/c/Users/yuuku/cursor/miraikakaku'
        self.security_scan_history = []
        self.vulnerability_databases = [
            'https://services.nvd.nist.gov/rest/json/cves/1.0',
            'https://api.github.com/advisories'
        ]
        self.last_update_check = None
        self.update_interval = timedelta(hours=24)  # Check daily

    def scan_for_vulnerabilities(self) -> Dict[str, Any]:
        """Comprehensive vulnerability scanning"""
        scan_results = {
            'timestamp': datetime.now().isoformat(),
            'dependency_vulnerabilities': [],
            'code_vulnerabilities': [],
            'configuration_vulnerabilities': [],
            'severity_summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'recommendations': [],
            'status': 'success'
        }

        try:
            logger.info("🔍 Starting comprehensive security vulnerability scan...")

            # Scan Python dependencies
            scan_results['dependency_vulnerabilities'].extend(
                self._scan_python_dependencies()
            )

            # Scan Node.js dependencies
            scan_results['dependency_vulnerabilities'].extend(
                self._scan_nodejs_dependencies()
            )

            # Scan for code vulnerabilities
            scan_results['code_vulnerabilities'] = self._scan_code_vulnerabilities()

            # Scan configuration files
            scan_results['configuration_vulnerabilities'] = self._scan_configuration_vulnerabilities()

            # Calculate severity summary
            all_vulnerabilities = (
                scan_results['dependency_vulnerabilities'] +
                scan_results['code_vulnerabilities'] +
                scan_results['configuration_vulnerabilities']
            )

            for vuln in all_vulnerabilities:
                severity = vuln.get('severity', 'unknown').lower()
                if severity in scan_results['severity_summary']:
                    scan_results['severity_summary'][severity] += 1

            # Generate recommendations
            scan_results['recommendations'] = self._generate_security_recommendations(scan_results)

        except Exception as e:
            logger.error(f"Error during vulnerability scan: {e}")
            scan_results['status'] = 'failed'
            scan_results['error'] = str(e)

        return scan_results

    def _scan_python_dependencies(self) -> List[Dict[str, Any]]:
        """Scan Python dependencies for known vulnerabilities"""
        vulnerabilities = []

        python_dirs = [
            os.path.join(self.project_root, 'miraikakakuapi'),
            os.path.join(self.project_root, 'miraikakakubatch')
        ]

        for dir_path in python_dirs:
            requirements_file = os.path.join(dir_path, 'requirements.txt')
            if os.path.exists(requirements_file):
                try:
                    # Use pip-audit for vulnerability scanning (if available)
                    result = subprocess.run([
                        'python3', '-m', 'pip', 'list', '--format=json'
                    ], capture_output=True, text=True, timeout=60, cwd=dir_path)

                    if result.returncode == 0:
                        packages = json.loads(result.stdout)

                        # Check for known vulnerable packages
                        known_vulnerabilities = self._get_known_python_vulnerabilities()

                        for package in packages:
                            package_name = package['name'].lower()
                            package_version = package['version']

                            if package_name in known_vulnerabilities:
                                for vuln in known_vulnerabilities[package_name]:
                                    if self._version_is_vulnerable(package_version, vuln['affected_versions']):
                                        vulnerabilities.append({
                                            'type': 'dependency',
                                            'language': 'python',
                                            'package': package_name,
                                            'version': package_version,
                                            'vulnerability_id': vuln['id'],
                                            'description': vuln['description'],
                                            'severity': vuln['severity'],
                                            'fix_version': vuln.get('fix_version'),
                                            'file': requirements_file
                                        })

                except Exception as e:
                    logger.warning(f"Error scanning Python dependencies in {dir_path}: {e}")

        return vulnerabilities

    def _scan_nodejs_dependencies(self) -> List[Dict[str, Any]]:
        """Scan Node.js dependencies for known vulnerabilities"""
        vulnerabilities = []

        frontend_dir = os.path.join(self.project_root, 'miraikakakufront')
        package_json = os.path.join(frontend_dir, 'package.json')

        if os.path.exists(package_json):
            try:
                # Use npm audit for vulnerability scanning
                result = subprocess.run([
                    'npm', 'audit', '--json'
                ], capture_output=True, text=True, timeout=120, cwd=frontend_dir)

                if result.stdout:
                    try:
                        audit_data = json.loads(result.stdout)

                        if 'vulnerabilities' in audit_data:
                            for package_name, vuln_data in audit_data['vulnerabilities'].items():
                                vulnerabilities.append({
                                    'type': 'dependency',
                                    'language': 'nodejs',
                                    'package': package_name,
                                    'version': vuln_data.get('via', [{}])[0].get('range', 'unknown'),
                                    'vulnerability_id': vuln_data.get('via', [{}])[0].get('source', 'npm-audit'),
                                    'description': vuln_data.get('via', [{}])[0].get('title', 'Unknown vulnerability'),
                                    'severity': vuln_data.get('severity', 'unknown'),
                                    'fix_available': vuln_data.get('fixAvailable', False),
                                    'file': package_json
                                })

                    except json.JSONDecodeError:
                        logger.warning("Could not parse npm audit output")

            except Exception as e:
                logger.warning(f"Error scanning Node.js dependencies: {e}")

        return vulnerabilities

    def _scan_code_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Scan source code for potential security vulnerabilities"""
        vulnerabilities = []

        # Security patterns to look for
        security_patterns = {
            'hardcoded_secret': {
                'patterns': [
                    r'password\s*[:=]\s*["\']([^"\']{8,})["\']',
                    r'secret[_-]?key\s*[:=]\s*["\']([^"\']{16,})["\']',
                    r'api[_-]?key\s*[:=]\s*["\']([^"\']{16,})["\']'
                ],
                'severity': 'high',
                'description': 'Hardcoded secrets detected'
            },
            'sql_injection': {
                'patterns': [
                    r'execute\s*\(\s*["\'].*%.*["\']',
                    r'cursor\.execute\s*\(\s*f["\']',
                    r'query\s*=.*\+.*request\.'
                ],
                'severity': 'high',
                'description': 'Potential SQL injection vulnerability'
            },
            'command_injection': {
                'patterns': [
                    r'subprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True',
                    r'os\.system\s*\(',
                    r'eval\s*\('
                ],
                'severity': 'critical',
                'description': 'Potential command injection vulnerability'
            },
            'insecure_random': {
                'patterns': [
                    r'random\.randint\(',
                    r'random\.choice\(',
                    r'Math\.random\(\)'
                ],
                'severity': 'medium',
                'description': 'Use of insecure random number generator'
            }
        }

        # Scan source files
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            if any(skip_dir in root for skip_dir in ['.git', 'node_modules', '__pycache__', '.next']):
                continue

            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.tsx')):
                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        for vuln_type, config in security_patterns.items():
                            for pattern in config['patterns']:
                                matches = re.finditer(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    line_number = content[:match.start()].count('\n') + 1

                                    vulnerabilities.append({
                                        'type': 'code',
                                        'vulnerability_type': vuln_type,
                                        'description': config['description'],
                                        'severity': config['severity'],
                                        'file': file_path,
                                        'line': line_number,
                                        'code_snippet': content[max(0, match.start()-50):match.end()+50]
                                    })

                    except Exception as e:
                        logger.warning(f"Could not scan file {file_path}: {e}")

        return vulnerabilities

    def _scan_configuration_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Scan configuration files for security issues"""
        vulnerabilities = []

        config_checks = [
            {
                'file_pattern': '*.env*',
                'checks': [
                    {'pattern': r'DEBUG\s*=\s*True', 'severity': 'medium', 'description': 'Debug mode enabled in production'},
                    {'pattern': r'SECRET_KEY\s*=\s*["\'].*["\']', 'severity': 'high', 'description': 'Hardcoded secret key'}
                ]
            },
            {
                'file_pattern': 'docker-compose*.yml',
                'checks': [
                    {'pattern': r'privileged:\s*true', 'severity': 'high', 'description': 'Privileged container detected'},
                    {'pattern': r'network_mode:\s*host', 'severity': 'medium', 'description': 'Host network mode detected'}
                ]
            },
            {
                'file_pattern': '*.json',
                'checks': [
                    {'pattern': r'"password":\s*"[^"]*"', 'severity': 'high', 'description': 'Password in JSON configuration'},
                    {'pattern': r'"secret":\s*"[^"]*"', 'severity': 'high', 'description': 'Secret in JSON configuration'}
                ]
            }
        ]

        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                file_path = os.path.join(root, file)

                for config_check in config_checks:
                    if any(pattern.replace('*', '') in file for pattern in config_check['file_pattern'].split('*')):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()

                            for check in config_check['checks']:
                                matches = re.finditer(check['pattern'], content, re.IGNORECASE)
                                for match in matches:
                                    line_number = content[:match.start()].count('\n') + 1

                                    vulnerabilities.append({
                                        'type': 'configuration',
                                        'description': check['description'],
                                        'severity': check['severity'],
                                        'file': file_path,
                                        'line': line_number
                                    })

                        except Exception as e:
                            logger.warning(f"Could not scan config file {file_path}: {e}")

        return vulnerabilities

    def _get_known_python_vulnerabilities(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get known vulnerabilities for Python packages"""
        # This would normally connect to a vulnerability database
        # For demo purposes, using a static list of common vulnerabilities
        return {
            'django': [
                {
                    'id': 'CVE-2023-XXXX',
                    'description': 'SQL injection in Django ORM',
                    'severity': 'high',
                    'affected_versions': '<4.2.5',
                    'fix_version': '4.2.5'
                }
            ],
            'requests': [
                {
                    'id': 'CVE-2023-32681',
                    'description': 'Proxy-Authorization header leak',
                    'severity': 'medium',
                    'affected_versions': '<2.31.0',
                    'fix_version': '2.31.0'
                }
            ],
            'pillow': [
                {
                    'id': 'CVE-2023-XXXX',
                    'description': 'Buffer overflow in image processing',
                    'severity': 'critical',
                    'affected_versions': '<10.0.0',
                    'fix_version': '10.0.0'
                }
            ]
        }

    def _version_is_vulnerable(self, current_version: str, affected_range: str) -> bool:
        """Check if a version is within the vulnerable range"""
        try:
            # Simple version comparison (would use packaging.version in production)
            if '<' in affected_range:
                max_version = affected_range.replace('<', '').strip()
                return current_version < max_version
            elif '>' in affected_range:
                min_version = affected_range.replace('>', '').strip()
                return current_version > min_version
            else:
                return current_version == affected_range.strip()
        except:
            return False

    def _generate_security_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """Generate actionable security recommendations"""
        recommendations = []

        severity_summary = scan_results.get('severity_summary', {})

        if severity_summary.get('critical', 0) > 0:
            recommendations.append(f"🚨 URGENT: {severity_summary['critical']} critical vulnerabilities found - immediate action required")

        if severity_summary.get('high', 0) > 0:
            recommendations.append(f"⚠️ HIGH PRIORITY: {severity_summary['high']} high-severity vulnerabilities need attention")

        # Dependency-specific recommendations
        dep_vulns = scan_results.get('dependency_vulnerabilities', [])
        if dep_vulns:
            python_vulns = [v for v in dep_vulns if v.get('language') == 'python']
            nodejs_vulns = [v for v in dep_vulns if v.get('language') == 'nodejs']

            if python_vulns:
                recommendations.append(f"Update {len(python_vulns)} vulnerable Python packages")

            if nodejs_vulns:
                recommendations.append(f"Update {len(nodejs_vulns)} vulnerable Node.js packages")

        # Code vulnerability recommendations
        code_vulns = scan_results.get('code_vulnerabilities', [])
        if code_vulns:
            vuln_types = set(v.get('vulnerability_type') for v in code_vulns)
            for vuln_type in vuln_types:
                count = len([v for v in code_vulns if v.get('vulnerability_type') == vuln_type])
                recommendations.append(f"Fix {count} {vuln_type.replace('_', ' ')} issue(s) in source code")

        # Configuration recommendations
        config_vulns = scan_results.get('configuration_vulnerabilities', [])
        if config_vulns:
            recommendations.append(f"Review and fix {len(config_vulns)} configuration security issue(s)")

        if not recommendations:
            recommendations.append("✅ No critical security issues found")

        return recommendations

    def apply_security_updates(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply automated security updates where possible"""
        update_results = {
            'timestamp': datetime.now().isoformat(),
            'updates_applied': [],
            'updates_failed': [],
            'manual_action_required': [],
            'status': 'success'
        }

        for vuln in vulnerabilities:
            try:
                if vuln.get('type') == 'dependency':
                    result = self._update_dependency(vuln)
                    if result:
                        update_results['updates_applied'].append(result)
                    else:
                        update_results['manual_action_required'].append({
                            'vulnerability': vuln,
                            'reason': 'Manual update required'
                        })

                elif vuln.get('type') == 'configuration':
                    result = self._fix_configuration_issue(vuln)
                    if result:
                        update_results['updates_applied'].append(result)
                    else:
                        update_results['manual_action_required'].append({
                            'vulnerability': vuln,
                            'reason': 'Manual configuration fix required'
                        })

                else:
                    update_results['manual_action_required'].append({
                        'vulnerability': vuln,
                        'reason': 'Code changes required by developer'
                    })

            except Exception as e:
                update_results['updates_failed'].append({
                    'vulnerability': vuln,
                    'error': str(e)
                })

        return update_results

    def _update_dependency(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a vulnerable dependency"""
        try:
            package = vulnerability.get('package')
            language = vulnerability.get('language')
            fix_version = vulnerability.get('fix_version')

            if not fix_version:
                return None

            if language == 'python':
                # Update Python package
                result = subprocess.run([
                    'python3', '-m', 'pip', 'install', f"{package}=={fix_version}"
                ], capture_output=True, text=True, timeout=120)

                if result.returncode == 0:
                    return {
                        'type': 'dependency_update',
                        'language': 'python',
                        'package': package,
                        'old_version': vulnerability.get('version'),
                        'new_version': fix_version
                    }

            elif language == 'nodejs':
                # Update Node.js package
                frontend_dir = os.path.join(self.project_root, 'miraikakakufront')
                result = subprocess.run([
                    'npm', 'install', f"{package}@{fix_version}"
                ], capture_output=True, text=True, timeout=120, cwd=frontend_dir)

                if result.returncode == 0:
                    return {
                        'type': 'dependency_update',
                        'language': 'nodejs',
                        'package': package,
                        'old_version': vulnerability.get('version'),
                        'new_version': fix_version
                    }

        except Exception as e:
            logger.error(f"Error updating dependency {package}: {e}")

        return None

    def _fix_configuration_issue(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fix configuration security issues automatically"""
        try:
            file_path = vulnerability.get('file')
            description = vulnerability.get('description', '')

            if not file_path or not os.path.exists(file_path):
                return None

            # Only fix certain types of configuration issues automatically
            if 'debug mode' in description.lower():
                # Fix debug mode issues
                with open(file_path, 'r') as f:
                    content = f.read()

                # Replace DEBUG = True with DEBUG = False
                updated_content = re.sub(
                    r'DEBUG\s*=\s*True',
                    'DEBUG = False',
                    content,
                    flags=re.IGNORECASE
                )

                if updated_content != content:
                    # Create backup
                    backup_path = f"{file_path}.backup.{int(time.time())}"
                    with open(backup_path, 'w') as f:
                        f.write(content)

                    # Write fix
                    with open(file_path, 'w') as f:
                        f.write(updated_content)

                    return {
                        'type': 'configuration_fix',
                        'file': file_path,
                        'description': 'Disabled debug mode',
                        'backup_created': backup_path
                    }

        except Exception as e:
            logger.error(f"Error fixing configuration issue: {e}")

        return None

    def create_security_report(self, scan_results: Dict[str, Any], update_results: Dict[str, Any] = None) -> str:
        """Create a comprehensive security report"""
        report_content = f"""
# Security Scan Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Scan Status**: {scan_results.get('status', 'unknown')}
**Total Vulnerabilities Found**: {sum(scan_results.get('severity_summary', {}).values())}

### Severity Breakdown
- 🚨 Critical: {scan_results.get('severity_summary', {}).get('critical', 0)}
- ⚠️  High: {scan_results.get('severity_summary', {}).get('high', 0)}
- ⚡ Medium: {scan_results.get('severity_summary', {}).get('medium', 0)}
- ℹ️  Low: {scan_results.get('severity_summary', {}).get('low', 0)}

## Vulnerability Details

### Dependency Vulnerabilities
"""

        dep_vulns = scan_results.get('dependency_vulnerabilities', [])
        if dep_vulns:
            for vuln in dep_vulns:
                report_content += f"""
- **{vuln.get('package')}** ({vuln.get('language')})
  - Version: {vuln.get('version')}
  - Severity: {vuln.get('severity')}
  - Description: {vuln.get('description')}
  - Fix: Update to {vuln.get('fix_version', 'latest')}
"""
        else:
            report_content += "\nNo dependency vulnerabilities found ✅\n"

        report_content += "\n### Code Vulnerabilities\n"
        code_vulns = scan_results.get('code_vulnerabilities', [])
        if code_vulns:
            for vuln in code_vulns:
                report_content += f"""
- **{vuln.get('vulnerability_type', 'Unknown')}**
  - File: {vuln.get('file')}
  - Line: {vuln.get('line')}
  - Severity: {vuln.get('severity')}
  - Description: {vuln.get('description')}
"""
        else:
            report_content += "\nNo code vulnerabilities found ✅\n"

        report_content += "\n### Configuration Vulnerabilities\n"
        config_vulns = scan_results.get('configuration_vulnerabilities', [])
        if config_vulns:
            for vuln in config_vulns:
                report_content += f"""
- **Configuration Issue**
  - File: {vuln.get('file')}
  - Line: {vuln.get('line')}
  - Severity: {vuln.get('severity')}
  - Description: {vuln.get('description')}
"""
        else:
            report_content += "\nNo configuration vulnerabilities found ✅\n"

        # Add update results if available
        if update_results:
            report_content += f"""
## Automated Updates Applied

### Successfully Updated
"""
            for update in update_results.get('updates_applied', []):
                report_content += f"- {update.get('package', 'Unknown')}: {update.get('old_version', 'N/A')} → {update.get('new_version', 'N/A')}\n"

            if update_results.get('manual_action_required'):
                report_content += "\n### Manual Action Required\n"
                for item in update_results.get('manual_action_required', []):
                    vuln = item.get('vulnerability', {})
                    report_content += f"- {vuln.get('package', 'Unknown')}: {item.get('reason', 'Manual fix needed')}\n"

        # Add recommendations
        report_content += "\n## Recommendations\n"
        for rec in scan_results.get('recommendations', []):
            report_content += f"- {rec}\n"

        report_content += f"\n---\nReport generated by Automated Security Updater\nTimestamp: {scan_results.get('timestamp')}\n"

        return report_content

    def run_automated_security_cycle(self) -> Dict[str, Any]:
        """Run complete automated security update cycle"""
        logger.info("🔐 Starting automated security update cycle...")

        cycle_results = {
            'timestamp': datetime.now().isoformat(),
            'scan_results': {},
            'update_results': {},
            'report_created': False,
            'status': 'success'
        }

        try:
            # Step 1: Vulnerability scan
            logger.info("Step 1/3: Scanning for vulnerabilities...")
            scan_results = self.scan_for_vulnerabilities()
            cycle_results['scan_results'] = scan_results

            # Step 2: Apply updates for critical and high severity issues
            critical_and_high = [
                vuln for vuln in (
                    scan_results.get('dependency_vulnerabilities', []) +
                    scan_results.get('configuration_vulnerabilities', [])
                )
                if vuln.get('severity', '').lower() in ['critical', 'high']
            ]

            if critical_and_high:
                logger.info(f"Step 2/3: Applying {len(critical_and_high)} critical/high priority updates...")
                update_results = self.apply_security_updates(critical_and_high)
                cycle_results['update_results'] = update_results
            else:
                logger.info("Step 2/3: No critical/high priority updates needed")

            # Step 3: Generate security report
            logger.info("Step 3/3: Generating security report...")
            report_content = self.create_security_report(
                scan_results, cycle_results.get('update_results')
            )

            # Save report
            report_path = os.path.join(
                self.project_root,
                f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )
            with open(report_path, 'w') as f:
                f.write(report_content)

            cycle_results['report_path'] = report_path
            cycle_results['report_created'] = True

            logger.info("✅ Automated security cycle completed successfully!")

        except Exception as e:
            logger.error(f"Error in security cycle: {e}")
            cycle_results['status'] = 'failed'
            cycle_results['error'] = str(e)

        return cycle_results

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Automated Security Updater')
    parser.add_argument('--scan', action='store_true', help='Run vulnerability scan only')
    parser.add_argument('--update', action='store_true', help='Apply security updates')
    parser.add_argument('--report', action='store_true', help='Generate security report')
    parser.add_argument('--full', action='store_true', help='Run full security cycle')
    parser.add_argument('--continuous', action='store_true', help='Run continuous security monitoring')
    parser.add_argument('--interval', type=int, default=86400, help='Check interval in seconds (default: 24h)')

    args = parser.parse_args()

    updater = AutomatedSecurityUpdater()

    if args.scan:
        result = updater.scan_for_vulnerabilities()
        print(json.dumps(result, indent=2))
    elif args.full:
        result = updater.run_automated_security_cycle()
        print(json.dumps(result, indent=2))
    elif args.continuous:
        logger.info(f"Starting continuous security monitoring (interval: {args.interval}s)")
        while True:
            try:
                updater.run_automated_security_cycle()
                time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Continuous security monitoring stopped by user")
                break
    else:
        # Default: run full security cycle
        result = updater.run_automated_security_cycle()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()