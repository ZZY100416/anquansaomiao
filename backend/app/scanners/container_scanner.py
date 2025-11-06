import subprocess
import json
from app.models.scan import Scan

class ContainerScanner:
    def scan(self, scan):
        """使用Trivy进行容器镜像扫描"""
        results = []
        
        # 从扫描配置中获取镜像名称
        config = json.loads(scan.config) if scan.config else {}
        image_name = config.get('image_name', '')
        
        if not image_name:
            # 模拟扫描结果
            # 注意：这是测试数据，因为没有配置镜像名称
            print(f"[Container] 警告: 未配置镜像名称，返回模拟数据")
            results.append({
                'severity': 'critical',
                'type': 'Vulnerability',
                'title': 'CVE-2023-67890: 容器镜像漏洞（模拟数据）',
                'description': '检测到容器镜像中存在安全漏洞。注意：这是测试数据，因为未配置镜像名称。请在扫描配置中填写 {"image_name": "your-image:tag"}。',
                'file_path': '',
                'line_number': None,
                'cve_id': 'CVE-2023-67890',
                'package_name': 'vulnerable-package',
                'package_version': '2.0.0',
                'fixed_version': '2.1.0',
                'raw_data': {'is_mock': True, 'reason': 'image_name_not_configured'}
            })
        else:
            try:
                # 执行Trivy扫描
                cmd = ['trivy', 'image', '--format', 'json', image_name]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    trivy_results = json.loads(result.stdout)
                    
                    for result_item in trivy_results.get('Results', []):
                        for vulnerability in result_item.get('Vulnerabilities', []):
                            results.append({
                                'severity': self._map_severity(vulnerability.get('Severity', 'UNKNOWN')),
                                'type': 'Vulnerability',
                                'title': vulnerability.get('Title', ''),
                                'description': vulnerability.get('Description', ''),
                                'file_path': '',
                                'line_number': None,
                                'cve_id': vulnerability.get('VulnerabilityID', ''),
                                'package_name': vulnerability.get('PkgName', ''),
                                'package_version': vulnerability.get('InstalledVersion', ''),
                                'fixed_version': vulnerability.get('FixedVersion', ''),
                                'raw_data': vulnerability
                            })
            except Exception as e:
                print(f"Trivy扫描失败: {str(e)}")
        
        return results
    
    def _map_severity(self, trivy_severity):
        """映射Trivy严重级别"""
        mapping = {
            'CRITICAL': 'critical',
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low',
            'UNKNOWN': 'info'
        }
        return mapping.get(trivy_severity, 'info')

