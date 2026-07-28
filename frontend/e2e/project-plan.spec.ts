import { test, expect } from '@playwright/test';

/**
 * L3端到端验证 - 项目计划（重点）
 *
 * 验证层级：L3（浏览器端到端）
 * 覆盖功能：
 * - 三视图切换（甘特/列表/看板）
 * - 任务新增（日期校验、父子范围）
 * - 行内编辑
 * - 日期冲突弹窗
 */

const TEST_USER = {
  username: 'admin',
  password: 'Admin@2026'
};

test.describe('项目计划 - 三视图与任务操作', () => {
  test.beforeEach(async ({ page }) => {
    // 登录并跳转到项目计划
    await page.goto('/login');
    await page.fill('input[placeholder="用户名"]', TEST_USER.username);
    await page.fill('input[placeholder="密码"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // 跳转到项目计划
    await page.goto('/project-plan');
    await expect(page).toHaveURL('/project-plan');
  });

  test('三视图切换正常', async ({ page }) => {
    // Tab 用 role=tab 定位，避免 text= 误匹配表格内容
    const ganttTab = page.getByRole('tab', { name: /甘特图/ });
    const listTab = page.getByRole('tab', { name: /列表/ });
    const kanbanTab = page.getByRole('tab', { name: /看板/ });

    // 默认甘特图：原生 table（非 .ant-table），表头含"任务名称/责任人/进度/状态"
    await expect(ganttTab).toHaveAttribute('aria-selected', 'true');
    const ganttHead = page.locator('thead').filter({ hasText: '责任人' }).first();
    await expect(ganttHead).toBeVisible();

    // 切列表：Ant Design Table 出现
    await listTab.click();
    await expect(page.locator('.ant-table')).toBeVisible({ timeout: 10000 });
    await expect(listTab).toHaveAttribute('aria-selected', 'true');

    // 切看板：5 个状态列 Card（待开始/进行中/已完成/已延期/待补材料）
    await kanbanTab.click();
    await page.waitForTimeout(800);
    for (const s of ['待开始', '进行中', '已完成', '已延期', '待补材料']) {
      await expect(
        page.locator('.ant-card-head-title').filter({ hasText: s }).first()
      ).toBeVisible({ timeout: 10000 });
    }

    // 切回甘特图，表头仍在
    await ganttTab.click();
    await expect(ganttHead).toBeVisible({ timeout: 10000 });
  });

  test('新增任务 - 日期倒挂被前端表单校验拦截', async ({ page }) => {
    await page.locator('button:has-text("新增任务")').first().click();
    const modal = page.locator('.ant-modal').filter({ hasText: '新增任务' });
    await expect(modal).toBeVisible({ timeout: 5000 });

    await modal.locator('#task_name, input[placeholder="如：设备安装"]').first()
      .fill('E2E日期倒挂用例');

    // 先填结束日，再填更晚的开始日 —— 触发 plan_start_date 的兜底 validator
    const startPicker = modal.locator('.ant-form-item').filter({ hasText: '计划开始' })
      .locator('input').first();
    const endPicker = modal.locator('.ant-form-item').filter({ hasText: '计划结束' })
      .locator('input').first();

    await endPicker.click();
    await endPicker.fill('2026-10-10');
    await page.keyboard.press('Enter');

    await startPicker.click();
    await startPicker.fill('2026-12-31');
    await page.keyboard.press('Enter');

    // 提交，断言前端拦截（后端 400 是第二层，这里验第一层）
    await modal.locator('.ant-modal-footer button.ant-btn-primary').click();
    await expect(
      modal.locator('.ant-form-item-explain-error').filter({ hasText: '计划开始不能晚于计划结束' })
    ).toBeVisible({ timeout: 5000 });

    // 弹窗未关闭 = 未提交成功
    await expect(modal).toBeVisible();
    await modal.locator('.ant-modal-close').click();
  });

  test('新增任务 - 选定父任务后日历限制在父范围内', async ({ page }) => {
    await page.locator('button:has-text("新增任务")').first().click();
    const modal = page.locator('.ant-modal').filter({ hasText: '新增任务' });
    await expect(modal).toBeVisible({ timeout: 5000 });

    // 选第一个父任务
    const parentSelect = modal.locator('.ant-form-item').filter({ hasText: '父任务' })
      .locator('.ant-select').first();
    await parentSelect.click();
    const firstOption = page.locator('.ant-select-dropdown .ant-select-item-option').first();
    await expect(firstOption).toBeVisible({ timeout: 5000 });
    await firstOption.click();

    // 层级自动推导（父 L1 → 子 L2）
    const levelInput = modal.locator('.ant-form-item').filter({ hasText: '当前任务层级' })
      .locator('input').first();
    await expect(levelInput).toHaveValue(/^L\d+（父任务 L\d+）$/, { timeout: 5000 });

    // 提示"父任务可用区间"，并解析出区间用于校验日历置灰
    const extra = modal.locator('.ant-form-item-extra').filter({ hasText: '父任务可用区间' });
    await expect(extra).toBeVisible({ timeout: 5000 });
    const rangeText = (await extra.textContent()) ?? '';
    const m = rangeText.match(/(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})/);
    expect(m, `未能从"${rangeText}"解析父任务区间`).not.toBeNull();

    // 打开"计划开始"日历，父范围外的日期应被置灰（disabledDate 生效）
    await modal.locator('.ant-form-item').filter({ hasText: '计划开始' })
      .locator('input').first().click();
    const panel = page.locator('.ant-picker-dropdown').last();
    await expect(panel).toBeVisible({ timeout: 5000 });

    const parentStart = m![1];
    const outside = panel.locator(`td[title="${parentStart}"]`).first();
    // 父开始日当天必须可选
    if (await outside.count()) {
      await expect(outside).not.toHaveClass(/ant-picker-cell-disabled/);
    }
    // 面板内存在被置灰的单元格，证明限制已施加
    await expect(panel.locator('td.ant-picker-cell-disabled').first()).toBeVisible();

    await page.keyboard.press('Escape');
    await modal.locator('.ant-modal-close').click();
  });

  test('行内编辑 - 状态浮层改状态并回写', async ({ page }) => {
    // 切到列表视图
    await page.getByRole('tab', { name: /列表/ }).click();
    await expect(page.locator('.ant-table')).toBeVisible({ timeout: 10000 });

    // 等数据行渲染（排除 antd 的占位行）
    const rows = page.locator('.ant-table-tbody tr.ant-table-row');
    await expect(rows.first()).toBeVisible({ timeout: 10000 });

    // 第一行的状态 Tag（状态列 render 成可点击 Tag）
    const firstRow = rows.first();
    const statusTag = firstRow.locator('.ant-tag').first();
    await expect(statusTag).toBeVisible();
    const before = (await statusTag.textContent())?.trim();

    // 点 Tag 弹出状态浮层（fixed 定位，无类名，用 5 个状态项文本定位）
    await statusTag.click();
    const STATUS = ['待开始', '进行中', '已完成', '已延期', '待补材料'];
    const popoverItem = (s: string) =>
      page.locator('div').filter({ hasText: new RegExp(`^${s}$`) }).last();
    await expect(popoverItem('待开始')).toBeVisible({ timeout: 5000 });

    // 选一个与当前不同的状态
    const target = STATUS.find(s => s !== before) ?? '进行中';
    await popoverItem(target).click();

    // 回写校验：局部更新，Tag 文本应变为目标状态（代码注释说明不整表重载）
    await expect(statusTag).toHaveText(target, { timeout: 10000 });

    // 浮层关闭
    await expect(popoverItem('待补材料')).toBeHidden({ timeout: 5000 });

    // 刷新后仍是新状态，确认已落库而非仅前端态
    await page.reload();
    await page.getByRole('tab', { name: /列表/ }).click();
    await expect(page.locator('.ant-table')).toBeVisible({ timeout: 10000 });
    await expect(
      page.locator('.ant-table-tbody tr.ant-table-row').first().locator('.ant-tag').first()
    ).toHaveText(target, { timeout: 10000 });
  });
});
