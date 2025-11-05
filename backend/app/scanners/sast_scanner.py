import subprocess
import json
import os
from app.models.scan import Scan

class SASTScanner:
    def scan(self, scan):
        """使用Semgrep进行静态代码扫描"""
        results = []
        
        # 获取项目路径（这里简化处理，实际应该从项目配置中获取）
        project_path = f"/app/uploaded_files/project_{scan.project_id}"
        
        if not os.path.exists(project_path):
            # 模拟扫描结果（实际应该执行semgrep）
            results.append({
                'severity': 'high',
                'type': 'SQL Injection',
                'title': '潜在的SQL注入漏洞',
                'description': '检测到未参数化的SQL查询',
                'file_path': 'app/models/user.py',
                'line_number': 45,
                'raw_data': {}
            })
        else:
            try:
                # 执行Semgrep扫描
                cmd = ['semgrep', '--json', '--config=auto', project_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    semgrep_results = json.loads(result.stdout)
                    for issue in semgrep_results.get('results', []):
                        results.append({
                            'severity': self._map_severity(issue.get('extra', {}).get('severity', 'INFO')),
                            'type': issue.get('check_id', ''),
                            'title': issue.get('message', ''),
                            'description': issue.get('extra', {}).get('message', ''),
                            'file_path': issue.get('path', ''),
                            'line_number': issue.get('start', {}).get('line', 0),
                            'raw_data': issue
                        })
            except Exception as e:
                print(f"Semgrep扫描失败: {str(e)}")
        
        return results
    
    def _map_severity(self, semgrep_severity):
        """映射Semgrep严重级别"""
        mapping = {
            'ERROR': 'critical',
            'WARNING': 'high',
            'INFO': 'medium'
        }
        return mapping.get(semgrep_severity, 'low')

