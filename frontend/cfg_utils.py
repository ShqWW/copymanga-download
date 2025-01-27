import sqlite3
import os

DBPATH = './copymanga-config.db'

CREATE_CONFIG_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS config (
    KEY TEXT PRIMARY KEY,
    VALUE TEXT
);
'''

initial_config = {
    "download_path": './',        # 下载路径
    "theme": "Auto",             # 主题设置
    "numthread": '8',            # 线程数量
    "url": "mangacopy.com",      # URL 地址
    "quality": "1"               # 质量设置
}

def initialize_db():
    if not os.path.exists(DBPATH):
        with sqlite3.connect(DBPATH) as conn:
            conn.execute("PRAGMA journal_mode=DELETE")
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                KEY TEXT PRIMARY KEY,
                VALUE TEXT
            );
            ''')
            for key, value in initial_config.items():
                cursor.execute("INSERT OR REPLACE INTO config (KEY, VALUE) VALUES (?, ?)", (key, value))
            conn.commit()

def read_config_dict(key=None):
    if key is None:
        return None
    with sqlite3.connect(DBPATH) as conn:
        conn.execute("PRAGMA journal_mode=DELETE")
        cursor = conn.cursor()
        cursor.execute("SELECT VALUE FROM config WHERE KEY = ?", (key,))
        result = cursor.fetchone()
        conn.commit()
        return result[0] if result else None

def write_config_dict(key, value):
    with sqlite3.connect(DBPATH) as conn:
        conn.execute("PRAGMA journal_mode=DELETE")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO config (KEY, VALUE) VALUES (?, ?)", (key, value))
        conn.commit()