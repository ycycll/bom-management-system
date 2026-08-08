import json
import logging
import re
from datetime import datetime
from typing import List, Dict

import numpy as np
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy import text

from crud.tool_function import CheckCleaner, Cleaner
from db.config import Session
from db.dict import model_data_ffb, model_fb_dict
from model import TPResponse, TPItem, ARCHIVE_SAVE_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

copilot = APIRouter(prefix="/copilot", tags=["技术准备"])


@copilot.post("/upload", response_model=TPResponse)
async def upload_file(file: UploadFile = File(...)):
    """上传Excel文件并处理技术准备"""

    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="只能上传 .xls 或 .xlsx 格式的文件")

    try:
        # 读取Excel文件
        df = pd.read_excel(file.file, dtype=str)

        # 列名处理
        df.columns = [re.sub(r'[^\u4e00-\u9fa5]', '', col) for col in df.columns]

        # 列筛选
        df = df[['工作令号', '物料号码', '物料长文本描述', '行项目备注',
                 '产品型号', '功率', '电压',
                 '频率', '安装方式', '绝缘等级', '防护等级', '出线方式', '环境条件', '冷却方式',
                 '防爆等级', '环境温度', '主接线盒位置及方向', '旋转方向', '轴承品牌', '海拔高度', '加热器',
                 '定子测温', '轴承测温']]

        # 去空白
        for i in df.columns:
            df[i] = df[i].str.strip()

        df['id'] = range(1, len(df) + 1)  # del col

        # 映射表
        map_position = {
            '顶部右出线': '顶右',
            '顶部左出线': '顶左',
            '顶部前出线': '顶前',
            '顶部后出线': '顶后',
            '左侧下出线': '左下',
            '左侧上出线': '左上',
            '右侧后出线': '右后',
            '右侧上出线': '右上',
            '右侧下出线': '右下',
            '左侧后出线': '左后',
            '': '顶右'
        }

        df['主接线盒位置及方向_del'] = df['主接线盒位置及方向'].fillna('顶部右出线').map(map_position)
        df['主接线盒位置及方向_del'] = df['主接线盒位置及方向_del'].str.replace('顶右', '')
        df['旋转方向'] = df['旋转方向'].str.replace('标准', '双向')
        df['海拔高度_del'] = '海拔高度:' + df['海拔高度'] + 'm'
        df['海拔高度_del'] = df['海拔高度_del'].str.replace(' ', '')
        df['环境温度_del'] = '环境温度:' + df['环境温度'] + '℃'
        df['电压_del'] = df['电压'] + 'V'
        df['频率_del'] = df['频率'] + 'Hz'

        # 清洗标准特征
        cleaner = Cleaner(df)
        cleaner.clean('电压_del', '380V')
        cleaner.clean('频率_del', '50Hz')
        cleaner.clean('绝缘等级', '155(F)', new_col=True)
        cleaner.clean('防护等级', 'IP55', new_col=True)
        cleaner.clean('环境条件', '户内', new_col=True)
        cleaner.clean('冷却方式', 'IC411', new_col=True)
        cleaner.clean('旋转方向', '双向', new_col=True)
        cleaner.clean('轴承品牌', '国内', new_col=True)
        cleaner.clean('加热器', '不带', new_col=True)
        cleaner.clean('定子测温', '不带', new_col=True)
        cleaner.clean('轴承测温', '不带', new_col=True)
        cleaner.clean('环境温度_del', '环境温度:-15～+40℃')
        cleaner.clean('海拔高度_del', '海拔高度:1000＜h≤1500m')
        cleaner.clean('海拔高度_del', '海拔高度:≤1000m')
        df['海拔高度_del'] = df['海拔高度_del'].str.replace('海拔高度:m', '')
        df['环境温度_del'] = df['环境温度_del'].str.replace('环境温度:℃', '')
        df = df.fillna('')

        # 技术准备列生成
        df['技术准备'] = (
                df['安装方式'] + ',' + df['电压_del'] + ',' + df['频率_del'] + ',' + df['绝缘等级_del'] + ',' +
                df['防护等级_del'] + ',' + df['环境条件_del'] + ',' + df['冷却方式_del'] + ',' +
                df['旋转方向_del'] + ',' + df['轴承品牌_del'] + ',' +
                df['主接线盒位置及方向_del'] + ',' + df['加热器_del'] + ',' + df[
                    '定子测温_del'] + ',' + df['轴承测温_del'] + ','
        )
        df['行项目备注'] = df['海拔高度_del'] + ',' + df['环境温度_del'] + ',' + df['行项目备注']
        df = df.loc[:, ~df.columns.str.contains('_del')]
        df['行项目备注'] = df['行项目备注'].str.replace(r',+', ',', regex=True).str.strip(',')

        # 分类处理出线方式
        df1 = df[~df['产品型号'].str.contains('YB', na=False)].copy()
        df2 = df[df['产品型号'].str.contains('YB', na=False)].copy()
        df1['出线方式_1'] = df1['出线方式'].fillna('葛兰头')
        map_df1_gl = {
            '其他': '',
            '葛兰头': '',
            '钢布': '钢布',
            '橡套电缆(喇叭口)': '喇叭口',
            '标准': '',
            '钢布式葛兰': '钢布不锈钢格兰',
            '尼龙格兰': ''
        }
        df1['出线方式_1'] = df1['出线方式_1'].map(map_df1_gl).fillna(df1['出线方式'])

        df2['出线方式_1'] = df2['出线方式'].fillna('橡套')
        map_df2_gl = {
            '钢布': '钢布',
            '橡套电缆(喇叭口)': '橡套',
            '标准': '橡套'
        }
        df2['出线方式_1'] = df2['出线方式_1'].map(map_df2_gl).fillna(df2['出线方式'])

        def proof_grade_tp(row):
            if 'BT' in str(row).upper():
                return 'BT4'
            elif 'CT' in str(row).upper():
                return 'CT4'
            else:
                return ''

        df2['防爆等级_del'] = df2['防爆等级'].astype(str).str.replace(' ', '').apply(proof_grade_tp)
        df2['行项目备注'] = df2['防爆等级_del'] + '//' + df2['行项目备注']
        df2 = df2.drop(columns='防爆等级_del')

        df = pd.concat([df1, df2], join='outer', ignore_index=True)

        # 最终拼接
        df['技术准备'] = df['技术准备'] + df['出线方式_1']
        df['技术准备'] = df['技术准备'].str.replace(r',+', ',', regex=True).str.strip(',')
        df['技术准备'] = df['技术准备'].str.strip(' ')
        df['行项目备注'] = df['行项目备注'].str.strip(' ')
        df = df.drop(columns='出线方式_1')

        df = df.sort_values(by='id')
        df = df.drop(columns='id')

        # 保存到数据库（这里需要根据实际情况创建表结构）
        # 暂时跳过数据库操作，因为需要先创建表结构

        # 转换为响应格式
        items = []
        for _, row in df.iterrows():
            item = TPItem(
                workNo=row.get('工作令号', ''),
                materialNo=row.get('物料号码', ''),
                materialDesc=row.get('物料长文本描述', ''),
                techPreparation=row.get('技术准备', ''),
                productType=row.get('产品型号', ''),
                power=row.get('功率', ''),
                volt=row.get('电压', ''),
                freq=row.get('频率', ''),
                mountingType=row.get('安装方式', ''),
                insulationClass=row.get('绝缘等级', ''),
                protectionClass=row.get('防护等级', ''),
                leadWireMethod=row.get('出线方式', ''),
                environmentalConditions=row.get('环境条件', ''),
                coolingMethod=row.get('冷却方式', ''),
                lineItemNotes=row.get('行项目备注', ''),
                explosionProofClass=row.get('防爆等级', ''),
                ambientTemperature=row.get('环境温度', ''),
                junctionBoxPosition=row.get('主接线盒位置及方向', ''),
                rotationDirection=row.get('旋转方向', ''),
                bearingBrand=row.get('轴承品牌', ''),
                altitude=row.get('海拔高度', ''),
                heater=row.get('加热器', ''),
                statorTempSensor=row.get('定子测温', ''),
                bearingTempSensor=row.get('轴承测温', '')
            )
            items.append(item)

        return TPResponse(
            code=200,
            message="处理成功",
            data=items,
            total=len(items)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@copilot.get("/recommend", tags=["推荐算法"])
async def recommend(
        techPreparation: str = '',
        productType: str = '',
        environmentalConditions: str = '',
):
    """推荐算法"""
    order = techPreparation.replace('，', ',')
    order = order.strip(' ,')
    order = order.replace('：', ':')

    # 处理订单
    order = productType + ',' + order

    # 处理防爆和非防爆
    if 'YB' in productType:
        if 'F' in environmentalConditions:
            env_2 = 'F'
        elif 'W' in environmentalConditions:
            env_2 = 'W'
        else:
            env_2 = ''
        # 修改订单内容
        order_elements = order.split(',')
        if environmentalConditions in order_elements:
            order_elements.remove(environmentalConditions)
            order_elements.append(env_2)
        order = ','.join(order_elements)
    else:
        # 非防爆处理
        pass  # 根据实际需求添加非防爆处理逻辑

    # 提取订单常量
    match_const = re.search(r'^([^-]*-\d+)', productType)
    order_const = match_const.group(1)
    order_const = order_const.replace('YE', 'WE')
    order_const = order_const.replace('YP', 'WEBP3')

    with Session() as session:
        # 查询 HUB 表
        query = text("SELECT * FROM hub")
        df_hub = pd.read_sql(query, session.bind)

        if df_hub.empty:
            logger.info("未找到匹配的技术准备")
            return {"code": 404, "message": "未找到匹配的技术准备", "data": None}

        # ===== 新增：定义重要特征及其惩罚系数 =====
        activation_function_features = {
            "底脚长圆孔": 0.9,
            "IC416": 0.8,
            "倒装": 0.7,
            "超低温": 0.7,
            "铝壳": 0.7,
            "-2": 0.8,
            "-4": 0.8,
            "-6": 0.8,
            "-8": 0.8,
        }

        # 匹配
        order_tags = set(order.split(','))

        # 预先识别订单中命中了哪些“重要特征”
        triggered_features = {}
        for feature, penalty in activation_function_features.items():
            if feature in order:
                triggered_features[feature] = penalty

        scores = []

        for hub_idx, row in df_hub.iterrows():
            hub_const = row['const']
            if str(order_const) != str(hub_const):
                continue
            hub_tags = set(row['recommendTP'].split(','))
            score = len(order_tags & hub_tags) / len(order_tags | hub_tags)

            for feature, penalty in triggered_features.items():
                if feature not in row['recommendTP']:
                    score *= penalty

            if score > 0:  # 过滤掉完全不相关的
                scores.append((score, hub_idx))

        # 按分数降序排列，取前 top_n
        scores.sort(key=lambda x: x[0], reverse=True)
        top_results = scores[:6]


        # 查询 COLOR 表
        match_paint = re.search(r'面漆:([A-Z]+\d+)', order)
        order_paint = match_paint.group(1) if match_paint else ('RAL5012' if 'YB' in productType else 'GE新油漆')
        query_color = "SELECT num FROM color WHERE color= :order_paint"
        color_row = session.execute(text(query_color), {"order_paint": order_paint}).fetchone()
        color = color_row[0] if color_row else ''

        # 部件推荐（规则引擎）
        components = []
        query_component = text("SELECT * FROM component_hub WHERE const = :const")
        df_components = pd.read_sql(query_component, session.bind, params={"const": order_const})

    # 构建结果
    results = []
    for rank, (score, idx) in enumerate(top_results, start=1):
        results.append({
            'rank': rank,  # 1=主选, 2=次选
            'recommendScore': round(score, 4),
            'recommendTP': df_hub.loc[idx, 'recommendTP'],
            'recommendNo': df_hub.loc[idx, 'recommendNo'],
            'recommendDesc': df_hub.loc[idx, 'recommendDesc'],
            'color': color,
        })
    if not df_components.empty:
        for _, row in df_components.iterrows():
            if row['technical_preparation'] in order_tags:
                components.append({
                    'component_id': row['component_id'],  # 料号
                    'component_desc': row['component_desc'],  # 描述
                })
    return {"code": 200, "message": "推荐成功", "data": results, "components": components}



@copilot.post("/check", tags=["校核"])
async def check(filterDF: List[Dict]):
    try:
        df_check = pd.DataFrame(filterDF, dtype=str)
        df_check['id'] = range(1, len(df_check) + 1)  # del col
        df_check['materialDesc'] = df_check['materialDesc'].str.replace('5-50', '5~50')
        df_check['techPreparation'] = df_check['techPreparation'].str.replace('：', ':')
        df_check.insert(loc=0, column='bomFalse', value='')
        map_position_check = {
            '顶部右出线': '顶右',
            '顶部左出线': '顶左',
            '顶部前出线': '顶前',
            '顶部后出线': '顶后',
            '左侧下出线': '左下',
            '左侧上出线': '左上',
            '右侧后出线': '右后',
            '右侧上出线': '右上',
            '右侧下出线': '右下',
            '左侧后出线': '左后',
            '': '顶右'
        }
        df_check['junctionBoxPosition_del'] = df_check['junctionBoxPosition'].fillna('顶部右出线')
        df_check['junctionBoxPosition_del'] = df_check['junctionBoxPosition_del'].map(map_position_check)
        df_check['junctionBoxPosition_del'] = df_check['junctionBoxPosition_del'].str.replace('顶右', '')
        map_jydj = {
            '155(F)': 'F级',
            '180(H)': 'H级',
            '': 'F级'
        }
        df_check['insulationClass_del'] = df_check['insulationClass'].fillna('155(F)')
        df_check['insulationClass_del'] = df_check['insulationClass_del'].map(map_jydj)
        df_check['insulationClass_del'] = df_check['insulationClass_del'].str.replace('F级', '')

        pattern = r'面漆:?([A-Z]+\d+)'
        df_check['面漆_del'] = df_check['techPreparation'].str.extract(pattern)
        df_check['面漆_del'] = df_check['面漆_del'].fillna('')

        checkcleaner = CheckCleaner(df_check)
        checkcleaner.check_and_clean('volt', '380')
        checkcleaner.check_and_clean('freq', '50')
        checkcleaner.check_and_clean('protectionClass', 'IP55')
        checkcleaner.check_and_clean('coolingMethod', 'IC411')
        checkcleaner.check_and_clean('bearingBrand', '国内')
        checkcleaner.check_and_clean('rotationDirection', '双向')
        checkcleaner.check_and_clean('mountingType', '重置')
        checkcleaner.check_in_description('面漆')
        checkcleaner.check_in_description('volt')
        checkcleaner.check_in_description('freq')
        checkcleaner.check_in_description('insulationClass')
        checkcleaner.check_in_description('protectionClass')
        checkcleaner.check_in_description('coolingMethod')
        checkcleaner.check_in_description('bearingBrand')
        checkcleaner.check_in_description('rotationDirection')
        checkcleaner.check_in_description('mountingType')
        checkcleaner.check_in_description('junctionBoxPosition')
        checkcleaner.check_normal_in_description('productType')
        checkcleaner.check_normal_in_description('power')

        bom_columns = df_check.filter(like='_bom').columns.tolist()
        df_check['bomFalse'] = df_check[bom_columns].sum(axis=1)
        df_check = df_check.loc[:, ~df_check.columns.str.contains('_bom')]

        df1_check = df_check[~df_check['productType'].str.contains('YB', na=False)].copy()  # 非
        df2_check = df_check[df_check['productType'].str.contains('YB', na=False)].copy()
        if not df1_check.empty:
            df1_check['leadWireMethod_del'] = df1_check['leadWireMethod'].fillna('葛兰头')
            map_df1_gl_check = {'其他': '',
                                '葛兰头': '',
                                '钢布': '钢布',
                                '橡套电缆(喇叭口)': '喇叭口',
                                '标准': '',
                                '钢布式葛兰': '',
                                '尼龙格兰': ''
                                }
            df1_check['leadWireMethod_del'] = df1_check['leadWireMethod_del'].map(map_df1_gl_check).fillna('')
            checkcleaner_df1 = CheckCleaner(df1_check)
            checkcleaner_df1.check_in_description('leadWireMethod')
            checkcleaner_df1.check_and_clean('environmentalConditions', '户内')
            checkcleaner_df1.check_in_description('environmentalConditions')
            checkcleaner_df1.review(col='environmentalConditions', col_standard_config='户内',
                                    col_non_standard_configs=['^.*?-.*?-\d[a-zA-Z]'])

            ffb_color_review_false = (~df1_check['techPreparation'].str.contains('面漆:', na=False)) & (
                ~df1_check['materialDesc'].str.contains('GE新油漆', na=False))
            if ffb_color_review_false.any():
                df1_check.loc[ffb_color_review_false, 'bomFalse'] = df1_check.loc[
                                                                        ffb_color_review_false, 'bomFalse'] + ',面漆'

        if not df2_check.empty:
            df2_check['leadWireMethod_del'] = df2_check['leadWireMethod'].fillna('橡套')
            map_df2_gl_check = {
                '钢布': '钢布',
                '橡套电缆(喇叭口)': '橡套',
                '标准': '橡套'
            }
            df2_check['leadWireMethod_del'] = df2_check['leadWireMethod_del'].map(map_df2_gl_check).fillna('')
            checkcleaner_df2 = CheckCleaner(df2_check)
            checkcleaner_df2.check_in_description('leadWireMethod')
            map_ep_2_check = {'C5': '防腐',
                              'F1': '防腐',
                              'F2': '防腐',
                              'GF2': '防腐',
                              'GTHWF2': '防腐',
                              'GWF1': '防腐',
                              'GWF2': '防腐',
                              'THF1': '防腐',
                              'THWF1': '防腐',
                              'THWF2': '防腐',
                              'WF1': '防腐',
                              'WF2': '防腐',
                              'WTHF2': '防腐',
                              'G': '',
                              'GW': '户外非防腐',
                              'TH': '',
                              'W': '户外非防腐',
                              '户内': ''
                              }
            df2_check['environmentalConditions_del'] = df2_check['environmentalConditions'].fillna('户内').map(
                map_ep_2_check).fillna('')
            checkcleaner_df2.check_in_description('environmentalConditions')

            fb_color_review_false = (~df2_check['techPreparation'].str.contains('面漆:', na=False)) & (
                ~df2_check['materialDesc'].str.contains('RAL5012', na=False))
            if fb_color_review_false.any():
                df2_check.loc[fb_color_review_false, 'bomFalse'] = df2_check.loc[
                                                                       fb_color_review_false, 'bomFalse'] + ',面漆'

        df_check = pd.concat([df1_check, df2_check], join='outer', ignore_index=True)
        df_check['bomFalse'] = df_check['bomFalse'] + df_check['leadWireMethod_bom'] + df_check[
            'environmentalConditions_bom']

        checkcleaner_pro = CheckCleaner(df_check)
        checkcleaner_pro.review(col='protectionClass', col_standard_config='IP55',
                                col_non_standard_configs=['IP65', 'IP66', 'IP56'])
        checkcleaner_pro.review(col='coolingMethod', col_standard_config='IC411',
                                col_non_standard_configs=['IC416', 'IC410', 'IC418'])
        checkcleaner_pro.review(col='bearingBrand', col_standard_config='国内',
                                col_non_standard_configs=['SKF', 'NSK', '哈瓦洛'])
        checkcleaner_pro.review(col='junctionBoxPosition', col_standard_config='顶部右出线',
                                col_non_standard_configs=['顶左', '右下', '顶前', '顶后', '左下', '左上', '右上',
                                                          '左后', '右后'])
        checkcleaner_pro.review(col='mountingType', col_standard_config='B3',
                                col_non_standard_configs=['B35', 'B34'])
        checkcleaner_pro.review(col='mountingType', col_standard_config='V1',
                                col_non_standard_configs=['V15', 'V18'])

        # 新增检查：型号含160/180/200且物料长文本描述无注油/注排油
        oil_model_condition = df_check['productType'].str.contains('160|180|200', na=False)
        oil_condition = ~df_check['materialDesc'].str.contains('注油|注排油', na=False)
        oil_error_condition = oil_model_condition & oil_condition
        if oil_error_condition.any():
            df_check.loc[oil_error_condition, 'bomFalse'] = df_check.loc[oil_error_condition, 'bomFalse'] + ',注油'

        # 新增检查：技术准备含金属风扇且物料长文本描述无金属风扇
        metal_fan_condition = df_check['techPreparation'].str.contains('金属风扇', na=False)
        metal_fan_desc_condition = ~df_check['materialDesc'].str.contains('金属风扇', na=False)
        metal_fan_error_condition = metal_fan_condition & metal_fan_desc_condition
        if metal_fan_error_condition.any():
            df_check.loc[metal_fan_error_condition, 'bomFalse'] = df_check.loc[
                                                                      metal_fan_error_condition, 'bomFalse'] + ',金属风扇'
        
        # 新增检查：电压接法校核
        # 前提：电压列为380或400（排除订单本身就规定异电压的情况）
        volt_normal = df_check['volt'].isin(['380', '400'])
        power_num = pd.to_numeric(df_check['power'], errors='coerce')
        # 3kW及以下：描述出现660/690为错误（小功率应为Y接法，相电压220V，不该出现660/690）
        low_power_error = (volt_normal &
                        (power_num <= 3) &
                        df_check['materialDesc'].str.contains(r'(?<!\d)(?:660|690)(?!\d)', na=False, regex=True))
        if low_power_error.any():
            df_check.loc[low_power_error, 'bomFalse'] = df_check.loc[low_power_error, 'bomFalse'] + ',电压接法'
        # 3kW以上：描述出现220/230为错误（大功率应为Δ接法，线电压380V，不该出现220/230）
        high_power_error = (volt_normal &
                            (power_num > 3) &
                            df_check['materialDesc'].str.contains(r'(?<!\d)(?:220|230)(?!\d)', na=False, regex=True))
        if high_power_error.any():
            df_check.loc[high_power_error, 'bomFalse'] = df_check.loc[high_power_error, 'bomFalse'] + ',电压接法'


        df_check = df_check.loc[:, ~df_check.columns.str.contains('_bom') & ~df_check.columns.str.contains('_del')]

        df_check = df_check.sort_values(by='id')
        df_check = df_check.drop(columns='id')
        df_check['bomFalse'] = df_check['bomFalse'].str.strip(',')
        df_check = df_check[['workNo', 'bomFalse']]
        return df_check.to_dict('records')
    except Exception as e:
        # 打印详细错误信息
        raise HTTPException(status_code=500, detail=f"校核失败: {str(e)}")


@copilot.post("/maintain", tags=["维护"])
async def maintain(filterDF: List[Dict]):
    try:
        with Session() as session:
            query_1 = text(f"SELECT * FROM in_ffb")
            result_1 = session.execute(query_1)
            df1_io = pd.DataFrame(result_1.fetchall(), columns=result_1.keys())

            query_2 = text(f"SELECT * FROM in_fb")
            result_2 = session.execute(query_2)
            df2_io = pd.DataFrame(result_2.fetchall(), columns=result_2.keys())

            query_3 = text(f"SELECT * FROM motor_conn")
            result_3 = session.execute(query_3)
            df3_io = pd.DataFrame(result_3.fetchall(), columns=result_3.keys())

            query_4 = text(f"SELECT * FROM cne")
            result_4 = session.execute(query_4)
            df4_io = pd.DataFrame(result_4.fetchall(), columns=result_4.keys())

            query_5 = text(f"SELECT * FROM bearing")
            result_5 = session.execute(query_5)
            bearing_io = pd.DataFrame(result_5.fetchall(), columns=result_5.keys())

        io_data_ffb = df1_io.set_index('in')['out']
        io_data_fb = df2_io.set_index('in')['out']
        io_motor_conn = df3_io.set_index('power_voltage')['conn_type']
        io_cne = df4_io.set_index('type')['cne']
        io_modify = bearing_io.set_index('param')['bearing']

        df = pd.DataFrame(filterDF, dtype=str)
        df = df[['workNo', 'materialNo', 'techPreparation', 'materialDesc',
                 'productType', 'power', 'volt',
                 'freq', 'protectionClass', 'insulationClass',
                 'coolingMethod', 'environmentalConditions', 'explosionProofClass', 'lineItemNotes']]
        df.columns = ['出厂编码', '物料号', '技术准备', '中文描述',
                      '型号', '额定功率', '额定电压',
                      '频率', '防护等级', '绝缘等级',
                      '冷却方式', '防腐等级', '防爆等级', '行项目备注']
        for column in df.columns:
            df[column] = df[column].str.strip()
        df['id'] = range(1, len(df) + 1)  # del col
        df['技术准备'] = df['技术准备'] + ',' + df['行项目备注']
        df['技术准备'] = df['技术准备'].str.replace('：', ':')
        df['技术准备'] = df['技术准备'].str.replace('M', 'm')
        df['防护等级'] = df['防护等级'].str.replace('IP', '', regex=False)
        df['冷却方式'] = df['冷却方式'].str.replace('IC', '', regex=False)
        df = df.drop(columns=['行项目备注'])

        df1 = df[~df['型号'].str.contains('YB', na=False)].copy()  # 非防爆
        df1['size'] = df1['型号'].str.extract(r'-(\d+)')  # size WE4-160L-2 取值160
        df2 = df[df['型号'].str.contains('YB', na=False)].copy()
        df2['size'] = df2['型号'].str.extract(r'(.*?-.*?\d+)')  # size YBX3-80M-2 取值YBX3-80
        if not df1.empty:
            df1['param_cat'] = df1['额定功率'].astype(str) + '&' + df1['额定电压'].astype(str)
            series_nep = df1['param_cat'].map(io_motor_conn)
            df1.insert(2, '接法', series_nep)
            df1 = df1.drop(columns=['param_cat'])

            df1['in'] = df1['型号'].astype(str) + '&' + df1['额定功率'].astype(str) + '&' + df1['额定电压'].astype(
                str)
            df1['out'] = df1['in'].map(io_data_ffb)
            df_split_nep = df1['out'].str.split('&', expand=True)
            df_split_nep.columns = ['电流', '转速', '效率', '功率因数', '重量', '标准编码', '噪声', '驱动端轴承',
                                    '非驱动轴承']
            df1 = pd.concat([df1, df_split_nep], axis=1)

            target_mask_zc = df1['型号'].str.contains('WEBP|YP', na=False)
            if target_mask_zc.any():
                concatenated_zc = (
                        df1.loc[target_mask_zc, '型号'].astype(str) + '&' +
                        df1.loc[target_mask_zc, '额定功率'].astype(str) + '&' +
                        df1.loc[target_mask_zc, '额定电压'].astype(str) + '&' +
                        df1.loc[target_mask_zc, '冷却方式'].astype(str)
                )
                list_zc = concatenated_zc.map(io_modify).str.split('&', expand=True)
                df1.loc[target_mask_zc, '驱动端轴承'] = list_zc[0]  # 第一列
                df1.loc[target_mask_zc, '非驱动轴承'] = list_zc[1]  # 第二列
            else:
                pass

            df1['铭牌料号'] = df1['size'].map(model_data_ffb['铭牌料号'])
            df1['打印模板'] = df1['size'].map(model_data_ffb['打印模板'])
            df1['绝缘等级'] = df1['绝缘等级'].replace('', np.nan)
            df1['绝缘等级'] = df1['绝缘等级'].fillna('F')
            df1['绝缘等级'] = df1['绝缘等级'].str.replace('155(F)', 'F')
        if not df2.empty:
            df2['防爆等级'] = df2['防爆等级'].fillna('')
            df2['param_cat'] = df2['额定功率'].astype(str) + '&' + df2['额定电压'].astype(str)
            series_ep = df2['param_cat'].map(io_motor_conn)
            df2.insert(2, '接法', series_ep)
            df2 = df2.drop(columns=['param_cat'])

            df2['in'] = df2['型号'].astype(str) + '&' + df2['额定功率'].astype(str) + '&' + df2['额定电压'].astype(
                str)
            df2['out'] = df2['in'].map(io_data_fb).str.replace('.0', '', regex=False)
            df_split_ep = df2['out'].str.split('&', expand=True)
            df_split_ep.columns = ['驱动端轴承', '非驱动轴承', '标准编码', '效率', '功率因数', '电流', '噪声',
                                   '转速', '重量']
            df2 = pd.concat([df2, df_split_ep], axis=1)

            def proof_grade(row):
                if 'BT' in str(row).upper():
                    return 'BT'
                elif 'CT' in str(row).upper():
                    return 'CT'
                else:
                    return ''

            df2['防爆等级_del'] = df2['防爆等级'].astype(str).str.replace(' ', '').apply(proof_grade)

            def get_cne_code(row, cne):
                explosion_type = row['防爆等级_del']  # 从行中获取防爆等级
                model = row['size']  # 从行中获取型号
                select = model + '&' + explosion_type
                if not select:
                    return ''  # 或者返回其他默认值
                return cne.get(select, '')  # 查找编码

            df2['备用列8'] = df2.apply(get_cne_code, args=(io_cne,), axis=1)
            df2 = df2.drop(columns=['防爆等级_del'])

            df2['铭牌料号'] = df2['size'].map(model_fb_dict['铭牌料号'])
            df2['打印模板'] = df2['size'].map(model_fb_dict['打印模板'])
            df2['绝缘等级'] = df2['绝缘等级'].replace('', np.nan)
            df2['绝缘等级'] = df2['绝缘等级'].fillna('155(F)')

        df = pd.concat([df1, df2], join='outer', axis=0, ignore_index=True)

        columns_to_drop = ['in', 'out', 'size']
        df = df.drop(columns=columns_to_drop)

        df['驱动端轴承'] = df['驱动端轴承'].str.strip()
        df['非驱动轴承'] = df['非驱动轴承'].str.strip()

        df['标准编码'] = df['标准编码'].str.replace('  ', ' ')
        df['防护等级'] = df['防护等级'].replace('', np.nan)
        df['冷却方式'] = df['冷却方式'].replace('', np.nan)
        df['冷却方式'] = df['冷却方式'].fillna('411')
        df['防护等级'] = df['防护等级'].fillna('55')

        df.loc[df['中文描述'].str.contains('SKF', na=False), '驱动端轴承'] = 'SKF ' + df.loc[
            df['中文描述'].str.contains('SKF', na=False), '驱动端轴承']
        df.loc[df['中文描述'].str.contains('NSK', na=False), '驱动端轴承'] = 'NSK ' + df.loc[
            df['中文描述'].str.contains('NSK', na=False), '驱动端轴承']
        df.loc[df['中文描述'].str.contains('哈瓦洛', na=False), '驱动端轴承'] = '哈瓦洛 ' + df.loc[
            df['中文描述'].str.contains('哈瓦洛', na=False), '驱动端轴承']
        df.loc[df['中文描述'].str.contains('FAG', na=False), '驱动端轴承'] = 'FAG ' + df.loc[
            df['中文描述'].str.contains('FAG', na=False), '驱动端轴承']
        df.loc[df['中文描述'].str.contains('SKF', na=False), '非驱动轴承'] = 'SKF ' + df.loc[
            df['中文描述'].str.contains('SKF', na=False), '非驱动轴承']
        df.loc[df['中文描述'].str.contains('NSK', na=False), '非驱动轴承'] = 'NSK ' + df.loc[
            df['中文描述'].str.contains('NSK', na=False), '非驱动轴承']
        df.loc[df['中文描述'].str.contains('哈瓦洛', na=False), '非驱动轴承'] = '哈瓦洛 ' + df.loc[
            df['中文描述'].str.contains('哈瓦洛', na=False), '非驱动轴承']
        df.loc[df['中文描述'].str.contains('FAG', na=False), '非驱动轴承'] = 'FAG ' + df.loc[
            df['中文描述'].str.contains('FAG', na=False), '非驱动轴承']

        df.loc[df['中文描述'].str.contains('角接', na=False), '接法'] = '△'
        df.loc[df['中文描述'].str.contains('星接', na=False), '接法'] = 'Y'
        #
        df['技术准备'] = df['技术准备'].str.replace('，', ',', regex=False)
        df['技术准备'] = df['技术准备'].str.replace('：', ':', regex=False)
        df['技术准备'] = df['技术准备'].str.replace('M', 'm', regex=False)
        df['环境温度'] = df['技术准备'].str.extract(r'(环境温度:[^℃]+℃)')
        df['海拔高度'] = df['技术准备'].str.extract(r'(海拔高度:[^m]+m)')

        df['噪声'] = df['噪声'].str.replace(' ', '')
        df['防腐等级'] = df['防腐等级'].str.replace('户内', '')

        df['工作制'] = '1'
        df['服务系数SF'] = '1'
        df['编码规则'] = ''
        df['备用13'] = ''

        ''''''
        model_modify = df['型号'].str.contains('E3-63|E4-63|E3-71|E4-71', na=False)
        if model_modify.any():
            df.loc[model_modify, '打印模板'] = '1-886010389900'

        ''''''

        df = df.sort_values(by='id')
        df = df.drop(columns=['技术准备', 'id'])

        # 处理JSON序列化问题
        df = df.fillna('')

        # 转换为字典返回
        result = df.to_dict('records')

        return result



    except Exception as e:
        # 打印详细错误信息
        raise HTTPException(status_code=500, detail=f"维护失败: {str(e)}")


@copilot.post("/recommend-to-db", response_model=TPResponse)
async def save_to_db(items: List[TPItem]):
    """将处理后的数据保存到数据库"""
    try:
        df = pd.DataFrame([item.dict() for item in items])
        df['const'] = df['productType'].str.extract(r'^([^-]*-\d+)')
        df = df[['productType', 'techPreparation', 'materialNo', 'materialDesc', 'environmentalConditions']]
        df['materialDesc'] = df['materialDesc'].str.strip(' ')
        df['recommendTP'] = df['techPreparation'].str.replace('，', ',').str.strip(' ,').str.replace('：', ':')
        df['recommendTP'] = df['productType'] + ',' + df['recommendTP']
        df1 = df[~df['productType'].str.contains('YB', na=False)].copy()  # 非防爆
        df2 = df[df['productType'].str.contains('YB', na=False)].copy()

        def sort_comma_elements_df1(cell):
            elements = cell.split(',')  # 分割字符串
            sorted_elements = sorted(elements)  # 排序
            return ','.join(sorted_elements)  # 重新连接

        def sort_comma_elements_df2(row):
            elements = row['recommendTP'].split(',')  # 分割订单字符串
            a = row['environmentalConditions']  # 获取型号列的值
            b = row['environmentalConditions_2']
            if a in elements:  # 如果型号在订单列表中，去掉它
                elements.remove(a)
                elements.append(b)
            sorted_elements = sorted(elements)  # 排序剩余元素
            return ','.join(sorted_elements)  # 重新连接

        if not df1.empty:
            df1['recommendTP'] = df1['recommendTP'].apply(sort_comma_elements_df1)
        if not df2.empty:
            def assign_b_column(row):
                a_value = str(row['environmentalConditions'])  # 确保是字符串（防止NaN）
                if 'F' in a_value:
                    return 'F'
                elif 'F' not in a_value and ('W' in a_value):
                    return 'W'
                else:
                    return ''

            df2['environmentalConditions_2'] = df2.apply(assign_b_column, axis=1)
            df2['recommendTP'] = df2.apply(sort_comma_elements_df2, axis=1)
            df2 = df2.drop(columns=['environmentalConditions_2'])
        df = pd.concat([df1, df2], join='outer', axis=0, ignore_index=True)
        df['recommendTP'] = df['recommendTP'].str.strip(',')
        df['materialNo'] = df['materialNo'].str.strip('')
        df['materialDesc'] = df['materialDesc'].str.strip('')
        df['const'] = df['productType'].str.extract(r'^([^-]*-\d+)')
        df['const'] = df['const'].str.replace('YE', 'WE')
        df['const'] = df['const'].str.replace('YP', 'WEBP3')

        df = df[['recommendTP', 'materialNo', 'materialDesc', 'const']]
        df.columns = ['recommendTP', 'recommendNo', 'recommendDesc', 'const']
        df = df.drop_duplicates(subset=['recommendTP'])

        with Session() as session:
            query = text(f"SELECT recommendTP FROM hub")
            existing_ids = pd.read_sql(query, session.bind)['recommendTP'].tolist()
        df = df[~df['recommendTP'].isin(existing_ids)]
        # 将 DataFrame 写入数据库
        df.to_sql('hub', con=Session().bind, if_exists='append', index=False)

        return TPResponse(
            code=200,
            message=f"成功插入 {len(df)} 条记录",
            data=items,
            total=len(items)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库写入失败: {str(e)}")


@copilot.post("/archive/save", tags=["存档"])
async def save_archive(archive_data: ARCHIVE_SAVE_MODEL):
    """保存进度 - 保存整个filterData"""
    try:
        with Session() as session:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_json = json.dumps(archive_data.archive_data, ensure_ascii=False)

            query = text("""
                INSERT INTO archives (flow_no, remark, archive_data, created_at, updated_at, record_count)
                VALUES (:flow_no, :remark, :data, :created, :updated, :count)
            """)
            session.execute(query, {
                "flow_no": archive_data.flow_no,
                "remark": archive_data.remark,
                "data": data_json,
                "created": now,
                "updated": now,
                "count": len(archive_data.archive_data)
            })
            session.commit()

            return {"code": 200, "message": "保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@copilot.get("/archive/list", tags=["读档"])
async def list_archives(page: int = 1, page_size: int = 10, keyword: str = ''):
    """列出所有存档（分页+搜索）"""
    try:
        with Session() as session:
            # 构建搜索条件
            where_clause = ""
            params = {}
            if keyword:
                where_clause = "WHERE flow_no LIKE :keyword OR remark LIKE :keyword"
                params['keyword'] = f'%{keyword}%'

            # 查询总数
            count_query = text(f"SELECT COUNT(*) FROM archives {where_clause}")
            total = session.execute(count_query, params).scalar()

            # 分页查询
            offset = (page - 1) * page_size
            query = text(f"""
                SELECT id, flow_no, remark, created_at, updated_at, record_count 
                FROM archives 
                {where_clause}
                ORDER BY updated_at DESC 
                LIMIT :limit OFFSET :offset
            """)
            params['limit'] = page_size
            params['offset'] = offset
            result = session.execute(query, params)
            archives = []
            for row in result:
                archives.append({
                    "id": row[0],
                    "flow_no": row[1],
                    "remark": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "record_count": row[5]
                })
            return {"code": 200, "message": "查询成功", "data": archives, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@copilot.get("/archive/load/{archive_id}", tags=["读档"])
async def load_archive(archive_id: int):
    """加载指定存档"""
    try:
        with Session() as session:
            query = text("SELECT archive_data FROM archives WHERE id = :id")
            result = session.execute(query, {"id": archive_id})
            row = result.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="存档不存在")

            archive_data = json.loads(row[0])
            return {"code": 200, "message": "加载成功", "data": archive_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载失败: {str(e)}")


@copilot.delete("/archive/delete/{archive_id}", tags=["存档"])
async def delete_archive(archive_id: int):
    """删除存档"""
    try:
        with Session() as session:
            query = text("DELETE FROM archives WHERE id = :id")
            result = session.execute(query, {"id": archive_id})
            session.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="存档不存在")

            return {"code": 200, "message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@copilot.post("/archive_history/save", tags=["归档"])
async def save_archive_history(archive_data: ARCHIVE_SAVE_MODEL):
    """归档 - 保存进度"""
    try:
        with Session() as session:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_json = json.dumps(archive_data.archive_data, ensure_ascii=False)

            query = text("""
                INSERT INTO archive_history (flow_no, remark, archive_data, created_at, updated_at, record_count)
                VALUES (:flow_no, :remark, :data, :created, :updated, :count)
            """)
            session.execute(query, {
                "flow_no": archive_data.flow_no,
                "remark": archive_data.remark,
                "data": data_json,
                "created": now,
                "updated": now,
                "count": len(archive_data.archive_data)
            })
            session.commit()
            return {"code": 200, "message": "归档成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"归档失败: {str(e)}")

@copilot.get("/archive_history/list", tags=["归档"])
async def list_archive_history(page: int = 1, page_size: int = 10, keyword: str = ''):
    """列出所有归档（分页+搜索）"""
    try:
        with Session() as session:
            where_clause = ""
            params = {}
            if keyword:
                where_clause = "WHERE flow_no LIKE :keyword OR remark LIKE :keyword"
                params['keyword'] = f'%{keyword}%'

            count_query = text(f"SELECT COUNT(*) FROM archive_history {where_clause}")
            total = session.execute(count_query, params).scalar()

            offset = (page - 1) * page_size
            query = text(f"""
                SELECT id, flow_no, remark, created_at, updated_at, record_count
                FROM archive_history
                {where_clause}
                ORDER BY updated_at DESC
                LIMIT :limit OFFSET :offset
            """)
            params['limit'] = page_size
            params['offset'] = offset
            result = session.execute(query, params)
            archives = []
            for row in result:
                archives.append({
                    "id": row[0], "flow_no": row[1], "remark": row[2],
                    "created_at": row[3], "updated_at": row[4], "record_count": row[5]
                })
            return {"code": 200, "message": "查询成功", "data": archives, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@copilot.get("/archive_history/load/{archive_id}", tags=["归档"])
async def load_archive_history(archive_id: int):
    """加载指定归档"""
    try:
        with Session() as session:
            query = text("SELECT archive_data FROM archive_history WHERE id = :id")
            result = session.execute(query, {"id": archive_id})
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="归档不存在")
            archive_data = json.loads(row[0])
            return {"code": 200, "message": "加载成功", "data": archive_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载失败: {str(e)}")

@copilot.delete("/archive_history/delete/{archive_id}", tags=["归档"])
async def delete_archive_history(archive_id: int):
    """删除归档"""
    try:
        with Session() as session:
            query = text("DELETE FROM archive_history WHERE id = :id")
            result = session.execute(query, {"id": archive_id})
            session.commit()
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="归档不存在")
            return {"code": 200, "message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@copilot.post("/archive/to_history/{archive_id}", tags=["归档"])
async def archive_to_history(archive_id: int):
    """把指定存档直接归档（存档列表里的快捷归档按钮调用）"""
    try:
        with Session() as session:
            # 1. 从存档表读取该条数据
            query = text("SELECT flow_no, remark, archive_data, record_count FROM archives WHERE id = :id")
            row = session.execute(query, {"id": archive_id}).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="存档不存在")

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert = text("""
                INSERT INTO archive_history (flow_no, remark, archive_data, created_at, updated_at, record_count)
                VALUES (:flow_no, :remark, :data, :created, :updated, :count)
            """)
            session.execute(insert, {
                "flow_no": row[0], "remark": row[1], "data": row[2],
                "created": now, "updated": now, "count": row[3]
            })
            session.commit()
            return {"code": 200, "message": "归档成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"归档失败: {str(e)}")