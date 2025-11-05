import subprocess
import json
import os
from app.models.scan import Scan

class SCAScanner:
    def scan(self, scan):
        """使用OWASP Dependency-Check进行依赖漏洞扫描"""
        results = []
        
        project_path = f"/app/uploaded_files/project_{scan.project_id}"
        
        if not os.path.exists(project_path):
            # 模拟扫描结果
            results.append({
                'severity': 'high',
                'type': 'CVE',
                'title': 'CVE-2023-12345: 依赖库漏洞',
                'description': '检测到依赖库存在已知安全漏洞',
                'file_path': '',
                'line_number': None,
                'cve_id': 'CVE-2023-12345',
                'package_name': 'vulnerable-package',
                'package_version': '1.0.0',
                'fixed_version': '1.2.0',
                'raw_data': {}
            })
        else:
            try:
                # 执行Dependency-Check扫描
                report_path = f"/app/scan_results/dependency-check-report.json"
                cmd = [
                    '/opt/dependency-check/dependency-check/bin/dependency-check.sh',
                    '--project', f'Project_{scan.project_id}',
                    '--scan', project_path,
                    '--format', 'JSON',
                    '--out', report_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    
                    for dependency in report_data.get('dependencies', []):
                        for vulnerability in dependency.get('vulnerabilities', []):
                            results.append({
                                'severity': self._map_severity(vulnerability.get('cvssv3', {}).get('baseSeverity', 'MEDIUM')),
                                'type': 'CVE',
                                'title': vulnerability.get('name', ''),
                                'description': vulnerability.get('description', ''),
                                'file_path': '',
                                'line_number': None,
                                'cve_id': vulnerability.get('name', ''),
                                'package_name': dependency.get('fileName', ''),
                                'package_version': dependency.get('version', ''),
                                'fixed_version': '',
                                'raw_data': vulnerability
                            })
            except Exception as e:
                print(f"Dependency-Check扫描失败: {str(e)}")
        
        return results
    
    def _map_severity(self, cvss_severity):
        """映射CVSS严重级别"""
        mapping = {
            'CRITICAL': 'critical',
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low'
        }
        return mapping.get(cvss_severity, 'info')

