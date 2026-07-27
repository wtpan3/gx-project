import React, { useState, useEffect } from 'react';
import {
  Card, Tabs, Input, Select, Button, Space, Table, Modal, Row, Col,
  Form, DatePicker, message, Tag, Progress, Statistic, Upload, List, Popconfirm
} from 'antd';
import {
  SearchOutlined, PlusOutlined, ExportOutlined, ImportOutlined,
  BarChartOutlined, UnorderedListOutlined, AppstoreOutlined, ReloadOutlined,
  UploadOutlined, DeleteOutlined, PaperClipOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import api from '../../services/api';
import dayjs from 'dayjs';
import './index.css';

const { Option } = Select;
const API_BASE = '/api/v1';
const FILE_HOST = ''; // api 实例已带 baseURL(host)，静态文件用相对路径即可

interface SummaryData {
  overall_progress: number;
  doing_count: number;
  delayed_count: number;
  my_tasks_count: number;
}

interface TaskItem {
  id: number;
  task_code: string;
  level: number;
  l1: string;
  l2: string;
  l3: string;
  l4: string;
  assignee_name: string;
  assignee_id?: number;
  school_name: string;
  school_id?: number;
  plan_start_date: string;
  plan_end_date: string;
  status: string;
  priority: string;
  stage_type: string;
  progress_note: string;
  progress?: number;
  parent_id?: number;
}

interface KanbanColumn {
  count: number;
  items: Array<{
    id: number;
    title: string;
    parent: string;
    assignee_name: string;
    school_name: string;
    is_delayed: boolean;
    delay_days: number;
  }>;
}

const ProjectPlan: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState<'gantt' | 'list' | 'kanban'>('gantt');
  
  // 汇总数据
  const [summary, setSummary] = useState<SummaryData>({
    overall_progress: 0,
    doing_count: 0,
    delayed_count: 0,
    my_tasks_count: 0
  });

  // 筛选条件
  const [filters, setFilters] = useState<{
    keyword: string;
    status: string | undefined;
    responsible_person_id: number | undefined;
    school_id: number | undefined;
    date_from?: string;
    date_to?: string;
    delayed?: boolean;
  }>({
    keyword: '',
    status: undefined,
    responsible_person_id: undefined,
    school_id: undefined
  });

  // 筛选选项
  const [filterOptions, setFilterOptions] = useState<{
    statuses: string[];
    assignees: Array<{ id: number; name: string }>;
    schools: Array<{ id: number; name: string }>;
  }>({
    statuses: [],
    assignees: [],
    schools: []
  });

  // 任务数据
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [kanbanData, setKanbanData] = useState<Record<string, KanbanColumn>>({});
  
  // 分页
  const [pagination, setPagination] = useState({ page: 1, pageSize: 50, total: 0 });

  // 任务详情抽屉
  const [detailVisible, setDetailVisible] = useState(false);
  const [currentTask, setCurrentTask] = useState<any>(null);

  // 佐证材料(设计§6.7.2)
  const [attachments, setAttachments] = useState<Array<{
    id: number; file_name: string; file_url: string; file_size: number;
    description: string; uploaded_at: string;
  }>>([]);
  const [uploadDesc, setUploadDesc] = useState('');

  // 新增/编辑任务弹窗
  const [taskModalVisible, setTaskModalVisible] = useState(false);
  const [taskForm] = Form.useForm();
  // 父任务下拉选项 + 选中父任务后自动确定的层级
  const [parentOptions, setParentOptions] = useState<Array<{ id: number; level: number; label: string }>>([]);
  const [childLevel, setChildLevel] = useState<string>('选择父任务后自动确定');

  // 筛选草稿(绑定控件,点「查询」才应用到 filters 触发加载)
  const [draftFilters, setDraftFilters] = useState<{
    keyword: string;
    status: string | undefined;
    responsible_person_id: number | undefined;
    school_id: number | undefined;
    date_from?: string;
    date_to?: string;
    delayed?: boolean;
  }>({ keyword: '', status: undefined, responsible_person_id: undefined, school_id: undefined });

  // 状态选择浮层(点状态标签弹出,fixed 定位)
  const [statusPopover, setStatusPopover] = useState<{
    taskId: number; current: string; top: number; left: number;
  } | null>(null);

  // 列表行内编辑当前单元格
  const [editingCell, setEditingCell] = useState<{ id: number; field: string } | null>(null);

  // 层级折叠:被折叠(收起)的父任务 key 集合
  const [collapsedKeys, setCollapsedKeys] = useState<Set<number>>(new Set());

  // 批量操作:勾选的行
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  // 加载汇总数据
  const loadSummary = async () => {
    try {
      // 传当前用户ID，后端才能正确统计"我的任务"数量
      let userId = 0;
      try { userId = JSON.parse(localStorage.getItem('user') || '{}').id || 0; } catch { userId = 0; }
      const response = await api.get(`${API_BASE}/project-plan/summary`, {
        params: userId ? { current_user_id: userId } : {}
      });
      setSummary(response.data);
    } catch (error: any) {
      message.error('加载汇总数据失败');
    }
  };

  // 加载筛选选项
  const loadFilterOptions = async () => {
    try {
      const response = await api.get(`${API_BASE}/project-plan/filters`);
      setFilterOptions(response.data);
    } catch (error: any) {
      message.error('加载筛选选项失败');
    }
  };

  // 加载可选父任务列表(新增任务下拉用)
  const loadParentOptions = async () => {
    try {
      const res = await api.get(`${API_BASE}/project-plan/parent-options`);
      setParentOptions(res.data.items || []);
    } catch (error: any) {
      setParentOptions([]);
    }
  };

  // 加载任务列表（甘特图/列表视图）
  const loadTasks = async () => {
    setLoading(true);
    try {
      const endpoint = activeView === 'gantt' ? 'gantt' : 'list';
      const params: any = { ...filters };
      
      if (activeView === 'list') {
        params.page = pagination.page;
        params.page_size = pagination.pageSize;
      }

      const response = await api.get(`${API_BASE}/project-plan/${endpoint}`, { params });
      
      if (activeView === 'list') {
        setTasks(response.data.items);
        setPagination(prev => ({ ...prev, total: response.data.total }));
      } else {
        setTasks(response.data.items);
      }
    } catch (error: any) {
      message.error('加载任务数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载看板数据
  const loadKanban = async () => {
    setLoading(true);
    try {
      const params: any = { ...filters };
      const response = await api.get(`${API_BASE}/project-plan/kanban`, { params });
      setKanbanData(response.data.columns);
    } catch (error: any) {
      message.error('加载看板数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 查看任务详情
  const viewTaskDetail = async (taskId: number) => {
    try {
      const response = await api.get(`${API_BASE}/project-plan/tasks/${taskId}`);
      setCurrentTask(response.data);
      setDetailVisible(true);
      loadAttachments(taskId);
    } catch (error: any) {
      message.error('加载任务详情失败');
    }
  };

  // 加载某任务的佐证材料
  const loadAttachments = async (taskId: number) => {
    try {
      const res = await api.get(`${API_BASE}/project-plan/tasks/${taskId}/attachments`);
      setAttachments(res.data.items || []);
    } catch (error: any) {
      setAttachments([]);
    }
  };

  // 上传佐证材料(antd Upload customRequest)
  const uploadAttachment = async (file: File) => {
    if (!currentTask?.id) return;
    const form = new FormData();
    form.append('file', file);
    if (uploadDesc) form.append('description', uploadDesc);
    try {
      await api.post(`${API_BASE}/project-plan/tasks/${currentTask.id}/attachments`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      message.success('上传成功');
      setUploadDesc('');
      loadAttachments(currentTask.id);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败');
    }
  };

  // 删除佐证材料
  const deleteAttachment = async (attachmentId: number) => {
    try {
      await api.delete(`${API_BASE}/project-plan/attachments/${attachmentId}`);
      message.success('已删除');
      if (currentTask?.id) loadAttachments(currentTask.id);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  // 刷新当前视图数据
  const reloadCurrentView = () => {
    if (activeView === 'kanban') loadKanban(); else loadTasks();
    loadSummary();
  };

  // 应用筛选(点「查询」)
  const applyFilters = () => {
    setPagination(prev => ({ ...prev, page: 1 }));
    setFilters({ ...draftFilters });
  };

  // 重置筛选(点「重置」)
  const resetFilters = () => {
    const empty = { keyword: '', status: undefined, responsible_person_id: undefined, school_id: undefined, date_from: undefined, date_to: undefined };
    setDraftFilters(empty);
    setPagination(prev => ({ ...prev, page: 1 }));
    setFilters(empty);
  };

  // 时间范围快捷选择(按截止日期,设计§6.4)
  const applyDatePreset = (preset: string) => {
    const today = dayjs();
    let from: string | undefined, to: string | undefined;
    if (preset === 'today') { from = today.format('YYYY-MM-DD'); to = from; }
    else if (preset === 'thisWeek') { from = today.startOf('week').format('YYYY-MM-DD'); to = today.endOf('week').format('YYYY-MM-DD'); }
    else if (preset === 'lastWeek') { const lw = today.subtract(1, 'week'); from = lw.startOf('week').format('YYYY-MM-DD'); to = lw.endOf('week').format('YYYY-MM-DD'); }
    else if (preset === 'nextWeek') { const nw = today.add(1, 'week'); from = nw.startOf('week').format('YYYY-MM-DD'); to = nw.endOf('week').format('YYYY-MM-DD'); }
    else if (preset === 'overdue') { from = undefined; to = today.subtract(1, 'day').format('YYYY-MM-DD'); } // 已逾期：截止日期<今天
    else { from = undefined; to = undefined; } // 全部时间
    setDraftFilters(prev => ({ ...prev, date_from: from, date_to: to }));
  };

  // 改任务状态(状态浮层选择 / 看板改状态,含父子联动由后端处理)
  const changeTaskStatus = async (taskId: number, newStatus: string) => {
    try {
      const res = await api.put(`${API_BASE}/project-plan/tasks/${taskId}`, { status: newStatus });
      message.success(res.data?.message || '状态已更新');
      setStatusPopover(null);
      // 局部更新当前行状态,避免整表重载导致甘特图滚动跳回顶部(问题3)
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
      if (activeView === 'kanban') loadKanban(); // 看板需重新分列
      loadSummary(); // 汇总卡片数字刷新
    } catch (error: any) {
      message.error(error.response?.data?.detail || '状态更新失败');
    }
  };

  // 删除单个任务(列表操作列)
  const deleteTask = async (taskId: number) => {
    try {
      await api.delete(`${API_BASE}/project-plan/tasks/${taskId}`);
      message.success('已删除');
      reloadCurrentView();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  // 行内编辑保存
  const saveInlineEdit = async (taskId: number, field: string, value: any) => {
    setEditingCell(null);
    try {
      await api.put(`${API_BASE}/project-plan/tasks/${taskId}`, { [field]: value });
      message.success('已保存');
      reloadCurrentView();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    }
  };

  // 批量操作
  const batchOperate = async (action: 'status' | 'assignee' | 'delete', value?: any) => {
    if (selectedRowKeys.length === 0) { message.warning('请先勾选任务'); return; }
    try {
      const res = await api.post(`${API_BASE}/project-plan/tasks/batch`, {
        task_ids: selectedRowKeys, action, value
      });
      message.success(res.data?.message || '批量操作完成');
      setSelectedRowKeys([]);
      reloadCurrentView();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '批量操作失败');
    }
  };

  // 切换某父任务折叠状态
  const toggleCollapse = (id: number) => {
    setCollapsedKeys(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  // 初始化加载
  useEffect(() => {
    loadSummary();
    loadFilterOptions();
    loadParentOptions();
  }, []);

  // 视图切换时重新加载数据
  useEffect(() => {
    if (activeView === 'kanban') {
      loadKanban();
    } else {
      loadTasks();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeView, filters, pagination.page, pagination.pageSize]);

  // 状态标签颜色映射
  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      '待开始': 'default',
      '进行中': 'processing',
      '已完成': 'success',
      '已延期': 'error',
      '待补材料': 'purple'
    };
    return colorMap[status] || 'default';
  };

  // 优先级标签颜色
  const getPriorityColor = (priority: string) => {
    const colorMap: Record<string, string> = {
      '高': 'red',
      '中': 'orange',
      '低': 'blue'
    };
    return colorMap[priority] || 'default';
  };

  // 5态与色值(状态浮层/看板共用)
  const STATUS_LIST = ['待开始', '进行中', '已完成', '已延期', '待补材料'];
  const STATUS_HEX: Record<string, string> = {
    '待开始': '#d9d9d9', '进行中': '#1677ff', '已完成': '#52c41a',
    '已延期': '#ff4d4f', '待补材料': '#fa8c16'
  };

  // 状态→甘特色条颜色(原型:待补材料归橙,同进行中色系)
  const ganttBarColor = (status: string): string => {
    const map: Record<string, string> = {
      '已完成': '#52c41a', '进行中': '#fa8c16', '待开始': '#d9d9d9',
      '已延期': '#ff4d4f', '待补材料': '#fa8c16'
    };
    return map[status] || '#d9d9d9';
  };

  // 状态→进度%(设计§6.4:已完成100/待开始0/进行中50/待补材料60)
  const statusToPercent = (status: string): number => {
    const map: Record<string, number> = {
      '已完成': 100, '进行中': 50, '待补材料': 60, '已延期': 40, '待开始': 0
    };
    return map[status] ?? 0;
  };

  // 甘特表格单元样式(还原原型 .gantt th/td)
  const ganttTh: React.CSSProperties = { padding: '8px 6px', borderBottom: '1px solid #f5f5f5', color: 'rgba(0,0,0,.45)', fontWeight: 500, background: '#fafafa', whiteSpace: 'nowrap', textAlign: 'center' };
  const ganttThLeft: React.CSSProperties = { ...ganttTh, textAlign: 'left' };
  const ganttTd: React.CSSProperties = { padding: '8px 6px', borderBottom: '1px solid #f5f5f5', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' };

  // 点状态标签 → 记录标签坐标,弹 fixed 浮层
  const openStatusPopover = (e: React.MouseEvent, taskId: number, current: string) => {
    e.stopPropagation();
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    setStatusPopover({ taskId, current, top: rect.bottom + 4, left: rect.left });
  };

  // 状态浮层(fixed 定位于标签正下方 4px,设计§6.4)
  const renderStatusPopover = () => {
    if (!statusPopover) return null;
    return (
      <>
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 1000 }}
          onClick={() => setStatusPopover(null)}
        />
        <div
          style={{
            position: 'fixed', top: statusPopover.top, left: statusPopover.left, zIndex: 1001,
            background: '#fff', borderRadius: 6, boxShadow: '0 3px 12px rgba(0,0,0,.15)',
            padding: 4, minWidth: 110
          }}
        >
          {STATUS_LIST.map(s => (
            <div
              key={s}
              onClick={() => changeTaskStatus(statusPopover.taskId, s)}
              style={{
                padding: '6px 12px', cursor: 'pointer', borderRadius: 4, fontSize: 13,
                background: s === statusPopover.current ? '#f0f5ff' : 'transparent',
                display: 'flex', alignItems: 'center', gap: 8
              }}
              onMouseEnter={e => (e.currentTarget.style.background = '#f5f5f5')}
              onMouseLeave={e => (e.currentTarget.style.background = s === statusPopover.current ? '#f0f5ff' : 'transparent')}
            >
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: STATUS_HEX[s] }} />
              {s}
            </div>
          ))}
        </div>
      </>
    );
  };

  // 渲染汇总卡片
  const renderSummaryCards = () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '16px' }}>
      <Card variant="borderless" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: '#fff' }}>
        <Statistic
          title={<span style={{ color: '#fff' }}>整体进度</span>}
          value={summary.overall_progress}
          suffix="%"
          styles={{ content: { color: '#fff' } }}
        />
        <Progress 
          percent={summary.overall_progress} 
          strokeColor="#fff" 
          showInfo={false}
          style={{ marginTop: 8 }}
        />
        <div style={{ fontSize: 12, marginTop: 8, opacity: 0.9 }}>按 L4 工作内容完成率计算</div>
      </Card>

      <Card
        variant="borderless"
        hoverable
        onClick={() => { setDraftFilters(prev => ({ ...prev, status: '进行中' })); setPagination(prev => ({ ...prev, page: 1 })); setFilters(prev => ({ ...prev, status: '进行中' })); }}
        style={{ cursor: 'pointer' }}
      >
        <Statistic
          title="进行中任务"
          value={summary.doing_count}
          suffix="项"
          styles={{ content: { color: '#fa8c16' } }}
        />
        <div style={{ fontSize: 12, marginTop: 8, color: '#8c8c8c' }}>点击筛选进行中任务 →</div>
      </Card>

      <Card
        variant="borderless"
        hoverable
        onClick={() => { setDraftFilters(prev => ({ ...prev, delayed: true })); setPagination(prev => ({ ...prev, page: 1 })); setFilters(prev => ({ ...prev, delayed: true })); }}
        style={{ cursor: 'pointer' }}
      >
        <Statistic
          title="已延期任务 🔴"
          value={summary.delayed_count}
          suffix="项"
          styles={{ content: { color: '#ff4d4f' } }}
        />
        <div style={{ fontSize: 12, marginTop: 8, color: '#8c8c8c' }}>计划结束日期 &lt; 今天 且 未完成</div>
      </Card>

      <Card variant="borderless" style={{ cursor: 'pointer' }} onClick={() => {
        // 从 localStorage 的 user 对象取当前用户 id（登录时缓存,见 Login.tsx）
        let userId = 0;
        try { userId = JSON.parse(localStorage.getItem('user') || '{}').id || 0; } catch { userId = 0; }
        if (userId) {
          setDraftFilters(prev => ({ ...prev, responsible_person_id: userId }));
          setPagination(prev => ({ ...prev, page: 1 }));
          setFilters(prev => ({ ...prev, responsible_person_id: userId }));
        } else {
          message.warning('未获取到当前用户信息,请重新登录');
        }
      }}>
        <Statistic
          title="我的任务"
          value={summary.my_tasks_count}
          suffix="项"
          styles={{ content: { color: '#722ed1' } }}
        />
        <div style={{ fontSize: 12, marginTop: 8, color: '#8c8c8c' }}>责任人 = 当前登录用户</div>
      </Card>
    </div>
  );

  // 渲染筛选工具栏
  const renderFilterToolbar = () => (
    <Card style={{ marginBottom: 16 }}>
      <Space wrap style={{ width: '100%', justifyContent: 'space-between' }}>
        <Space wrap>
          <Input
            placeholder="🔍 搜索任务名称..."
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
            value={draftFilters.keyword}
            onChange={(e) => setDraftFilters({ ...draftFilters, keyword: e.target.value })}
            onPressEnter={applyFilters}
            allowClear
          />

          <Select
            placeholder="全部状态"
            style={{ width: 120 }}
            value={draftFilters.status ?? '__ALL__'}
            onChange={(value) => setDraftFilters({ ...draftFilters, status: value === '__ALL__' ? undefined : value })}
          >
            <Option value="__ALL__">全部状态</Option>
            {filterOptions.statuses.map(status => (
              <Option key={status} value={status}>{status}</Option>
            ))}
          </Select>

          <Select
            placeholder="全部责任人"
            style={{ width: 140 }}
            value={draftFilters.responsible_person_id != null ? String(draftFilters.responsible_person_id) : '__ALL__'}
            onChange={(value) => setDraftFilters({ ...draftFilters, responsible_person_id: value === '__ALL__' ? undefined : Number(value) })}
          >
            <Option value="__ALL__">全部责任人</Option>
            {filterOptions.assignees.map(assignee => (
              <Option key={assignee.id} value={String(assignee.id)}>{assignee.name}</Option>
            ))}
          </Select>

          <Select
            placeholder="全部学校"
            style={{ width: 140 }}
            value={draftFilters.school_id != null ? String(draftFilters.school_id) : '__ALL__'}
            onChange={(value) => setDraftFilters({ ...draftFilters, school_id: value === '__ALL__' ? undefined : Number(value) })}
          >
            <Option value="__ALL__">全部学校</Option>
            {filterOptions.schools.map(school => (
              <Option key={school.id} value={String(school.id)}>{school.name}</Option>
            ))}
          </Select>

          <Select
            placeholder="时间范围"
            style={{ width: 140 }}
            onChange={(v) => applyDatePreset(v || 'all')}
            options={[
              { value: 'all', label: '全部时间' },
              { value: 'today', label: '今日' },
              { value: 'thisWeek', label: '本周' },
              { value: 'lastWeek', label: '上周' },
              { value: 'nextWeek', label: '下周' },
              { value: 'overdue', label: '已逾期' },
            ]}
          />

          <Button type="primary" icon={<SearchOutlined />} onClick={applyFilters}>查询</Button>
          <Button icon={<ReloadOutlined />} onClick={resetFilters}>重置</Button>
        </Space>

        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setTaskModalVisible(true)}>
            新增任务
          </Button>
          <Button icon={<ImportOutlined />}>导入</Button>
          <Button icon={<ExportOutlined />}>导出</Button>
        </Space>
      </Space>
    </Card>
  );

  // 判断某任务是否有子任务(用于显示折叠图标)
  // 使用parent_id判断是否有子任务
  const hasChildren = (record: TaskItem) =>
    tasks.some(t => t.parent_id === record.id);

  // 计算可见任务(应用折叠过滤) - 基于parent_id的树形结构
  const getVisibleTasks = (): TaskItem[] => {
    if (collapsedKeys.size === 0) return tasks;

    // 递归检查某任务的所有祖先是否有被折叠的
    const hasCollapsedAncestor = (task: TaskItem): boolean => {
      if (!task.parent_id) return false;
      if (collapsedKeys.has(task.parent_id)) return true;
      const parent = tasks.find(t => t.id === task.parent_id);
      return parent ? hasCollapsedAncestor(parent) : false;
    };

    return tasks.filter(t => !hasCollapsedAncestor(t));
  };

  // 列表视图列定义
  const listColumns: ColumnsType<TaskItem> = [
    {
      title: '任务名称',
      dataIndex: 'l4',
      key: 'task_name',
      width: 320,
      render: (text, record) => {
        const indent = (record.level - 1) * 20;
        const displayText = text || record.l3 || record.l2 || record.l1;
        const showToggle = hasChildren(record);
        const collapsed = collapsedKeys.has(record.id);
        return (
          <div style={{ paddingLeft: indent, display: 'flex', alignItems: 'center' }}>
            <span
              onClick={(e) => { e.stopPropagation(); if (showToggle) toggleCollapse(record.id); }}
              style={{ width: 16, display: 'inline-block', cursor: showToggle ? 'pointer' : 'default', color: '#8c8c8c' }}
            >
              {showToggle ? (collapsed ? '►' : '▼') : ''}
            </span>
            <Button
              type="link"
              style={{ padding: 0, height: 'auto', fontWeight: record.level <= 2 ? 600 : 400, color: record.level === 1 ? '#1677ff' : undefined }}
              onClick={() => viewTaskDetail(record.id)}
            >
              {record.level >= 4 ? '└ ' : ''}{displayText}
            </Button>
          </div>
        );
      }
    },
    {
      title: '责任人',
      dataIndex: 'assignee_name',
      key: 'assignee',
      width: 120,
      render: (name, record) => {
        if (editingCell?.id === record.id && editingCell.field === 'responsible_person_id') {
          return (
            <Select
              size="small" autoFocus defaultOpen style={{ width: '100%' }}
              defaultValue={record.assignee_id}
              onBlur={() => setEditingCell(null)}
              onChange={(v) => saveInlineEdit(record.id, 'responsible_person_id', v)}
            >
              {filterOptions.assignees.map(a => <Option key={a.id} value={a.id}>{a.name}</Option>)}
            </Select>
          );
        }
        return (
          <span style={{ cursor: 'pointer' }} onDoubleClick={() => setEditingCell({ id: record.id, field: 'responsible_person_id' })}>
            {name || <span style={{ color: '#bfbfbf' }}>双击指派</span>}
          </span>
        );
      }
    },
    {
      title: '计划开始',
      dataIndex: 'plan_start_date',
      key: 'plan_start',
      width: 130,
      render: (val, record) => {
        if (editingCell?.id === record.id && editingCell.field === 'plan_start_date') {
          return (
            <DatePicker
              size="small" autoFocus open style={{ width: '100%' }}
              defaultValue={val ? dayjs(val) : undefined}
              onOpenChange={(o) => { if (!o) setEditingCell(null); }}
              onChange={(d) => saveInlineEdit(record.id, 'plan_start_date', d ? d.format('YYYY-MM-DD') : null)}
            />
          );
        }
        return <span style={{ cursor: 'pointer' }} onDoubleClick={() => setEditingCell({ id: record.id, field: 'plan_start_date' })}>{val || '-'}</span>;
      }
    },
    {
      title: '计划结束',
      dataIndex: 'plan_end_date',
      key: 'plan_end',
      width: 130,
      render: (val, record) => {
        if (editingCell?.id === record.id && editingCell.field === 'plan_end_date') {
          return (
            <DatePicker
              size="small" autoFocus open style={{ width: '100%' }}
              defaultValue={val ? dayjs(val) : undefined}
              onOpenChange={(o) => { if (!o) setEditingCell(null); }}
              onChange={(d) => saveInlineEdit(record.id, 'plan_end_date', d ? d.format('YYYY-MM-DD') : null)}
            />
          );
        }
        return <span style={{ cursor: 'pointer' }} onDoubleClick={() => setEditingCell({ id: record.id, field: 'plan_end_date' })}>{val || '-'}</span>;
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 110,
      render: (status, record) => (
        <Tag
          color={getStatusColor(status)}
          style={{ cursor: 'pointer' }}
          onClick={(e) => { e.preventDefault(); openStatusPopover(e, record.id, status); }}
        >
          {status}
        </Tag>
      )
    },
    {
      title: '进展说明',
      dataIndex: 'progress_note',
      key: 'note',
      width: 280,
      ellipsis: true,
      render: (val, record) => {
        if (editingCell?.id === record.id && editingCell.field === 'progress_note') {
          return (
            <Input
              size="small" autoFocus style={{ width: '100%' }}
              defaultValue={val || ''}
              onBlur={() => setEditingCell(null)}
              onPressEnter={(e) => saveInlineEdit(record.id, 'progress_note', e.currentTarget.value)}
            />
          );
        }
        return (
          <span style={{ cursor: 'pointer' }} onDoubleClick={() => setEditingCell({ id: record.id, field: 'progress_note' })}>
            {val || <span style={{ color: '#bfbfbf' }}>双击编辑</span>}
          </span>
        );
      }
    },
    {
      title: '进度',
      key: 'progress',
      dataIndex: 'progress',
      width: 90,
      render: (_, record) => {
        const st = (record.plan_end_date && dayjs(record.plan_end_date).isBefore(dayjs(), 'day') && record.status !== '已完成')
          ? '已延期' : record.status;
        const pct = record.progress != null ? record.progress : statusToPercent(st);
        if (editingCell?.id === record.id && editingCell.field === 'progress') {
          return (
            <Input
              size="small" autoFocus type="number" min={0} max={100} style={{ width: '100%' }}
              defaultValue={pct}
              onBlur={() => setEditingCell(null)}
              onPressEnter={(e) => {
                const v = Math.max(0, Math.min(100, parseInt(e.currentTarget.value || '0', 10)));
                saveInlineEdit(record.id, 'progress', v);
              }}
            />
          );
        }
        return (
          <span style={{ cursor: 'pointer', color: ganttBarColor(st) }}
            onDoubleClick={() => setEditingCell({ id: record.id, field: 'progress' })}>
            {pct}%
          </span>
        );
      }
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => {
            // 点"编辑"实际是给当前任务新建子任务
            const currentUserId = JSON.parse(localStorage.getItem('user') || '{}').id || 0;
            taskForm.resetFields();
            taskForm.setFieldsValue({
              parent_id: record.id,
              responsible_person_id: currentUserId,
              plan_start_date: dayjs(),
              status: '待开始'
            });
            setTaskModalVisible(true);
          }}>编辑</Button>
          <Popconfirm
            title="确认删除该任务?"
            description="删除为软删除,可恢复"
            onConfirm={() => deleteTask(record.id)}
            okText="删除" cancelText="取消" okButtonProps={{ danger: true }}
          >
            <Button type="link" size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 渲染甘特图视图（按原型 V2.2：任务名/责任人/时间轴/进度/状态 五列，色条 left%/width% 定位）
  const renderGanttView = () => {
    const rows = getVisibleTasks();
    // 计算时间轴范围
    const dates: number[] = [];
    tasks.forEach(t => {
      if (t.plan_start_date) dates.push(dayjs(t.plan_start_date).valueOf());
      if (t.plan_end_date) dates.push(dayjs(t.plan_end_date).valueOf());
    });
    let minD = dates.length ? dayjs(Math.min(...dates)).startOf('month') : dayjs().startOf('month');
    let maxD = dates.length ? dayjs(Math.max(...dates)).endOf('month') : dayjs().add(5, 'month').endOf('month');
    if (maxD.diff(minD, 'month') < 1) maxD = minD.add(1, 'month').endOf('month');
    const totalMs = maxD.valueOf() - minD.valueOf();

    // 月份刻度
    const months: string[] = [];
    let cur = minD.startOf('month');
    while (cur.isBefore(maxD) || cur.isSame(maxD, 'month')) {
      months.push(cur.format('MM月'));
      cur = cur.add(1, 'month');
    }

    const today = dayjs();
    const barGeom = (t: TaskItem) => {
      if (!t.plan_start_date || !t.plan_end_date) return null;
      const s = dayjs(t.plan_start_date).valueOf();
      const e = dayjs(t.plan_end_date).valueOf();
      const left = Math.max(0, ((s - minD.valueOf()) / totalMs) * 100);
      const width = Math.max(1, ((e - s) / totalMs) * 100);
      return { left, width: Math.min(width, 100 - left) };
    };
    // 延期判断：计划结束<今天 且 未完成
    const effStatus = (t: TaskItem) =>
      (t.plan_end_date && dayjs(t.plan_end_date).isBefore(today, 'day') && t.status !== '已完成')
        ? '已延期' : t.status;

    return (
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', minWidth: 1000, borderCollapse: 'collapse', fontSize: 13, tableLayout: 'fixed' }}>
          <colgroup>
            <col style={{ width: 260 }} /><col style={{ width: 90 }} />
            <col style={{ minWidth: 500 }} /><col style={{ width: 56 }} /><col style={{ width: 90 }} />
          </colgroup>
          <thead>
            <tr>
              <th style={ganttThLeft}>阶段 / 任务</th>
              <th style={ganttTh}>责任人</th>
              <th style={{ ...ganttTh, padding: 0 }}>
                <div style={{ display: 'flex', fontSize: 11, color: 'rgba(0,0,0,.45)' }}>
                  {months.map((m, i) => (
                    <span key={m + i} style={{ flex: 1, textAlign: 'center', borderLeft: i === 0 ? 'none' : '1px solid #f0f0f0', padding: '4px 0' }}>{m}</span>
                  ))}
                </div>
              </th>
              <th style={ganttTh}>进度</th>
              <th style={ganttTh}>状态</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(t => {
              const st = effStatus(t);
              const geom = barGeom(t);
              // 进度：优先用真实 progress 字段,回退到状态映射(问题:进度显示与列表一致)
              const pct = t.progress != null ? t.progress : statusToPercent(st);
              // 原型样式：只显示本级名称,层级由缩进(paddingLeft)体现,不用面包屑
              const displayText = t.l4 || t.l3 || t.l2 || t.l1;
              const showToggle = hasChildren(t);
              const collapsed = collapsedKeys.has(t.id);
              return (
                <tr key={t.id} style={{ borderBottom: '1px solid #f5f5f5', cursor: 'pointer' }}>
                  <td style={{ ...ganttTd, textAlign: 'left', paddingLeft: (t.level - 1) * 20 + 6 }} onClick={() => viewTaskDetail(t.id)}>
                    <span
                      onClick={(e) => { e.stopPropagation(); if (showToggle) toggleCollapse(t.id); }}
                      style={{ width: 16, display: 'inline-block', cursor: showToggle ? 'pointer' : 'default', color: '#8c8c8c' }}
                    >{showToggle ? (collapsed ? '►' : '▼') : ''}</span>
                    <span style={{ fontWeight: t.level <= 2 ? 600 : 400, color: t.level === 1 ? '#1677ff' : undefined }}>
                      {t.level >= 4 ? '└ ' : ''}{displayText}
                    </span>
                  </td>
                  <td style={{ ...ganttTd, textAlign: 'center' }}>{t.assignee_name || '-'}</td>
                  <td style={{ ...ganttTd, padding: '8px 6px' }}>
                    <div style={{ position: 'relative', height: 22 }}>
                      {geom && (
                        <div style={{
                          position: 'absolute', top: 4, height: 14, borderRadius: 7,
                          left: `${geom.left}%`, width: `${geom.width}%`, background: ganttBarColor(st)
                        }} title={`${t.plan_start_date} ~ ${t.plan_end_date}`} />
                      )}
                    </div>
                  </td>
                  <td style={{ ...ganttTd, textAlign: 'center', fontSize: 12, color: ganttBarColor(st) }}>{pct}%</td>
                  <td style={{ ...ganttTd, textAlign: 'center' }} onClick={(e) => e.stopPropagation()}>
                    <Tag color={getStatusColor(st)} style={{ cursor: 'pointer' }} onClick={(e) => { e.preventDefault(); openStatusPopover(e, t.id, t.status); }}>
                      {st}
                    </Tag>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div style={{ display: 'flex', gap: 18, fontSize: 12, color: 'rgba(0,0,0,.55)', padding: '12px 4px 0', alignItems: 'center' }}>
          {[['已完成', '#52c41a'], ['进行中', '#fa8c16'], ['待开始', '#d9d9d9'], ['已延期', '#ff4d4f']].map(([label, c]) => (
            <span key={label} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 14, height: 10, borderRadius: 3, background: c }} />{label}
            </span>
          ))}
        </div>
      </div>
    );
  };

  // 渲染看板视图
  const renderKanbanView = () => {
    const statusList = ['待开始', '进行中', '已完成', '已延期', '待补材料'];
    const statusColors: Record<string, string> = {
      '待开始': '#d9d9d9',
      '进行中': '#fa8c16',
      '已完成': '#52c41a',
      '已延期': '#ff4d4f',
      '待补材料': '#722ed1'
    };

    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
        {statusList.map(status => {
          const column = kanbanData[status] || { count: 0, items: [] };
          return (
            <div key={status}>
              <Card
                title={
                  <Space>
                    <span>{status}</span>
                    <Tag color={statusColors[status]}>{column.count}</Tag>
                  </Space>
                }
                style={{ borderTop: `3px solid ${statusColors[status]}` }}
              >
                {column.items.map(item => (
                  <Card.Grid
                    key={item.id}
                    hoverable
                    style={{ width: '100%', cursor: 'pointer', padding: 12 }}
                    onClick={() => viewTaskDetail(item.id)}
                  >
                    <div style={{ fontWeight: 500, marginBottom: 4 }}>{item.title}</div>
                    <div style={{ fontSize: 12, color: '#8c8c8c' }}>
                      {item.parent} · {item.assignee_name}
                    </div>
                    <div style={{ marginTop: 6 }}>
                      <Tag
                        color={getStatusColor(status)}
                        style={{ cursor: 'pointer' }}
                        onClick={(e) => { e.preventDefault(); openStatusPopover(e, item.id, status); }}
                      >
                        {status}
                      </Tag>
                      {item.is_delayed && (
                        <Tag color="error">逾期{item.delay_days}天</Tag>
                      )}
                    </div>
                  </Card.Grid>
                ))}
              </Card>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 汇总卡片 */}
      {renderSummaryCards()}

      {/* 视图切换Tab */}
      <Tabs
        activeKey={activeView}
        onChange={(key) => setActiveView(key as any)}
        items={[
          { key: 'gantt', label: <span><BarChartOutlined /> 甘特图</span> },
          { key: 'list', label: <span><UnorderedListOutlined /> 列表</span> },
          { key: 'kanban', label: <span><AppstoreOutlined /> 看板</span> }
        ]}
      />

      {/* 筛选工具栏 */}
      {renderFilterToolbar()}

      {/* 数据一致性提示 */}
      <Card style={{ marginBottom: 16, background: '#fffbe6', border: '1px solid #ffe58f' }}>
        <div style={{ fontSize: 13, color: '#ad6800' }}>
          <b>📐 数据一致性规则：</b>
          项目计划任务在首页里程碑、项目计划、交付进展等多处展示，<b>任一处维护后，所有页面自动同步</b>——同一任务只有一个状态。
        </div>
      </Card>

      {/* 视图内容 */}
      <Card loading={loading}>
        {activeView === 'gantt' && renderGanttView()}

        {activeView === 'list' && (
          <>
            {selectedRowKeys.length > 0 && (
              <div style={{ marginBottom: 12, padding: '8px 12px', background: '#e6f4ff', borderRadius: 4, display: 'flex', alignItems: 'center', gap: 12 }}>
                <span>已选 {selectedRowKeys.length} 项</span>
                <Select
                  size="small" placeholder="批量改状态" style={{ width: 130 }}
                  value={undefined}
                  onChange={(v) => batchOperate('status', v)}
                >
                  {STATUS_LIST.map(s => <Option key={s} value={s}>{s}</Option>)}
                </Select>
                <Select
                  size="small" placeholder="批量指派责任人" style={{ width: 150 }}
                  value={undefined}
                  onChange={(v) => batchOperate('assignee', v)}
                >
                  {filterOptions.assignees.map(a => <Option key={a.id} value={a.id}>{a.name}</Option>)}
                </Select>
                <Button size="small" danger onClick={() => {
                  Modal.confirm({
                    title: `确认删除选中的 ${selectedRowKeys.length} 个任务?`,
                    content: '删除为软删除(标记失效),可后续恢复。',
                    okText: '删除', okButtonProps: { danger: true }, cancelText: '取消',
                    onOk: () => batchOperate('delete')
                  });
                }}>批量删除</Button>
                <Button size="small" type="link" onClick={() => setSelectedRowKeys([])}>取消选择</Button>
              </div>
            )}
            <Table
              columns={listColumns}
              dataSource={getVisibleTasks()}
              rowKey="id"
              rowSelection={{
                selectedRowKeys,
                onChange: (keys) => setSelectedRowKeys(keys)
              }}
              scroll={{ x: 'max-content' }}
              pagination={activeView === 'list' ? {
                current: pagination.page,
                pageSize: pagination.pageSize,
                total: pagination.total,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条`,
                onChange: (page, pageSize) => setPagination({ ...pagination, page, pageSize })
              } : false}
            />
          </>
        )}

        {activeView === 'kanban' && renderKanbanView()}
      </Card>

      {/* 任务详情弹窗（居中 Modal，匹配原型 detailModal） */}
      <Modal
        title="任务详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        width={560}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>关闭</Button>,
          <Button key="sub" onClick={() => {
            setDetailVisible(false);
            setTaskModalVisible(true);
          }}>➕ 创建子任务</Button>,
          <Button key="edit" type="primary" onClick={() => {
            setDetailVisible(false);
            setTaskModalVisible(true);
          }}>✏️ 编辑当前任务</Button>
        ]}
      >
        {currentTask && (
          <div className="detail-list">
            <Row gutter={[16, 12]}>
              <Col span={12}><div className="desc-item"><span className="desc-k">任务名称</span><span className="desc-v">{currentTask.work_content_l4 || currentTask.task_package_l3 || currentTask.sub_phase_l2 || currentTask.project_phase_l1}</span></div></Col>
              <Col span={12}><div className="desc-item"><span className="desc-k">任务编码</span><span className="desc-v">{currentTask.task_code}</span></div></Col>
              <Col span={12}><div className="desc-item"><span className="desc-k">任务层级</span><span className="desc-v">{
                currentTask.work_detail_l5 ? 'L5' :
                currentTask.work_content_l4 ? 'L4' :
                currentTask.task_package_l3 ? 'L3' :
                currentTask.sub_phase_l2 ? 'L2' : 'L1'
              }</span></div></Col>
              <Col span={12}><div className="desc-item"><span className="desc-k">状态</span><span className="desc-v"><Tag color={getStatusColor(currentTask.status)}>{currentTask.status}</Tag></span></div></Col>
              <Col span={12}><div className="desc-item"><span className="desc-k">优先级</span><span className="desc-v"><Tag color={getPriorityColor(currentTask.priority)}>{currentTask.priority}</Tag></span></div></Col>
              <Col span={12}><div className="desc-item"><span className="desc-k">关联阶段</span><span className="desc-v">{currentTask.stage_type || '-'}</span></div></Col>
              <Col span={12}><div className="desc-item"><span className="desc-k">责任人</span><span className="desc-v">{currentTask.assignee_name || '-'}</span></div></Col>
              <Col span={12}><div className="desc-item"><span className="desc-k">关联学校</span><span className="desc-v">{currentTask.school_name || '全项目'}</span></div></Col>
              <Col span={24}><div className="desc-item"><span className="desc-k">计划工期</span><span className="desc-v">{currentTask.plan_start_date} ~ {currentTask.plan_end_date}</span></div></Col>
              <Col span={12}><div className="desc-item"><span className="desc-k">实际结束</span><span className="desc-v">{currentTask.actual_end_date || <span style={{ color: 'rgba(0,0,0,.35)' }}>未完成</span>}</span></div></Col>
              <Col span={24}><div className="desc-item"><span className="desc-k">进展说明</span><span className="desc-v">{currentTask.progress_note || '-'}</span></div></Col>
              <Col span={24}><div className="desc-item"><span className="desc-k">交付物</span><span className="desc-v">{currentTask.deliverables || '-'}</span></div></Col>
            </Row>

            {/* 佐证材料(设计§6.7.2) */}
            <div style={{ marginTop: 12 }}>
              <div style={{ fontWeight: 600, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                <PaperClipOutlined /> 佐证材料
              </div>
              <List
                size="small"
                bordered
                locale={{ emptyText: '暂无材料' }}
                dataSource={attachments}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <a key="dl" href={`${FILE_HOST}${item.file_url}`} target="_blank" rel="noreferrer">下载</a>,
                      <Popconfirm
                        key="del"
                        title="确认删除该材料?"
                        onConfirm={() => deleteAttachment(item.id)}
                        okText="删除" cancelText="取消"
                      >
                        <Button type="link" size="small" danger icon={<DeleteOutlined />} style={{ padding: 0 }} />
                      </Popconfirm>
                    ]}
                  >
                    <div style={{ overflow: 'hidden' }}>
                      <div style={{ fontSize: 13 }}>{item.file_name}</div>
                      {item.description && <div style={{ fontSize: 12, color: '#8c8c8c' }}>{item.description}</div>}
                    </div>
                  </List.Item>
                )}
              />
              <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                <Input
                  size="small"
                  placeholder="材料说明(可选)"
                  value={uploadDesc}
                  onChange={(e) => setUploadDesc(e.target.value)}
                  style={{ flex: 1 }}
                />
                <Upload
                  showUploadList={false}
                  beforeUpload={(file) => { uploadAttachment(file as any); return false; }}
                >
                  <Button size="small" icon={<UploadOutlined />}>上传材料</Button>
                </Upload>
              </div>
              <div style={{ fontSize: 12, color: '#bfbfbf', marginTop: 4 }}>
                支持 PDF/Office文档/图片,单个≤20MB
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* 新增任务弹窗（按原型图4：父任务挂靠 + 层级自动 + 进度数字） */}
      <Modal
        title="新增任务"
        open={taskModalVisible}
        onCancel={() => {
          setTaskModalVisible(false);
          taskForm.resetFields();
          setChildLevel('选择父任务后自动确定');
        }}
        onOk={() => {
          taskForm.validateFields().then(async (values) => {
            try {
              const payload = { ...values };
              ['plan_start_date', 'plan_end_date'].forEach((f) => {
                if (payload[f] && dayjs.isDayjs(payload[f])) payload[f] = payload[f].format('YYYY-MM-DD');
              });
              await api.post(`${API_BASE}/project-plan/tasks`, payload);
              message.success('任务创建成功');
              setTaskModalVisible(false);
              taskForm.resetFields();
              setChildLevel('选择父任务后自动确定');
              loadParentOptions(); // 新任务可能成为新的父选项
              if (activeView === 'kanban') {
                loadKanban();
              } else {
                loadTasks();
              }
              loadSummary();
            } catch (error: any) {
              message.error(error.response?.data?.detail || '创建任务失败');
            }
          });
        }}
        width={640}
      >
        <Form
          form={taskForm}
          layout="vertical"
          onValuesChange={(changed) => {
            // 选择父任务后自动确定当前层级（子层级 = 父层级 + 1）
            if ('parent_id' in changed) {
              const p = parentOptions.find(o => o.id === changed.parent_id);
              setChildLevel(p ? `L${p.level + 1}（父任务 L${p.level}）` : '选择父任务后自动确定');
            }
          }}
        >
          <Form.Item label="任务名称" name="task_name" rules={[{ required: true, message: '请输入任务名称' }]}>
            <Input placeholder="如：设备安装" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="父任务" name="parent_id" tooltip="必须挂靠到某个父任务；顶级任务可留空">
                <Select
                  allowClear
                  showSearch
                  optionFilterProp="children"
                  placeholder="— 请选择父任务 —"
                >
                  {parentOptions.map(o => (
                    <Option key={o.id} value={o.id}>{o.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="当前任务层级" tooltip="子任务层级 = 父任务层级 + 1">
                <Input value={childLevel} readOnly style={{ background: '#f5f5f5', color: 'rgba(0,0,0,.55)' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="责任人" name="responsible_person_id" rules={[{ required: true, message: '请选择责任人' }]}>
                <Select placeholder="选择责任人">
                  {filterOptions.assignees.map(a => (
                    <Option key={a.id} value={a.id}>{a.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="关联学校" name="school_id" tooltip="非必填，留空表示全项目">
                <Select allowClear placeholder="选择学校（可留空）">
                  {filterOptions.schools.map(s => (
                    <Option key={s.id} value={s.id}>{s.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="计划开始" name="plan_start_date" rules={[{ required: true, message: '请选择计划开始' }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="计划结束" name="plan_end_date" rules={[{ required: true, message: '请选择计划结束' }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="状态" name="status" initialValue="待开始" rules={[{ required: true }]}>
                <Select>
                  {STATUS_LIST.map(s => (
                    <Option key={s} value={s}>{s}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="进度 %" name="progress" initialValue={0}>
                <Input type="number" min={0} max={100} placeholder="0-100" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="进展说明" name="progress_note">
            <Input.TextArea rows={3} placeholder="如：一楼机房已就位，二楼电力改造中" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 状态选择浮层（fixed 定位于标签正下方，设计§6.4） */}
      {renderStatusPopover()}
    </div>
  );
};

export default ProjectPlan;
