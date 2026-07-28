// WBS任务类型定义

export interface WbsTask {
  id: number;
  project_id: number;
  task_code: string;
  parent_id?: number;
  project_phase_l1: string;
  sub_phase_l2: string;
  task_package_l3: string;
  work_content_l4: string;
  work_detail_l5?: string;

  priority: '高' | '中' | '低';
  stage_type?: '到货验收' | '加电测试' | '校级验收' | '培训' | '无';
  status: '待开始' | '进行中' | '已完成' | '已延期' | '待补材料';

  plan_start_date: string;
  plan_end_date: string;
  actual_start_date?: string;
  actual_end_date?: string;

  responsible_person_id: number;
  school_id: number;
  source_device_id?: number;
  construction_year?: number;

  progress_note?: string;
  deliverables?: string;

  is_orphan: number;
  requires_material: number;
  material_status?: '无要求' | '待上传' | '部分上传' | '已完成';

  // 关联字段
  assignee_name?: string;
  school_name?: string;

  created_at: string;
  updated_at: string;
}

export interface WbsTaskListResponse {
  total: number;
  items: WbsTask[];
}

export interface WbsTaskCreate {
  project_id: number;
  task_code: string;
  parent_id?: number;
  project_phase_l1: string;
  sub_phase_l2: string;
  task_package_l3: string;
  work_content_l4: string;
  work_detail_l5?: string;
  priority: '高' | '中' | '低';
  stage_type?: '到货验收' | '加电测试' | '校级验收' | '培训' | '无';
  status: '待开始' | '进行中' | '已完成' | '已延期' | '待补材料';
  plan_start_date: string;
  plan_end_date: string;
  actual_start_date?: string;
  actual_end_date?: string;
  responsible_person_id: number;
  school_id: number;
  source_device_id?: number;
  construction_year?: number;
  progress_note?: string;
  deliverables?: string;
  requires_material?: number;
  material_status?: '无要求' | '待上传' | '部分上传' | '已完成';
}
