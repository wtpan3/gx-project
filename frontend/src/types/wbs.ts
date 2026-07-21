// WBS任务类型定义

export interface WbsTask {
  id: number;
  construction_year: string;
  project_phase_l1: string;
  sub_phase_l2: string;
  task_package_l3: string;
  work_content_l4: string;
  work_detail_l5?: string;

  task_code: string;
  priority: '高' | '中' | '低';
  status: '待开始' | '进行中' | '已完成' | '已暂停';

  plan_start_date?: string;
  plan_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;

  responsible_person_id?: number;
  school_id?: number;

  progress_note?: string;
  deliverables?: string;

  // 关联字段
  assignee_name?: string;
  school_name?: string;

  is_orphan: number;
  created_at: string;
  updated_at: string;
}

export interface WbsTaskListResponse {
  total: number;
  items: WbsTask[];
}

export interface WbsTaskCreate {
  construction_year: string;
  project_phase_l1: string;
  sub_phase_l2: string;
  task_package_l3: string;
  work_content_l4: string;
  work_detail_l5?: string;
  task_code: string;
  priority: '高' | '中' | '低';
  status: '待开始' | '进行中' | '已完成' | '已暂停';
  plan_start_date?: string;
  plan_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  responsible_person_id?: number;
  school_id?: number;
  progress_note?: string;
  deliverables?: string;
}
