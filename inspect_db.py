import sqlite3
import os
p = os.path.join('instance','dermaura.db')
print('DB path:', p)
if not os.path.exists(p):
    print('DB not found')
    raise SystemExit(1)
conn = sqlite3.connect(p)
c = conn.cursor()
for row in c.execute("SELECT id, name, image FROM product ORDER BY id DESC LIMIT 10"):
    print(row)
conn.close()
