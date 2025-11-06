import subprocess
import json
import os
from datetime import datetime
from app import db
from app.models.scan import Scan, ScanResult
from app.scanners.sast_scanner import SASTScanner
from app.scanners.sca_scanner import SCAScanner
from app.scanners.container_scanner import ContainerScanner
from app.scanners.rasp_scanner import RASPScanner

class ScannerService:
    def __init__(self):
        self.sast_scanner = SASTScanner()
        self.sca_scanner = SCAScanner()
        self.container_scanner = ContainerScanner()
        self.rasp_scanner = RASPScanner()
    
    def start_scan(self, scan_id):
        import sys
        scan = Scan.query.get(scan_id)
        if not scan:
            raise ValueError(f"扫描任务 {scan_id} 不存在")
        
        scan.status = 'running'
        scan.started_at = datetime.utcnow()
        db.session.commit()
        
        print(f'[ScannerService] 开始执行扫描: scan_id={scan_id}, type={scan.scan_type}', file=sys.stderr)
        
        try:
            print(f'[ScannerService] 准备调用扫描器: type={scan.scan_type}', file=sys.stderr)
            
            if scan.scan_type == 'sast':
                print(f'[ScannerService] 调用SAST扫描器', file=sys.stderr)
                results = self.sast_scanner.scan(scan)
            elif scan.scan_type == 'sca':
                print(f'[ScannerService] 调用SCA扫描器', file=sys.stderr)
                results = self.sca_scanner.scan(scan)
            elif scan.scan_type == 'container':
                print(f'[ScannerService] 调用容器扫描器', file=sys.stderr)
                results = self.container_scanner.scan(scan)
            elif scan.scan_type == 'rasp':
                print(f'[ScannerService] 调用RASP扫描器', file=sys.stderr)
                results = self.rasp_scanner.scan(scan)
            else:
                raise ValueError(f"不支持的扫描类型: {scan.scan_type}")
            
            print(f'[ScannerService] 扫描器调用完成，返回 {len(results)} 个结果', file=sys.stderr)
            
            print(f'[ScannerService] 扫描器返回 {len(results)} 个结果', file=sys.stderr)
            
            # 保存扫描结果
            saved_count = 0
            for result_data in results:
                try:
                    result = ScanResult(
                        scan_id=scan_id,
                        severity=result_data.get('severity', 'info'),
                        vulnerability_type=result_data.get('type', ''),
                        title=result_data.get('title', ''),
                        description=result_data.get('description', ''),
                        file_path=result_data.get('file_path', ''),
                        line_number=result_data.get('line_number'),
                        cve_id=result_data.get('cve_id', ''),
                        package_name=result_data.get('package_name', ''),
                        package_version=result_data.get('package_version', ''),
                        fixed_version=result_data.get('fixed_version', ''),
                        raw_data=json.dumps(result_data.get('raw_data', {}))
                    )
                    db.session.add(result)
                    saved_count += 1
                except Exception as e:
                    print(f'[ScannerService] 保存结果失败: {str(e)}, result_data={result_data}', file=sys.stderr)
            
            db.session.commit()
            print(f'[ScannerService] 成功保存 {saved_count} 个扫描结果', file=sys.stderr)
            
            scan.status = 'completed'
            scan.completed_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            import traceback
            print(f'[ScannerService] 扫描执行失败: {str(e)}', file=sys.stderr)
            print(f'[ScannerService] 错误堆栈: {traceback.format_exc()}', file=sys.stderr)
            scan.status = 'failed'
            scan.completed_at = datetime.utcnow()
            db.session.commit()
            raise e

