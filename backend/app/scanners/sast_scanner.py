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
            # 注意：这是测试数据，因为项目文件不存在
            print(f"[SAST] 警告: 项目路径不存在 {project_path}，返回模拟数据")
            results.append({
                'severity': 'high',
                'type': 'SQL Injection',
                'title': '潜在的SQL注入漏洞（模拟数据）',
                'description': '检测到未参数化的SQL查询。注意：这是测试数据，因为项目文件不存在。请上传项目代码到 /app/uploaded_files/project_{project_id} 目录。',
                'file_path': 'app/models/user.py',
                'line_number': 45,
                'raw_data': {'is_mock': True, 'reason': 'project_path_not_found', 'path': project_path}
            })
        else:
            try:
                import sys
                print(f'[SAST] 开始扫描项目: {project_path}', file=sys.stderr)
                
                # 执行Semgrep扫描
                # 恢复到最简单的配置（和ID 15成功时一样）
                # 使用相对路径"."，让Semgrep在项目目录内运行，能正确读取.semgrepignore
                cmd = ['semgrep', '--json', '--config=auto', '.']
                
                print(f'[SAST] 执行命令: {" ".join(cmd)} (工作目录: {project_path})', file=sys.stderr)
                
                # 在项目目录内执行，让Semgrep能正确读取.semgrepignore和默认忽略规则
                # 超时时间设置为300秒（和原来成功时一样）
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=project_path  # 关键：在项目目录内执行
                )
                
                print(f'[SAST] Semgrep返回码: {result.returncode}', file=sys.stderr)
                if result.stderr:
                    print(f'[SAST] Semgrep错误输出: {result.stderr[:500]}', file=sys.stderr)
                
                if result.returncode == 0:
                    try:
                        semgrep_results = json.loads(result.stdout)
                        issue_count = len(semgrep_results.get('results', []))
                        print(f'[SAST] Semgrep扫描完成，发现 {issue_count} 个问题', file=sys.stderr)
                        
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
                    except json.JSONDecodeError as e:
                        print(f'[SAST] 解析Semgrep JSON输出失败: {str(e)}', file=sys.stderr)
                        print(f'[SAST] 输出内容（前500字符）: {result.stdout[:500]}', file=sys.stderr)
                else:
                    print(f'[SAST] Semgrep扫描失败，返回码: {result.returncode}', file=sys.stderr)
                    print(f'[SAST] 错误输出: {result.stderr}', file=sys.stderr)
                    
            except subprocess.TimeoutExpired:
                print(f'[SAST] Semgrep扫描超时（超过300秒）', file=sys.stderr)
                print(f'[SAST] 提示: 项目文件过多，扫描超时。', file=sys.stderr)
            except Exception as e:
                import traceback
                print(f'[SAST] Semgrep扫描异常: {str(e)}', file=sys.stderr)
                print(f'[SAST] 错误堆栈: {traceback.format_exc()}', file=sys.stderr)
        
        print(f'[SAST] 扫描完成，共返回 {len(results)} 个结果', file=sys.stderr)
        
        return results
    
    def _map_severity(self, semgrep_severity):
        """映射Semgrep严重级别"""
        mapping = {
            'ERROR': 'critical',
            'WARNING': 'high',
            'INFO': 'medium'
        }
        return mapping.get(semgrep_severity, 'low')

