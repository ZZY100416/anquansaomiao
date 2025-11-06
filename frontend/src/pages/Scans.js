import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Select,
  Input,
  message,
  Tag,
  Descriptions,
  Space,
  Typography,
  Card,
} from 'antd';
import { PlusOutlined, EyeOutlined } from '@ant-design/icons';
import api from '../services/api';

const { Text, Paragraph } = Typography;

const { Option } = Select;

const Scans = () => {
  const [scans, setScans] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [resultsModalVisible, setResultsModalVisible] = useState(false);
  const [results, setResults] = useState([]);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [selectedScan, setSelectedScan] = useState(null);
  const [form] = Form.useForm();
  const [selectedScanType, setSelectedScanType] = useState('');

  useEffect(() => {
    fetchScans();
    fetchProjects();
  }, []);

  const fetchScans = async () => {
    setLoading(true);
    try {
      const data = await api.get('/scans');
      setScans(data || []);
    } catch (error) {
      console.error('获取扫描任务失败:', error);
      setScans([]);
      // 只在明确错误时显示消息
      if (error.response?.status !== 422) {
        message.error('获取扫描任务失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const data = await api.get('/projects');
      setProjects(data);
    } catch (error) {
      console.error('获取项目列表失败:', error);
    }
  };

  const handleCreate = () => {
    form.resetFields();
    setModalVisible(true);
  };

  const handleSubmit = async (values) => {
    try {
      await api.post('/scans', values);
      message.success('扫描任务已创建');
      setModalVisible(false);
      fetchScans();
    } catch (error) {
      message.error('创建扫描任务失败');
    }
  };

  const handleViewResults = async (scan) => {
    setSelectedScan(scan);
    setResultsModalVisible(true);
    setResultsLoading(true);
    try {
      const data = await api.get(`/scans/${scan.id}/results`);
      setResults(data || []);
      if (!data || data.length === 0) {
        message.info('该扫描任务暂无结果');
      }
    } catch (error) {
      console.error('获取扫描结果失败:', error);
      message.error('获取扫描结果失败');
      setResults([]);
    } finally {
      setResultsLoading(false);
    }
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

  const getStatusTag = (status) => {
    const statusMap = {
      pending: { color: 'default', text: '等待中' },
      running: { color: 'processing', text: '运行中' },
      completed: { color: 'success', text: '已完成' },
      failed: { color: 'error', text: '失败' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getScanTypeTag = (type) => {
    const typeMap = {
      sast: { color: 'blue', text: 'SAST' },
      sca: { color: 'green', text: 'SCA' },
      container: { color: 'orange', text: '容器扫描' },
      rasp: { color: 'red', text: 'RASP' },
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getConfigPlaceholder = (scanType) => {
    const placeholders = {
      sast: '{}  // SAST扫描不需要配置',
      sca: '{}  // SCA扫描不需要配置',
      container: '{"image_name": "nginx:latest"}  // 必需：镜像名称',
      rasp: '{"app_id": "your-app-id"}  // 必需：应用ID，可选：start_time, end_time',
    };
    return placeholders[scanType] || '{}';
  };

  const getConfigHelp = (scanType) => {
    const helpTexts = {
      sast: 'SAST扫描会自动扫描项目代码，无需配置',
      sca: 'SCA扫描会自动扫描项目依赖，无需配置',
      container: '必需字段：image_name（镜像名称，如 "nginx:latest"）',
      rasp: '必需字段：app_id（应用ID）。可选：start_time（开始时间），end_time（结束时间）',
    };
    return helpTexts[scanType] || '请填写JSON格式的扫描配置';
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '项目ID',
      dataIndex: 'project_id',
      key: 'project_id',
      width: 100,
    },
    {
      title: '扫描类型',
      dataIndex: 'scan_type',
      key: 'scan_type',
      render: (type) => getScanTypeTag(type),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => getStatusTag(status),
    },
    {
      title: '结果数量',
      dataIndex: 'result_count',
      key: 'result_count',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => (text ? new Date(text).toLocaleString() : '-'),
    },
    {
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      render: (text) => (text ? new Date(text).toLocaleString() : '-'),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => handleViewResults(record)}
          disabled={record.status !== 'completed'}
        >
          查看结果
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>扫描任务</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreate}
        >
          新建扫描
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={scans}
        rowKey="id"
        loading={loading}
      />
      <Modal
        title="新建扫描任务"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} onFinish={handleSubmit} layout="vertical">
          <Form.Item
            name="project_id"
            label="选择项目"
            rules={[{ required: true, message: '请选择项目' }]}
          >
            <Select placeholder="请选择项目">
              {projects.map((project) => (
                <Option key={project.id} value={project.id}>
                  {project.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="scan_type"
            label="扫描类型"
            rules={[{ required: true, message: '请选择扫描类型' }]}
          >
            <Select 
              placeholder="请选择扫描类型"
              onChange={(value) => {
                setSelectedScanType(value);
                // 根据扫描类型设置默认配置
                if (value === 'sast' || value === 'sca') {
                  form.setFieldsValue({ config: '{}' });
                } else if (value === 'container') {
                  form.setFieldsValue({ config: '{"image_name": "nginx:latest"}' });
                } else if (value === 'rasp') {
                  form.setFieldsValue({ config: '{"app_id": "your-app-id"}' });
                }
              }}
            >
              <Option value="sast">SAST - 静态代码扫描</Option>
              <Option value="sca">SCA - 依赖漏洞扫描</Option>
              <Option value="container">容器镜像扫描</Option>
              <Option value="rasp">RASP - 运行时安全扫描</Option>
            </Select>
          </Form.Item>
          <Form.Item 
            name="config" 
            label="扫描配置（JSON格式）"
            help={getConfigHelp(selectedScanType)}
          >
            <Input.TextArea
              rows={4}
              placeholder={getConfigPlaceholder(selectedScanType)}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 扫描结果详情Modal */}
      <Modal
        title={`扫描结果详情 - ${selectedScan ? `扫描ID: ${selectedScan.id}` : ''}`}
        open={resultsModalVisible}
        onCancel={() => {
          setResultsModalVisible(false);
          setSelectedScan(null);
          setResults([]);
        }}
        footer={null}
        width={1000}
      >
        {selectedScan && (
          <div>
            <Descriptions column={2} bordered style={{ marginBottom: 16 }}>
              <Descriptions.Item label="扫描类型">
                {getScanTypeTag(selectedScan.scan_type)}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                {getStatusTag(selectedScan.status)}
              </Descriptions.Item>
              <Descriptions.Item label="结果数量">
                {results.length} 个
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {selectedScan.created_at
                  ? new Date(selectedScan.created_at).toLocaleString()
                  : '-'}
              </Descriptions.Item>
            </Descriptions>

            {resultsLoading ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                加载中...
              </div>
            ) : results.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Paragraph>暂无扫描结果</Paragraph>
              </div>
            ) : (
              <div>
                <h3 style={{ marginBottom: 16 }}>漏洞详情</h3>
                {results.map((result, index) => (
                  <Card
                    key={result.id || index}
                    style={{ marginBottom: 16 }}
                    title={
                      <Space>
                        {getSeverityTag(result.severity)}
                        <Text strong>{result.title || result.vulnerability_type}</Text>
                      </Space>
                    }
                  >
                    <Descriptions column={1} size="small">
                      <Descriptions.Item label="漏洞类型">
                        {result.vulnerability_type || '-'}
                      </Descriptions.Item>
                      <Descriptions.Item label="描述">
                        <Paragraph style={{ margin: 0 }}>
                          {result.description || '-'}
                        </Paragraph>
                      </Descriptions.Item>
                      {result.file_path && (
                        <Descriptions.Item label="文件路径">
                          {result.file_path}
                          {result.line_number && `:${result.line_number}`}
                        </Descriptions.Item>
                      )}
                      {result.cve_id && (
                        <Descriptions.Item label="CVE ID">
                          <Text code>{result.cve_id}</Text>
                        </Descriptions.Item>
                      )}
                      {result.package_name && (
                        <Descriptions.Item label="包名">
                          {result.package_name}
                          {result.package_version && ` (${result.package_version})`}
                        </Descriptions.Item>
                      )}
                      {result.fixed_version && (
                        <Descriptions.Item label="修复版本">
                          <Text type="success">{result.fixed_version}</Text>
                        </Descriptions.Item>
                      )}
                      {result.raw_data && (
                        <Descriptions.Item label="原始数据">
                          <pre
                            style={{
                              maxHeight: 200,
                              overflow: 'auto',
                              fontSize: 12,
                              background: '#f5f5f5',
                              padding: 8,
                              borderRadius: 4,
                            }}
                          >
                            {typeof result.raw_data === 'string'
                              ? result.raw_data
                              : JSON.stringify(result.raw_data, null, 2)}
                          </pre>
                        </Descriptions.Item>
                      )}
                    </Descriptions>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Scans;

