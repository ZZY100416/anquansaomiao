import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const Reports = () => {
  return (
    <div>
      <Title level={2}>报告中心</Title>
      <Card>
        <p>报告功能开发中...</p>
        <p>您可以查看扫描任务的详细结果，并导出PDF/HTML格式的安全报告。</p>
      </Card>
    </div>
  );
};

export default Reports;

