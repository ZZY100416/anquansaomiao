import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic } from 'antd';
import {
  ProjectOutlined,
  ScanOutlined,
  BugOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import api from '../services/api';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await api.get('/reports/dashboard');
      setDashboardData(data);
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getChartOption = () => {
    if (!dashboardData) return {};

    return {
      title: {
        text: '漏洞严重级别分布',
        left: 'center',
      },
      tooltip: {
        trigger: 'item',
      },
      series: [
        {
          name: '漏洞分布',
          type: 'pie',
          radius: '50%',
          data: [
            { value: dashboardData.severity_stats.critical, name: '严重', itemStyle: { color: '#ff4d4f' } },
            { value: dashboardData.severity_stats.high, name: '高危', itemStyle: { color: '#ff7a45' } },
            { value: dashboardData.severity_stats.medium, name: '中危', itemStyle: { color: '#faad14' } },
            { value: dashboardData.severity_stats.low, name: '低危', itemStyle: { color: '#52c41a' } },
            { value: dashboardData.severity_stats.info, name: '信息', itemStyle: { color: '#1890ff' } },
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    };
  };

  if (loading) {
    return <div>加载中...</div>;
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>仪表盘</h1>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="项目总数"
              value={dashboardData?.total_projects || 0}
              prefix={<ProjectOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="扫描任务"
              value={dashboardData?.total_scans || 0}
              prefix={<ScanOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已完成扫描"
              value={dashboardData?.completed_scans || 0}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="发现漏洞"
              value={
                (dashboardData?.severity_stats?.critical || 0) +
                (dashboardData?.severity_stats?.high || 0) +
                (dashboardData?.severity_stats?.medium || 0) +
                (dashboardData?.severity_stats?.low || 0) +
                (dashboardData?.severity_stats?.info || 0)
              }
              prefix={<BugOutlined />}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="漏洞统计">
            <ReactECharts option={getChartOption()} style={{ height: 400 }} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;

