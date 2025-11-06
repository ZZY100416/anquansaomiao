import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Tag,
  Upload,
  Space,
  Descriptions,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined, FileOutlined } from '@ant-design/icons';
import api from '../services/api';
import axios from 'axios';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProject, setUploadProject] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);
  const [editingProject, setEditingProject] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const data = await api.get('/projects');
      setProjects(data || []);
    } catch (error) {
      // 如果API返回错误，设置空数组，不显示错误（可能是422但不影响功能）
      console.error('获取项目列表失败:', error);
      setProjects([]);
      // 只在明确错误时显示消息
      if (error.response?.status !== 422) {
        message.error('获取项目列表失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingProject(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingProject(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/projects/${id}`);
      message.success('删除成功');
      fetchProjects();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleUpload = (project) => {
    setUploadProject(project);
    setUploadModalVisible(true);
    fetchFileInfo(project.id);
  };

  const fetchFileInfo = async (projectId) => {
    try {
      const data = await api.get(`/projects/${projectId}/files`);
      setFileInfo(data);
    } catch (error) {
      console.error('获取文件信息失败:', error);
      setFileInfo({ has_files: false });
    }
  };

  const handleFileUpload = async (options) => {
    const { file, onSuccess, onError } = options;
    setUploading(true);
    
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('开始上传文件:', file.name, '大小:', file.size, '项目ID:', uploadProject?.id);
      
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
      const response = await axios.post(
        `${API_BASE_URL}/projects/${uploadProject.id}/upload`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            console.log('上传进度:', percentCompleted + '%');
          },
        }
      );
      
      console.log('上传成功，响应:', response.data);
      message.success(`文件上传成功！${response.data.file_count ? `共 ${response.data.file_count} 个文件` : ''}`);
      
      // 调用onSuccess，让Upload组件知道上传成功
      if (onSuccess) {
        onSuccess(response.data, file);
      }
      
      // 延迟刷新文件信息，确保后端文件已保存
      setTimeout(() => {
        fetchFileInfo(uploadProject.id);
      }, 500);
      
      fetchProjects();
    } catch (error) {
      console.error('上传失败:', error);
      console.error('错误详情:', error.response?.data);
      const errorMsg = error.response?.data?.error || error.message || '上传失败';
      message.error(errorMsg);
      if (onError) {
        onError(error);
      }
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingProject) {
        await api.put(`/projects/${editingProject.id}`, values);
        message.success('更新成功');
      } else {
        await api.post('/projects', values);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchProjects();
    } catch (error) {
      message.error(editingProject ? '更新失败' : '创建失败');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '项目类型',
      dataIndex: 'project_type',
      key: 'project_type',
      render: (type) => (type ? <Tag>{type}</Tag> : '-'),
    },
    {
      title: '扫描次数',
      dataIndex: 'scan_count',
      key: 'scan_count',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text) => (text ? new Date(text).toLocaleString() : '-'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<UploadOutlined />}
            onClick={() => handleUpload(record)}
          >
            上传文件
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个项目吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>项目管理</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleCreate}
        >
          新建项目
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={projects}
        rowKey="id"
        loading={loading}
      />
      <Modal
        title={editingProject ? '编辑项目' : '新建项目'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} onFinish={handleSubmit} layout="vertical">
          <Form.Item
            name="name"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="description" label="项目描述">
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item name="repository_url" label="代码仓库地址">
            <Input />
          </Form.Item>
          <Form.Item name="project_type" label="项目类型">
            <Input placeholder="如: java, python, nodejs, docker" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 文件上传Modal */}
      <Modal
        title={`上传项目文件 - ${uploadProject?.name || ''}`}
        open={uploadModalVisible}
        onCancel={() => {
          setUploadModalVisible(false);
          setUploadProject(null);
          setFileInfo(null);
        }}
        footer={[
          <Button key="refresh" onClick={() => uploadProject && fetchFileInfo(uploadProject.id)}>
            刷新状态
          </Button>,
          <Button key="close" onClick={() => {
            setUploadModalVisible(false);
            setUploadProject(null);
            setFileInfo(null);
          }}>
            关闭
          </Button>,
        ]}
        width={600}
      >
        {uploadProject && (
          <div>
            <Descriptions column={1} bordered style={{ marginBottom: 16 }}>
              <Descriptions.Item label="项目ID">{uploadProject.id}</Descriptions.Item>
              <Descriptions.Item label="项目名称">{uploadProject.name}</Descriptions.Item>
              <Descriptions.Item label="项目类型">
                {uploadProject.project_type || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="文件状态">
                {fileInfo?.has_files ? (
                  <Space>
                    <Tag color="green">已上传</Tag>
                    <span>{fileInfo.file_count} 个文件</span>
                    <span>({(fileInfo.total_size / 1024 / 1024).toFixed(2)} MB)</span>
                  </Space>
                ) : (
                  <Tag color="default">未上传</Tag>
                )}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginBottom: 16 }}>
              <h4>上传说明：</h4>
              <ul style={{ paddingLeft: 20, marginBottom: 16 }}>
                <li>支持上传ZIP压缩包，会自动解压</li>
                <li>支持上传单个文件</li>
                <li>上传的文件将用于SAST和SCA扫描</li>
                <li>文件路径：<code>/app/uploaded_files/project_{uploadProject.id}</code></li>
              </ul>
            </div>

            <Upload
              customRequest={handleFileUpload}
              showUploadList={true}
              maxCount={1}
              accept=".zip,.tar,.tar.gz,.gz"
              beforeUpload={(file) => {
                // 验证文件大小（限制100MB）
                const isLt100M = file.size / 1024 / 1024 < 100;
                if (!isLt100M) {
                  message.error('文件大小不能超过100MB');
                  return Upload.LIST_IGNORE;
                }
                // 不在这里上传，使用customRequest
                return false;
              }}
              onChange={(info) => {
                console.log('Upload onChange:', info);
                // 如果上传成功，刷新文件信息
                if (info.file.status === 'done') {
                  setTimeout(() => {
                    fetchFileInfo(uploadProject.id);
                  }, 1000);
                }
              }}
            >
              <Button
                type="primary"
                icon={<UploadOutlined />}
                loading={uploading}
                block
                disabled={uploading}
              >
                {uploading ? '上传中...' : '选择文件上传'}
              </Button>
            </Upload>
            {uploading && (
              <div style={{ marginTop: 8, textAlign: 'center' }}>
                <span>正在上传，请稍候...</span>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Projects;

