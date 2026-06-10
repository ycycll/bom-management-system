from fastapi import APIRouter
from sqlalchemy import text

from db.config import Session
from model import WEModel, WEUpdateModel

we = APIRouter(prefix="/we", tags=["样本管理"])


@we.get("/search_filter", tags=["筛选查询"])
async def search_filter(we_type: str = '', we_volt: str = '', we_freq: str = '', we_material: str = '',
                        page_num: int = 1,
                        page_size: int = 12):
    """筛选查询样本"""
    with Session() as session:
        sql = "SELECT * FROM we WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM we WHERE 1=1"
        params = {}

        if we_type:
            sql += " AND we_type LIKE :we_type"
            count_sql += " AND we_type LIKE :we_type"
            params["we_type"] = f"%{we_type}%"

        if we_volt:
            sql += " AND we_volt = :we_volt"
            count_sql += " AND we_volt = :we_volt"
            params["we_volt"] = we_volt

        if we_freq:
            sql += " AND we_freq = :we_freq"
            count_sql += " AND we_freq = :we_freq"
            params["we_freq"] = we_freq

        if we_material:
            sql += " AND we_material = :we_material"
            count_sql += " AND we_material = :we_material"
            params["we_material"] = we_material

        sql += " ORDER BY id DESC"

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


@we.post("/add", tags=["添加样本"])
async def add_user(we_model: WEModel):
    """添加用户"""
    if (not we_model.we_type or not we_model.we_power or not we_model.we_speed or not we_model.we_eff or not we_model.we_factor or not we_model.we_tor_mul
            or not we_model.we_cur_mul or not we_model.we_max_tor_mul or not we_model.we_weight or not we_model.we_noise_p or not we_model.we_noise_w
            or not we_model.we_inertia or not we_model.we_torque or not we_model.we_freq or not we_model.we_volt or not we_model.we_cur or not we_model.we_material):
        return {"code": 400, "msg": "参数错误"}
    with Session() as session:
        user_dict = we_model.model_dump(exclude={'id'})
        sql = text("""
                        INSERT INTO we (we_type,we_power,we_speed,we_eff,we_factor,we_tor_mul,we_cur_mul,we_max_tor_mul,
                        we_weight,we_noise_p,we_noise_w,we_inertia,we_torque,we_freq,we_volt,we_cur,we_material) 
                        VALUES (:we_type,:we_power, :we_speed, :we_eff, :we_factor, :we_tor_mul, :we_cur_mul, :we_max_tor_mul,
                        :we_weight, :we_noise_p, :we_noise_w, :we_inertia, :we_torque, :we_freq, :we_volt, :we_cur, :we_material)
                    """)
        session.execute(sql, user_dict)
        session.commit()
        return {"code": 200, "data": user_dict}


@we.put("/update", tags=["修改样本"])
async def update_user(we_model: WEUpdateModel):
    """修改用户"""
    if not we_model.id:
        return {"code": 400, "msg": "ID不能为空"}

    with Session() as session:
        user_dict = we_model.model_dump(exclude={'id'}, exclude_none=True)

        if not user_dict:
            return {"code": 400, "msg": "至少需要一个要修改的字段"}
        set_parts = []
        for key in user_dict.keys():
            set_parts.append(f"{key} = :{key}")

        sql = text("UPDATE we SET " + ", ".join(set_parts) + " WHERE id = :id")
        user_dict["id"] = we_model.id

        session.execute(sql, user_dict)
        session.commit()
        return {"code": 200, "data": user_dict}


@we.delete("/delete/{sample_id}", tags=["删除用户"])
async def delete_user(sample_id: int):
    """删除样本"""
    if not sample_id:
        return {"code": 400, "msg": "样本 ID 不能为空"}
    with Session() as session:
        sql = text("DELETE FROM we WHERE id = :id")
        session.execute(sql, {"id": sample_id})
        session.commit()
        return {"code": 200, "msg": "删除成功"}
