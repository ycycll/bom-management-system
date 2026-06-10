import requests
import pandas as pd
import io

# 测试配置
BASE_URL = "http://localhost:8060"
UPLOAD_URL = f"{BASE_URL}/copilot/upload"


def create_test_excel():
    """创建测试用的Excel文件"""
    # 创建测试数据
    data = {
        '工作令号': ['WO001', 'WO002'],
        '物料号码': ['MAT001', 'MAT002'],
        '物料长文本描述': ['测试物料1', '测试物料2'],
        '产品型号': ['Y2-80M1-2', 'YB2-100L1-4'],
        '功率': ['0.75', '2.2'],
        '电压': ['380', '380'],
        '频率': ['50', '50'],
        '安装方式': ['B3', 'B5'],
        '绝缘等级': ['155(F)', '155(F)'],
        '防护等级': ['IP55', 'IP55'],
        '出线方式': ['葛兰头', '橡套电缆(喇叭口)'],
        '环境条件': ['户内', '户内'],
        '冷却方式': ['IC411', 'IC411'],
        '行项目备注': ['测试备注1', '测试备注2'],
        '防爆等级': ['', 'Ex d IIB T4'],
        '环境温度': ['-15～+40', '-15～+40'],
        '主接线盒位置及方向': ['顶部右出线', '顶部左出线'],
        '旋转方向': ['标准', '标准'],
        '轴承品牌': ['国内', '国内'],
        '海拔高度': ['≤1000', '≤1000'],
        '加热器': ['不带', '不带'],
        '定子测温': ['不带', '不带'],
        '轴承测温': ['不带', '不带']
    }

    df = pd.DataFrame(data)

    # 保存到内存
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return output


def test_upload():
    """测试上传接口"""
    print("=" * 50)
    print("开始测试技术准备上传接口")
    print("=" * 50)

    # 1. 测试API是否可达
    print("\n1. 测试API是否可达...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✓ API文档页面可访问")
        else:
            print(f"✗ API文档页面返回状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 无法连接到服务器: {e}")
        print("请确保服务器已启动: uvicorn main:app --reload")
        return

    # 2. 测试文件上传
    print("\n2. 测试文件上传...")
    try:
        excel_file = create_test_excel()

        files = {
            'file': ('test_tp.xlsx', excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }

        response = requests.post(UPLOAD_URL, files=files)

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✓ 上传成功!")
            print(f"返回码: {result.get('code')}")
            print(f"消息: {result.get('message')}")
            print(f"数据条数: {result.get('total')}")

            # 显示第一条数据
            data = result.get('data', [])
            if data:
                print("\n第一条数据预览:")
                first_item = data[0]
                for key, value in first_item.items():
                    print(f"  {key}: {value}")
        elif response.status_code == 404:
            print("✗ 404错误 - 接口不存在")
            print(f"请检查URL是否正确: {UPLOAD_URL}")
        elif response.status_code == 422:
            print("✗ 422错误 - 请求参数错误")
            print(f"响应内容: {response.text}")
        else:
            print(f"✗ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"✗ 请求异常: {e}")


if __name__ == "__main__":
    test_upload()

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)