from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from db.config import Session
import json

archive_query = APIRouter(prefix="/archive_query", tags=["归档查询"])


def _build_where(flow_no: str, keyword: str, start_date: str, end_date: str):
    """SQL 侧过滤：流程号 / 关键字 / 时间范围（工作令号在 JSON 明细里，只能 Python 过滤）"""
    conditions, params = [], {}
    if flow_no:
        conditions.append("flow_no = :flow_no")
        params['flow_no'] = flow_no
    if keyword:
        conditions.append("(flow_no LIKE :keyword OR remark LIKE :keyword)")
        params['keyword'] = f'%{keyword}%'
    if start_date:
        conditions.append("created_at >= :start_date")
        params['start_date'] = f'{start_date} 00:00:00'
    if end_date:
        conditions.append("created_at <= :end_date")
        params['end_date'] = f'{end_date} 23:59:59'
    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where_clause, params


def _query_rows(session, flow_no, work_no, keyword, start_date, end_date):
    """按 SQL 条件查全量 → 解析 JSON → 按工作令号过滤，返回带明细的记录列表"""
    where_clause, params = _build_where(flow_no, keyword, start_date, end_date)
    query = text(f"""
        SELECT id, flow_no, remark, archive_data, created_at, updated_at, record_count
        FROM archive_history
        {where_clause}
        ORDER BY created_at DESC
    """)
    rows = []
    for row in session.execute(query, params):
        try:
            items = json.loads(row[3])
        except Exception:
            items = []
        if work_no:
            w = work_no.lower()
            if not any(w in str(it.get('workNo', '')).lower() for it in items):
                continue
        rows.append({
            "id": row[0], "flow_no": row[1], "remark": row[2],
            "items": items, "item_count": len(items),
            "created_at": row[4], "updated_at": row[5], "record_count": row[6],
        })
    return rows


@archive_query.get("/flows")
async def list_flows():
    """流程号下拉选项"""
    try:
        with Session() as session:
            result = session.execute(text(
                "SELECT DISTINCT flow_no FROM archive_history WHERE flow_no IS NOT NULL ORDER BY flow_no"
            ))
            return {"code": 200, "data": [row[0] for row in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@archive_query.get("/list")
async def list_archive(page: int = 1, page_size: int = 10,
                       flow_no: str = '', work_no: str = '',
                       keyword: str = '', start_date: str = '', end_date: str = ''):
    """归档记录分页列表（含明细，展开行直接用）"""
    try:
        with Session() as session:
            rows = _query_rows(session, flow_no, work_no, keyword, start_date, end_date)
            total = len(rows)
            start = (page - 1) * page_size
            return {"code": 200, "message": "查询成功",
                    "data": rows[start:start + page_size], "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@archive_query.get("/flatten")
async def flatten_archive(flow_no: str = '', work_no: str = '',
                          keyword: str = '', start_date: str = '', end_date: str = '',
                          limit: int = 10000):
    """按时间铺开全部明细（一行一个工作令号），导出也用它"""
    try:
        with Session() as session:
            rows = _query_rows(session, flow_no, work_no, keyword, start_date, end_date)
            flat = []
            for r in rows:
                for it in r["items"]:
                    item = dict(it)
                    item["archive_time"] = r["created_at"]
                    item["flow_no"] = r["flow_no"]
                    item["remark"] = r["remark"]
                    flat.append(item)
                if len(flat) >= limit:
                    flat = flat[:limit]
                    break
            return {"code": 200, "message": "查询成功", "data": flat, "total": len(flat)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")