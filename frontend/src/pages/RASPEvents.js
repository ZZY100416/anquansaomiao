import React, { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Tag,
  Button,
  message,
  Select,
  DatePicker,
  Space,
  Modal,
  Descriptions,
} from 'antd';
import {
  SyncOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import moment from 'moment';

const { RangePicker } = DatePicker;
const { Option } = Select;

const RASPEvents = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [raspStatus, setRaspStatus] = useState(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [filters, setFilters] = useState({
    app_id: '',
    severity: '',
    handled: '',
    dateRange: null,
  });

  useEffect(() => {
    fetchRASPStatus();
    fetchEvents();
  }, []);

  const fetchRASPStatus = async () => {
    try {
      const status = await api.get('/rasp/status');
      setRaspStatus(status);
    } catch (error) {
      console.error('获取RASP状态失败:', error);
    }
  };

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const params = {
        page: 1,
        per_page: 50,
      };
      
      if (filters.app_id) params.app_id = filters.app_id;
      if (filters.severity) params.severity = filters.severity;
      if (filters.handled !== '') params.handled = filters.handled;
      if (filters.dateRange && filters.dateRange.length === 2) {
        params.start_time = filters.dateRange[0].toISOString();
        params.end_time = filters.dateRange[1].toISOString();
      }
      
      const data = await api.get('/rasp/events', { params });
      setEvents(data.events || []);
    } catch (error) {
      message.error('获取RASP事件失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      await api.post('/rasp/events/sync', {
        app_id: filters.app_id || '',
      });
      message.success('同步成功');
      fetchEvents();
    } catch (error) {
      message.error('同步失败');
    }
  };

  const handleEvent = async (eventId) => {
    try {
      await api.post(`/rasp/events/${eventId}/handle`);
      message.success('已标记为已处理');
      fetchEvents();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const showDetail = (event) => {
    setSelectedEvent(event);
    setDetailVisible(true);
  };

  const getSeverityTag = (severity) => {
    const severityMap = {
      critical: { color: 'red', text: '严重' },
      high: { color: 'orange', text: '高危' },
      medium: { color: 'gold', text: '中危' },
      low: { color: 'blue', text: '低危' },
      info: { color: 'default', text: '信息' },
    };
    const config = severityMap[severity] || { color: 'default', text: severity };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '应用ID',
      dataIndex: 'app_id',
      key: 'app_id',
      width: 120,
    },
    {
      title: '攻击类型',
      dataIndex: 'attack_type',
      key: 'attack_type',
      width: 150,
    },
    {
      title: '严重级别',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity) => getSeverityTag(severity),
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: '客户端IP',
      dataIndex: 'client_ip',
      key: 'client_ip',
      width: 120,
    },
    {
      title: '事件时间',
      dataIndex: 'event_time',
      key: 'event_time',
      width: 180,
      render: (text) => (text ? moment(text).format('YYYY-MM-DD HH:mm:ss') : '-'),
    },
    {
      title: '状态',
      dataIndex: 'handled',
      key: 'handled',
      width: 100,
      render: (handled) => (
        <Tag color={handled ? 'green' : 'red'}>
          {handled ? '已处理' : '未处理'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => showDetail(record)}>
            详情
          </Button>
          {!record.handled && (
            <Button
              type="link"
              size="small"
              onClick={() => handleEvent(record.id)}
            >
              标记已处理
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>RASP运行时安全事件</h1>
        <Space>
          <Button
            icon={<SyncOutlined />}
            onClick={handleSync}
            loading={loading}
          >
            同步事件
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchEvents}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {raspStatus && (
        <Card style={{ marginBottom: 16 }}>
          <Space>
            <span>OpenRASP状态:</span>
            <Tag color={raspStatus.status === 'connected' ? 'green' : 'red'}>
              {raspStatus.status === 'connected' ? '已连接' : '未连接'}
            </Tag>
            {raspStatus.message && <span>{raspStatus.message}</span>}
          </Space>
        </Card>
      )}

      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Select
            placeholder="筛选严重级别"
            style={{ width: 150 }}
            allowClear
            value={filters.severity}
            onChange={(value) => setFilters({ ...filters, severity: value })}
          >
            <Option value="critical">严重</Option>
            <Option value="high">高危</Option>
            <Option value="medium">中危</Option>
            <Option value="low">低危</Option>
            <Option value="info">信息</Option>
          </Select>
          <Select
            placeholder="筛选处理状态"
            style={{ width: 150 }}
            allowClear
            value={filters.handled}
            onChange={(value) => setFilters({ ...filters, handled: value })}
          >
            <Option value="false">未处理</Option>
            <Option value="true">已处理</Option>
          </Select>
          <RangePicker
            showTime
            onChange={(dates) => setFilters({ ...filters, dateRange: dates })}
          />
          <Button type="primary" onClick={fetchEvents}>
            查询
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={events}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <Modal
        title="RASP事件详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={800}
      >
        {selectedEvent && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="事件ID">
              {selectedEvent.event_id}
            </Descriptions.Item>
            <Descriptions.Item label="应用ID">
              {selectedEvent.app_id}
            </Descriptions.Item>
            <Descriptions.Item label="攻击类型">
              {selectedEvent.attack_type}
            </Descriptions.Item>
            <Descriptions.Item label="严重级别">
              {getSeverityTag(selectedEvent.severity)}
            </Descriptions.Item>
            <Descriptions.Item label="消息">
              {selectedEvent.message}
            </Descriptions.Item>
            <Descriptions.Item label="请求URL">
              {selectedEvent.url}
            </Descriptions.Item>
            <Descriptions.Item label="客户端IP">
              {selectedEvent.client_ip}
            </Descriptions.Item>
            <Descriptions.Item label="User Agent">
              {selectedEvent.user_agent}
            </Descriptions.Item>
            <Descriptions.Item label="文件路径">
              {selectedEvent.file_path}
              {selectedEvent.line_number && `:${selectedEvent.line_number}`}
            </Descriptions.Item>
            <Descriptions.Item label="事件时间">
              {selectedEvent.event_time
                ? moment(selectedEvent.event_time).format('YYYY-MM-DD HH:mm:ss')
                : '-'}
            </Descriptions.Item>
            {selectedEvent.attack_params && (
              <Descriptions.Item label="攻击参数">
                <pre>{JSON.stringify(selectedEvent.attack_params, null, 2)}</pre>
              </Descriptions.Item>
            )}
            {selectedEvent.stack_trace && (
              <Descriptions.Item label="堆栈跟踪">
                <pre style={{ maxHeight: 200, overflow: 'auto' }}>
                  {selectedEvent.stack_trace}
                </pre>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default RASPEvents;

