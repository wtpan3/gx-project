import { test, expect } from '@playwright/test';

/**
 * L3端到端验证 - 登录与Dashboard
 *
 * 验证层级：L3（浏览器端到端）
 * 覆盖功能：登录、Dashboard总览卡片、待办列表
 */

const TEST_USER = {
  username: 'admin',
  password: 'Admin@2026'
};

test.describe('登录与Dashboard', () => {
  test('登录成功并跳转Dashboard', async ({ page }) => {
    // 访问登录页
    await page.goto('/login');
    await expect(page).toHaveTitle(/GX教育项目.*管理系统/);

    // 填写登录表单（Ant Design Form渲染的input有placeholder属性）
    await page.fill('input[placeholder="用户名"]', TEST_USER.username);
    await page.fill('input[placeholder="密码"]', TEST_USER.password);

    // 点击登录按钮（使用htmlType="submit"更可靠）
    await page.click('button[type="submit"]');

    // 验证跳转到Dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // 验证Dashboard核心元素存在（使用Card标题的精确选择器）
    await expect(page.locator('.ant-card-head-title:has-text("交付进度")')).toBeVisible();
  });

  test('Dashboard总览卡片显示', async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('input[placeholder="用户名"]', TEST_USER.username);
    await page.fill('input[placeholder="密码"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // 验证核心Card标题存在（使用精确选择器避免匹配多个元素）
    await expect(page.locator('.ant-card-head-title:has-text("交付进度")')).toBeVisible();
    await expect(page.locator('.ant-card-head-title:has-text("关键里程碑")')).toBeVisible();
    await expect(page.locator('.ant-card-head-title').filter({ hasText: /^项目风险跟踪/ })).toBeVisible();

    // 验证顶部统计卡片区域存在
    const statCards = page.locator('.stat-card');
    await expect(statCards.first()).toBeVisible();
  });

  test('Dashboard待办区两栏与时间筛选', async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('input[placeholder="用户名"]', TEST_USER.username);
    await page.fill('input[placeholder="密码"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // 待办区容器（Dashboard.tsx 用的是 .todo-panels，两个 Card 并排）
    const todoPanels = page.locator('.todo-panels');
    await expect(todoPanels).toBeVisible();

    // 两栏标题：项目待办 / 我的待办
    const projectCard = todoPanels.locator('.ant-card').filter({ hasText: '项目待办' }).first();
    const myCard = todoPanels.locator('.ant-card').filter({ hasText: '我的待办' }).first();
    await expect(projectCard).toBeVisible();
    await expect(myCard).toBeVisible();

    // 每栏都有 今日/本周/本月 筛选器，默认选中"本周"
    for (const card of [projectCard, myCard]) {
      for (const label of ['今日', '本周', '本月']) {
        await expect(card.locator(`text=${label}`).first()).toBeVisible();
      }
    }

    // 表头四列存在
    await expect(projectCard.locator('.todo-header .col-name')).toHaveText('待办内容');
    await expect(projectCard.locator('.todo-header .col-person')).toHaveText('责任人');

    // 切换到"今日"：列表区要么有项，要么显示"暂无待办"，不能空白
    await projectCard.locator('text=今日').first().click();
    await page.waitForTimeout(800); // 等接口返回
    const list = projectCard.locator('.todo-list');
    await expect(list).toBeVisible();
    const itemCount = await list.locator('.todo-item').count();
    if (itemCount === 0) {
      await expect(list.locator('.todo-empty')).toHaveText('暂无待办');
    }

    // 切回"本周"仍正常渲染
    await projectCard.locator('text=本周').first().click();
    await page.waitForTimeout(800);
    await expect(list).toBeVisible();
  });
});
