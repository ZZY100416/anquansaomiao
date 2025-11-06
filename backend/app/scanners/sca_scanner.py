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
            # 注意：这是测试数据，因为项目文件不存在
            print(f"[SCA] 警告: 项目路径不存在 {project_path}，返回模拟数据")
            results.append({
                'severity': 'high',
                'type': 'CVE',
                'title': 'CVE-2023-12345: 依赖库漏洞（模拟数据）',
                'description': '检测到依赖库存在已知安全漏洞。注意：这是测试数据，因为项目文件不存在。请上传项目代码到 /app/uploaded_files/project_{project_id} 目录。',
                'file_path': '',
                'line_number': None,
                'cve_id': 'CVE-2023-12345',
                'package_name': 'vulnerable-package',
                'package_version': '1.0.0',
                'fixed_version': '1.2.0',
                'raw_data': {'is_mock': True, 'reason': 'project_path_not_found', 'path': project_path}
            })
        else:
            try:
                import sys
                print(f'[SCA] 开始扫描项目: {project_path}', file=sys.stderr)
                
                # 检查Dependency-Check是否安装
                check_cmd = ['/opt/dependency-check/dependency-check/bin/dependency-check.sh', '--version']
                check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
                
                # 检查输出中是否包含"not installed"（占位符脚本的输出）
                dep_check_available = (
                    check_result.returncode == 0 and 
                    'not installed' not in check_result.stdout.lower() and
                    'not installed' not in check_result.stderr.lower()
                )
                
                if not dep_check_available:
                    print(f'[SCA] 警告: Dependency-Check未安装或不可用', file=sys.stderr)
                    print(f'[SCA] 检查输出: {check_result.stdout} {check_result.stderr}', file=sys.stderr)
                    print(f'[SCA] 尝试使用替代方案扫描依赖（pip-audit, npm audit等）...', file=sys.stderr)
                    
                    # 使用替代方案扫描
                    results.extend(self._scan_with_alternatives(project_path))
                    print(f'[SCA] 替代方案扫描完成，共返回 {len(results)} 个结果', file=sys.stderr)
                    return results
                
                # 确保报告目录存在
                report_dir = "/app/scan_results"
                os.makedirs(report_dir, exist_ok=True)
                report_path = os.path.join(report_dir, f"dependency-check-report-{scan.project_id}.json")
                
                # 执行Dependency-Check扫描
                cmd = [
                    '/opt/dependency-check/dependency-check/bin/dependency-check.sh',
                    '--project', f'Project_{scan.project_id}',
                    '--scan', project_path,
                    '--format', 'JSON',
                    '--out', report_dir,
                    '--disableRetireJS',  # 禁用RetireJS以提高速度
                    '--disableAssembly',  # 禁用程序集分析
                    '--disableOssIndex',  # 禁用OSS Index（如果没有配置）
                ]
                
                print(f'[SCA] 执行命令: {" ".join(cmd)}', file=sys.stderr)
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                
                print(f'[SCA] Dependency-Check返回码: {result.returncode}', file=sys.stderr)
                if result.stderr:
                    print(f'[SCA] Dependency-Check错误输出: {result.stderr[:1000]}', file=sys.stderr)
                if result.stdout:
                    print(f'[SCA] Dependency-Check输出: {result.stdout[:500]}', file=sys.stderr)
                
                # 查找报告文件（Dependency-Check会自动生成文件名）
                possible_report_files = [
                    report_path,
                    os.path.join(report_dir, f"dependency-check-report.json"),
                    os.path.join(report_dir, f"dependency-check-report-Project_{scan.project_id}.json"),
                ]
                
                report_file = None
                for possible_file in possible_report_files:
                    if os.path.exists(possible_file):
                        report_file = possible_file
                        print(f'[SCA] 找到报告文件: {report_file}', file=sys.stderr)
                        break
                
                if not report_file:
                    print(f'[SCA] 警告: 报告文件不存在', file=sys.stderr)
                    print(f'[SCA] 检查过的路径: {possible_report_files}', file=sys.stderr)
                    # 列出报告目录中的所有文件
                    if os.path.exists(report_dir):
                        files = os.listdir(report_dir)
                        print(f'[SCA] 报告目录中的文件: {files}', file=sys.stderr)
                else:
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                        
                        dependencies = report_data.get('dependencies', [])
                        print(f'[SCA] 报告中发现 {len(dependencies)} 个依赖', file=sys.stderr)
                        
                        vulnerability_count = 0
                        for dependency in dependencies:
                            vulnerabilities = dependency.get('vulnerabilities', [])
                            if vulnerabilities:
                                vulnerability_count += len(vulnerabilities)
                                for vulnerability in vulnerabilities:
                                    results.append({
                                        'severity': self._map_severity(vulnerability.get('cvssv3', {}).get('baseSeverity', 'MEDIUM')),
                                        'type': 'CVE',
                                        'title': vulnerability.get('name', ''),
                                        'description': vulnerability.get('description', ''),
                                        'file_path': dependency.get('fileName', ''),
                                        'line_number': None,
                                        'cve_id': vulnerability.get('name', ''),
                                        'package_name': dependency.get('fileName', ''),
                                        'package_version': dependency.get('version', ''),
                                        'fixed_version': '',
                                        'raw_data': vulnerability
                                    })
                        
                        print(f'[SCA] 发现 {vulnerability_count} 个漏洞', file=sys.stderr)
                        
                        if vulnerability_count == 0:
                            print(f'[SCA] 提示: 未发现漏洞，可能原因：', file=sys.stderr)
                            print(f'[SCA] 1. 依赖库都是安全的', file=sys.stderr)
                            print(f'[SCA] 2. 项目中没有依赖文件（pom.xml, package.json, requirements.txt等）', file=sys.stderr)
                            print(f'[SCA] 3. Dependency-Check未正确识别依赖', file=sys.stderr)
                    except json.JSONDecodeError as e:
                        print(f'[SCA] 解析JSON报告失败: {str(e)}', file=sys.stderr)
                        print(f'[SCA] 报告文件内容（前500字符）: {open(report_file, "r").read()[:500]}', file=sys.stderr)
                    except Exception as e:
                        import traceback
                        print(f'[SCA] 处理报告文件失败: {str(e)}', file=sys.stderr)
                        print(f'[SCA] 错误堆栈: {traceback.format_exc()}', file=sys.stderr)
                        
            except subprocess.TimeoutExpired:
                print(f'[SCA] Dependency-Check扫描超时（超过600秒）', file=sys.stderr)
            except Exception as e:
                import traceback
                print(f'[SCA] Dependency-Check扫描异常: {str(e)}', file=sys.stderr)
                print(f'[SCA] 错误堆栈: {traceback.format_exc()}', file=sys.stderr)
        
        print(f'[SCA] 扫描完成，共返回 {len(results)} 个结果', file=sys.stderr)
        
        return results
    
    def _scan_with_alternatives(self, project_path):
        """使用替代方案扫描依赖（pip-audit, npm audit等）"""
        import sys
        results = []
        
        # 检查项目类型并扫描
        # 1. Python项目 - 使用pip-audit
        if os.path.exists(os.path.join(project_path, 'requirements.txt')) or \
           os.path.exists(os.path.join(project_path, 'setup.py')) or \
           os.path.exists(os.path.join(project_path, 'pyproject.toml')):
            print(f'[SCA] 检测到Python项目，尝试使用pip-audit扫描...', file=sys.stderr)
            results.extend(self._scan_python_dependencies(project_path))
        
        # 2. Node.js项目 - 使用npm audit
        if os.path.exists(os.path.join(project_path, 'package.json')):
            print(f'[SCA] 检测到Node.js项目，尝试使用npm audit扫描...', file=sys.stderr)
            results.extend(self._scan_nodejs_dependencies(project_path))
        
        # 3. Java项目 - 使用Maven或Gradle
        if os.path.exists(os.path.join(project_path, 'pom.xml')):
            print(f'[SCA] 检测到Maven项目，但需要Maven环境（暂不支持）', file=sys.stderr)
        elif os.path.exists(os.path.join(project_path, 'build.gradle')):
            print(f'[SCA] 检测到Gradle项目，但需要Gradle环境（暂不支持）', file=sys.stderr)
        
        return results
    
    def _scan_python_dependencies(self, project_path):
        """使用pip-audit扫描Python依赖"""
        import sys
        results = []
        
        try:
            # 检查pip-audit是否可用
            check_cmd = ['pip-audit', '--version']
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
            
            if check_result.returncode != 0:
                # 尝试安装pip-audit
                print(f'[SCA] pip-audit未安装，尝试安装...', file=sys.stderr)
                install_result = subprocess.run(
                    ['pip', 'install', 'pip-audit'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if install_result.returncode != 0:
                    print(f'[SCA] pip-audit安装失败: {install_result.stderr}', file=sys.stderr)
                    return results
            
            # 查找requirements.txt
            req_file = None
            for req_file_name in ['requirements.txt', 'requirements-dev.txt']:
                req_path = os.path.join(project_path, req_file_name)
                if os.path.exists(req_path):
                    req_file = req_path
                    break
            
            if not req_file:
                print(f'[SCA] 未找到requirements.txt文件，尝试扫描整个项目目录', file=sys.stderr)
                # 如果没有requirements.txt，尝试扫描整个目录
                cmd = ['pip-audit', '--format', 'json', '--desc', '.']
            else:
                # 执行pip-audit扫描requirements.txt
                cmd = ['pip-audit', '--format', 'json', '--desc', '--requirement', req_file]
            
            print(f'[SCA] 执行pip-audit命令: {" ".join(cmd)}', file=sys.stderr)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=project_path
            )
            
            print(f'[SCA] pip-audit返回码: {result.returncode}', file=sys.stderr)
            if result.stderr:
                print(f'[SCA] pip-audit错误输出: {result.stderr[:500]}', file=sys.stderr)
            
            # pip-audit即使有漏洞也可能返回非0，需要检查输出
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulns = audit_data.get('vulnerabilities', [])
                    if not vulns and isinstance(audit_data, dict):
                        # 尝试其他可能的字段名
                        vulns = audit_data.get('vulns', [])
                    
                    for vuln in vulns:
                        # 处理不同的输出格式
                        if isinstance(vuln, dict):
                            results.append({
                                'severity': self._map_severity(vuln.get('severity', 'MEDIUM')),
                                'type': 'CVE',
                                'title': vuln.get('id', vuln.get('name', '')),
                                'description': vuln.get('description', ''),
                                'file_path': req_file or 'project',
                                'line_number': None,
                                'cve_id': vuln.get('id', ''),
                                'package_name': vuln.get('name', ''),
                                'package_version': vuln.get('installed_version', vuln.get('version', '')),
                                'fixed_version': vuln.get('fixed_version', ''),
                                'raw_data': vuln
                            })
                    print(f'[SCA] pip-audit发现 {len(results)} 个漏洞', file=sys.stderr)
                except json.JSONDecodeError as e:
                    print(f'[SCA] pip-audit输出解析失败: {str(e)}', file=sys.stderr)
                    print(f'[SCA] 输出内容（前500字符）: {result.stdout[:500]}', file=sys.stderr)
            elif result.returncode == 0:
                print(f'[SCA] pip-audit扫描完成，未发现漏洞', file=sys.stderr)
        except Exception as e:
            import traceback
            print(f'[SCA] pip-audit扫描异常: {str(e)}', file=sys.stderr)
            print(f'[SCA] 错误堆栈: {traceback.format_exc()}', file=sys.stderr)
        
        return results
    
    def _scan_nodejs_dependencies(self, project_path):
        """使用npm audit扫描Node.js依赖"""
        import sys
        results = []
        
        try:
            # 检查npm是否可用
            check_cmd = ['npm', '--version']
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
            
            if check_result.returncode != 0:
                print(f'[SCA] npm未安装，无法扫描Node.js依赖', file=sys.stderr)
                return results
            
            # 执行npm audit扫描
            cmd = ['npm', 'audit', '--json']
            print(f'[SCA] 执行npm audit命令: {" ".join(cmd)}', file=sys.stderr)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=project_path
            )
            
            # npm audit即使有漏洞也可能返回非0，需要检查输出
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get('vulnerabilities', {})
                    
                    for vuln_id, vuln_info in vulnerabilities.items():
                        for via in vuln_info.get('via', []):
                            if isinstance(via, dict) and 'cwe' not in via:  # 跳过CWE引用
                                results.append({
                                    'severity': self._map_npm_severity(vuln_info.get('severity', 'moderate')),
                                    'type': 'CVE',
                                    'title': vuln_id,
                                    'description': vuln_info.get('title', ''),
                                    'file_path': 'package.json',
                                    'line_number': None,
                                    'cve_id': vuln_id,
                                    'package_name': via.get('name', ''),
                                    'package_version': via.get('version', ''),
                                    'fixed_version': vuln_info.get('fixAvailable', {}).get('version', ''),
                                    'raw_data': vuln_info
                                })
                    print(f'[SCA] npm audit发现 {len(results)} 个漏洞', file=sys.stderr)
                except json.JSONDecodeError:
                    print(f'[SCA] npm audit输出解析失败', file=sys.stderr)
            elif result.stderr:
                print(f'[SCA] npm audit错误: {result.stderr}', file=sys.stderr)
        except Exception as e:
            import traceback
            print(f'[SCA] npm audit扫描异常: {str(e)}', file=sys.stderr)
            print(f'[SCA] 错误堆栈: {traceback.format_exc()}', file=sys.stderr)
        
        return results
    
    def _map_npm_severity(self, npm_severity):
        """映射npm audit严重级别"""
        mapping = {
            'critical': 'critical',
            'high': 'high',
            'moderate': 'medium',
            'low': 'low',
            'info': 'info'
        }
        return mapping.get(npm_severity.lower(), 'medium')
    
    def _map_severity(self, cvss_severity):
        """映射CVSS严重级别"""
        mapping = {
            'CRITICAL': 'critical',
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low'
        }
        return mapping.get(cvss_severity, 'info')

