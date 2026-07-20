"""用户管理接口（仅管理员、项目经理可访问）"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, SetPasswordRequest
from app.core.security import get_password_hash, require_roles

router = APIRouter()

# 用户管理权限：管理员、项目经理
require_admin_or_pm = require_roles('admin', 'project_manager')


@router.get('')
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    role: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias='status'),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_pm),
):
    """获取用户列表（分页+筛选），返回 {total, items}"""
    query = db.query(User)
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) | (User.real_name.contains(keyword))
        )
    if role:
        query = query.filter(User.role == role)
    if status_filter:
        query = query.filter(User.status == status_filter)
    total = query.count()
    users = query.order_by(User.id).offset((page - 1) * page_size).limit(page_size).all()
    return {
        'total': total,
        'items': [UserResponse.model_validate(u) for u in users],
    }


@router.post('', response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_pm),
):
    """新增用户"""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='用户名已存在')
    if db.query(User).filter(User.phone == user_data.phone).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='手机号已存在')
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        role=user_data.role,
        phone=user_data.phone,
        email=user_data.email,
        status='启用',
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/{user_id}', response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_pm),
):
    """获取单个用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户不存在')
    return user


@router.put('/{user_id}', response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_pm),
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户不存在')
    update_data = user_data.model_dump(exclude_unset=True)
    # 手机号唯一性校验
    if 'phone' in update_data and update_data['phone'] != user.phone:
        if db.query(User).filter(User.phone == update_data['phone']).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='手机号已存在')
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete('/{user_id}')
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_pm),
):
    """停用用户（软删除）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户不存在')
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='不能停用自己')
    user.status = '停用'
    db.commit()
    return {'message': '用户已停用'}


@router.post('/{user_id}/reset-password')
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_pm),
):
    """重置密码为默认值 Admin@2026"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户不存在')
    user.password_hash = get_password_hash('Admin@2026')
    db.commit()
    return {'message': '密码已重置为 Admin@2026'}


@router.post('/{user_id}/set-password')
def set_password(
    user_id: int,
    payload: SetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_pm),
):
    """管理员为指定用户设置新密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户不存在')
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='新密码长度不能少于6位')
    user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {'message': '密码修改成功'}
