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
        # 默认地址：http://192.168.203.141:8086
        base_url = os.getenv('OPENRASP_API_URL', 'http://192.168.203.141:8086')
        self.rasp_api_url = base_url.rstrip('/')
        
        # OpenRASP使用Cookie认证（RASP_AUTH_ID），而不是API Key
        # 可以通过环境变量配置Cookie，或者通过登录API获取
        self.rasp_auth_cookie = os.getenv('OPENRASP_AUTH_COOKIE', '')
        self.rasp_api_key = os.getenv('OPENRASP_API_KEY', '')  # 保留兼容性
        
        # 如果配置了用户名密码，可以通过登录获取Cookie
        self.rasp_username = os.getenv('OPENRASP_USERNAME', '')
        self.rasp_password = os.getenv('OPENRASP_PASSWORD', '')
        
        import sys
        print(f"[RASP] OpenRASP基础地址: {self.rasp_api_url}", file=sys.stderr)
        if self.rasp_auth_cookie:
            print(f"[RASP] 已配置Cookie认证", file=sys.stderr)
        elif self.rasp_username and self.rasp_password:
            print(f"[RASP] 已配置用户名密码，将尝试登录获取Cookie", file=sys.stderr)
        else:
            print(f"[RASP] 警告: 未配置认证信息，API调用可能失败", file=sys.stderr)
    
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
        
        # 统一使用_get_all_events，它支持app_id参数
        results.extend(self._get_all_events(app_id, start_time, end_time))
        
        return results
    
    def _get_auth_cookie(self):
        """通过登录获取OpenRASP的认证Cookie"""
        if not self.rasp_username or not self.rasp_password:
            return None
        
        try:
            import sys
            # 尝试不同的登录API路径
            login_paths = [
                f'{self.rasp_api_url}/v1/api/user/login',
                f'{self.rasp_api_url}/api/user/login',
                f'{self.rasp_api_url}/v1/api/login',
                f'{self.rasp_api_url}/api/login',
            ]
            
            # 尝试不同的登录数据格式
            login_data_formats = [
                {
                    'username': self.rasp_username,
                    'password': self.rasp_password
                },
                {
                    'user': self.rasp_username,
                    'pass': self.rasp_password
                },
                {
                    'name': self.rasp_username,
                    'pwd': self.rasp_password
                }
            ]
            
            for login_url in login_paths:
                for login_data in login_data_formats:
                    try:
                        print(f"[RASP] 尝试登录获取Cookie: {login_url}, 数据格式: {login_data}", file=sys.stderr)
                        
                        response = requests.post(
                            login_url,
                            json=login_data,
                            headers={
                                'Content-Type': 'application/json',
                                'Accept': 'application/json, text/plain, */*',
                                'Origin': self.rasp_api_url,
                                'Referer': f'{self.rasp_api_url}/',
                            },
                            timeout=10
                        )
                        
                        print(f"[RASP] 登录响应状态码: {response.status_code}", file=sys.stderr)
                        print(f"[RASP] 登录响应内容: {response.text[:200]}", file=sys.stderr)
                    
                        # 检查响应（即使状态码是200，响应体可能包含401错误）
                        try:
                            response_data = response.json()
                            # 如果响应体中有status: 401，说明认证失败
                            if response_data.get('status') == 401 or 'Unauthorized' in str(response_data):
                                print(f"[RASP] 登录失败: 用户名或密码错误", file=sys.stderr)
                                print(f"[RASP] 响应数据: {response_data}", file=sys.stderr)
                                continue  # 尝试下一个数据格式
                        except:
                            pass
                        
                        if response.status_code == 200:
                            # 从响应头中提取Cookie（Set-Cookie）
                            set_cookie_header = response.headers.get('Set-Cookie', '')
                            print(f"[RASP] Set-Cookie头: {set_cookie_header}", file=sys.stderr)
                            
                            if 'RASP_AUTH_ID' in set_cookie_header:
                                # 从Set-Cookie头中提取RASP_AUTH_ID的值
                                import re
                                match = re.search(r'RASP_AUTH_ID=([^;]+)', set_cookie_header)
                                if match:
                                    auth_cookie_value = match.group(1)
                                    print(f"[RASP] 登录成功，获取到Cookie: RASP_AUTH_ID={auth_cookie_value[:20]}...", file=sys.stderr)
                                    return f'RASP_AUTH_ID={auth_cookie_value}'
                            
                            # 也尝试从cookies对象中获取
                            cookies = response.cookies
                            print(f"[RASP] 响应cookies: {dict(cookies)}", file=sys.stderr)
                            auth_cookie = cookies.get('RASP_AUTH_ID')
                            if auth_cookie:
                                print(f"[RASP] 登录成功，从cookies对象获取到Cookie", file=sys.stderr)
                                return f'RASP_AUTH_ID={auth_cookie}'
                            
                            # 如果响应是JSON，可能Cookie在响应体中
                            try:
                                response_data = response.json()
                                print(f"[RASP] 登录响应数据: {response_data}", file=sys.stderr)
                                # 某些API可能返回token而不是Cookie
                                if 'token' in response_data:
                                    print(f"[RASP] 提示: API返回token而不是Cookie，可能需要使用token认证", file=sys.stderr)
                                # 检查是否真的登录成功
                                if response_data.get('status') == 401:
                                    print(f"[RASP] 登录失败: 响应体中的status是401", file=sys.stderr)
                                    continue  # 尝试下一个数据格式
                            except:
                                pass
                            
                            print(f"[RASP] 登录成功但未找到Cookie，响应头: {dict(response.headers)}", file=sys.stderr)
                        elif response.status_code == 401:
                            print(f"[RASP] 登录失败: HTTP 401 Unauthorized", file=sys.stderr)
                            print(f"[RASP] 响应: {response.text[:200]}", file=sys.stderr)
                            continue  # 尝试下一个数据格式
                        elif response.status_code == 404:
                            print(f"[RASP] 登录路径不存在: {login_url}", file=sys.stderr)
                            break  # 尝试下一个路径
                        else:
                            print(f"[RASP] 登录失败，状态码: {response.status_code}, 响应: {response.text[:200]}", file=sys.stderr)
                except Exception as e:
                    print(f"[RASP] 登录路径 {login_url} 异常: {str(e)}", file=sys.stderr)
                    continue
            
            print(f"[RASP] 所有登录路径都失败", file=sys.stderr)
        except Exception as e:
            import sys
            import traceback
            print(f"[RASP] 登录异常: {str(e)}", file=sys.stderr)
            print(f"[RASP] 错误堆栈: {traceback.format_exc()}", file=sys.stderr)
        
        return None
    
    def _get_all_events(self, app_id='', start_time='', end_time=''):
        """获取RASP事件（支持指定app_id或获取所有应用的事件）"""
        results = []
        
        try:
            # 调用OpenRASP API获取事件列表
            # 从Network标签找到正确的API路径：/v1/api/log/attack/search (POST方法)
            base = self.rasp_api_url.rstrip('/')
            api_path = f'{base}/v1/api/log/attack/search'
            
            import sys
            print(f"[RASP] 使用API路径: {api_path} (POST方法)", file=sys.stderr)
            if app_id:
                print(f"[RASP] 指定app_id: {app_id}", file=sys.stderr)
            else:
                print(f"[RASP] 获取所有应用的事件", file=sys.stderr)
            
            # 设置请求头（根据Network标签中的请求头）
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain, */*',
                'Origin': self.rasp_api_url,
                'Referer': f'{self.rasp_api_url}/',
            }
            
            # 获取认证Cookie
            auth_cookie = self.rasp_auth_cookie
            if not auth_cookie and self.rasp_username and self.rasp_password:
                auth_cookie = self._get_auth_cookie()
            
            # 如果配置了Cookie，添加到请求头
            if auth_cookie:
                headers['Cookie'] = auth_cookie
                print(f"[RASP] 使用Cookie认证", file=sys.stderr)
            elif self.rasp_api_key:
                # 兼容API Key方式（如果支持）
                headers['Authorization'] = f'Bearer {self.rasp_api_key}'
                headers['X-OpenRASP-Token'] = self.rasp_api_key
                print(f"[RASP] 使用API Key认证", file=sys.stderr)
            else:
                print(f"[RASP] 警告: 未配置认证信息", file=sys.stderr)
            
            print(f"[RASP] 请求头: {dict(headers)}", file=sys.stderr)
            
            # OpenRASP的API使用POST方法，请求格式根据Payload标签确定
            # 需要传递 data 对象和分页参数
            import time
            from datetime import datetime, timedelta
            
            # 计算时间范围（默认最近30天）
            end_time_ms = int(time.time() * 1000)  # 当前时间（毫秒）
            start_time_ms = int((time.time() - 30 * 24 * 3600) * 1000)  # 30天前（毫秒）
            
            # 如果配置了时间范围，使用配置的时间
            if start_time:
                try:
                    # 支持多种时间格式
                    if isinstance(start_time, str):
                        dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        start_time_ms = int(dt.timestamp() * 1000)
                    else:
                        start_time_ms = int(start_time)
                except:
                    pass
            
            if end_time:
                try:
                    if isinstance(end_time, str):
                        dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        end_time_ms = int(dt.timestamp() * 1000)
                    else:
                        end_time_ms = int(end_time)
                except:
                    pass
            
            # 构建请求数据（根据Payload标签的格式）
            request_data = {
                'data': {
                    'start_time': start_time_ms,
                    'end_time': end_time_ms,
                    'attack_type': [],  # 空数组表示获取所有攻击类型
                    'attack_source': '',
                    'app_id': app_id if app_id else '',  # 如果指定了app_id，使用它；否则为空获取所有应用
                    'url': '',
                    'header': '',
                    'request_id': '',
                    'request_method': '',
                    'intercept_state': ['block', 'log'],  # 获取拦截和记录的事件
                    'plugin_message': '',
                    'plugin_algorithm': '',
                    'server_hostname': '',
                    'stack_md5': '',
                    'stack': ''
                },
                'page': 1,
                'perpage': 100  # 每页100条记录
            }
            
            print(f"[RASP] 请求参数: {json.dumps(request_data, indent=2)}", file=sys.stderr)
            
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
                    
                    # 如果返回401/403，可能需要认证
                    if response.status_code in [401, 403]:
                        print(f"[RASP] 提示: 可能需要认证，请检查OPENRASP_API_KEY配置", file=sys.stderr)
                    
                    # 如果返回404，可能是路径不对或需要不同的参数
                    if response.status_code == 404:
                        print(f"[RASP] 提示: API路径可能不正确，或需要特定的请求参数", file=sys.stderr)
                        # 尝试不带参数的POST
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
                print(f"[RASP] API请求失败，返回模拟数据", file=sys.stderr)
                print(f"[RASP] 提示: 请检查认证信息（Cookie）和API路径", file=sys.stderr)
                print(f"[RASP] API路径: {api_path}", file=sys.stderr)
                print(f"[RASP] 文档地址: https://rasp.baidu.com/doc/install/main.html", file=sys.stderr)
                results.append({
                    'severity': 'info',
                    'type': 'RASP Connection',
                    'title': 'OpenRASP API连接失败（模拟数据）',
                    'description': f'无法连接到OpenRASP API。请检查：\n1. Cookie认证是否正确配置（OPENRASP_AUTH_COOKIE）\n2. API路径是否正确: {api_path}\n3. 网络连接是否正常\n请参考OpenRASP文档: https://rasp.baidu.com/doc/install/main.html',
                    'file_path': '',
                    'line_number': None,
                    'raw_data': {
                        'is_mock': True,
                        'reason': 'rasp_api_failed',
                        'api_url': api_path,
                        'base_url': self.rasp_api_url,
                        'status_code': response.status_code if response else 'No response',
                        'note': '请检查OpenRASP认证和API配置'
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
            import sys
            # 设置请求头
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Origin': self.rasp_api_url,
                'Referer': f'{self.rasp_api_url}/',
            }
            
            # 获取认证Cookie
            auth_cookie = self.rasp_auth_cookie
            if not auth_cookie and self.rasp_username and self.rasp_password:
                print(f"[RASP] get_rasp_status: 尝试登录获取Cookie", file=sys.stderr)
                auth_cookie = self._get_auth_cookie()
            
            # 如果配置了Cookie，添加到请求头
            if auth_cookie:
                headers['Cookie'] = auth_cookie
                print(f"[RASP] get_rasp_status: 使用Cookie认证", file=sys.stderr)
            elif self.rasp_api_key:
                headers['Authorization'] = f'Bearer {self.rasp_api_key}'
                headers['X-OpenRASP-Token'] = self.rasp_api_key
            else:
                print(f"[RASP] get_rasp_status: 警告: 未配置认证信息", file=sys.stderr)
            
            # 尝试不同的状态API路径
            status_paths = [
                f'{self.rasp_api_url}/v1/api/status',
                f'{self.rasp_api_url}/api/status',
                f'{self.rasp_api_url}/status',
            ]
            
            for status_url in status_paths:
                try:
                    print(f"[RASP] get_rasp_status: 尝试路径: {status_url}", file=sys.stderr)
                    response = requests.get(status_url, headers=headers, timeout=5)
                    print(f"[RASP] get_rasp_status: 响应状态码: {response.status_code}", file=sys.stderr)
                    
                    if response.status_code == 200:
                        return {
                            'status': 'connected',
                            'data': response.json()
                        }
                    elif response.status_code != 404:
                        # 如果不是404，说明路径存在但可能认证失败
                        return {
                            'status': 'error',
                            'message': f'HTTP {response.status_code}'
                        }
                except Exception as e:
                    print(f"[RASP] get_rasp_status: 路径 {status_url} 失败: {str(e)}", file=sys.stderr)
                    continue
            
            # 所有路径都失败
            return {
                'status': 'disconnected',
                'message': '无法连接到OpenRASP服务，请检查地址和认证信息'
            }
            
        except Exception as e:
            import sys
            import traceback
            print(f"[RASP] get_rasp_status: 异常: {str(e)}", file=sys.stderr)
            print(f"[RASP] get_rasp_status: 错误堆栈: {traceback.format_exc()}", file=sys.stderr)
            return {
                'status': 'disconnected',
                'message': str(e)
            }

