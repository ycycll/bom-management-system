from fastapi import APIRouter
from fastapi.responses import FileResponse
from sqlalchemy import text
import os

from db.config import Session

draw = APIRouter(prefix="/draw", tags=["图纸管理"])


@draw.get("/list")
async def get_draw_list(draw_name: str = '', remark: str = '',
                        page_num: int = 1, page_size: int = 20):
    """模糊搜索图纸列表"""
    with Session() as session:
        sql = "SELECT * FROM draw WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM draw WHERE 1=1"
        params = {}

        if draw_name:
            sql += " AND draw_name LIKE :draw_name"
            count_sql += " AND draw_name LIKE :draw_name"
            params["draw_name"] = f"%{draw_name}%"

        if remark:
            sql += " AND remark LIKE :remark"
            count_sql += " AND remark LIKE :remark"
            params["remark"] = f"%{remark}%"

        sql += " ORDER BY id DESC"
        offset = (page_num - 1) * page_size
        sql += " LIMIT :page_size OFFSET :offset"
        params["page_size"] = page_size
        params["offset"] = offset

        resp = session.execute(text(sql), params)
        json_resp = [dict(zip(resp.keys(), row)) for row in resp]
        total = session.execute(text(count_sql), params).fetchone()[0]
        return {"code": 200, "data": json_resp, "total": total}


@draw.get("/file/{draw_id}")
async def get_draw_file(draw_id: int):
    """根据ID返回图纸文件流（供前端 iframe 展示）"""
    with Session() as session:
        resp = session.execute(
            text("SELECT address FROM draw WHERE id = :id"),
            {"id": draw_id}
        ).fetchone()

        if not resp:
            return {"code": 404, "msg": "图纸不存在"}

        file_path = resp[0]

        if not os.path.exists(file_path):
            return {"code": 404, "msg": f"文件不存在: {file_path}"}

        return FileResponse(
            path=file_path,
            media_type="application/pdf",   # 如果有 DWG/其他格式需调整
            headers={"Content-Disposition": "inline"}  # inline 让浏览器直接显示
        )