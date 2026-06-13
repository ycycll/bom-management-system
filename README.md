

# BOM 管理系统

BOM（Bill of Materials）管理系统是一个基于 FastAPI 后端和 Vue 3 前端构建的全栈管理平台，旨在帮助企业高效管理物料清单及相关协议文档。系统集成了智能推荐算法、数据校验清理等 AI 辅助功能，可应用于制造业、工程项目管理等场景。

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| 后端 | Python 3.10、FastAPI、Pydantic |
| 前端 | Vue 3、Vite、Element Plus |
| 数据库 | MongoDB（配置文件位于 `back/db/config.py`） |

## 功能模块

### 1. 样本管理（样本）
管理各类物料样本数据，支持按类型、电压、频率、材质等条件筛选查询，提供完整的增删改查接口。

### 2. 协议管理（协议）
管理和维护合作协议、技术协议等文档，支持关键词搜索、分页浏览及版本更新。

### 3. 智能助手（Copilot）
- **文件上传**：支持上传技术文档并解析处理
- **智能推荐**：基于技术准备条件、产品类型、环境条件等因素推荐合适的物料或方案
- **数据校核**：对物料数据进行自动化校验核查
- **数据维护**：批量处理和维护物料数据

### 4. 智能问答（Defog）
基于 RAG（检索增强生成）技术的问答模块，可针对技术文档进行智能问答。

### 5. 图纸管理（图纸）
管理技术图纸文件，支持按名称、备注搜索，获取图纸文件内容。

### 6. Hub 管理
集中管理推荐数据，支持条件筛选、删除等操作。

### 7. 数据校验工具
提供标准特征清理和校验功能，包括：
- 常规值清除
- 描述字段校验
- 非标准配置检查

## 项目结构

```
bom-management-system/
├── back/                    # 后端服务
│   ├── crud/               # 业务接口层
│   │   ├── agreement.py    # 协议管理
│   │   ├── copilot.py      # 智能助手
│   │   ├── defog.py       # 智能问答
│   │   ├── draw.py        # 图纸管理
│   │   ├── hub.py         # Hub 管理
│   │   ├── tool_function.py  # 工具函数
│   │   └── we.py          # 样本管理
│   ├── db/                # 数据库配置
│   ├── model.py           # 数据模型定义
│   ├── main.py           # 应用入口
│   └── static/           # 静态资源
│
└── front/                 # 前端应用
    ├── src/
    │   ├── views/        # 页面视图
    │   │   ├── agreement.vue
    │   │   ├── copilot.vue
    │   │   ├── defog.vue
    │   │   ├── draw.vue
    │   │   ├── home.vue
    │   │   ├── hub.vue
    │   │   ├── login.vue
    │   │   └── sample.vue
    │   ├── component/    # 公共组件
    │   ├── router/      # 路由配置
    │   └── main.js      # 应用入口
    └── package.json
```

## 快速开始

### 后端启动

```bash
cd back
pip install -r requirements.txt  # 安装依赖
uvicorn main:app --reload      # 启动服务
```

后端服务默认运行在 `http://localhost:8000`

### 前端启动

```bash
cd front
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`

## 接口文档

服务启动后，可访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 许可证

请查看项目根目录下的 LICENSE 文件获取许可信息。