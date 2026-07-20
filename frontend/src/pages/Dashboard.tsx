import React, { useEffect, useState } from 'react';
import { Card, Spin, message } from 'antd';
import { dashboardService } from '../services/dashboard';
import './Dashboard.css';

interface StatCard {
  label: string;
  value: number;
  unit: string;
  badge_red: boolean;
}

interface ProgressItem {
  label: string;
  count: number;
  color: string;
}

interface SoftwareModuleProgress {
  name: string;
  phase: string;
  progress: number;
}

interface DeliveryProgress {
  overall_progress: number;
  school_progress: ProgressItem[];
  school_completed: number;
  school_total: number;
  hardware_progress: ProgressItem[];
  hardware_completed: number;
  hardware_total: number;
  software_modules: SoftwareModuleProgress[];
}

interface Milestone {
  phase: string;
  task: string;
  plan_start_date: string | null;
  plan_end_date: string | null;
  status: string;
}

interface RiskItem {
  id: number;
  risk_level: string;
  description: string;
  impact: string | null;
  response_plan: string | null;
  owner_name: string | null;
  registered_at: string | null;
  plan_close_date: string | null;
  status: string;
}

interface TodoItem {
  id: number;
  task_name: string;
  priority: string;
  assignee_name: string | null;
  plan_end_date: string | null;
  status: string;
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [statCards, setStatCards] = useState<StatCard[]>([]);
  const [deliveryProgress, setDeliveryProgress] = useState<DeliveryProgress | null>(null);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [projectTodos, setProjectTodos] = useState<TodoItem[]>([]);
  const [myTodos, setMyTodos] = useState<TodoItem[]>([]);
  const [projectTodoRange, setProjectTodoRange] = useState('week');
  const [myTodoRange, setMyTodoRange] = useState('week');

  useEffect(() => {
    fetchOverview();
    fetchTodos('project', 'week');
    fetchTodos('mine', 'week');
  }, []);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const data = await dashboardService.getOverview();
      setStatCards(data.stat_cards);
      setDeliveryProgress(data.delivery_progress);
      setMilestones(data.milestones);
      setRisks(data.risks);
    } catch (error) {
      message.error('加载首页数据失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchTodos = async (scope: string, range: string) => {
    try {
      const data = await dashboardService.getTodos(scope, range);
      if (scope === 'project') {
        setProjectTodos(data);
      } else {
        setMyTodos(data);
      }
    } catch (error) {
      message.error(`加载${scope === 'project' ? '项目' : '我的'}待办失败`);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '100px' }}><Spin size="large" /></div>;
  }

  return (
    <div className="dashboard-container">
      {/* ① 顶部卡片区(7个,横向滚动) */}
      <div className="stat-scroll">
        <div className="stat-row">
          {statCards.map((card, idx) => (
            <div key={idx} className="stat-card">
              <div className="label">{card.label}</div>
              <div className={`value ${card.badge_red ? 'badge-red' : ''}`}>
                {card.value}<span className="unit"> {card.unit}</span>
              </div>
              <div className="drill">查看详情 →</div>
            </div>
          ))}
        </div>
      </div>

      {/* ② 交付进度 */}
      <Card title="交付进度" style={{ marginBottom: 16 }}>
        {deliveryProgress && (
          <>
            {/* 整体进度(顶部) */}
            <div className="overall-wrap">
              <div className="overall">
                <div className="big-bar">
                  <div className="big-bar-fill" style={{ width: `${deliveryProgress.overall_progress}%` }}></div>
                </div>
                <div className="pct">{deliveryProgress.overall_progress}%</div>
              </div>
              <div style={{ fontSize: 12, color: '#999', marginTop: 8 }}>
                项目整体进度 = 已完成末级任务数 / 总末级任务数
              </div>
            </div>

            {/* 三栏:学校/硬件/软件 */}
            <div className="progress-scroll">
              <div className="progress-row">
                {/* 学校交付进度 */}
                <div className="progress-col">
                  <div style={{ fontWeight: 600, marginBottom: 12 }}>学校交付进度</div>
                  <div className="donut-wrap">
                    <div className="donut">
                      <div className="inner">
                        <div className="pct">{Math.round((deliveryProgress.school_completed / deliveryProgress.school_total) * 100)}%</div>
                        <div className="sub">已完成{deliveryProgress.school_completed}所</div>
                      </div>
                    </div>
                    <div className="legend">
                      {deliveryProgress.school_progress.map((item, idx) => (
                        <div key={idx} className="legend-item">
                          <span className="dot" style={{ background: item.color }}></span>
                          <span>{item.label}</span>
                          <span>{item.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 硬件交付进度 */}
                <div className="progress-col">
                  <div style={{ fontWeight: 600, marginBottom: 12 }}>硬件交付进度</div>
                  <div className="donut-wrap">
                    <div className="donut">
                      <div className="inner">
                        <div className="pct">{Math.round((deliveryProgress.hardware_completed / deliveryProgress.hardware_total) * 100)}%</div>
                        <div className="sub">已验收{deliveryProgress.hardware_completed}台</div>
                      </div>
                    </div>
                    <div className="legend">
                      {deliveryProgress.hardware_progress.map((item, idx) => (
                        <div key={idx} className="legend-item">
                          <span className="dot" style={{ background: item.color }}></span>
                          <span>{item.label}</span>
                          <span>{item.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 软件平台交付进度 */}
                <div className="progress-col">
                  <div style={{ fontWeight: 600, marginBottom: 12 }}>软件平台交付进度</div>
                  <div className="soft-list">
                    {deliveryProgress.software_modules.map((mod, idx) => (
                      <div key={idx} className="soft-item">
                        <div className="top">
                          <span>
                            {mod.name} <span className={`tag tag-${getStatusTagClass(mod.phase)}`}>{mod.phase}</span>
                          </span>
                          <span>{mod.progress}%</span>
                        </div>
                        <div className="bar">
                          <span style={{ width: `${mod.progress}%`, background: getProgressColor(mod.phase) }}></span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </Card>

      {/* ③ 关键里程碑 */}
      <Card title="关键里程碑" extra={<span style={{ color: '#1677ff', cursor: 'pointer' }}>查看完整计划 →</span>} style={{ marginBottom: 16 }}>
        <div className="gantt-container">
          <table className="gantt">
            <thead>
              <tr>
                <th className="stage">阶段</th>
                <th className="task">任务</th>
                <th className="axis">时间轴</th>
                <th style={{ width: 120 }}>计划开始时间</th>
                <th style={{ width: 140 }}>计划完成时间</th>
                <th style={{ width: 100 }}>状态</th>
              </tr>
            </thead>
            <tbody>
              {milestones.map((m, idx) => (
                <tr key={idx}>
                  <td className="stage" title={m.phase}>{m.phase}</td>
                  <td className="task" title={m.task}>{m.task}</td>
                  <td className="gbar-cell"></td>
                  <td className="date start">{m.plan_start_date || '-'}</td>
                  <td className="date finish">{m.plan_end_date || '-'}</td>
                  <td className={`status st-${getStatusClass(m.status)}`}>{m.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* ④ 项目风险跟踪 */}
      <Card title={`项目风险跟踪(活跃 ${risks.length} 项)`} extra={<span style={{ color: '#1677ff', cursor: 'pointer' }}>查看全部 →</span>} style={{ marginBottom: 16 }}>
        <div className="tb-container">
          <table className="tb">
            <colgroup>
              <col style={{ width: 90 }} />
              <col style={{ width: 180 }} />
              <col style={{ width: 180 }} />
              <col style={{ width: 180 }} />
              <col style={{ width: 120 }} />
              <col style={{ width: 140 }} />
              <col style={{ width: 140 }} />
              <col style={{ width: 100 }} />
            </colgroup>
            <thead>
              <tr>
                <th>等级</th>
                <th>风险描述</th>
                <th>风险影响评估</th>
                <th>应对方案</th>
                <th>责任人</th>
                <th>登记时间</th>
                <th>计划关闭时间</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {risks.map((r) => (
                <tr key={r.id} style={{ cursor: 'pointer' }}>
                  <td><span className={`lv lv-${getLevelClass(r.risk_level)}`}>{r.risk_level}</span></td>
                  <td title={r.description}>{r.description}</td>
                  <td title={r.impact || ''}>{r.impact || '-'}</td>
                  <td title={r.response_plan || ''}>{r.response_plan || '-'}</td>
                  <td>{r.owner_name || '-'}</td>
                  <td>{r.registered_at || '-'}</td>
                  <td>{r.plan_close_date || '-'}</td>
                  <td>{r.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* ⑤ 待办区(两个独立框) */}
      <div className="todo-panels">
        {/* 项目待办 */}
        <Card
          title="项目待办"
          extra={
            <div className="filter-btns">
              {['month', 'week', 'today'].map(r => (
                <button
                  key={r}
                  className={projectTodoRange === r ? 'active' : ''}
                  onClick={() => { setProjectTodoRange(r); fetchTodos('project', r); }}
                >
                  {r === 'month' ? '本月' : r === 'week' ? '本周' : '今日'}
                </button>
              ))}
            </div>
          }
        >
          <div className="todo-list">
            {projectTodos.map(t => (
              <div key={t.id} className="todo-item">
                <div><strong>{t.task_name}</strong></div>
                <div style={{ fontSize: 12, color: '#999' }}>
                  负责人: {t.assignee_name || '未指定'} | 截止: {t.plan_end_date || '-'}
                </div>
              </div>
            ))}
            {projectTodos.length === 0 && <div style={{ textAlign: 'center', color: '#999', padding: 20 }}>暂无待办</div>}
          </div>
        </Card>

        {/* 我的待办 */}
        <Card
          title="我的待办"
          extra={
            <div className="filter-btns">
              {['month', 'week', 'today'].map(r => (
                <button
                  key={r}
                  className={myTodoRange === r ? 'active' : ''}
                  onClick={() => { setMyTodoRange(r); fetchTodos('mine', r); }}
                >
                  {r === 'month' ? '本月' : r === 'week' ? '本周' : '今日'}
                </button>
              ))}
            </div>
          }
        >
          <div className="todo-list">
            {myTodos.map(t => (
              <div key={t.id} className="todo-item">
                <div><strong>{t.task_name}</strong></div>
                <div style={{ fontSize: 12, color: '#999' }}>截止: {t.plan_end_date || '-'}</div>
              </div>
            ))}
            {myTodos.length === 0 && <div style={{ textAlign: 'center', color: '#999', padding: 20 }}>暂无待办</div>}
          </div>
        </Card>
      </div>
    </div>
  );
};

// 辅助函数
const getStatusTagClass = (status: string) => {
  if (status === '已上线') return 'on';
  if (status === '测试中') return 'test';
  return 'dev';
};

const getProgressColor = (status: string) => {
  if (status === '已上线') return '#52c41a';
  if (status === '测试中') return '#fa8c16';
  return '#1677ff';
};

const getStatusClass = (status: string) => {
  if (status === '已完成') return 'done';
  if (status === '进行中') return 'doing';
  return 'todo';
};

const getLevelClass = (level: string) => {
  if (level === '高') return 'h';
  if (level === '中') return 'm';
  return 'l';
};

export default Dashboard;