from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GX教育项目交付管理系统", version="2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "GX教育项目交付管理系统 API", "version": "2.1"}

@app.get("/health")
def health():
    return {"status": "ok"}
from app.api.v1 import auth, users, dashboard
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["首页仪表盘"])
