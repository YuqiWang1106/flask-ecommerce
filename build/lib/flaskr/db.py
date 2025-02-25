import sqlite3
from flask import g, current_app

def get_db() -> sqlite3.Connection:
    """获取 SQLite 数据库连接，确保读取 `app.config['DATABASE']`"""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],  # ✅ 确保这里是 `app.config["DATABASE"]`
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 让查询结果支持字典访问
    return g.db


def close_db(e=None) -> None:
    """关闭数据库连接"""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    """注册数据库相关的函数"""
    app.teardown_appcontext(close_db)

def initialize_northwind():
    """检查 `northwind.db` 是否已有 `Authentication` 和 `Shopping_cart` 表，如果没有，则创建"""
    db = get_db()

    # ✅ 1. 创建 `Authentication` 表（不依赖其他表）
    db.execute("""
        CREATE TABLE IF NOT EXISTS Authentication (
            UserID TEXT PRIMARY KEY,
            PasswordHash TEXT NOT NULL,
            SessionID TEXT
        );
    """)

    # ✅ 2. 确保 Products 表存在（如果不存在则创建）
    db.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY,
            ProductName TEXT NOT NULL,
            UnitPrice REAL,
            UnitsInStock INTEGER
        );
    """)

    # ✅ 3. 创建 Shopping_cart 表（现在可以安全地引用 Products 表）
    db.execute("""
        CREATE TABLE IF NOT EXISTS Shopping_cart (
            ShopperID INTEGER NOT NULL,
            ProductID INTEGER NOT NULL,
            Quantity INTEGER NOT NULL DEFAULT 1,
            AddedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
            PRIMARY KEY (ShopperID, ProductID)
        );
    """)

    # ✅ 4. 在 `Employees` 表中插入 `EmployeeID=999999`（如果它还不存在）
    db.execute("""
        INSERT INTO Employees (EmployeeID, LastName, FirstName)
        SELECT 999999, 'WEB', 'WEB'
        WHERE NOT EXISTS (
            SELECT 1 FROM Employees WHERE EmployeeID = 999999
        );
    """)

    db.commit()
