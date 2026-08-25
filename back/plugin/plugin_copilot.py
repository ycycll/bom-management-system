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

plugin_copilot = APIRouter(prefix="/plugin_copilot", tags=["插件辅助"])


@plugin_copilot.post("/tp", tags=["技术准备"])
async def tp(data: List[Dict]):
    df = pd.DataFrame(data, dtype=str)
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
    df['绝缘等级'] = df['绝缘等级'].str.replace('155（F)', '155(F)')
    df['绝缘等级'] = df['绝缘等级'].str.replace('180（H)', '180(H)')
    df['绝缘等级'] = df['绝缘等级'].replace('F', '155(F)')

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
        '尼龙格兰': '',
        '标配': ''
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

    return {"code": 200, "message": "处理成功", "data": items, "total": len(items)}


@plugin_copilot.post("/check", tags=["校核"])
async def check(filterDF: List[Dict]):
    try:
        df_check = pd.DataFrame(filterDF, dtype=str)
        df_check['id'] = range(1, len(df_check) + 1)  # del col
        df_check['materialDesc'] = df_check['materialDesc'].str.replace('5-50', '5~50')
        df_check['freq'] = df_check['freq'].str.replace('5-50', '5~50')
        df_check.insert(loc=0, column='bomFalse', value='')

        df_check['insulationClass'] = df_check['insulationClass'].str.replace('155（F)', '155(F)')
        df_check['insulationClass'] = df_check['insulationClass'].str.replace('180（H)', '180(H)')
        df_check['insulationClass'] = df_check['insulationClass'].replace('F', '155(F)')

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

        checkcleaner = CheckCleaner(df_check)
        checkcleaner.check_and_clean('volt', '380')
        checkcleaner.check_and_clean('freq', '50')
        checkcleaner.check_and_clean('protectionClass', 'IP55')
        checkcleaner.check_and_clean('coolingMethod', 'IC411')
        checkcleaner.check_and_clean('bearingBrand', '国内')
        checkcleaner.check_and_clean('rotationDirection', '双向')
        checkcleaner.check_and_clean('mountingType', '重置')
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