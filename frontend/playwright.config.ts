import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 配置 - GX项目L3端到端验证
 *
 * 用途：验证前后端集成（浏览器真实交互）
 * 覆盖：登录、Dashboard、项目计划（甘特/列表/看板）、风险管理
 */
export default defineConfig({
  testDir: './e2e',

  // 超时配置
  timeout: 30 * 1000,           // 单个测试30s
  expect: { timeout: 5000 },     // 断言5s

  // 失败重试
  retries: process.env.CI ? 2 : 0,

  // 并行worker数
  workers: process.env.CI ? 1 : undefined,

  // 报告
  reporter: [
    ['html', { outputFolder: 'e2e-report' }],
    ['list']
  ],

  use: {
    // 基础URL（本地开发）
    baseURL: 'http://localhost:3000',

    // 追踪（失败时保留）
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // 浏览器配置
    actionTimeout: 10000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // 本地开发服务器配置（可选，手动启动更灵活）
  // webServer: {
  //   command: 'npm start',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
});
