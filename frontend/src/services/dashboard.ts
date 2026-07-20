import api from './api';

export const dashboardService = {
  /**
   * 获取首页总览数据
   */
  getOverview: async () => {
    const response = await api.get('/api/v1/dashboard/overview');
    return response.data;
  },

  /**
   * 获取待办任务
   * @param scope 'project' | 'mine'
   * @param range 'week' | 'month' | 'today'
   */
  getTodos: async (scope: string, range: string) => {
    const response = await api.get('/api/v1/dashboard/todos', {
      params: { scope, range }
    });
    return response.data;
  }
};
