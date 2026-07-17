"""
数据库初始化脚本 - MySQL版
创建表结构 + 插入种子数据
"""
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_database():
    print("开始初始化数据库...")

    # 创建所有表
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    print("[OK] 表结构创建完成")

    # 插入种子数据
    db = SessionLocal()
    try:
        # 检查是否已有数据
        existing_user = db.query(User).first()
        if existing_user:
            print("[WARN] 数据库已有数据，跳过种子数据初始化")
            return

        # 创建管理员账号
        admin_user = User(
            username="admin",
            password_hash=pwd_context.hash("123456"),
            real_name="系统管理员",
            role="admin",
            phone="13800000001",
            email="admin@gx.com",
            status="启用"
        )
        db.add(admin_user)

        # 创建测试项目经理
        pm_user = User(
            username="pm001",
            password_hash=pwd_context.hash("123456"),
            real_name="张项目经理",
            role="project_manager",
            phone="13800000002",
            email="pm@gx.com",
            status="启用"
        )
        db.add(pm_user)

        db.commit()
        print("[OK] 种子数据创建完成")
        print("\n默认账号：")
        print("  管理员: admin / 123456")
        print("  项目经理: pm001 / 123456")

    except Exception as e:
        print(f"[ERROR] 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
