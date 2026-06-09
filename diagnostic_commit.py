import sqlite3
import os

db_path = "example.db"
print("Файл БД:", os.path.abspath(db_path))

con = sqlite3.connect(db_path)
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS t(x INT);")
con.commit()
cur.execute("DELETE FROM t;")
con.commit()

cur.execute("INSERT INTO t(x) VALUES (1);")
con.commit()   # <-- добавлен commit

con.close()

con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("SELECT COUNT(*) FROM t;")
count = cur.fetchone()[0]
print("Количество строк в таблице после вставки С commit():", count)
con.close()
