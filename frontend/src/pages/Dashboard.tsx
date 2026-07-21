import React, { useEffect, useState, useCallback } from 'react';
import { Card, Spin, message } from 'antd';
import { useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [statCards, setStatCards] = useState<StatCard[]>([]);
  const [deliveryProgress, setDeliveryProgress] = useState<DeliveryProgress | null>(null);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [projectTodos, setProjectTodos] = useState<TodoItem[]>([]);
  const [myTodos, setMyTodos] = useState<TodoItem[]>([]);
  const [projectTodoRange, setProjectTodoRange] = useState('week');
  const [myTodoRange, setMyTodoRange] = useState('week');

  const fetchTodos = useCallback(async (scope: string, range: string) => {
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
  }, []);

  useEffect(() => {
    fetchOverview();
    fetchTodos('project', 'week');
    fetchTodos('mine', 'week');
  }, [fetchTodos]);

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

  // 环形图渲染函数 - 使用useMemo优化
  const renderDonutChart = useCallback((items: ProgressItem[], total: number) => {
    if (!items || items.length === 0) return null;

    // 确保总和为100%：如果数据总和不等于total，强制填充到100%
    const actualTotal = items.reduce((sum, item) => sum + item.count, 0);
    const useTotal = actualTotal > 0 ? actualTotal : total;

    let cumulativePercent = 0;
    const segments = items.map(item => {
      const percent = (item.count / useTotal) * 100;
      const segment = {
        ...item,
        percent,
        startPercent: cumulativePercent
      };
      cumulativePercent += percent;
      return segment;
    });

    return (
      <svg viewBox="0 0 42 42" style={{ width: '180px', height: '180px' }}>
        {segments.map((seg, idx) => {
          const circumference = 2 * Math.PI * 15.91549430918954;
          // 配合下方 rotate(-90) 让起点在12点方向，offset只需按起始百分比顺时针偏移
          const offset = -circumference * (seg.startPercent / 100);
          const dashLength = circumference * (seg.percent / 100);
          // 即使count=0，也显示0%（dashLength=0会自动不显示，但在图例中保留）
          return (
            <circle
              key={idx}
              cx="21"
              cy="21"
              r="15.91549430918954"
              fill="transparent"
              stroke={seg.color}
              strokeWidth="5"
              strokeDasharray={`${dashLength} ${circumference}`}
              strokeDashoffset={offset}
              transform="rotate(-90 21 21)"
              style={{ transition: 'all 0.3s' }}
            />
          );
        })}
      </svg>
    );
  }, []);

  // 时间轴甘特图渲染
  const renderGanttBar = useCallback((milestone: Milestone) => {
    if (!milestone.plan_start_date || !milestone.plan_end_date) {
      return <div style={{ color: '#999', fontSize: 12 }}>-</div>;
    }

    const start = new Date(milestone.plan_start_date);
    const end = new Date(milestone.plan_end_date);

    // 计算时间范围（以所有里程碑的最早和最晚日期为准）
    const allDates = milestones.flatMap(m =>
      [m.plan_start_date, m.plan_end_date].filter(Boolean).map(d => new Date(d!))
    );
    const minDate = new Date(Math.min(...allDates.map(d => d.getTime())));
    const maxDate = new Date(Math.max(...allDates.map(d => d.getTime())));
    const totalDays = (maxDate.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24);

    const startOffset = ((start.getTime() - minDate.getTime()) / (1000 * 60 * 60 * 24)) / totalDays * 100;
    const duration = ((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) / totalDays * 100;

    let barColor = '#1677ff';
    if (milestone.status === '已完成') barColor = '#52c41a';
    else if (milestone.status === '进行中') barColor = '#fa8c16';
    else if (milestone.status === '已延期') barColor = '#ff4d4f';

    return (
      <div style={{ position: 'relative', height: '24px', background: '#f5f5f5', borderRadius: '4px' }}>
        <div
          style={{
            position: 'absolute',
            left: `${startOffset}%`,
            width: `${duration}%`,
            height: '100%',
            background: barColor,
            borderRadius: '4px',
            minWidth: '2px'
          }}
        />
      </div>
    );
  }, [milestones]);

  // 卡片点击跳转
  const handleCardClick = useCallback((label: string) => {
    const routeMap: Record<string, string> = {
      '覆盖学校': '/schools',
      '重点学校': '/schools?filter=key',
      '系统总数': '/device-systems',
      '设备类型': '/devices',
      '产线类型': '/production-lines',
      '外采设备': '/devices?filter=external',
      '硬件总数': '/devices'
    };
    const route = routeMap[label];
    if (route) {
      navigate(route);
    }
  }, [navigate]);

  // 辅助函数
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

  const getStatusTagClass = (phase: string) => {
    if (phase === '上线运行') return 'on';
    if (phase === '软件测试' || phase === '软件部署') return 'test';
    if (phase === '需求收集' || phase === '需求确认') return 'req';
    return 'dev';
  };

  const getProgressColor = (phase: string) => {
    if (phase === '上线运行') return '#52c41a';
    if (phase === '软件测试' || phase === '软件部署') return '#fa8c16';
    if (phase === '需求收集' || phase === '需求确认') return '#8c8c8c';
    return '#1677ff';
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
            <div key={idx} className="stat-card" onClick={() => handleCardClick(card.label)}>
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
                      {renderDonutChart(deliveryProgress.school_progress, deliveryProgress.school_total)}
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
                      {renderDonutChart(deliveryProgress.hardware_progress, deliveryProgress.hardware_total)}
                      <div className="inner">
                        <div className="pct">{Math.round((deliveryProgress.hardware_completed / deliveryProgress.hardware_total) * 100)}%</div>
                        <div className="sub">已完成{deliveryProgress.hardware_completed}台</div>
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

                {/* 平台交付进度 */}
                <div className="progress-col">
                  <div style={{ fontWeight: 600, marginBottom: 12 }}>平台交付进度</div>
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
            <colgroup>
              <col style={{ width: 100 }} />
              <col style={{ width: 140 }} />
              <col style={{ minWidth: 300 }} />
              <col style={{ width: 110 }} />
              <col style={{ width: 110 }} />
              <col style={{ width: 80 }} />
            </colgroup>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', paddingLeft: 8 }}>阶段</th>
                <th style={{ textAlign: 'left' }}>任务</th>
                <th>时间轴</th>
                <th>计划开始</th>
                <th>计划完成</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {milestones.map((m, idx) => (
                <tr key={idx}>
                  <td style={{ textAlign: 'left', paddingLeft: 8 }} title={m.phase}>{m.phase}</td>
                  <td style={{ textAlign: 'left' }} title={m.task}>{m.task}</td>
                  <td style={{ padding: '8px 12px' }}>{renderGanttBar(m)}</td>
                  <td style={{ fontSize: 12 }}>{m.plan_start_date || '-'}</td>
                  <td style={{ fontSize: 12 }}>{m.plan_end_date || '-'}</td>
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
              <col style={{ width: 60 }} />
              <col style={{ width: 280 }} />
              <col style={{ width: 180 }} />
              <col style={{ width: 280 }} />
              <col style={{ width: 80 }} />
              <col style={{ width: 100 }} />
              <col style={{ width: 100 }} />
              <col style={{ width: 80 }} />
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
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>项目待办</span>
              <span style={{ color: '#1677ff', cursor: 'pointer', fontSize: 14, fontWeight: 400 }} onClick={() => navigate('/todos?type=project')}>查看全部 →</span>
            </div>
          }
          style={{ flex: 1 }}
        >
          {/* 筛选器 */}
          <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
            {['today', 'week', 'month'].map(r => (
              <span
                key={r}
                style={{
                  cursor: 'pointer',
                  padding: '4px 12px',
                  borderRadius: 4,
                  background: projectTodoRange === r ? '#1677ff' : '#fff',
                  color: projectTodoRange === r ? '#fff' : '#666',
                  border: `1px solid ${projectTodoRange === r ? '#1677ff' : '#d9d9d9'}`,
                  fontSize: 13,
                  transition: 'all 0.2s'
                }}
                onClick={() => {
                  setProjectTodoRange(r);
                  fetchTodos('project', r);
                }}
              >
                {r === 'today' ? '今日' : r === 'week' ? '本周' : '本月'}
              </span>
            ))}
          </div>

          {/* 表头 */}
          <div className="todo-header">
            <div className="col-name">待办内容</div>
            <div className="col-person">责任人</div>
            <div className="col-date">计划完成时间</div>
            <div className="col-action-project">操作</div>
          </div>

          <div className="todo-list">
            {projectTodos.map(t => (
              <div key={t.id} className={`todo-item ${t.priority === '高' ? 'lv-high' : t.priority === '中' ? 'lv-mid' : 'lv-low'}`}>
                <div className="col-name name" title={t.task_name}>{t.task_name}</div>
                <div className="col-person">{t.assignee_name || '-'}</div>
                <div className="col-date">{t.plan_end_date}</div>
                <div className="col-action-project">
                  <span className="assign-btn" onClick={() => message.info(`指定负责人: ${t.task_name}`)}>指定负责人</span>
                  <span className="edit-btn" onClick={() => message.info(`编辑待办: ${t.task_name}`)}>编辑</span>
                </div>
              </div>
            ))}
            {projectTodos.length === 0 && <div className="todo-empty">暂无待办</div>}
          </div>
        </Card>

        {/* 我的待办 */}
        <Card
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>我的待办</span>
              <span style={{ color: '#1677ff', cursor: 'pointer', fontSize: 14, fontWeight: 400 }} onClick={() => navigate('/todos?type=mine')}>查看全部 →</span>
            </div>
          }
          style={{ flex: 1 }}
        >
          {/* 筛选器 */}
          <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
            {['today', 'week', 'month'].map(r => (
              <span
                key={r}
                style={{
                  cursor: 'pointer',
                  padding: '4px 12px',
                  borderRadius: 4,
                  background: myTodoRange === r ? '#1677ff' : '#fff',
                  color: myTodoRange === r ? '#fff' : '#666',
                  border: `1px solid ${myTodoRange === r ? '#1677ff' : '#d9d9d9'}`,
                  fontSize: 13,
                  transition: 'all 0.2s'
                }}
                onClick={() => {
                  setMyTodoRange(r);
                  fetchTodos('mine', r);
                }}
              >
                {r === 'today' ? '今日' : r === 'week' ? '本周' : '本月'}
              </span>
            ))}
          </div>

          {/* 表头 */}
          <div className="todo-header">
            <div className="col-name">待办内容</div>
            <div className="col-date">计划完成时间</div>
            <div className="col-action-mine">操作</div>
          </div>

          <div className="todo-list">
            {myTodos.map(t => (
              <div key={t.id} className={`todo-item ${t.priority === '高' ? 'lv-high' : t.priority === '中' ? 'lv-mid' : 'lv-low'}`}>
                <div className="col-name name" title={t.task_name}>{t.task_name}</div>
                <div className="col-date">{t.plan_end_date}</div>
                <div className="col-action-mine">
                  <span className="complete-btn" onClick={() => message.info(`完成待办: ${t.task_name}`)}>完成</span>
                  <span className="transfer-btn" onClick={() => message.info(`转办待办: ${t.task_name}`)}>转办</span>
                </div>
              </div>
            ))}
            {myTodos.length === 0 && <div className="todo-empty">暂无待办</div>}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
