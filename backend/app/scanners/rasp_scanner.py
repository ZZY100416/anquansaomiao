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
        # 默认地址：http://192.168.203.141:8086/api
        self.rasp_api_url = os.getenv('OPENRASP_API_URL', 'http://192.168.203.141:8086/api')
        self.rasp_api_key = os.getenv('OPENRASP_API_KEY', '')
        import sys
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
            response = requests.get(
                f'{self.rasp_api_url}/events',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('data', [])
                
                for event in events:
                    results.append({
                        'severity': self._map_severity(event.get('severity', 'medium')),
                        'type': event.get('type', 'RASP Event'),
                        'title': event.get('message', '运行时安全事件'),
                        'description': event.get('description', ''),
                        'file_path': event.get('file_path', ''),
                        'line_number': event.get('line_number'),
                        'cve_id': '',
                        'package_name': '',
                        'package_version': '',
                        'fixed_version': '',
                        'raw_data': {
                            'event_id': event.get('id'),
                            'app_id': event.get('app_id'),
                            'timestamp': event.get('timestamp'),
                            'attack_type': event.get('attack_type'),
                            'attack_params': event.get('attack_params'),
                            'stack_trace': event.get('stack_trace'),
                            'request_id': event.get('request_id'),
                            'url': event.get('url'),
                            'user_agent': event.get('user_agent'),
                            'client_ip': event.get('client_ip')
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

