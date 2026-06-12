from typing import List, Dict

from pydantic import BaseModel


class WEModel(BaseModel):
    id: int | None = None
    we_type: str
    we_power: str
    we_speed: str
    we_eff: str
    we_factor: str
    we_tor_mul: str
    we_cur_mul: str
    we_max_tor_mul: str
    we_weight: str
    we_noise_p: str
    we_noise_w: str
    we_inertia: str
    we_torque: str
    we_freq: str
    we_volt: str
    we_cur: str
    we_material: str


class WEUpdateModel(BaseModel):
    id: int | None = None
    we_type: str | None = None
    we_power: str | None = None
    we_speed: str | None = None
    we_eff: str | None = None
    we_factor: str | None = None
    we_tor_mul: str | None = None
    we_cur_mul: str | None = None
    we_max_tor_mul: str | None = None
    we_weight: str | None = None
    we_noise_p: str | None = None
    we_noise_w: str | None = None
    we_inertia: str | None = None
    we_torque: str | None = None
    we_freq: str | None = None
    we_volt: str | None = None
    we_cur: str | None = None
    we_material: str | None = None


class TPItem(BaseModel):
    """技术准备项目"""
    workNo: str  # 工作令号
    materialNo: str  # 物料号码
    materialDesc: str  # 物料长文本描述
    techPreparation: str  # 技术准备
    productType: str  # 产品型号
    power: str  # 功率
    volt: str  # 电压
    freq: str  # 频率
    mountingType: str  # 安装方式
    insulationClass: str  # 绝缘等级
    protectionClass: str  # 防护等级（如 IP54）
    leadWireMethod: str  # 出线方式
    environmentalConditions: str  # 环境条件
    coolingMethod: str  # 冷却方式
    lineItemNotes: str  # 行项目备注
    explosionProofClass: str  # 防爆等级（如 Ex d IIB T4）
    ambientTemperature: str  # 环境温度
    junctionBoxPosition: str  # 主接线盒位置及方向
    rotationDirection: str  # 旋转方向
    bearingBrand: str  # 轴承品牌
    altitude: str  # 海拔高度
    heater: str  # 加热器
    statorTempSensor: str  # 定子测温
    bearingTempSensor: str  # 轴承测温


class TPResponse(BaseModel):
    """技术准备响应"""
    code: int
    message: str
    data: List[TPItem]
    total: int


class QueryRequest(BaseModel):
    query: str


class AGREEMENT_MODEL(BaseModel):
    id: int | None = None
    agreement_id: str
    name: str
    tp: str


class AGREEMENT_UPDATE_MODEL(BaseModel):
    id: int | None = None
    agreement_id: str | None = None
    name: str | None = None
    tp: str | None = None


class ARCHIVE_SAVE_MODEL(BaseModel):
    flow_no: str  # 流程号
    remark: str = ''  # 备注
    archive_data: List[Dict]  # 完整的filterData数据

