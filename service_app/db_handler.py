# db_handler.py
import sqlite3
from datetime import datetime

DB_NAME = "task_logs.db"

def init_db():
    """Инициализирует базу данных, создавая таблицу для хранения данных."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_task_status(task_name, status):
    """
    Записывает статус выполнения задачи в базу данных.

    :param task_name: Имя задачи.
    :param status: Статус выполнения ('success' или 'failure').
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO task_logs (task_name, status, timestamp)
        VALUES (?, ?, ?)
    """, (task_name, status, timestamp))
    conn.commit()
    conn.close()

def get_last_task_status(task_name):
    """
    Возвращает последний статус выполнения задачи по имени.

    :param task_name: Имя задачи.
    :return: Словарь с последним статусом или None, если задачи не найдено.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, timestamp
        FROM task_logs
        WHERE task_name = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (task_name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"task_name": task_name, "status": result[0], "timestamp": result[1]}
    else:
        return None
