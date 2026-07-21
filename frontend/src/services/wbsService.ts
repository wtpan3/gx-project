// WBS任务API服务
import axios from 'axios';
import { WbsTask, WbsTaskListResponse, WbsTaskCreate } from '../types/wbs';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export const wbsApi = {
  // 获取任务列表
  getWbsTasks: async (params: {
    page: number;
    page_size: number;
    status?: string;
    keyword?: string;
  }): Promise<WbsTaskListResponse> => {
    const response = await axios.get(`${API_BASE}/wbs-tasks`, { params });
    return response.data;
  },

  // 获取任务详情
  getWbsTaskDetail: async (id: number): Promise<WbsTask> => {
    const response = await axios.get(`${API_BASE}/wbs-tasks/${id}`);
    return response.data;
  },

  // 创建任务
  createWbsTask: async (data: WbsTaskCreate): Promise<WbsTask> => {
    const response = await axios.post(`${API_BASE}/wbs-tasks`, data);
    return response.data;
  },

  // 更新任务
  updateWbsTask: async (id: number, data: Partial<WbsTaskCreate>): Promise<WbsTask> => {
    const response = await axios.put(`${API_BASE}/wbs-tasks/${id}`, data);
    return response.data;
  },

  // 删除任务
  deleteWbsTask: async (id: number): Promise<void> => {
    await axios.delete(`${API_BASE}/wbs-tasks/${id}`);
  },
};
