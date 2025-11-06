import requests
import json
import os
from app.models.scan import Scan

class RASPScanner:
    """
    OpenRASP运行时应用自我保护扫描器
    集成OpenRASP管理后台API，获取运行时安全事件
    """
    
    def __init__(self):
        # OpenRASP管理后台API地址（从环境变量或配置读取）
        # 注意：OpenRASP的API路径可能不是/api，需要根据实际文档调整
        # 默认地址：http://192.168.203.141:8086
        base_url = os.getenv('OPENRASP_API_URL', 'http://192.168.203.141:8086')
        # 如果URL已经包含/api，直接使用；否则尝试不同的API路径
        if '/api' in base_url:
            self.rasp_api_url = base_url
        else:
            # 尝试不同的API路径
            self.rasp_api_url = base_url.rstrip('/')
        self.rasp_api_key = os.getenv('OPENRASP_API_KEY', '')
        import sys
        print(f"[RASP] OpenRASP基础地址: {base_url}", file=sys.stderr)
        print(f"[RASP] OpenRASP API地址: {self.rasp_api_url}", file=sys.stderr)
    
    def scan(self, scan):
        """
        从OpenRASP获取运行时安全事件
        """
        results = []
        
        # 从扫描配置中获取参数
        config = json.loads(scan.config) if scan.config else {}
        app_id = config.get('app_id', '')
        start_time = config.get('start_time', '')
        end_time = config.get('end_time', '')
        
        if not app_id:
            # 如果没有指定app_id，尝试获取所有应用的事件
            results.extend(self._get_all_events())
        else:
            # 获取指定应用的事件
            results.extend(self._get_app_events(app_id, start_time, end_time))
        
        return results
    
    def _get_all_events(self):
        """获取所有应用的RASP事件"""
        results = []
        
        try:
            # 调用OpenRASP API获取事件列表
            # 注意：这里需要根据实际的OpenRASP API文档调整
            headers = {}
            if self.rasp_api_key:
                headers['Authorization'] = f'Bearer {self.rasp_api_key}'
            
            # 获取事件列表
            # 从Network标签找到正确的API路径：/v1/api/log/attack/search (POST方法)
            base = self.rasp_api_url.rstrip('/')
            api_path = f'{base}/v1/api/log/attack/search'
            
            import sys
            print(f"[RASP] 使用API路径: {api_path} (POST方法)", file=sys.stderr)
            
            # OpenRASP的API使用POST方法，需要传递查询参数
            # 根据OpenRASP的API，可能需要传递分页、过滤等参数
            request_data = {
                'page': 1,
                'size': 100,  # 获取前100条记录
                # 可以根据扫描配置添加更多过滤条件
            }
            
            try:
                # 使用POST请求
                response = requests.post(
                    api_path,
                    headers=headers,
                    json=request_data,
                    timeout=30
                )
                print(f"[RASP] POST请求返回状态码: {response.status_code}", file=sys.stderr)
                
                if response.status_code != 200:
                    print(f"[RASP] API请求失败，状态码: {response.status_code}", file=sys.stderr)
                    print(f"[RASP] 响应内容: {response.text[:500]}", file=sys.stderr)
                    # 如果失败，尝试不带参数的POST
                    print(f"[RASP] 尝试不带参数的POST请求", file=sys.stderr)
                    response = requests.post(api_path, headers=headers, json={}, timeout=30)
                    print(f"[RASP] 第二次POST请求返回状态码: {response.status_code}", file=sys.stderr)
                    
            except requests.exceptions.ConnectionError as e:
                print(f"[RASP] 连接错误: {str(e)}", file=sys.stderr)
                response = None
            except Exception as e:
                print(f"[RASP] API请求异常: {str(e)}", file=sys.stderr)
                import traceback
                print(f"[RASP] 错误堆栈: {traceback.format_exc()}", file=sys.stderr)
                response = None
            
            if not response or response.status_code != 200:
                import sys
                print(f"[RASP] 所有API路径都失败，返回模拟数据", file=sys.stderr)
                print(f"[RASP] 提示: 请查看OpenRASP文档确认正确的API路径", file=sys.stderr)
                print(f"[RASP] 文档地址: https://rasp.baidu.com/doc/install/main.html", file=sys.stderr)
                results.append({
                    'severity': 'info',
                    'type': 'RASP Connection',
                    'title': 'OpenRASP API连接失败（模拟数据）',
                    'description': f'无法连接到OpenRASP API。请检查API地址和路径是否正确。\n尝试的路径: {api_paths}\n请参考OpenRASP文档: https://rasp.baidu.com/doc/install/main.html\n或者查看OpenRASP管理后台的API文档。',
                    'file_path': '',
                    'line_number': None,
                    'raw_data': {
                        'is_mock': True,
                        'reason': 'rasp_api_failed',
                        'api_urls': api_paths,
                        'base_url': self.rasp_api_url,
                        'note': '请查看OpenRASP API文档确认正确的API端点'
                    }
                })
                return results
            
            if response.status_code == 200:
                data = response.json()
                import sys
                print(f"[RASP] API响应数据结构: {type(data)}, 键: {list(data.keys()) if isinstance(data, dict) else 'N/A'}", file=sys.stderr)
                print(f"[RASP] API响应数据预览: {str(data)[:500]}", file=sys.stderr)
                
                # OpenRASP的响应格式可能是 data.data 或 data.list 或直接是数组
                events = []
                if isinstance(data, dict):
                    # 尝试不同的数据字段
                    if 'data' in data:
                        events = data.get('data', [])
                        if isinstance(events, dict) and 'list' in events:
                            events = events.get('list', [])
                    elif 'list' in data:
                        events = data.get('list', [])
                    elif 'result' in data:
                        events = data.get('result', [])
                        if isinstance(events, dict) and 'data' in events:
                            events = events.get('data', [])
                    elif 'items' in data:
                        events = data.get('items', [])
                elif isinstance(data, list):
                    events = data
                
                print(f"[RASP] 解析到 {len(events)} 个事件", file=sys.stderr)
                
                for event in events:
                    # OpenRASP事件字段可能不同，需要适配
                    attack_type = event.get('attack_type') or event.get('type') or event.get('attackType') or 'RASP Event'
                    message = event.get('message') or event.get('alert_message') or event.get('alertMessage') or '运行时安全事件'
                    severity = event.get('severity') or event.get('level') or 'medium'
                    
                    results.append({
                        'severity': self._map_severity(severity),
                        'type': attack_type,
                        'title': message,
                        'description': event.get('description') or event.get('detail') or '',
                        'file_path': event.get('file_path') or event.get('filePath') or '',
                        'line_number': event.get('line_number') or event.get('lineNumber'),
                        'cve_id': '',
                        'package_name': '',
                        'package_version': '',
                        'fixed_version': '',
                        'raw_data': {
                            'event_id': event.get('id') or event.get('_id'),
                            'app_id': event.get('app_id') or event.get('appId'),
                            'timestamp': event.get('timestamp') or event.get('time') or event.get('request_time'),
                            'attack_type': attack_type,
                            'attack_params': event.get('attack_params') or event.get('attackParams'),
                            'stack_trace': event.get('stack_trace') or event.get('stackTrace'),
                            'request_id': event.get('request_id') or event.get('requestId'),
                            'url': event.get('url') or event.get('request_url'),
                            'user_agent': event.get('user_agent') or event.get('userAgent'),
                            'client_ip': event.get('client_ip') or event.get('clientIp') or event.get('request_source'),
                            'intercept_state': event.get('intercept_state') or event.get('interceptState'),
                            'original_event': event  # 保存原始事件数据
                        }
                    })
            else:
                # API调用失败，返回模拟数据（用于演示）
                print(f"[RASP] 警告: OpenRASP API调用失败 (状态码: {response.status_code})，返回模拟数据")
                results.append({
                    'severity': 'high',
                    'type': 'SQL Injection',
                    'title': '检测到SQL注入攻击尝试（模拟数据）',
                    'description': 'OpenRASP在运行时检测到SQL注入攻击。注意：这是测试数据，因为OpenRASP API连接失败。请确保OpenRASP服务已启动并配置正确的API地址。',
                    'file_path': '',
                    'line_number': None,
                    'raw_data': {
                        'is_mock': True,
                        'reason': 'rasp_api_failed',
                        'status_code': response.status_code,
                        'api_url': self.rasp_api_url,
                        'message': 'OpenRASP API连接失败，这是模拟数据',
                        'note': '请配置正确的OPENRASP_API_URL和OPENRASP_API_KEY'
                    }
                })
        except Exception as e:
            # 如果OpenRASP未运行或无法连接，返回提示信息
            print(f"[RASP] 警告: OpenRASP连接失败: {str(e)}，返回模拟数据")
            results.append({
                'severity': 'info',
                'type': 'RASP Connection',
                'title': 'OpenRASP连接失败（模拟数据）',
                'description': f'无法连接到OpenRASP管理后台: {str(e)}。请确保OpenRASP已正确安装并运行。注意：这是测试数据，因为无法连接到OpenRASP服务。',
                'file_path': '',
                'line_number': None,
                'raw_data': {
                    'is_mock': True,
                    'reason': 'rasp_connection_failed',
                    'error': str(e),
                    'api_url': self.rasp_api_url,
                    'note': '请检查OpenRASP配置和网络连接'
                }
            })
        
        return results
    
    def _get_app_events(self, app_id, start_time=None, end_time=None):
        """获取指定应用的RASP事件"""
        results = []
        
        try:
            headers = {}
            if self.rasp_api_key:
                headers['Authorization'] = f'Bearer {self.rasp_api_key}'
            
            params = {'app_id': app_id}
            if start_time:
                params['start_time'] = start_time
            if end_time:
                params['end_time'] = end_time
            
            response = requests.get(
                f'{self.rasp_api_url}/events',
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('data', [])
                
                for event in events:
                    results.append({
                        'severity': self._map_severity(event.get('severity', 'medium')),
                        'type': event.get('attack_type', 'RASP Event'),
                        'title': event.get('message', '运行时安全事件'),
                        'description': self._format_event_description(event),
                        'file_path': event.get('file_path', ''),
                        'line_number': event.get('line_number'),
                        'cve_id': '',
                        'package_name': '',
                        'package_version': '',
                        'fixed_version': '',
                        'raw_data': event
                    })
        except Exception as e:
            print(f"[RASP] 警告: 获取应用 {app_id} 的事件失败: {str(e)}，返回模拟数据")
            results.append({
                'severity': 'info',
                'type': 'RASP Connection',
                'title': 'OpenRASP连接失败（模拟数据）',
                'description': f'无法获取应用 {app_id} 的事件: {str(e)}。注意：这是测试数据，因为无法连接到OpenRASP服务。',
                'file_path': '',
                'line_number': None,
                'raw_data': {
                    'is_mock': True,
                    'reason': 'rasp_get_app_events_failed',
                    'error': str(e),
                    'app_id': app_id,
                    'api_url': self.rasp_api_url
                }
            })
        
        return results
    
    def _format_event_description(self, event):
        """格式化事件描述"""
        desc_parts = []
        
        if event.get('attack_type'):
            desc_parts.append(f"攻击类型: {event.get('attack_type')}")
        
        if event.get('url'):
            desc_parts.append(f"请求URL: {event.get('url')}")
        
        if event.get('client_ip'):
            desc_parts.append(f"客户端IP: {event.get('client_ip')}")
        
        if event.get('attack_params'):
            desc_parts.append(f"攻击参数: {event.get('attack_params')}")
        
        return ' | '.join(desc_parts) if desc_parts else '运行时安全事件'
    
    def _map_severity(self, rasp_severity):
        """映射OpenRASP严重级别到统一格式"""
        mapping = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            'block': 'critical',  # 拦截事件视为严重
            'log': 'medium',      # 日志事件视为中危
            'ignore': 'info'       # 忽略事件视为信息
        }
        return mapping.get(rasp_severity.lower(), 'medium')
    
    def get_rasp_status(self):
        """获取OpenRASP服务状态"""
        try:
            headers = {}
            if self.rasp_api_key:
                headers['Authorization'] = f'Bearer {self.rasp_api_key}'
            
            response = requests.get(
                f'{self.rasp_api_url}/status',
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    'status': 'connected',
                    'data': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}'
                }
        except Exception as e:
            return {
                'status': 'disconnected',
                'message': str(e)
            }

