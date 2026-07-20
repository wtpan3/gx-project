import React, { useState, useMemo } from 'react';
import { Table, Tag, Drawer, Descriptions, Select, Space, Button, Segmented, Input, Tag as ATag } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';

// 项目计划 WBS —— 界面原型（静态示例数据），后续接入 /api/v1/wbs-tasks
// WBS 5级层级：L1项目阶段 > L2子阶段 > L3任务包 > L4工作内容(统计口径) > L5明细
// 支持：树形/列表视图、状态筛选(接收首页下钻的status参数)、行点击详情抽屉下钻

interface WbsTask {
  id: number;
  key: string;
  name: string; // 当前层级名称
  level: number; // 1-4
  stage_type?: string;
  plan_start_date?: string;
  plan_end_date?: string;
  status?: string;
  assignee_name?: string;
  school_name?: string;
  progress_note?: string;
  deliverables?: string;
  children?: WbsTask[];
}

const STATUS_COLOR: Record<string, string> = {
  待开始: 'default',
  进行中: 'processing',
  已完成: 'success',
  已延期: 'error',
  待补材料: 'warning',
};

// 静态示例数据：树形结构（L1>L2>L3>L4）
const MOCK_TREE: WbsTask[] = [
  {
    id: 1, key: '1', name: '启动规划', level: 1,
    children: [
      {
        id: 11, key: '1-1', name: '实施方案编制', level: 2,
        children: [
          {
            id: 111, key: '1-1-1', name: '完成实施方案', level: 3,
            children: [
              { id: 1111, key: '1-1-1-1', name: '编写实施方案初稿', level: 4, stage_type: '无', plan_start_date: '2026-01-05', plan_end_date: '2026-01-15', status: '已完成', assignee_name: '张项目经理', school_name: '高新一中', deliverables: '实施方案V1.0' },
            ],
          },
        ],
      },
    ],
  },
  {
    id: 2, key: '2', name: '交付实施', level: 1,
    children: [
      {
        id: 21, key: '2-1', name: '硬件交付', level: 2,
        children: [
          {
            id: 211, key: '2-1-1', name: '完成AI英语听说设备交付', level: 3,
            children: [
              { id: 2111, key: '2-1-1-1', name: '完成设备到货', level: 4, stage_type: '到货验收', plan_start_date: '2026-02-01', plan_end_date: '2026-02-10', status: '已完成', assignee_name: '李校园经理', school_name: '高新一中', deliverables: '到货验收单' },
              { id: 2112, key: '2-1-1-2', name: '完成设备安装', level: 4, stage_type: '加电测试', plan_start_date: '2026-02-11', plan_end_date: '2026-02-20', status: '进行中', assignee_name: '李校园经理', school_name: '高新一中' },
              { id: 2113, key: '2-1-1-3', name: '完成设备调试', level: 4, stage_type: '加电测试', plan_start_date: '2026-02-21', plan_end_date: '2026-02-25', status: '待开始', assignee_name: '李校园经理', school_name: '高新一中' },
            ],
          },
        ],
      },
      {
        id: 22, key: '2-2', name: '应用培训', level: 2,
        children: [
          {
            id: 221, key: '2-2-1', name: '完成教师培训', level: 3,
            children: [
              { id: 2211, key: '2-2-1-1', name: '完成教师培训', level: 4, stage_type: '培训', plan_start_date: '2026-03-01', plan_end_date: '2026-03-05', status: '已延期', assignee_name: '王校园经理', school_name: '高新二中', progress_note: '培训场地未落实' },
            ],
          },
        ],
      },
    ],
  },
  {
    id: 3, key: '3', name: '验收移交', level: 1,
    children: [
      {
        id: 31, key: '3-1', name: '竣工资料提交', level: 2,
        children: [
          {
            id: 311, key: '3-1-1', name: '提交竣工资料', level: 3,
            children: [
              { id: 3111, key: '3-1-1-1', name: '整理竣工资料', level: 4, stage_type: '校级验收', plan_start_date: '2026-05-01', plan_end_date: '2026-05-10', status: '待补材料', assignee_name: '张项目经理', school_name: '高新一中' },
            ],
          },
        ],
      },
    ],
  },
];

// 收集所有 L4 叶子任务（用于列表视图和筛选）
const collectL4 = (nodes: WbsTask[]): WbsTask[] => {
  const result: WbsTask[] = [];
  const walk = (arr: WbsTask[]) => {
    arr.forEach((n) => {
      if (n.level === 4) result.push(n);
      if (n.children) walk(n.children);
    });
  };
  walk(nodes);
  return result;
};

const ProjectPlan: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialStatus = searchParams.get('status') || undefined;

  const [view, setView] = useState<'tree' | 'list'>('tree');
  const [statusFilter, setStatusFilter] = useState<string | undefined>(initialStatus);
  const [keyword, setKeyword] = useState('');
  const [detail, setDetail] = useState<WbsTask | null>(null);

  const l4List = useMemo(() => collectL4(MOCK_TREE), []);

  const filteredList = useMemo(() => {
    return l4List.filter((t) => {
      if (statusFilter && t.status !== statusFilter) return false;
      if (keyword && !t.name.includes(keyword)) return false;
      return true;
    });
  }, [l4List, statusFilter, keyword]);

  const statusTag = (s?: string) => s ? <Tag color={STATUS_COLOR[s]}>{s}</Tag> : '-';

  // 树形视图列
  const treeColumns = [
    { title: '任务层级（L1>L2>L3>L4）', dataIndex: 'name', key: 'name', width: 320 },
    { title: '关联阶段', dataIndex: 'stage_type', key: 'stage_type', width: 100, render: (v: string) => v || '-' },
    { title: '计划开始', dataIndex: 'plan_start_date', key: 's', width: 110, render: (v: string) => v || '-' },
    { title: '计划结束', dataIndex: 'plan_end_date', key: 'e', width: 110, render: (v: string) => v || '-' },
    { title: '状态', dataIndex: 'status', key: 'status', width: 100, render: statusTag },
    { title: '责任人', dataIndex: 'assignee_name', key: 'a', width: 110, render: (v: string) => v || '-' },
    { title: '关联学校', dataIndex: 'school_name', key: 'sc', width: 110, render: (v: string) => v || '-' },
  ];

  // 列表视图列（仅L4）
  const listColumns = [
    { title: '工作内容(L4)', dataIndex: 'name', key: 'name' },
    { title: '关联阶段', dataIndex: 'stage_type', key: 'stage_type', width: 100, render: (v: string) => v || '-' },
    { title: '计划开始', dataIndex: 'plan_start_date', key: 's', width: 110 },
    { title: '计划结束', dataIndex: 'plan_end_date', key: 'e', width: 110 },
    { title: '状态', dataIndex: 'status', key: 'status', width: 100, render: statusTag },
    { title: '责任人', dataIndex: 'assignee_name', key: 'a', width: 110 },
    { title: '关联学校', dataIndex: 'school_name', key: 'sc', width: 110 },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Space>
          <h2 style={{ margin: 0 }}>项目计划</h2>
          <ATag color="blue">示例数据（待接入后端）</ATag>
        </Space>
        <Segmented
          value={view}
          onChange={(v) => setView(v as 'tree' | 'list')}
          options={[{ label: 'WBS树形', value: 'tree' }, { label: 'L4列表', value: 'list' }]}
        />
      </div>

      {/* 筛选栏 */}
      <Space style={{ marginBottom: 16 }} wrap>
        <Input
          placeholder="搜索工作内容"
          prefix={<SearchOutlined />}
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          style={{ width: 220 }}
          allowClear
        />
        <Select
          placeholder="按状态筛选"
          value={statusFilter}
          onChange={setStatusFilter}
          style={{ width: 160 }}
          allowClear
          options={['待开始', '进行中', '已完成', '已延期', '待补材料'].map((s) => ({ label: s, value: s }))}
        />
        {(statusFilter || keyword) && (
          <Button icon={<ReloadOutlined />} onClick={() => { setStatusFilter(undefined); setKeyword(''); }}>清除筛选</Button>
        )}
        {statusFilter && <ATag color="processing">当前筛选：{statusFilter}</ATag>}
      </Space>

      {view === 'tree' ? (
        <Table
          columns={treeColumns}
          dataSource={MOCK_TREE}
          rowKey="key"
          pagination={false}
          defaultExpandAllRows
          onRow={(record) => ({
            onClick: () => { if (record.level === 4) setDetail(record); },
            style: record.level === 4 ? { cursor: 'pointer' } : {},
          })}
        />
      ) : (
        <Table
          columns={listColumns}
          dataSource={filteredList}
          rowKey="id"
          onRow={(record) => ({ onClick: () => setDetail(record), style: { cursor: 'pointer' } })}
        />
      )}

      {/* 详情抽屉（下钻） */}
      <Drawer
        title={detail ? `任务详情 - ${detail.name}` : '任务详情'}
        width={600}
        open={!!detail}
        onClose={() => setDetail(null)}
        extra={<Button type="primary">编辑</Button>}
      >
        {detail && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="工作内容(L4)">{detail.name}</Descriptions.Item>
            <Descriptions.Item label="关联阶段">{detail.stage_type || '-'}</Descriptions.Item>
            <Descriptions.Item label="状态">{statusTag(detail.status)}</Descriptions.Item>
            <Descriptions.Item label="计划开始">{detail.plan_start_date || '-'}</Descriptions.Item>
            <Descriptions.Item label="计划结束">{detail.plan_end_date || '-'}</Descriptions.Item>
            <Descriptions.Item label="责任人">{detail.assignee_name || '-'}</Descriptions.Item>
            <Descriptions.Item label="关联学校">{detail.school_name || '-'}</Descriptions.Item>
            <Descriptions.Item label="进展说明">{detail.progress_note || '-'}</Descriptions.Item>
            <Descriptions.Item label="输出物">{detail.deliverables || '-'}</Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </div>
  );
};

export default ProjectPlan;
