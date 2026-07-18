"""认证接口：登录、获取当前用户、登出、修改密码"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, Token, ChangePasswordRequest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)

router = APIRouter()


def authenticate_user(db: Session, username: str, password: str):
    """验证用户名密码，成功返回User，失败返回None"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """登录，返回JWT"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='用户名或密码错误',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if user.status != '启用':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='账号已停用')
    access_token = create_access_token(data={'sub': str(user.id)})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/me', response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user


@router.post('/logout')
def logout(current_user: User = Depends(get_current_user)):
    """登出（无状态，前端清除token即可）"""
    return {'message': '登出成功'}


@router.put('/change-password')
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改当前用户密码"""
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='原密码错误')
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='新密码长度不能少于6位')
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {'message': '密码修改成功'}
