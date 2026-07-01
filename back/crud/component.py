from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy import text

from db.config import Session

component = APIRouter(prefix="/component", tags=["部件推荐"])


from model import ComponentModel, UpdateComponentModel



@component.get("/list")
async def get_component_list(
    const: str = '',
    technical_preparation: str = '',
    component_id: str = '',
    component_desc: str = '',
    page_num: int = 1, page_size: int = 10
):
    """获取部件推荐列表，支持分页和搜索"""
    with Session() as session:
        sql = "SELECT * FROM component_hub WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM component_hub WHERE 1=1"
        params = {}

        if const:
            sql += " AND const LIKE :const"
            count_sql += " AND const LIKE :const"
            params["const"] = f"%{const}%"

        if technical_preparation:
            sql += " AND technical_preparation LIKE :technical_preparation"
            count_sql += " AND technical_preparation LIKE :technical_preparation"
            params["technical_preparation"] = f"%{technical_preparation}%"

        if component_id:
            sql += " AND component_id LIKE :component_id"
            count_sql += " AND component_id LIKE :component_id"
            params["component_id"] = f"%{component_id}%"

        if component_desc:
            sql += " AND component_desc LIKE :component_desc"
            count_sql += " AND component_desc LIKE :component_desc"
            params["component_desc"] = f"%{component_desc}%"

        offset = (page_num - 1) * page_size
        sql += " LIMIT :page_size OFFSET :offset"
        params["page_size"] = page_size
        params["offset"] = offset

        resp = session.execute(text(sql), params)
        json_resp = [dict(zip(resp.keys(), row)) for row in resp]

        total = session.execute(text(count_sql), params).fetchone()[0]
        return {"json_resp": json_resp, "total": total}


@component.post("/add")
async def add_component(data: ComponentModel = Body(...)):
    """新增部件推荐"""
    if not data.const or not data.technical_preparation or not data.component_id or not data.component_desc:
        raise HTTPException(status_code=400, detail="所有字段均为必填")

    with Session() as session:
        # 检查是否已存在
        check_sql = text("""
            SELECT COUNT(*) FROM component_hub 
            WHERE const = :const AND technical_preparation = :technical_preparation AND component_id = :component_id
        """)
        count = session.execute(check_sql, {
            "const": data.const,
            "technical_preparation": data.technical_preparation,
            "component_id": data.component_id
        }).fetchone()[0]

        if count > 0:
            raise HTTPException(status_code=400, detail="该部件已存在")

        sql = text("""
            INSERT INTO component_hub (const, technical_preparation, component_id, component_desc)
            VALUES (:const, :technical_preparation, :component_id, :component_desc)
        """)
        session.execute(sql, {
            "const": data.const,
            "technical_preparation": data.technical_preparation,
            "component_id": data.component_id,
            "component_desc": data.component_desc
        })
        session.commit()
        return {"code": 200, "message": "新增成功"}


@component.put("/update")
async def update_component(data: UpdateComponentModel = Body(...)):
    """更新部件推荐"""
    if not data.const or not data.technical_preparation or not data.component_id or not data.component_desc:
        raise HTTPException(status_code=400, detail="所有字段均为必填")

    with Session() as session:
        # 使用原始值定位记录
        where_const = data.old_const or data.const
        where_tp = data.old_technical_preparation or data.technical_preparation
        where_cid = data.old_component_id or data.component_id

        sql = text("""
            UPDATE component_hub 
            SET const = :const, technical_preparation = :technical_preparation, 
                component_id = :component_id, component_desc = :component_desc
            WHERE const = :where_const AND technical_preparation = :where_tp AND component_id = :where_cid
        """)
        result = session.execute(sql, {
            "const": data.const,
            "technical_preparation": data.technical_preparation,
            "component_id": data.component_id,
            "component_desc": data.component_desc,
            "where_const": where_const,
            "where_tp": where_tp,
            "where_cid": where_cid
        })
        session.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="记录不存在")

        return {"code": 200, "message": "更新成功"}


@component.delete("/delete")
async def delete_component(data: ComponentModel = Body(...)):
    """删除部件推荐"""
    with Session() as session:
        sql = text("""
            DELETE FROM component_hub 
            WHERE const = :const AND technical_preparation = :technical_preparation AND component_id = :component_id
        """)
        result = session.execute(sql, {
            "const": data.const,
            "technical_preparation": data.technical_preparation,
            "component_id": data.component_id
        })
        session.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="记录不存在")

        return {"code": 200, "message": "删除成功"}