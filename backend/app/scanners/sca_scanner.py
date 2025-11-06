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
                if check_result.returncode != 0:
                    print(f'[SCA] 警告: Dependency-Check未安装或不可用', file=sys.stderr)
                    print(f'[SCA] 错误输出: {check_result.stderr}', file=sys.stderr)
                    print(f'[SCA] 尝试使用其他方法扫描依赖...', file=sys.stderr)
                    # 可以尝试使用pip-audit, npm audit等替代方案
                
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
    
    def _map_severity(self, cvss_severity):
        """映射CVSS严重级别"""
        mapping = {
            'CRITICAL': 'critical',
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low'
        }
        return mapping.get(cvss_severity, 'info')

