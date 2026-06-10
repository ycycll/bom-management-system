from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "mysql+pymysql://root:2001@localhost:3306/project?charset=utf8mb4"

# 创建引擎（带连接池）
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # 连接池大小
    max_overflow=12,        # 最大溢出连接数
    pool_recycle=10000,      # 连接回收时间（秒）
    pool_pre_ping=True,     # 连接前 ping 测试
    echo=False              # 是否打印 SQL
)

# 创建 Session 工厂
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

