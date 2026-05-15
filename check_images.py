import sqlite3
conn=sqlite3.connect('instance/dermaura.db')
c=conn.cursor()
c.execute('select name,image_url from product limit 5')
for row in c.fetchall():
    print(row)
