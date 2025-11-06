import subprocess
import json
import sys
from app.models.scan import Scan

class ContainerScanner:
    def scan(self, scan):
        """使用Trivy进行容器镜像扫描"""
        results = []
        
        # 从扫描配置中获取镜像名称
        try:
            if scan.config:
                # 如果config是字符串，解析JSON
                if isinstance(scan.config, str):
                    config = json.loads(scan.config)
                # 如果已经是字典，直接使用
                elif isinstance(scan.config, dict):
                    config = scan.config
                else:
                    config = {}
            else:
                config = {}
        except (json.JSONDecodeError, TypeError) as e:
            print(f"[Container] 配置解析失败: {str(e)}, config={scan.config}", file=sys.stderr)
            config = {}
        
        image_name = config.get('image_name', '') if isinstance(config, dict) else ''
        
        if not image_name:
            # 模拟扫描结果
            # 注意：这是测试数据，因为没有配置镜像名称
            print(f"[Container] 警告: 未配置镜像名称，返回模拟数据", file=sys.stderr)
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
            return results
        
        # 检查Trivy是否安装
        try:
            check_cmd = ['trivy', '--version']
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
            if check_result.returncode != 0 or 'not installed' in check_result.stdout.lower():
                print(f"[Container] 警告: Trivy未安装或不可用", file=sys.stderr)
                print(f"[Container] 检查输出: {check_result.stdout} {check_result.stderr}", file=sys.stderr)
                results.append({
                    'severity': 'info',
                    'type': 'Scanner Error',
                    'title': 'Trivy扫描器未安装（模拟数据）',
                    'description': 'Trivy扫描器未安装或不可用。请确保Trivy已正确安装在容器中。注意：这是测试数据，因为Trivy未安装。',
                    'file_path': '',
                    'line_number': None,
                    'cve_id': '',
                    'package_name': '',
                    'package_version': '',
                    'fixed_version': '',
                    'raw_data': {'is_mock': True, 'reason': 'trivy_not_installed', 'check_output': check_result.stdout + check_result.stderr}
                })
                return results
        except Exception as e:
            print(f"[Container] 检查Trivy安装失败: {str(e)}", file=sys.stderr)
            results.append({
                'severity': 'info',
                'type': 'Scanner Error',
                'title': 'Trivy扫描器检查失败（模拟数据）',
                'description': f'无法检查Trivy是否安装: {str(e)}。注意：这是测试数据，因为Trivy检查失败。',
                'file_path': '',
                'line_number': None,
                'cve_id': '',
                'package_name': '',
                'package_version': '',
                'fixed_version': '',
                'raw_data': {'is_mock': True, 'reason': 'trivy_check_failed', 'error': str(e)}
            })
            return results
        
        # 执行Trivy扫描
        try:
            print(f"[Container] 开始扫描镜像: {image_name}", file=sys.stderr)
            
            # 使用Trivy扫描镜像（添加--skip-db-update可以加快速度，但可能缺少最新漏洞数据）
            cmd = ['trivy', 'image', '--format', 'json', '--quiet', image_name]
            
            print(f"[Container] 执行命令: {' '.join(cmd)}", file=sys.stderr)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            print(f"[Container] Trivy返回码: {result.returncode}", file=sys.stderr)
            
            if result.stderr:
                print(f"[Container] Trivy错误输出: {result.stderr[:1000]}", file=sys.stderr)
            
            if result.returncode == 0:
                try:
                    trivy_results = json.loads(result.stdout)
                    
                    # Trivy的JSON格式：{"Results": [...]}
                    vulnerability_count = 0
                    for result_item in trivy_results.get('Results', []):
                        vulnerabilities = result_item.get('Vulnerabilities', [])
                        vulnerability_count += len(vulnerabilities)
                        
                        for vulnerability in vulnerabilities:
                            results.append({
                                'severity': self._map_severity(vulnerability.get('Severity', 'UNKNOWN')),
                                'type': 'Vulnerability',
                                'title': vulnerability.get('Title', vulnerability.get('VulnerabilityID', '')),
                                'description': vulnerability.get('Description', ''),
                                'file_path': result_item.get('Target', ''),
                                'line_number': None,
                                'cve_id': vulnerability.get('VulnerabilityID', ''),
                                'package_name': vulnerability.get('PkgName', ''),
                                'package_version': vulnerability.get('InstalledVersion', ''),
                                'fixed_version': vulnerability.get('FixedVersion', ''),
                                'raw_data': vulnerability
                            })
                    
                    print(f"[Container] 扫描完成，发现 {vulnerability_count} 个漏洞", file=sys.stderr)
                    
                    if vulnerability_count == 0:
                        print(f"[Container] 提示: 未发现漏洞，可能原因：", file=sys.stderr)
                        print(f"[Container] 1. 镜像确实没有漏洞", file=sys.stderr)
                        print(f"[Container] 2. 镜像不存在或无法访问", file=sys.stderr)
                        print(f"[Container] 3. Trivy数据库未更新", file=sys.stderr)
                        
                except json.JSONDecodeError as e:
                    print(f"[Container] 解析Trivy JSON输出失败: {str(e)}", file=sys.stderr)
                    print(f"[Container] 输出内容（前500字符）: {result.stdout[:500]}", file=sys.stderr)
                    results.append({
                        'severity': 'info',
                        'type': 'Scanner Error',
                        'title': 'Trivy输出解析失败（模拟数据）',
                        'description': f'无法解析Trivy的JSON输出: {str(e)}。注意：这是测试数据，因为输出解析失败。',
                        'file_path': '',
                        'line_number': None,
                        'cve_id': '',
                        'package_name': '',
                        'package_version': '',
                        'fixed_version': '',
                        'raw_data': {'is_mock': True, 'reason': 'json_parse_failed', 'error': str(e), 'output_preview': result.stdout[:500]}
                    })
            else:
                # Trivy返回非0，可能是镜像不存在、网络问题等
                error_msg = result.stderr or result.stdout or '未知错误'
                print(f"[Container] Trivy扫描失败，返回码: {result.returncode}", file=sys.stderr)
                print(f"[Container] 错误信息: {error_msg[:1000]}", file=sys.stderr)
                
                results.append({
                    'severity': 'info',
                    'type': 'Scanner Error',
                    'title': 'Trivy扫描失败（模拟数据）',
                    'description': f'Trivy扫描失败: {error_msg[:500]}。可能原因：镜像不存在、网络问题、权限问题等。注意：这是测试数据，因为扫描失败。',
                    'file_path': '',
                    'line_number': None,
                    'cve_id': '',
                    'package_name': '',
                    'package_version': '',
                    'fixed_version': '',
                    'raw_data': {'is_mock': True, 'reason': 'trivy_scan_failed', 'returncode': result.returncode, 'error': error_msg[:500]}
                })
                
        except subprocess.TimeoutExpired:
            print(f"[Container] Trivy扫描超时（超过600秒）", file=sys.stderr)
            results.append({
                'severity': 'info',
                'type': 'Scanner Error',
                'title': 'Trivy扫描超时（模拟数据）',
                'description': 'Trivy扫描超时（超过600秒）。可能原因：镜像太大、网络太慢等。注意：这是测试数据，因为扫描超时。',
                'file_path': '',
                'line_number': None,
                'cve_id': '',
                'package_name': '',
                'package_version': '',
                'fixed_version': '',
                'raw_data': {'is_mock': True, 'reason': 'trivy_scan_timeout'}
            })
        except Exception as e:
            import traceback
            print(f"[Container] Trivy扫描异常: {str(e)}", file=sys.stderr)
            print(f"[Container] 错误堆栈: {traceback.format_exc()}", file=sys.stderr)
            results.append({
                'severity': 'info',
                'type': 'Scanner Error',
                'title': 'Trivy扫描异常（模拟数据）',
                'description': f'Trivy扫描过程中发生异常: {str(e)}。注意：这是测试数据，因为扫描异常。',
                'file_path': '',
                'line_number': None,
                'cve_id': '',
                'package_name': '',
                'package_version': '',
                'fixed_version': '',
                'raw_data': {'is_mock': True, 'reason': 'trivy_scan_exception', 'error': str(e)}
            })
        
        print(f"[Container] 扫描完成，共返回 {len(results)} 个结果", file=sys.stderr)
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

