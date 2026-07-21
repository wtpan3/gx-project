import React, { useState, useEffect } from 'react';
import {
  Table, Button, Input, Select, Space, Drawer, Descriptions,
  Modal, Form, DatePicker, message, Popconfirm, Tag
} from 'antd';
import { PlusOutlined, SearchOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { WbsTask, WbsTaskCreate } from '../../types/wbs';
import { wbsApi } from '../../services/wbsService';
import './index.css';

const { Option } = Select;
const { RangePicker } = DatePicker;

const ProjectPlan: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<WbsTask[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // 筛选条件
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [keyword, setKeyword] = useState('');

  // 详情抽屉
  const [detailVisible, setDetailVisible] = useState(false);
  const [currentTask, setCurrentTask] = useState<WbsTask | null>(null);

  // 新增对话框
  const [createVisible, setCreateVisible] = useState(false);
  const [form] = Form.useForm();

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      const params: any = { page, page_size: pageSize };
      if (statusFilter) params.status = statusFilter;
      if (keyword.trim()) params.keyword = keyword.trim();

      const response = await wbsApi.getWbsTasks(params);
      setDataSource(response.items);
      setTotal(response.total);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, statusFilter, keyword]);

  // 查看详情
  const handleViewDetail = async (record: WbsTask) => {
    try {
      const detail = await wbsApi.getWbsTaskDetail(record.id);
      setCurrentTask(detail);
      setDetailVisible(true);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取详情失败');
    }
  };

  // 删除任务
  const handleDelete = async (id: number) => {
    try {
      await wbsApi.deleteWbsTask(id);
      message.success('删除成功');
      loadData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  // 创建任务
  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      const data: WbsTaskCreate = {
        ...values,
        plan_start_date: values.plan_dates ? values.plan_dates[0].format('YYYY-MM-DD') : undefined,
        plan_end_date: values.plan_dates ? values.plan_dates[1].format('YYYY-MM-DD') : undefined,
      };
      delete (data as any).plan_dates;

      await wbsApi.createWbsTask(data);
      message.success('创建成功');
      setCreateVisible(false);
      form.resetFields();
      loadData();
    } catch (error: any) {
      if (error.errorFields) return;
      message.error(error.response?.data?.detail || '创建失败');
    }
  };

  // 优先级Tag颜色
  const getPriorityColor = (priority: string) => {
    const colorMap: Record<string, string> = { 高: 'red', 中: 'orange', 低: 'blue' };
    return colorMap[priority] || 'default';
  };

  // 状态Tag颜色
  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      待开始: 'default',
      进行中: 'processing',
      已完成: 'success',
      已暂停: 'warning',
    };
    return colorMap[status] || 'default';
  };

  // 表格列定义
  const columns: ColumnsType<WbsTask> = [
    { title: 'ID', dataIndex: 'id', width: 60, fixed: 'left' },
    { title: '任务编码', dataIndex: 'task_code', width: 120, fixed: 'left' },
    { title: '建设年份', dataIndex: 'construction_year', width: 100 },
    { title: 'L1-项目阶段', dataIndex: 'project_phase_l1', width: 140 },
    { title: 'L2-子阶段', dataIndex: 'sub_phase_l2', width: 140 },
    { title: 'L3-任务包', dataIndex: 'task_package_l3', width: 140 },
    { title: 'L4-工作内容', dataIndex: 'work_content_l4', width: 200 },
    { title: 'L5-工作明细', dataIndex: 'work_detail_l5', width: 160, ellipsis: true },
    {
      title: '优先级',
      dataIndex: 'priority',
      width: 90,
      render: (priority: string) => <Tag color={getPriorityColor(priority)}>{priority}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status: string) => <Tag color={getStatusColor(status)}>{status}</Tag>,
    },
    { title: '计划开始', dataIndex: 'plan_start_date', width: 120 },
    { title: '计划完成', dataIndex: 'plan_end_date', width: 120 },
    { title: '责任人', dataIndex: 'assignee_name', width: 100 },
    { title: '关联学校', dataIndex: 'school_name', width: 140, ellipsis: true },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          <Popconfirm
            title="确定删除此任务吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="project-plan-container">
      <div className="page-header">
        <h2>WBS任务管理</h2>
      </div>

      {/* 筛选栏 */}
      <div className="filter-bar">
        <Space size="middle">
          <Select
            placeholder="状态筛选"
            style={{ width: 140 }}
            allowClear
            value={statusFilter}
            onChange={setStatusFilter}
          >
            <Option value="待开始">待开始</Option>
            <Option value="进行中">进行中</Option>
            <Option value="已完成">已完成</Option>
            <Option value="已暂停">已暂停</Option>
          </Select>

          <Input
            placeholder="搜索L4工作内容"
            prefix={<SearchOutlined />}
            style={{ width: 240 }}
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            allowClear
          />

          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateVisible(true)}>
            新增任务
          </Button>
        </Space>
      </div>

      {/* 数据表格 */}
      <Table
        columns={columns}
        dataSource={dataSource}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1800 }}
        pagination={{
          current: page,
          pageSize,
          total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPage(page);
            setPageSize(pageSize);
          },
        }}
      />

      {/* 详情抽屉 */}
      <Drawer
        title="任务详情"
        width={720}
        open={detailVisible}
        onClose={() => setDetailVisible(false)}
      >
        {currentTask && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="任务编码" span={2}>{currentTask.task_code}</Descriptions.Item>
            <Descriptions.Item label="建设年份">{currentTask.construction_year}</Descriptions.Item>
            <Descriptions.Item label="优先级">
              <Tag color={getPriorityColor(currentTask.priority)}>{currentTask.priority}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="状态" span={2}>
              <Tag color={getStatusColor(currentTask.status)}>{currentTask.status}</Tag>
            </Descriptions.Item>

            <Descriptions.Item label="L1-项目阶段" span={2}>{currentTask.project_phase_l1}</Descriptions.Item>
            <Descriptions.Item label="L2-子阶段" span={2}>{currentTask.sub_phase_l2}</Descriptions.Item>
            <Descriptions.Item label="L3-任务包" span={2}>{currentTask.task_package_l3}</Descriptions.Item>
            <Descriptions.Item label="L4-工作内容" span={2}>{currentTask.work_content_l4}</Descriptions.Item>
            <Descriptions.Item label="L5-工作明细" span={2}>{currentTask.work_detail_l5 || '-'}</Descriptions.Item>

            <Descriptions.Item label="计划开始">{currentTask.plan_start_date || '-'}</Descriptions.Item>
            <Descriptions.Item label="计划完成">{currentTask.plan_end_date || '-'}</Descriptions.Item>
            <Descriptions.Item label="实际开始">{currentTask.actual_start_date || '-'}</Descriptions.Item>
            <Descriptions.Item label="实际完成">{currentTask.actual_end_date || '-'}</Descriptions.Item>

            <Descriptions.Item label="责任人">{currentTask.assignee_name || '-'}</Descriptions.Item>
            <Descriptions.Item label="关联学校">{currentTask.school_name || '-'}</Descriptions.Item>

            <Descriptions.Item label="进度说明" span={2}>{currentTask.progress_note || '-'}</Descriptions.Item>
            <Descriptions.Item label="交付物" span={2}>{currentTask.deliverables || '-'}</Descriptions.Item>

            <Descriptions.Item label="创建时间" span={2}>{currentTask.created_at}</Descriptions.Item>
            <Descriptions.Item label="更新时间" span={2}>{currentTask.updated_at}</Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>

      {/* 新增任务对话框 */}
      <Modal
        title="新增WBS任务"
        open={createVisible}
        onOk={handleCreate}
        onCancel={() => {
          setCreateVisible(false);
          form.resetFields();
        }}
        width={800}
        okText="创建"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item label="任务编码" name="task_code" rules={[{ required: true, message: '请输入任务编码' }]}>
            <Input placeholder="如: WBS-T999" />
          </Form.Item>

          <Form.Item label="建设年份" name="construction_year" rules={[{ required: true }]}>
            <Input placeholder="如: 2026" />
          </Form.Item>

          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item label="L1-项目阶段" name="project_phase_l1" style={{ flex: 1 }} rules={[{ required: true }]}>
              <Input placeholder="如: 交付实施" />
            </Form.Item>
            <Form.Item label="L2-子阶段" name="sub_phase_l2" style={{ flex: 1 }} rules={[{ required: true }]}>
              <Input placeholder="如: 硬件交付" />
            </Form.Item>
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item label="L3-任务包" name="task_package_l3" style={{ flex: 1 }} rules={[{ required: true }]}>
              <Input placeholder="如: 设备交付" />
            </Form.Item>
            <Form.Item label="L4-工作内容" name="work_content_l4" style={{ flex: 1 }} rules={[{ required: true }]}>
              <Input placeholder="如: A校设备到货验收" />
            </Form.Item>
          </div>

          <Form.Item label="L5-工作明细" name="work_detail_l5">
            <Input placeholder="详细工作说明（可选）" />
          </Form.Item>

          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item label="优先级" name="priority" initialValue="中" style={{ flex: 1 }}>
              <Select>
                <Option value="高">高</Option>
                <Option value="中">中</Option>
                <Option value="低">低</Option>
              </Select>
            </Form.Item>
            <Form.Item label="状态" name="status" initialValue="待开始" style={{ flex: 1 }}>
              <Select>
                <Option value="待开始">待开始</Option>
                <Option value="进行中">进行中</Option>
                <Option value="已完成">已完成</Option>
                <Option value="已暂停">已暂停</Option>
              </Select>
            </Form.Item>
          </div>

          <Form.Item label="计划日期" name="plan_dates">
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>

          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item label="责任人ID" name="responsible_person_id" style={{ flex: 1 }}>
              <Input type="number" placeholder="如: 1" />
            </Form.Item>
            <Form.Item label="关联学校ID" name="school_id" style={{ flex: 1 }}>
              <Input type="number" placeholder="如: 1" />
            </Form.Item>
          </div>

          <Form.Item label="进度说明" name="progress_note">
            <Input.TextArea rows={2} placeholder="任务进展说明（可选）" />
          </Form.Item>

          <Form.Item label="交付物" name="deliverables">
            <Input placeholder="交付物说明（可选）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ProjectPlan;
