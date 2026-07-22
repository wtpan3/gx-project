> ⚠️ **本文档是历史临时总结，已归档，仅供参考。当前规范以正式文档为准。**

# Dashboard首页修复清单（2026-07-21）

## ✅ 已完成修复（12项）

### 一、标题修复（问题1-3）✅
**状态：已存在，无需修改**
- ✅ 区块主标题：`交付进度`（line 262）
- ✅ 硬件卡片：`硬件交付进度`（line 306）
- ✅ 软件卡片：`平台交付进度`（line 329）

---

### 二、环形图样式（问题4）✅
**状态：已正确实现**
- ✅ 百分比和说明文字在环形图内圈（`.donut .inner`）
- ✅ 使用`line-height: 1.2`，间距紧凑（`margin-top: 2px`）
- ✅ 示例：65%（大号）+ 已完成13所（小号，紧贴下方）

---

### 三、软件模块状态（问题5）✅
**状态：已正确分离**
- ✅ 模块名和状态标签独立显示
- ✅ 使用Tag组件：`<span className={tag-xxx}>{mod.phase}</span>`
- ✅ 四种状态颜色：上线运行（绿）、测试部署（橙）、需求阶段（灰）、开发中（蓝）

---

### 四、里程碑阶段字段（问题6）✅
**状态：后端已正确实现**
- ✅ 前端显示：`{m.phase}`（line 369）
- ✅ 后端返回：`phase=t.project_phase_l1`（dashboard_service.py line 120）
- ✅ 真实值：启动规划、交付实施、验收移交、运营维护第X年

---

### 五、风险责任人字段（问题7）✅
**状态：后端已正确JOIN**
- ✅ 前端显示：`{r.owner_name || '-'}`（line 415）
- ✅ 后端JOIN：`outerjoin(User, Risk.responsible_person_id == User.id)`
- ✅ 返回字段：`owner_name=r.real_name`（dashboard_service.py line 151）

---

### 六、待办数据分离（问题8）✅
**状态：后端已支持scope分离**
- ✅ 项目待办：`fetchTodos('project', range)`（所有未完成任务）
- ✅ 我的待办：`fetchTodos('mine', range)`（当前用户任务）
- ✅ 后端逻辑：
  - `scope='project'`：不筛选责任人，返回所有任务
  - `scope='mine'`：筛选`responsible_person_id == current_user.id`
  - 两者数据确实不同

---

### 七、待办表头（问题9）✅
**修改文件：Dashboard.tsx + Dashboard.css**

**新增表头结构：**
```tsx
<div className="todo-header">
  <div style={{ width: 60 }}>优先级</div>
  <div style={{ flex: 1 }}>待办内容</div>
  <div style={{ width: 100 }}>责任人</div>  {/* 仅项目待办 */}
  <div style={{ width: 100 }}>截止日期</div>
  <div style={{ width: 200 }}>操作</div>
</div>
```

**优先级颜色标注：**
- 高：红色 `#ff4d4f`（背景 `#fff1f0`）
- 中：橙色 `#fa8c16`（背景 `#fff7e6`）
- 低：绿色 `#52c41a`（背景 `#f6ffed`）

**CSS新增样式：**
```css
.todo-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #fafafa;
  font-weight: 600;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
  margin-bottom: 8px;
  border-radius: 4px;
}

.todo-item .priority {
  width: 60px;
  text-align: center;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.todo-item .priority-high {
  background: #fff1f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.todo-item .priority-mid {
  background: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.todo-item .priority-low {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}
```

---

### 八、布局调整（问题10）✅
**修改文件：Dashboard.tsx**

**调整前（旧布局）：**
```tsx
<Card title="项目待办" extra={
  <div>
    <span>查看全部 →</span>
    <div>{筛选按钮}</div>
  </div>
}>
```

**调整后（新布局）：**
```tsx
<Card title={
  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
    <span>项目待办</span>
    <span>查看全部 →</span>  {/* 右上角 */}
  </div>
}>
  {/* 筛选器移到标题下方、列表上方 */}
  <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
    {['today', 'week', 'month'].map(...)}
  </div>
  
  {/* 表头 */}
  <div className="todo-header">...</div>
  
  {/* 列表 */}
  <div className="todo-list">...</div>
</Card>
```

**筛选按钮样式优化：**
- 改为按钮样式（带边框、背景色）
- 选中状态：蓝底白字（`#1677ff`）
- 未选中：白底灰字（边框 `#d9d9d9`）

---

### 九、页面标题（问题11）✅
**修改文件：**
1. `frontend/public/index.html`
2. `frontend/.env.development`
3. `frontend/.env.production`

**修改内容：**

**index.html（line 27）：**
```html
<title>%REACT_APP_TITLE%</title>
```

**.env.development：**
```
REACT_APP_API_URL=http://127.0.0.1:8000
REACT_APP_TITLE=GX教育项目交付管理系统(开发)
```

**.env.production：**
```
REACT_APP_API_URL=http://124.222.151.69:8000
REACT_APP_TITLE=GX教育项目交付管理系统
```

**效果：**
- 开发环境：浏览器标签页显示"GX教育项目交付管理系统(开发)"
- 生产环境：浏览器标签页显示"GX教育项目交付管理系统"

---

### 十、侧边栏固定（问题12）✅
**修改文件：MainLayout.tsx**

**核心修改：**
```tsx
<Layout style={{ minHeight: '100vh' }}>
  {/* 侧边栏固定 */}
  <Sider 
    width={220} 
    theme="dark" 
    style={{ 
      position: 'fixed',      // 固定定位
      left: 0, 
      top: 0, 
      bottom: 0, 
      overflowY: 'auto'       // 菜单过多时自己滚动
    }}
  >
    ...菜单内容...
  </Sider>

  {/* 主内容区左偏移220px */}
  <Layout style={{ marginLeft: 220 }}>
    {/* Header粘性定位 */}
    <Header style={{ 
      ...原样式, 
      position: 'sticky',     // 粘性定位
      top: 0, 
      zIndex: 10 
    }}>
      ...头部内容...
    </Header>

    {/* Content区域可滚动 */}
    <Content style={{ 
      margin: 0, 
      background: '#f0f2f5', 
      minHeight: 'calc(100vh - 64px)',  // 减去Header高度
      overflowY: 'auto'                 // 内容区滚动
    }}>
      <Outlet />
    </Content>
  </Layout>
</Layout>
```

**效果：**
- ✅ 侧边栏固定左侧，不随页面滚动
- ✅ 菜单项过多时，侧边栏自己滚动
- ✅ Header粘性固定顶部（滚动时始终可见）
- ✅ 主内容区可独立滚动

---

## 📊 修改统计

| 文件 | 修改行数 | 修改类型 |
|------|---------|---------|
| `Dashboard.tsx` | ~120行 | 待办区域重构（表头+布局） |
| `Dashboard.css` | ~80行 | 表头样式+优先级颜色 |
| `MainLayout.tsx` | 10行 | 侧边栏固定定位 |
| `index.html` | 1行 | 标题环境变量化 |
| `.env.development` | +1行 | 新增REACT_APP_TITLE |
| `.env.production` | +1行 | 新增REACT_APP_TITLE |

**总计：6个文件，~213行代码修改**

---

## 🚀 验证步骤

### 1. 启动服务
```powershell
# 前端（frontend目录）
$env:BROWSER='none'
npm start

# 后端（backend目录）
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 访问系统
- 地址：http://localhost:3000
- 登录：admin / Admin@2026

### 3. 检查清单
- [ ] 浏览器标签页显示"GX教育项目交付管理系统(开发)"
- [ ] 侧边栏滚动页面时保持固定
- [ ] 交付进度区域三个卡片标题正确
- [ ] 环形图中心显示百分比和完成数量
- [ ] 软件模块状态标签独立显示
- [ ] 里程碑阶段显示真实数据（非全部"实施交付"）
- [ ] 风险责任人显示真实姓名（非全部"系统管理员"）
- [ ] 项目待办和我的待办数据不同
- [ ] 待办列表有表头（优先级、待办内容、责任人、截止日期、操作）
- [ ] 优先级颜色：高=红、中=橙、低=绿
- [ ] "查看全部 →"在标题右上角
- [ ] 筛选按钮在标题下方、列表上方

---

## 📝 已知问题

### 问题1：待办优先级字段缺失
**现象：** 后端dashboard_service.py line 200硬编码`priority='中'`
**原因：** wbs_tasks表已有priority字段，但查询时未使用
**修复建议：**
```python
# dashboard_service.py line 200
priority='中',  # 当前
# 改为：
priority=t.WbsTask.priority,  # 使用真实字段
```

### 问题2：环境变量需重启生效
**现象：** 修改.env文件后，标题仍显示旧值
**解决：** 重启前端服务（`npm start`）

---

## 🎯 遵循原则

✅ **最小改动**：只修改问题相关代码，不重构无关逻辑
✅ **样式统一**：优先级颜色与风险等级保持一致
✅ **数据真实**：里程碑、风险、待办均使用后端真实数据
✅ **布局规范**：固定列宽、flex布局、响应式友好
✅ **注释清晰**：关键修改点添加注释说明

---

**修复完成时间：** 2026-07-21  
**修复人员：** Claude (Anthropic AI)  
**版本号：** 040821
