"""
GX项目交付管理系统 V2.1 - 后端API
基于需求文档V2.1完整实现
"""
import os
import json
import shutil
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
import sqlite3
import zipfile
from pathlib import Path

SECRET_KEY = "gx-project-secret-key-2026-v2.1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "gx.db")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # 用户表
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
        real_name TEXT NOT NULL, role TEXT DEFAULT 'campus_manager', phone TEXT UNIQUE,
        email TEXT, status TEXT DEFAULT '启用', created_at TEXT, updated_at TEXT)""")

    # 学校表
    c.execute("""CREATE TABLE IF NOT EXISTS schools (
        id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL,
        region TEXT, address TEXT, campus_manager_id INTEGER, contact_person TEXT,
        contact_phone TEXT, project_status TEXT DEFAULT '未启动', remark TEXT,
        created_at TEXT, updated_at TEXT,
        FOREIGN KEY (campus_manager_id) REFERENCES users(id))""")

    # 设备系统字典
    c.execute("""CREATE TABLE IF NOT EXISTS device_systems (
        id INTEGER PRIMARY KEY, project_name TEXT NOT NULL, construction_year TEXT NOT NULL,
        system_name TEXT NOT NULL, device_name TEXT NOT NULL, brand TEXT, model TEXT,
        params TEXT, device_type TEXT DEFAULT '硬件', unit TEXT DEFAULT '台',
        plan_quantity INTEGER DEFAULT 0, is_enabled INTEGER DEFAULT 1, created_at TEXT, updated_at TEXT)""")

    # 供应商表
    c.execute("""CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, contact_person TEXT,
        contact_phone TEXT, contact_email TEXT, remark TEXT, created_at TEXT, updated_at TEXT)""")

    # 模板表
    c.execute("""CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, template_type TEXT NOT NULL,
        stage TEXT, file_path TEXT, version TEXT DEFAULT 'V1.0', description TEXT,
        status TEXT DEFAULT '启用', created_at TEXT, updated_at TEXT)""")

    # 数据字典表
    c.execute("""CREATE TABLE IF NOT EXISTS dict_items (
        id INTEGER PRIMARY KEY, category TEXT NOT NULL, label TEXT NOT NULL,
        value TEXT NOT NULL, sort_order INTEGER DEFAULT 0, is_enabled INTEGER DEFAULT 1,
        parent_value TEXT, created_at TEXT, updated_at TEXT)""")

    # 项目信息表
    c.execute("""CREATE TABLE IF NOT EXISTS project_info (
        id INTEGER PRIMARY KEY, project_name TEXT NOT NULL, project_code TEXT UNIQUE NOT NULL,
        start_date TEXT, end_date TEXT, overall_status TEXT DEFAULT '未启动',
        created_at TEXT, updated_at TEXT)""")

    # WBS任务表（5级结构）
    c.execute("""CREATE TABLE IF NOT EXISTS wbs_tasks (
        id INTEGER PRIMARY KEY, phase_l1 TEXT NOT NULL, phase_l2 TEXT,
        task_package_l3 TEXT, work_content_l4 TEXT, work_detail_l5 TEXT,
        stage_type TEXT, plan_start_date TEXT, plan_end_date TEXT,
        status TEXT DEFAULT '待开始', actual_start_date TEXT, actual_end_date TEXT,
        assignee_id INTEGER, progress_note TEXT, deliverables TEXT, school_id INTEGER,
        construction_year TEXT, source_device_id INTEGER, is_orphan INTEGER DEFAULT 0,
        material_desc TEXT, created_at TEXT, updated_at TEXT,
        FOREIGN KEY (assignee_id) REFERENCES users(id),
        FOREIGN KEY (school_id) REFERENCES schools(id))""")

    # 任务附件表
    c.execute("""CREATE TABLE IF NOT EXISTS task_attachments (
        id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, file_name TEXT NOT NULL,
        file_path TEXT NOT NULL, file_size INTEGER, upload_by INTEGER,
        upload_time TEXT, description TEXT,
        FOREIGN KEY (task_id) REFERENCES wbs_tasks(id),
        FOREIGN KEY (upload_by) REFERENCES users(id))""")

    # 设备信息表
    c.execute("""CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY, project_name TEXT, construction_year TEXT,
        system_id INTEGER, system_name TEXT, device_name TEXT,
        brand TEXT, model TEXT, params TEXT, device_type TEXT, unit TEXT DEFAULT '台',
        source TEXT, quantity INTEGER DEFAULT 1, school_id INTEGER, install_location TEXT,
        status TEXT DEFAULT '待发货', supplier_id INTEGER, plan_arrival_date TEXT,
        delivery_no TEXT, delivery_date TEXT, arrival_date TEXT, install_date TEXT,
        debug_date TEXT, accept_date TEXT, remark TEXT, created_at TEXT, updated_at TEXT,
        FOREIGN KEY (system_id) REFERENCES device_systems(id),
        FOREIGN KEY (school_id) REFERENCES schools(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id))""")

    # 培训表
    c.execute("""CREATE TABLE IF NOT EXISTS trainings (
        id INTEGER PRIMARY KEY, type TEXT NOT NULL, content TEXT NOT NULL,
        target_audience TEXT, person_count INTEGER, duration_days INTEGER,
        location TEXT, training_method TEXT, exam_method TEXT, plan_date TEXT,
        actual_date TEXT, status TEXT DEFAULT '待培训', related_task_id INTEGER,
        is_district INTEGER DEFAULT 0, created_at TEXT, updated_at TEXT,
        FOREIGN KEY (related_task_id) REFERENCES wbs_tasks(id))""")

    # 培训与学校关联表
    c.execute("""CREATE TABLE IF NOT EXISTS training_schools (
        id INTEGER PRIMARY KEY, training_id INTEGER NOT NULL, school_id INTEGER NOT NULL,
        FOREIGN KEY (training_id) REFERENCES trainings(id),
        FOREIGN KEY (school_id) REFERENCES schools(id))""")

    # 培训附件表
    c.execute("""CREATE TABLE IF NOT EXISTS training_attachments (
        id INTEGER PRIMARY KEY, training_id INTEGER NOT NULL, file_name TEXT NOT NULL,
        file_path TEXT NOT NULL, file_size INTEGER, upload_by INTEGER,
        upload_time TEXT, file_type TEXT,
        FOREIGN KEY (training_id) REFERENCES trainings(id),
        FOREIGN KEY (upload_by) REFERENCES users(id))""")

    # 风险表
    c.execute("""CREATE TABLE IF NOT EXISTS risks (
        id INTEGER PRIMARY KEY, risk_desc TEXT NOT NULL, trigger_condition TEXT,
        impact_description TEXT, probability TEXT, impact TEXT, risk_level TEXT DEFAULT '低',
        response_strategy TEXT, response_deadline TEXT, responsible_person_id INTEGER,
        status TEXT DEFAULT '待处理', school_id INTEGER, created_at TEXT, updated_at TEXT,
        FOREIGN KEY (responsible_person_id) REFERENCES users(id),
        FOREIGN KEY (school_id) REFERENCES schools(id))""")

    # 风险与任务关联表
    c.execute("""CREATE TABLE IF NOT EXISTS risk_tasks (
        id INTEGER PRIMARY KEY, risk_id INTEGER NOT NULL, task_id INTEGER NOT NULL,
        FOREIGN KEY (risk_id) REFERENCES risks(id),
        FOREIGN KEY (task_id) REFERENCES wbs_tasks(id))""")

    # 报告表
    c.execute("""CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY, report_type TEXT NOT NULL, report_scope TEXT NOT NULL,
        school_id INTEGER, period_start TEXT, period_end TEXT, title TEXT,
        content TEXT, created_at TEXT, updated_at TEXT,
        FOREIGN KEY (school_id) REFERENCES schools(id))""")

    # 项目复盘表
    c.execute("""CREATE TABLE IF NOT EXISTS project_reviews (
        id INTEGER PRIMARY KEY, project_name TEXT NOT NULL, review_date TEXT,
        goal_achievement TEXT, main_issues TEXT, success_experience TEXT,
        improvement_suggestions TEXT, attachments TEXT, created_at TEXT, updated_at TEXT)""")

    # 文件表（交付材料库）
    c.execute("""CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY, file_name TEXT NOT NULL, file_path TEXT NOT NULL,
        file_size INTEGER, file_type TEXT, source_module TEXT, source_id INTEGER,
        school_id INTEGER, is_district INTEGER DEFAULT 0, stage_type TEXT,
        upload_by INTEGER, upload_time TEXT,
        FOREIGN KEY (school_id) REFERENCES schools(id),
        FOREIGN KEY (upload_by) REFERENCES users(id))""")

    # 站内消息表
    c.execute("""CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL,
        content TEXT, link_url TEXT, is_read INTEGER DEFAULT 0, read_at TEXT,
        created_at TEXT, FOREIGN KEY (user_id) REFERENCES users(id))""")

    # 邮件日志表
    c.execute("""CREATE TABLE IF NOT EXISTS email_logs (
        id INTEGER PRIMARY KEY, user_id INTEGER, recipient_email TEXT,
        subject TEXT, content TEXT, status TEXT, error_message TEXT, sent_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id))""")

    # 操作日志表
    c.execute("""CREATE TABLE IF NOT EXISTS operation_logs (
        id INTEGER PRIMARY KEY, user_id INTEGER, module TEXT, action TEXT,
        target_id INTEGER, before_data TEXT, after_data TEXT, ip_address TEXT,
        created_at TEXT, batch_file_name TEXT, batch_success_count INTEGER, batch_fail_count INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id))""")

    conn.commit()
    conn.close()

init_db()

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(p): return pwd_context.hash(p)
def verify_password(p, h): return pwd_context.verify(p, h)

def create_access_token(data):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def log_operation(user_id, module, action, target_id=None, before_data=None, after_data=None, ip_address=None, batch_file_name=None, batch_success_count=None, batch_fail_count=None):
    """记录操作日志"""
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""INSERT INTO operation_logs(user_id, module, action, target_id, before_data, after_data, ip_address, created_at, batch_file_name, batch_success_count, batch_fail_count)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id, module, action, target_id, json.dumps(before_data) if before_data else None,
         json.dumps(after_data) if after_data else None, ip_address, now, batch_file_name, batch_success_count, batch_fail_count))
    conn.commit()
    conn.close()

security = HTTPBearer()

async def get_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except:
        raise HTTPException(401, "无效的认证凭据")
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not u or u["status"] != "启用": raise HTTPException(401, "用户无效")
    return dict(u)

# 权限检查装饰器
def check_permission(*allowed_roles):
    def dependency(u: dict = Depends(get_user)):
        if u["role"] not in allowed_roles:
            raise HTTPException(403, "没有权限执行此操作")
        return u
    return dependency

app = FastAPI(title="GX项目交付管理系统 V2.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ========== Pydantic 模型 ==========
class LoginReq(BaseModel): username: str; password: str
class UserCreate(BaseModel): username: str; password: str; real_name: str; role: str = "campus_manager"; phone: str; email: Optional[str] = None
class UserUpdate(BaseModel): real_name: Optional[str] = None; role: Optional[str] = None; phone: Optional[str] = None; email: Optional[str] = None; status: Optional[str] = None

class SchoolCreate(BaseModel): code: str; full_name: str; region: Optional[str] = None; address: Optional[str] = None; campus_manager_id: Optional[int] = None; contact_person: Optional[str] = None; contact_phone: Optional[str] = None; project_status: str = "未启动"; remark: Optional[str] = None
class SchoolUpdate(BaseModel): full_name: Optional[str] = None; region: Optional[str] = None; address: Optional[str] = None; campus_manager_id: Optional[int] = None; contact_person: Optional[str] = None; contact_phone: Optional[str] = None; project_status: Optional[str] = None; remark: Optional[str] = None

class DeviceSystemCreate(BaseModel): project_name: str; construction_year: str; system_name: str; device_name: str; brand: Optional[str] = None; model: Optional[str] = None; params: Optional[str] = None; device_type: str = "硬件"; unit: str = "台"; plan_quantity: int = 0
class DeviceSystemUpdate(BaseModel): project_name: Optional[str] = None; construction_year: Optional[str] = None; system_name: Optional[str] = None; device_name: Optional[str] = None; brand: Optional[str] = None; model: Optional[str] = None; params: Optional[str] = None; device_type: Optional[str] = None; unit: Optional[str] = None; plan_quantity: Optional[int] = None; is_enabled: Optional[int] = None

class SupplierCreate(BaseModel): name: str; contact_person: Optional[str] = None; contact_phone: Optional[str] = None; contact_email: Optional[str] = None; remark: Optional[str] = None
class SupplierUpdate(BaseModel): name: Optional[str] = None; contact_person: Optional[str] = None; contact_phone: Optional[str] = None; contact_email: Optional[str] = None; remark: Optional[str] = None

class TemplateCreate(BaseModel): name: str; template_type: str; stage: Optional[str] = None; version: str = "V1.0"; description: Optional[str] = None; status: str = "启用"
class DictItemCreate(BaseModel): category: str; label: str; value: str; sort_order: int = 0; parent_value: Optional[str] = None

class ProjectInfoCreate(BaseModel): project_name: str; project_code: str; start_date: str; end_date: str; overall_status: str = "未启动"
class ProjectInfoUpdate(BaseModel): project_name: Optional[str] = None; start_date: Optional[str] = None; end_date: Optional[str] = None; overall_status: Optional[str] = None

class WbsTaskCreate(BaseModel): phase_l1: str; phase_l2: Optional[str] = None; task_package_l3: str; work_content_l4: str; work_detail_l5: Optional[str] = None; stage_type: Optional[str] = None; plan_start_date: str; plan_end_date: str; status: str = "待开始"; assignee_id: Optional[int] = None; school_id: Optional[int] = None; construction_year: Optional[str] = None; source_device_id: Optional[int] = None
class WbsTaskUpdate(BaseModel): phase_l1: Optional[str] = None; phase_l2: Optional[str] = None; task_package_l3: Optional[str] = None; work_content_l4: Optional[str] = None; work_detail_l5: Optional[str] = None; stage_type: Optional[str] = None; plan_start_date: Optional[str] = None; plan_end_date: Optional[str] = None; status: Optional[str] = None; actual_start_date: Optional[str] = None; actual_end_date: Optional[str] = None; assignee_id: Optional[int] = None; progress_note: Optional[str] = None; deliverables: Optional[str] = None; school_id: Optional[int] = None; construction_year: Optional[str] = None; material_desc: Optional[str] = None

class DeviceCreate(BaseModel): system_id: int; device_name: str; quantity: int = 1; source: str; school_id: Optional[int] = None; install_location: Optional[str] = None; status: str = "待发货"; supplier_id: Optional[int] = None; plan_arrival_date: Optional[str] = None; delivery_no: Optional[str] = None; remark: Optional[str] = None
class DeviceUpdate(BaseModel): system_id: Optional[int] = None; device_name: Optional[str] = None; quantity: Optional[int] = None; source: Optional[str] = None; school_id: Optional[int] = None; install_location: Optional[str] = None; status: Optional[str] = None; supplier_id: Optional[int] = None; plan_arrival_date: Optional[str] = None; delivery_no: Optional[str] = None; delivery_date: Optional[str] = None; arrival_date: Optional[str] = None; install_date: Optional[str] = None; debug_date: Optional[str] = None; accept_date: Optional[str] = None; remark: Optional[str] = None

class TrainingCreate(BaseModel): type: str; content: str; target_audience: Optional[str] = None; person_count: Optional[int] = None; duration_days: Optional[int] = None; location: Optional[str] = None; training_method: Optional[str] = None; exam_method: Optional[str] = None; plan_date: str; status: str = "待培训"; is_district: bool = False; school_ids: Optional[List[int]] = None
class TrainingUpdate(BaseModel): type: Optional[str] = None; content: Optional[str] = None; target_audience: Optional[str] = None; person_count: Optional[int] = None; duration_days: Optional[int] = None; location: Optional[str] = None; training_method: Optional[str] = None; exam_method: Optional[str] = None; plan_date: Optional[str] = None; actual_date: Optional[str] = None; status: Optional[str] = None

class RiskCreate(BaseModel): risk_desc: str; probability: str; impact: str; trigger_condition: Optional[str] = None; impact_description: Optional[str] = None; response_strategy: Optional[str] = None; response_deadline: Optional[str] = None; responsible_person_id: Optional[int] = None; status: str = "待处理"; school_id: Optional[int] = None; task_ids: Optional[List[int]] = None
class RiskUpdate(BaseModel): risk_desc: Optional[str] = None; probability: Optional[str] = None; impact: Optional[str] = None; trigger_condition: Optional[str] = None; impact_description: Optional[str] = None; response_strategy: Optional[str] = None; response_deadline: Optional[str] = None; responsible_person_id: Optional[int] = None; status: Optional[str] = None; school_id: Optional[int] = None

class NotificationCreate(BaseModel): user_id: int; title: str; content: Optional[str] = None; link_url: Optional[str] = None

# ========== 认证接口 ==========
@app.post("/api/login")
async def login(req: LoginReq):
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE username=?", (req.username,)).fetchone()
    conn.close()
    if not u or not verify_password(req.password, u["password_hash"]):
        raise HTTPException(401, "用户名或密码错误")
    if u["status"] != "启用": raise HTTPException(403, "账号已禁用")
    token = create_access_token({"sub": str(u["id"])})
    return {"access_token": token, "user": {"id": u["id"], "username": u["username"], "real_name": u["real_name"], "role": u["role"]}}

@app.get("/api/me")
async def me(u=Depends(get_user)):
    return {"id": u["id"], "username": u["username"], "real_name": u["real_name"], "role": u["role"], "phone": u["phone"], "email": u["email"]}

# ========== 首页统计 ==========
@app.get("/api/stats")
async def get_stats(
    construction_year: str = None,
    school_id: int = None,
    stage_type: str = None,
    u=Depends(get_user)
):
    conn = get_db()

    # 基础统计
    school_count = conn.execute("SELECT COUNT(*) FROM schools").fetchone()[0]
    device_count = conn.execute("SELECT COALESCE(SUM(quantity),0) FROM devices").fetchone()[0]

    # WBS任务统计（仅L4层级）
    task_where = "1=1"
    task_params = []
    if construction_year:
        task_where += " AND construction_year=?"
        task_params.append(construction_year)
    if school_id:
        task_where += " AND school_id=?"
        task_params.append(school_id)
    if stage_type:
        task_where += " AND stage_type=?"
        task_params.append(stage_type)

    total_tasks = conn.execute(f"SELECT COUNT(*) FROM wbs_tasks WHERE {task_where}", task_params).fetchone()[0]
    done_tasks = conn.execute(f"SELECT COUNT(*) FROM wbs_tasks WHERE {task_where} AND status='已完成'", task_params).fetchone()[0]
    progress_tasks = conn.execute(f"SELECT COUNT(*) FROM wbs_tasks WHERE {task_where} AND status='进行中'", task_params).fetchone()[0]
    delayed_tasks = conn.execute(f"SELECT COUNT(*) FROM wbs_tasks WHERE {task_where} AND status='已延期'", task_params).fetchone()[0]
    pending_tasks = conn.execute(f"SELECT COUNT(*) FROM wbs_tasks WHERE {task_where} AND status='待开始'", task_params).fetchone()[0]
    material_pending_tasks = conn.execute(f"SELECT COUNT(*) FROM wbs_tasks WHERE {task_where} AND status='待补材料'", task_params).fetchone()[0]

    # 设备状态分布
    device_where = "1=1"
    device_params = []
    if construction_year:
        device_where += " AND construction_year=?"
        device_params.append(construction_year)
    if school_id:
        device_where += " AND school_id=?"
        device_params.append(school_id)

    status_dist = {r[0]: r[1] for r in conn.execute(f"SELECT status, COALESCE(SUM(quantity),0) FROM devices WHERE {device_where} GROUP BY status", device_params).fetchall()}

    # 学校设备分布
    school_dist = {r[0]: r[1] for r in conn.execute("SELECT s.full_name, COALESCE(SUM(d.quantity),0) FROM schools s LEFT JOIN devices d ON s.id=d.school_id GROUP BY s.id", []).fetchall()}

    # 健康度评分
    high_risks = conn.execute("SELECT COUNT(*) FROM risks WHERE risk_level='高' AND status != '已关闭'").fetchone()[0]

    # 计算健康度
    health_score = 100
    health_score -= min(delayed_tasks * 5, 40)  # 延期任务扣分
    health_score -= min(material_pending_tasks * 3, 30)  # 待补材料扣分
    health_score -= min(high_risks * 10, 20)  # 高风险扣分

    health_level = "健康" if health_score >= 80 else "一般" if health_score >= 60 else "高风险"

    conn.close()

    return {
        "school_count": school_count,
        "device_count": device_count,
        "task_total": total_tasks,
        "task_done": done_tasks,
        "task_progress": progress_tasks,
        "task_delayed": delayed_tasks,
        "task_pending": pending_tasks,
        "task_material_pending": material_pending_tasks,
        "progress": round(done_tasks / total_tasks * 100, 1) if total_tasks else 0,
        "status_dist": status_dist,
        "school_dist": school_dist,
        "health_score": max(health_score, 0),
        "health_level": health_level,
        "high_risks": high_risks
    }

# ========== 用户管理 ==========
@app.get("/api/users")
async def get_users(keyword: str = None, role: str = None, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    q = "SELECT id, username, real_name, role, phone, email, status, created_at FROM users WHERE 1=1"
    p = []
    if keyword:
        q += " AND (username LIKE ? OR real_name LIKE ?)"
        p.extend([f"%{keyword}%", f"%{keyword}%"])
    if role:
        q += " AND role=?"
        p.append(role)
    users = [dict(r) for r in conn.execute(q + " ORDER BY id", p).fetchall()]
    conn.close()
    return users

@app.post("/api/users")
async def create_user(user: UserCreate, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute("""INSERT INTO users(username, password_hash, real_name, role, phone, email, status, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?)""",
            (user.username, hash_password(user.password), user.real_name, user.role, user.phone, user.email, "启用", now, now))
        conn.commit()
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        log_operation(u["id"], "用户管理", "新增", user_id, None, {"username": user.username, "role": user.role})
        return {"id": user_id, "message": "创建成功"}
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(400, "用户名或手机号已存在")

@app.put("/api/users/{id}")
async def update_user(id: int, user: UserUpdate, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    old = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()
    if not old:
        conn.close()
        raise HTTPException(404, "用户不存在")

    data = {k: v for k, v in user.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE users SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    log_operation(u["id"], "用户管理", "更新", id, dict(old) if old else None, data)
    return {"ok": True}

@app.delete("/api/users/{id}")
async def delete_user(id: int, u=Depends(check_permission("admin"))):
    conn = get_db()
    # 检查是否被引用
    ref_count = conn.execute("SELECT COUNT(*) FROM schools WHERE campus_manager_id=?", (id,)).fetchone()[0]
    if ref_count > 0:
        conn.close()
        raise HTTPException(400, "该用户已被学校引用，无法删除")

    old = conn.execute("SELECT * FROM users WHERE id=?", (id,)).fetchone()
    conn.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_operation(u["id"], "用户管理", "删除", id, dict(old) if old else None, None)
    return {"ok": True}

@app.post("/api/users/{id}/reset-password")
async def reset_password(id: int, u=Depends(check_permission("admin"))):
    new_password = "123456"  # 默认密码
    conn = get_db()
    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_password), id))
    conn.commit()
    conn.close()
    log_operation(u["id"], "用户管理", "重置密码", id)
    return {"message": "密码已重置为: 123456"}

# ========== 学校管理 ==========
@app.get("/api/schools")
async def get_schools(keyword: str = None, project_status: str = None, campus_manager_id: int = None, u=Depends(get_user)):
    conn = get_db()
    q = """SELECT s.*, u.real_name as campus_manager_name FROM schools s
           LEFT JOIN users u ON s.campus_manager_id=u.id WHERE 1=1"""
    p = []
    if keyword:
        q += " AND (s.code LIKE ? OR s.full_name LIKE ?)"
        p.extend([f"%{keyword}%", f"%{keyword}%"])
    if project_status:
        q += " AND s.project_status=?"
        p.append(project_status)
    if campus_manager_id:
        q += " AND s.campus_manager_id=?"
        p.append(campus_manager_id)

    # 校园经理只能看自己负责的学校
    if u["role"] == "campus_manager":
        q += " AND s.campus_manager_id=?"
        p.append(u["id"])

    schools = [dict(r) for r in conn.execute(q + " ORDER BY s.code", p).fetchall()]

    # 统计每个学校的设备数量和任务数量
    for s in schools:
        s["device_count"] = conn.execute("SELECT COALESCE(SUM(quantity),0) FROM devices WHERE school_id=?", (s["id"],)).fetchone()[0]
        s["task_count"] = conn.execute("SELECT COUNT(*) FROM wbs_tasks WHERE school_id=?", (s["id"],)).fetchone()[0]

    conn.close()
    return schools

@app.post("/api/schools")
async def create_school(school: SchoolCreate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute("""INSERT INTO schools(code, full_name, region, address, campus_manager_id, contact_person, contact_phone, project_status, remark, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (school.code, school.full_name, school.region, school.address, school.campus_manager_id, school.contact_person, school.contact_phone, school.project_status, school.remark, now, now))
        conn.commit()
        school_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        log_operation(u["id"], "学校管理", "新增", school_id, None, {"code": school.code, "full_name": school.full_name})
        return {"id": school_id, "message": "创建成功"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(400, "学校编码已存在")

@app.put("/api/schools/{id}")
async def update_school(id: int, school: SchoolUpdate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    old = conn.execute("SELECT * FROM schools WHERE id=?", (id,)).fetchone()
    if not old:
        conn.close()
        raise HTTPException(404, "学校不存在")

    data = {k: v for k, v in school.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE schools SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    log_operation(u["id"], "学校管理", "更新", id, dict(old) if old else None, data)
    return {"ok": True}

@app.delete("/api/schools/{id}")
async def delete_school(id: int, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    # 检查是否被引用
    ref_count = conn.execute("SELECT COUNT(*) FROM wbs_tasks WHERE school_id=?", (id,)).fetchone()[0]
    if ref_count > 0:
        conn.close()
        raise HTTPException(400, "该学校已有任务关联，无法删除")

    old = conn.execute("SELECT * FROM schools WHERE id=?", (id,)).fetchone()
    conn.execute("DELETE FROM schools WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_operation(u["id"], "学校管理", "删除", id, dict(old) if old else None, None)
    return {"ok": True}

# ========== 设备系统字典 ==========
@app.get("/api/device-systems")
async def get_device_systems(
    project_name: str = None,
    construction_year: str = None,
    system_name: str = None,
    u=Depends(get_user)
):
    conn = get_db()
    q = "SELECT * FROM device_systems WHERE is_enabled=1"
    p = []
    if project_name:
        q += " AND project_name=?"
        p.append(project_name)
    if construction_year:
        q += " AND construction_year=?"
        p.append(construction_year)
    if system_name:
        q += " AND (system_name LIKE ? OR device_name LIKE ?)"
        p.extend([f"%{system_name}%", f"%{system_name}%"])

    systems = [dict(r) for r in conn.execute(q + " ORDER BY construction_year, system_name", p).fetchall()]
    conn.close()
    return systems

@app.post("/api/device-systems")
async def create_device_system(ds: DeviceSystemCreate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute("""INSERT INTO device_systems(project_name, construction_year, system_name, device_name, brand, model, params, device_type, unit, plan_quantity, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (ds.project_name, ds.construction_year, ds.system_name, ds.device_name, ds.brand, ds.model, ds.params, ds.device_type, ds.unit, ds.plan_quantity, now, now))
        conn.commit()
        ds_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        log_operation(u["id"], "设备系统字典", "新增", ds_id, None, {"device_name": ds.device_name})
        return {"id": ds_id}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(400, "该设备字典已存在")

@app.put("/api/device-systems/{id}")
async def update_device_system(id: int, ds: DeviceSystemUpdate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    old = conn.execute("SELECT * FROM device_systems WHERE id=?", (id,)).fetchone()
    data = {k: v for k, v in ds.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE device_systems SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    log_operation(u["id"], "设备系统字典", "更新", id, dict(old) if old else None, data)
    return {"ok": True}

@app.delete("/api/device-systems/{id}")
async def delete_device_system(id: int, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    # 软删除
    conn.execute("UPDATE device_systems SET is_enabled=0 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_operation(u["id"], "设备系统字典", "删除", id)
    return {"ok": True}

# ========== 供应商管理 ==========
@app.get("/api/suppliers")
async def get_suppliers(u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    suppliers = [dict(r) for r in conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()]
    conn.close()
    return suppliers

@app.post("/api/suppliers")
async def create_supplier(s: SupplierCreate, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute("INSERT INTO suppliers(name, contact_person, contact_phone, contact_email, remark, created_at, updated_at) VALUES(?,?,?,?,?,?,?)",
            (s.name, s.contact_person, s.contact_phone, s.contact_email, s.remark, now, now))
        conn.commit()
        supplier_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        log_operation(u["id"], "供应商管理", "新增", supplier_id, None, {"name": s.name})
        return {"id": supplier_id}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(400, "供应商名称已存在")

@app.put("/api/suppliers/{id}")
async def update_supplier(id: int, s: SupplierUpdate, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    data = {k: v for k, v in s.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE suppliers SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/suppliers/{id}")
async def delete_supplier(id: int, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    conn.execute("DELETE FROM suppliers WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_operation(u["id"], "供应商管理", "删除", id)
    return {"ok": True}

# ========== 数据字典 ==========
@app.get("/api/dict-items")
async def get_dict_items(category: str = None, u=Depends(get_user)):
    conn = get_db()
    q = "SELECT * FROM dict_items WHERE is_enabled=1"
    p = []
    if category:
        q += " AND category=?"
        p.append(category)
    items = [dict(r) for r in conn.execute(q + " ORDER BY category, sort_order", p).fetchall()]
    conn.close()
    return items

@app.post("/api/dict-items")
async def create_dict_item(item: DictItemCreate, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO dict_items(category, label, value, sort_order, parent_value, created_at, updated_at) VALUES(?,?,?,?,?,?,?)",
        (item.category, item.label, item.value, item.sort_order, item.parent_value, now, now))
    conn.commit()
    conn.close()
    return {"ok": True}

# ========== 项目信息 ==========
@app.get("/api/project-info")
async def get_project_info(u=Depends(get_user)):
    conn = get_db()
    info = conn.execute("SELECT * FROM project_info ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(info) if info else None

@app.post("/api/project-info")
async def create_project_info(info: ProjectInfoCreate, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute("INSERT INTO project_info(project_name, project_code, start_date, end_date, overall_status, created_at, updated_at) VALUES(?,?,?,?,?,?,?)",
            (info.project_name, info.project_code, info.start_date, info.end_date, info.overall_status, now, now))
        conn.commit()
        conn.close()
        return {"ok": True}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(400, "项目编码已存在")

@app.put("/api/project-info/{id}")
async def update_project_info(id: int, info: ProjectInfoUpdate, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    data = {k: v for k, v in info.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE project_info SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    return {"ok": True}

# ========== WBS任务管理 ==========
@app.get("/api/wbs-tasks")
async def get_wbs_tasks(
    construction_year: str = None,
    school_id: int = None,
    stage_type: str = None,
    status: str = None,
    u=Depends(get_user)
):
    conn = get_db()
    q = """SELECT t.*, s.full_name as school_name, u.real_name as assignee_name
           FROM wbs_tasks t
           LEFT JOIN schools s ON t.school_id=s.id
           LEFT JOIN users u ON t.assignee_id=u.id
           WHERE 1=1"""
    p = []
    if construction_year:
        q += " AND t.construction_year=?"
        p.append(construction_year)
    if school_id:
        q += " AND t.school_id=?"
        p.append(school_id)
    if stage_type:
        q += " AND t.stage_type=?"
        p.append(stage_type)
    if status:
        q += " AND t.status=?"
        p.append(status)

    # 校园经理只能看自己学校的任务
    if u["role"] == "campus_manager":
        q += " AND t.school_id IN (SELECT id FROM schools WHERE campus_manager_id=?)"
        p.append(u["id"])

    tasks = [dict(r) for r in conn.execute(q + " ORDER BY t.phase_l1, t.phase_l2, t.task_package_l3, t.work_content_l4", p).fetchall()]
    conn.close()
    return tasks

@app.post("/api/wbs-tasks")
async def create_wbs_task(task: WbsTaskCreate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 获取设备字典信息
    device_info = None
    if task.source_device_id:
        device_info = conn.execute("SELECT * FROM device_systems WHERE id=?", (task.source_device_id,)).fetchone()

    conn.execute("""INSERT INTO wbs_tasks(phase_l1, phase_l2, task_package_l3, work_content_l4, work_detail_l5, stage_type, plan_start_date, plan_end_date, status, assignee_id, school_id, construction_year, source_device_id, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (task.phase_l1, task.phase_l2, task.task_package_l3, task.work_content_l4, task.work_detail_l5, task.stage_type, task.plan_start_date, task.plan_end_date, task.status, task.assignee_id, task.school_id, task.construction_year, task.source_device_id, now, now))
    conn.commit()
    task_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    log_operation(u["id"], "项目计划", "新增", task_id, None, {"task_package_l3": task.task_package_l3})
    return {"id": task_id}

@app.put("/api/wbs-tasks/{id}")
async def update_wbs_task(id: int, task: WbsTaskUpdate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    old = conn.execute("SELECT * FROM wbs_tasks WHERE id=?", (id,)).fetchone()

    data = {k: v for k, v in task.dict(exclude_unset=True).items() if v is not None}

    # 处理状态变更 - 检查是否需要设置实际时间
    if task.status == "已完成" and old and old["status"] != "已完成":
        data["actual_end_date"] = datetime.now().strftime("%Y-%m-%d")
    elif task.status == "进行中" and old and old["status"] == "待开始":
        data["actual_start_date"] = datetime.now().strftime("%Y-%m-%d")

    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE wbs_tasks SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    log_operation(u["id"], "项目计划", "更新", id, dict(old) if old else None, data)
    return {"ok": True}

@app.delete("/api/wbs-tasks/{id}")
async def delete_wbs_task(id: int, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    # 删除关联的附件
    conn.execute("DELETE FROM task_attachments WHERE task_id=?", (id,))
    conn.execute("DELETE FROM wbs_tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_operation(u["id"], "项目计划", "删除", id)
    return {"ok": True}

# 任务附件上传
@app.post("/api/wbs-tasks/{id}/attachments")
async def upload_task_attachment(id: int, file: UploadFile = File(...), u=Depends(get_user)):
    conn = get_db()
    task = conn.execute("SELECT * FROM wbs_tasks WHERE id=?", (id,)).fetchone()
    if not task:
        conn.close()
        raise HTTPException(404, "任务不存在")

    # 保存文件
    task_dir = os.path.join(UPLOAD_DIR, "tasks", str(id))
    os.makedirs(task_dir, exist_ok=True)
    file_path = os.path.join(task_dir, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(file_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("INSERT INTO task_attachments(task_id, file_name, file_path, file_size, upload_by, upload_time) VALUES(?,?,?,?,?,?)",
        (id, file.filename, file_path, file_size, u["id"], now))
    conn.commit()
    conn.close()

    return {"ok": True, "file_name": file.filename}

@app.get("/api/wbs-tasks/{id}/attachments")
async def get_task_attachments(id: int, u=Depends(get_user)):
    conn = get_db()
    attachments = [dict(r) for r in conn.execute("SELECT a.*, u.real_name as upload_by_name FROM task_attachments a LEFT JOIN users u ON a.upload_by=u.id WHERE a.task_id=?", (id,)).fetchall()]
    conn.close()
    return attachments

# ========== 设备管理 ==========
@app.get("/api/devices")
async def get_devices(
    construction_year: str = None,
    school_id: int = None,
    status: str = None,
    system_id: int = None,
    u=Depends(get_user)
):
    conn = get_db()
    q = """SELECT d.*, ds.system_name, ds.device_name as device_dict_name, ds.brand as device_brand, ds.model as device_model, ds.params as device_params, ds.device_type, ds.unit as device_unit,
           s.full_name as school_name, sup.name as supplier_name
           FROM devices d
           LEFT JOIN device_systems ds ON d.system_id=ds.id
           LEFT JOIN schools s ON d.school_id=s.id
           LEFT JOIN suppliers sup ON d.supplier_id=sup.id
           WHERE 1=1"""
    p = []
    if construction_year:
        q += " AND d.construction_year=?"
        p.append(construction_year)
    if school_id:
        q += " AND d.school_id=?"
        p.append(school_id)
    if status:
        q += " AND d.status=?"
        p.append(status)
    if system_id:
        q += " AND d.system_id=?"
        p.append(system_id)

    devices = [dict(r) for r in conn.execute(q + " ORDER BY d.id DESC", p).fetchall()]
    conn.close()
    return devices

@app.post("/api/devices")
async def create_device(device: DeviceCreate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 获取设备字典信息并复制
    ds = conn.execute("SELECT * FROM device_systems WHERE id=?", (device.system_id,)).fetchone()
    if not ds:
        conn.close()
        raise HTTPException(404, "设备字典不存在")

    conn.execute("""INSERT INTO devices(project_name, construction_year, system_id, system_name, device_name, brand, model, params, device_type, unit, source, quantity, school_id, install_location, status, supplier_id, plan_arrival_date, delivery_no, remark, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (ds["project_name"], ds["construction_year"], device.system_id, ds["system_name"], device.device_name, ds["brand"], ds["model"], ds["params"], ds["device_type"], ds["unit"], device.source, device.quantity, device.school_id, device.install_location, device.status, device.supplier_id, device.plan_arrival_date, device.delivery_no, device.remark, now, now))
    conn.commit()
    device_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    log_operation(u["id"], "设备信息", "新增", device_id, None, {"device_name": device.device_name})
    return {"id": device_id}

@app.put("/api/devices/{id}")
async def update_device(id: int, device: DeviceUpdate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    old = conn.execute("SELECT * FROM devices WHERE id=?", (id,)).fetchone()
    data = {k: v for k, v in device.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE devices SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    log_operation(u["id"], "设备信息", "更新", id, dict(old) if old else None, data)
    return {"ok": True}

@app.delete("/api/devices/{id}")
async def delete_device(id: int, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    conn.execute("DELETE FROM devices WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_operation(u["id"], "设备信息", "删除", id)
    return {"ok": True}

# ========== 培训管理 ==========
@app.get("/api/trainings")
async def get_trainings(
    type: str = None,
    status: str = None,
    is_district: bool = None,
    school_id: int = None,
    u=Depends(get_user)
):
    conn = get_db()
    q = "SELECT * FROM trainings WHERE 1=1"
    p = []
    if type:
        q += " AND type=?"
        p.append(type)
    if status:
        q += " AND status=?"
        p.append(status)
    if is_district is not None:
        q += " AND is_district=?"
        p.append(1 if is_district else 0)
    if school_id:
        q += " AND id IN (SELECT training_id FROM training_schools WHERE school_id=?)"
        p.append(school_id)

    trainings = [dict(r) for r in conn.execute(q + " ORDER BY plan_date DESC", p).fetchall()]

    # 获取关联学校
    for t in trainings:
        schools = conn.execute("SELECT s.id, s.full_name FROM training_schools ts JOIN schools s ON ts.school_id=s.id WHERE ts.training_id=?", (t["id"],)).fetchall()
        t["schools"] = [dict(s) for s in schools]

    conn.close()
    return trainings

@app.post("/api/trainings")
async def create_training(training: TrainingCreate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("""INSERT INTO trainings(type, content, target_audience, person_count, duration_days, location, training_method, exam_method, plan_date, status, is_district, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (training.type, training.content, training.target_audience, training.person_count, training.duration_days, training.location, training.training_method, training.exam_method, training.plan_date, training.status, 1 if training.is_district else 0, now, now))
    conn.commit()
    training_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # 关联学校
    if training.school_ids and not training.is_district:
        for school_id in training.school_ids:
            conn.execute("INSERT INTO training_schools(training_id, school_id) VALUES(?,?)", (training_id, school_id))
        conn.commit()

    conn.close()
    log_operation(u["id"], "培训管理", "新增", training_id, None, {"content": training.content})
    return {"id": training_id}

@app.put("/api/trainings/{id}")
async def update_training(id: int, training: TrainingUpdate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    data = {k: v for k, v in training.dict(exclude_unset=True).items() if v is not None}
    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE trainings SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/trainings/{id}")
async def delete_training(id: int, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    conn.execute("DELETE FROM training_schools WHERE training_id=?", (id,))
    conn.execute("DELETE FROM training_attachments WHERE training_id=?", (id,))
    conn.execute("DELETE FROM trainings WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_operation(u["id"], "培训管理", "删除", id)
    return {"ok": True}

# 培训附件上传
@app.post("/api/trainings/{id}/attachments")
async def upload_training_attachment(id: int, file: UploadFile = File(...), u=Depends(get_user)):
    conn = get_db()
    task_dir = os.path.join(UPLOAD_DIR, "trainings", str(id))
    os.makedirs(task_dir, exist_ok=True)
    file_path = os.path.join(task_dir, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(file_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("INSERT INTO training_attachments(training_id, file_name, file_path, file_size, upload_by, upload_time) VALUES(?,?,?,?,?,?)",
        (id, file.filename, file_path, file_size, u["id"], now))
    conn.commit()
    conn.close()
    return {"ok": True}

# ========== 风险管理 ==========
@app.get("/api/risks")
async def get_risks(
    level: str = None,
    status: str = None,
    school_id: int = None,
    u=Depends(get_user)
):
    conn = get_db()
    q = """SELECT r.*, s.full_name as school_name, u.real_name as responsible_name
           FROM risks r
           LEFT JOIN schools s ON r.school_id=s.id
           LEFT JOIN users u ON r.responsible_person_id=u.id
           WHERE 1=1"""
    p = []
    if level:
        q += " AND r.risk_level=?"
        p.append(level)
    if status:
        q += " AND r.status=?"
        p.append(status)
    if school_id:
        q += " AND r.school_id=?"
        p.append(school_id)

    risks = [dict(r) for r in conn.execute(q + " ORDER BY r.risk_level DESC, r.id DESC", p).fetchall()]

    # 获取关联任务
    for r in risks:
        tasks = conn.execute("SELECT t.id, t.work_content_l4 FROM risk_tasks rt JOIN wbs_tasks t ON rt.task_id=t.id WHERE rt.risk_id=?", (r["id"],)).fetchall()
        r["related_tasks"] = [dict(t) for t in tasks]

    conn.close()
    return risks

@app.post("/api/risks")
async def create_risk(risk: RiskCreate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 计算风险等级
    prob_map = {"高": 3, "中": 2, "低": 1}
    impact_map = {"高": 3, "中": 2, "低": 1}
    score = prob_map.get(risk.probability, 1) * impact_map.get(risk.impact, 1)
    risk_level = "高" if score >= 6 else "中" if score >= 4 else "低"

    conn.execute("""INSERT INTO risks(risk_desc, probability, impact, risk_level, trigger_condition, impact_description, response_strategy, response_deadline, responsible_person_id, status, school_id, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (risk.risk_desc, risk.probability, risk.impact, risk_level, risk.trigger_condition, risk.impact_description, risk.response_strategy, risk.response_deadline, risk.responsible_person_id, risk.status, risk.school_id, now, now))
    conn.commit()
    risk_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # 关联任务
    if risk.task_ids:
        for task_id in risk.task_ids:
            conn.execute("INSERT INTO risk_tasks(risk_id, task_id) VALUES(?,?)", (risk_id, task_id))
        conn.commit()

    conn.close()
    log_operation(u["id"], "风险管理", "新增", risk_id, None, {"risk_desc": risk.risk_desc})
    return {"id": risk_id}

@app.put("/api/risks/{id}")
async def update_risk(id: int, risk: RiskUpdate, u=Depends(check_permission("admin", "project_manager", "campus_manager"))):
    conn = get_db()
    data = {k: v for k, v in risk.dict(exclude_unset=True).items() if v is not None}

    # 重新计算风险等级
    if risk.probability or risk.impact:
        old = conn.execute("SELECT * FROM risks WHERE id=?", (id,)).fetchone()
        prob = risk.probability or old["probability"]
        imp = risk.impact or old["impact"]
        prob_map = {"高": 3, "中": 2, "低": 1}
        score = prob_map.get(prob, 1) * prob_map.get(imp, 1)
        data["risk_level"] = "高" if score >= 6 else "中" if score >= 4 else "低"

    if data:
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(f"UPDATE risks SET {','.join(f'{k}=?' for k in data)} WHERE id=?", list(data.values()) + [id])
        conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/risks/{id}")
async def delete_risk(id: int, u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    conn.execute("DELETE FROM risk_tasks WHERE risk_id=?", (id,))
    conn.execute("DELETE FROM risks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_operation(u["id"], "风险管理", "删除", id)
    return {"ok": True}

# ========== 交付进展 ==========
@app.get("/api/delivery-progress")
async def get_delivery_progress(
    construction_year: str = None,
    school_id: int = None,
    u=Depends(get_user)
):
    conn = get_db()

    # 获取所有学校
    schools_query = "SELECT * FROM schools"
    schools_params = []
    if school_id:
        schools_query += " WHERE id=?"
        schools_params.append(school_id)
    schools = [dict(s) for s in conn.execute(schools_query, schools_params).fetchall()]

    # 阶段类型
    stages = ["到货验收", "加电测试", "校级验收", "培训"]

    result = []
    for school in schools:
        school_data = {
            "school_id": school["id"],
            "school_name": school["full_name"],
            "stages": {}
        }

        for stage in stages:
            # 统计该学校该阶段的任务
            tasks = conn.execute("""SELECT status, COUNT(*) as count FROM wbs_tasks
                WHERE school_id=? AND stage_type=? GROUP BY status""",
                (school["id"], stage)).fetchall()

            total = sum(t["count"] for t in tasks)
            done = sum(t["count"] for t in tasks if t["status"] == "已完成")

            # 检查材料完整性
            materials = conn.execute("SELECT COUNT(*) FROM task_attachments WHERE task_id IN (SELECT id FROM wbs_tasks WHERE school_id=? AND stage_type=?)",
                (school["id"], stage)).fetchone()[0]

            material_status = "齐全" if materials >= total and total > 0 else "缺失" if total > 0 else "无"

            school_data["stages"][stage] = {
                "total": total,
                "done": done,
                "progress": round(done / total * 100, 1) if total > 0 else 0,
                "material_status": material_status
            }

        result.append(school_data)

    conn.close()
    return result

# ========== 操作日志 ==========
@app.get("/api/operation-logs")
async def get_operation_logs(
    module: str = None,
    user_id: int = None,
    start_date: str = None,
    end_date: str = None,
    u=Depends(check_permission("admin"))
):
    conn = get_db()
    q = """SELECT l.*, u.username, u.real_name FROM operation_logs l
           LEFT JOIN users u ON l.user_id=u.id WHERE 1=1"""
    p = []
    if module:
        q += " AND l.module=?"
        p.append(module)
    if user_id:
        q += " AND l.user_id=?"
        p.append(user_id)
    if start_date:
        q += " AND l.created_at >= ?"
        p.append(start_date)
    if end_date:
        q += " AND l.created_at <= ?"
        p.append(end_date)

    logs = [dict(r) for r in conn.execute(q + " ORDER BY l.created_at DESC LIMIT 500", p).fetchall()]
    conn.close()
    return logs

# ========== 交付材料库 ==========
@app.get("/api/files")
async def get_files(
    school_id: int = None,
    stage_type: str = None,
    source_module: str = None,
    is_district: bool = None,
    u=Depends(get_user)
):
    conn = get_db()
    q = """SELECT f.*, s.full_name as school_name, u.real_name as upload_by_name
           FROM files f
           LEFT JOIN schools s ON f.school_id=s.id
           LEFT JOIN users u ON f.upload_by=u.id
           WHERE 1=1"""
    p = []
    if school_id:
        q += " AND f.school_id=?"
        p.append(school_id)
    if stage_type:
        q += " AND f.stage_type=?"
        p.append(stage_type)
    if source_module:
        q += " AND f.source_module=?"
        p.append(source_module)
    if is_district is not None:
        q += " AND f.is_district=?"
        p.append(1 if is_district else 0)

    files = [dict(r) for r in conn.execute(q + " ORDER BY f.upload_time DESC", p).fetchall()]
    conn.close()
    return files

@app.post("/api/files")
async def upload_file(
    file: UploadFile = File(...),
    school_id: int = None,
    stage_type: str = None,
    source_module: str = None,
    source_id: int = None,
    is_district: bool = False,
    u=Depends(get_user)
):
    file_dir = os.path.join(UPLOAD_DIR, "files")
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(file_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    conn.execute("""INSERT INTO files(file_name, file_path, file_size, file_type, source_module, source_id, school_id, is_district, stage_type, upload_by, upload_time)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (file.filename, file_path, file_size, file.content_type, source_module, source_id, school_id, 1 if is_district else 0, stage_type, u["id"], now))
    conn.commit()
    conn.close()
    return {"ok": True}

# ========== 站内消息 ==========
@app.get("/api/notifications")
async def get_notifications(u=Depends(get_user)):
    conn = get_db()
    notifications = [dict(r) for r in conn.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 50", (u["id"],)).fetchall()]
    conn.close()
    return notifications

@app.post("/api/notifications/{id}/read")
async def mark_notification_read(id: int, u=Depends(get_user)):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE notifications SET is_read=1, read_at=? WHERE id=? AND user_id=?", (now, id, u["id"]))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.post("/api/notifications/read-all")
async def mark_all_read(u=Depends(get_user)):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE notifications SET is_read=1, read_at=? WHERE user_id=?", (now, u["id"]))
    conn.commit()
    conn.close()
    return {"ok": True}

# 创建通知
def create_notification(user_id, title, content, link_url=None):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO notifications(user_id, title, content, link_url, created_at) VALUES(?,?,?,?,?)",
        (user_id, title, content, link_url, now))
    conn.commit()
    conn.close()

# ========== 报告管理 ==========
@app.get("/api/reports")
async def get_reports(
    report_type: str = None,
    report_scope: str = None,
    school_id: int = None,
    u=Depends(get_user)
):
    conn = get_db()
    q = "SELECT * FROM reports WHERE 1=1"
    p = []
    if report_type:
        q += " AND report_type=?"
        p.append(report_type)
    if report_scope:
        q += " AND report_scope=?"
        p.append(report_scope)
    if school_id:
        q += " AND school_id=?"
        p.append(school_id)

    reports = [dict(r) for r in conn.execute(q + " ORDER BY created_at DESC", p).fetchall()]
    conn.close()
    return reports

# ========== 项目复盘 ==========
@app.get("/api/project-reviews")
async def get_project_reviews(u=Depends(check_permission("admin", "project_manager"))):
    conn = get_db()
    reviews = [dict(r) for r in conn.execute("SELECT * FROM project_reviews ORDER BY review_date DESC").fetchall()]
    conn.close()
    return reviews

@app.post("/api/project-reviews")
async def create_project_review(
    goal_achievement: str,
    main_issues: str,
    success_experience: str = None,
    improvement_suggestions: str = None,
    u=Depends(check_permission("admin", "project_manager"))
):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d")

    # 获取项目名称
    project = conn.execute("SELECT project_name FROM project_info ORDER BY id DESC LIMIT 1").fetchone()
    project_name = project["project_name"] if project else "GX项目"

    conn.execute("""INSERT INTO project_reviews(project_name, review_date, goal_achievement, main_issues, success_experience, improvement_suggestions, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?)""",
        (project_name, now, goal_achievement, main_issues, success_experience, improvement_suggestions, now, now))
    conn.commit()
    conn.close()
    return {"ok": True}

# ========== 模板管理 ==========
@app.get("/api/templates")
async def get_templates(template_type: str = None, stage: str = None, u=Depends(get_user)):
    conn = get_db()
    q = "SELECT * FROM templates WHERE status='启用'"
    p = []
    if template_type:
        q += " AND template_type=?"
        p.append(template_type)
    if stage:
        q += " AND stage=?"
        p.append(stage)
    templates = [dict(r) for r in conn.execute(q + " ORDER BY id DESC", p).fetchall()]
    conn.close()
    return templates

@app.post("/api/templates")
async def create_template(
    name: str,
    template_type: str,
    stage: str = None,
    version: str = "V1.0",
    description: str = None,
    file: UploadFile = File(...),
    u=Depends(check_permission("admin", "project_manager", "campus_manager"))
):
    template_dir = os.path.join(UPLOAD_DIR, "templates")
    os.makedirs(template_dir, exist_ok=True)
    file_path = os.path.join(template_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 同一类型+阶段的其他模板停用
    conn.execute("UPDATE templates SET status='停用' WHERE template_type=? AND stage=?", (template_type, stage))

    conn.execute("""INSERT INTO templates(name, template_type, stage, file_path, version, description, status, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (name, template_type, stage, file_path, version, description, "启用", now, now))
    conn.commit()
    conn.close()
    return {"ok": True}

# ========== 全局筛选数据 ==========
@app.get("/api/global-filters")
async def get_global_filters(u=Depends(get_user)):
    conn = get_db()

    # 建设年份
    years = [r[0] for r in conn.execute("SELECT DISTINCT construction_year FROM device_systems WHERE is_enabled=1 ORDER BY construction_year DESC").fetchall()]
    if not years:
        years = ["2026", "2027", "2028"]

    # 学校列表
    schools = [dict(r) for r in conn.execute("SELECT id, full_name FROM schools ORDER BY code").fetchall()]

    # 阶段类型（从数据字典）
    stages = [dict(r) for r in conn.execute("SELECT value, label FROM dict_items WHERE category='关联阶段' AND is_enabled=1 ORDER BY sort_order").fetchall()]
    if not stages:
        stages = [{"value": "到货验收", "label": "到货验收"}, {"value": "加电测试", "label": "加电测试"}, {"value": "校级验收", "label": "校级验收"}, {"value": "培训", "label": "培训"}]

    conn.close()
    return {
        "construction_years": years,
        "schools": schools,
        "stages": stages
    }

# ========== 文件下载 ==========
@app.get("/api/download/{file_id}")
async def download_file(file_id: int, u=Depends(get_user)):
    conn = get_db()
    file_info = conn.execute("SELECT * FROM files WHERE id=?", (file_id,)).fetchone()
    if not file_info:
        conn.close()
        raise HTTPException(404, "文件不存在")
    conn.close()
    return FileResponse(file_info["file_path"], filename=file_info["file_name"])

# 挂载静态文件
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# 前端静态文件服务
@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/login")
async def login_page():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(frontend_path, "login.html"))

# 挂载静态文件（不含html自动路由）
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
