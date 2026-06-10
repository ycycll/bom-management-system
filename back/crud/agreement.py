from fastapi import APIRouter
from sqlalchemy import text

from db.config import Session
from model import AGREEMENT_MODEL, AGREEMENT_UPDATE_MODEL

agreement = APIRouter(prefix="/agreement", tags=["协议管理"])


@agreement.get("/list", tags=["获取协议列表"])
async def get_agreement_list(keyword: str = "", page_num: int = 1, page_size: int = 2):
    """获取协议列表，支持按协议号或协议名称搜索"""
    with Session() as session:
        sql = "SELECT * FROM agreement WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM agreement WHERE 1=1"
        params = {}

        if keyword:
            sql += " AND (agreement_id LIKE :keyword OR name LIKE :keyword)"
            count_sql += " AND (agreement_id LIKE :keyword OR name LIKE :keyword)"
            params["keyword"] = f"%{keyword}%"

        sql += " ORDER BY id DESC"

        offset = (page_num - 1) * page_size
        sql += " LIMIT :page_size OFFSET :offset"
        params["page_size"] = page_size
        params["offset"] = offset

        resp = session.execute(text(sql), params)
        json_resp = [dict(zip(resp.keys(), row)) for row in resp]

        total = session.execute(text(count_sql), params).fetchone()[0]
        return {"code": 200, "data": json_resp, "total": total}


@agreement.post("/add", tags=["添加协议文件"])
async def add_agreement(agreement_model: AGREEMENT_MODEL):
    """添加协议"""
    if (not agreement_model.agreement_id
            or not agreement_model.name
            or not agreement_model.tp
    ):
        return {"code": 400, "msg": "参数错误"}
    with Session() as session:
        user_dict = agreement_model.model_dump(exclude={'id'})
        sql = text("""
                        INSERT INTO agreement (agreement_id, name,tp) 
                        VALUES (:agreement_id, :name, :tp)
                    """)
        session.execute(sql, user_dict)
        session.commit()
        return {"code": 200, "data": user_dict}


@agreement.put("/update", tags=["修改协议"])
async def update_agreement(agreement_model: AGREEMENT_UPDATE_MODEL):
    """修改协议"""
    if not agreement_model.id:
        return {"code": 400, "msg": "ID不能为空"}

    with Session() as session:
        agreement_dict = agreement_model.model_dump(exclude={'id'}, exclude_none=True)

        if not agreement_dict:
            return {"code": 400, "msg": "至少需要一个要修改的字段"}
        set_parts = []
        for key in agreement_dict.keys():
            set_parts.append(f"{key} = :{key}")

        sql = text("UPDATE agreement SET " + ", ".join(set_parts) + " WHERE id = :id")
        agreement_dict["id"] = agreement_model.id

        session.execute(sql, agreement_dict)
        session.commit()
        return {"code": 200, "data": agreement_dict}


@agreement.delete("/delete/{_id}", tags=["删除协议"])
async def delete_agreement(_id: int):
    """删除协议"""
    if not _id:
        return {"code": 400, "msg": "协议 ID 不能为空"}
    with Session() as session:
        sql = text("DELETE FROM agreement WHERE id = :id")
        session.execute(sql, {"id": _id})
        session.commit()
        return {"code": 200, "msg": "删除成功"}
