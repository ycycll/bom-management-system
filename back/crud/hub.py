from fastapi import APIRouter
from sqlalchemy import text

from db.config import Session

hub = APIRouter(prefix="/hub", tags=["仓库管理"])


@hub.get("/list")
async def get_hub_list(recommendTP: str = '',
                       recommendNo: str = '',
                       recommendDesc: str = '',
                       const: str = '',
                       page_num: int = 1, page_size: int = 6):
    """获取hub列表，支持分页和搜索"""

    with Session() as session:
        sql = "SELECT * FROM hub WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM hub WHERE 1=1"
        params = {}

        if recommendTP:
            sql += " AND recommendTP LIKE :recommendTP"
            count_sql += " AND recommendTP LIKE :recommendTP"
            params["recommendTP"] = f"%{recommendTP}%"

        if recommendNo:
            sql += " AND recommendNo LIKE :recommendNo"
            count_sql += " AND recommendNo LIKE :recommendNo"
            params["recommendNo"] = f"%{recommendNo}%"

        if recommendDesc:
            sql += " AND recommendDesc LIKE :recommendDesc"
            count_sql += " AND recommendDesc LIKE :recommendDesc"
            params["recommendDesc"] = f"%{recommendDesc}%"

        if const:
            sql += " AND const LIKE :const"
            count_sql += " AND const LIKE :const"
            params["const"] = f"%{const}%"

        # 计算分页参数
        offset = (page_num - 1) * page_size
        sql += " LIMIT :page_size OFFSET :offset"
        params["page_size"] = page_size
        params["offset"] = offset

        # 执行查询
        resp = session.execute(text(sql), params)
        json_resp = [dict(zip(resp.keys(), row)) for row in resp]

        # 查询总数
        total = session.execute(text(count_sql), params).fetchone()[0]
        return {"json_resp": json_resp, "total": total}


@hub.delete("/delete/{recommendTP}")
async def delete_hub_id(recommendTP: str):
    """删除推荐仓库行"""
    if not recommendTP:
        return {"code": 400, "msg": "样本 ID 不能为空"}
    with Session() as session:
        sql = text("DELETE FROM hub WHERE recommendTP = :recommendTP")
        session.execute(sql, {"recommendTP": recommendTP})
        session.commit()
        return {"code": 200, "msg": "删除成功"}
