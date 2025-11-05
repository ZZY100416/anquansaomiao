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
  Space,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import api from '../services/api';

const { Option } = Select;

const Scans = () => {
  const [scans, setScans] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchScans();
    fetchProjects();
  }, []);

  const fetchScans = async () => {
    setLoading(true);
    try {
      const data = await api.get('/scans');
      setScans(data);
    } catch (error) {
      message.error('获取扫描任务失败');
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
            <Select placeholder="请选择扫描类型">
              <Option value="sast">SAST - 静态代码扫描</Option>
              <Option value="sca">SCA - 依赖漏洞扫描</Option>
              <Option value="container">容器镜像扫描</Option>
              <Option value="rasp">RASP - 运行时安全扫描</Option>
            </Select>
          </Form.Item>
          <Form.Item name="config" label="扫描配置（JSON格式）">
            <Input.TextArea
              rows={4}
              placeholder='{"image_name": "nginx:latest"}'
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Scans;

