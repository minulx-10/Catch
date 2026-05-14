import sqlite3
import os

DB_PATH = 'catchbot.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 유저 정보 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coin INTEGER DEFAULT 0,
        explore_count INTEGER DEFAULT 0
    )
    ''')
    
    # 생물 도감 (정적 데이터)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS creatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        grade TEXT,
        combat_power INTEGER,
        trait TEXT,
        biomes TEXT,
        weather_condition TEXT,
        price INTEGER DEFAULT 0
    )
    ''')
    
    # 유저 인벤토리 (보유 생물)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        creature_id INTEGER,
        catch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(creature_id) REFERENCES creatures(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

# 초기 생물 데이터 삽입
def seed_creatures():
    conn = get_connection()
    cursor = conn.cursor()
    
    initial_data = [
        ('벼메뚜기', 'N', 5, '군집형', '숲,들판', '비가 오거나 날씨가 안 좋을 경우 등장 확률 감소', 50),
        ('개미', 'N', 1, '군집형', '숲,들판', '비가 오거나 날씨가 안 좋을 경우 등장 확률 감소', 10),
        ('지렁이', 'N', 3, '자기 보호형', '숲,들판', '비가 오거나 비 온 뒤 흐린 날씨에 등장', 20),
        ('들개', 'N', 100, '돌격형', '숲,들판', '날씨가 안 좋을 경우 등장 확률 감소', 150),
        ('배추흰나비', 'N', 1, '관상형', '숲,들판', '비가 오거나 날씨가 안 좋을 경우 등장 확률 감소', 30)
    ]
    
    for creature in initial_data:
        cursor.execute('''
        INSERT OR IGNORE INTO creatures (name, grade, combat_power, trait, biomes, weather_condition, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', creature)
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_creatures()
    print("Database initialized and seeded.")
