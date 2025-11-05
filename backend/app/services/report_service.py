from app.models.scan import Scan, ScanResult
from datetime import datetime

class ReportService:
    def generate_html_report(self, scan_id):
        """生成HTML格式报告"""
        scan = Scan.query.get(scan_id)
        if not scan:
            return {'error': '扫描任务不存在'}
        
        results = ScanResult.query.filter_by(scan_id=scan_id).all()
        
        # 按严重级别分组
        severity_groups = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
        for result in results:
            if result.severity in severity_groups:
                severity_groups[result.severity].append(result.to_dict())
        
        return {
            'scan': scan.to_dict(),
            'summary': {
                'total': len(results),
                'critical': len(severity_groups['critical']),
                'high': len(severity_groups['high']),
                'medium': len(severity_groups['medium']),
                'low': len(severity_groups['low']),
                'info': len(severity_groups['info'])
            },
            'results': severity_groups
        }
    
    def generate_pdf_report(self, scan_id):
        """生成PDF格式报告（简化实现）"""
        # 这里应该使用ReportLab等库生成PDF
        # 为简化，返回HTML内容
        html_report = self.generate_html_report(scan_id)
        
        html_content = f"""
        <html>
        <head><title>安全扫描报告 - {scan_id}</title></head>
        <body>
            <h1>安全扫描报告</h1>
            <p>扫描ID: {scan_id}</p>
            <p>扫描类型: {html_report['scan']['scan_type']}</p>
            <p>总漏洞数: {html_report['summary']['total']}</p>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8')

