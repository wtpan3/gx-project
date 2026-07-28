# -*- coding: utf-8 -*-
"""核对 SQLAlchemy 模型字段与数据库实际列是否一致"""
import os
import sys

import pymysql
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.wbs_task import WbsTask
from app.models.device import Device
from app.models.todo import Todo
from app.models.software_module import SoftwareModule
from app.models.production_line import ProductionLine
from app.models.school import School
from app.models.risk import Risk

MODELS = [WbsTask, Device, Todo, SoftwareModule, ProductionLine, School, Risk]

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
)

all_ok = True
with conn.cursor() as cur:
    for m in MODELS:
        table = m.__tablename__
        model_cols = {c.name for c in m.__table__.columns}

        cur.execute(f'SHOW COLUMNS FROM `{table}`')
        db_cols = {r[0] for r in cur.fetchall()}

        only_model = model_cols - db_cols
        only_db = db_cols - model_cols

        if not only_model and not only_db:
            print(f'[OK]   {table:<20} {len(model_cols)} cols matched')
        else:
            all_ok = False
            print(f'[DIFF] {table}')
            if only_model:
                print(f'         model has, db missing: {sorted(only_model)}')
            if only_db:
                print(f'         db has, model missing: {sorted(only_db)}')

conn.close()
print('\n' + ('ALL MATCHED' if all_ok else 'MISMATCH FOUND'))
sys.exit(0 if all_ok else 1)
