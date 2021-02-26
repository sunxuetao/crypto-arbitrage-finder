import psycopg2
import pandas as pd

conn = psycopg2.connect(database="postgres",
                        user="postgres",
                        password="Awesome1@#",
                        host="54.254.134.82",
                        port="5432")

# create table
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS COMPANY
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AGE            INT     NOT NULL,
       ADDRESS        CHAR(50),
       SALARY         REAL);''')

# insert records
# cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (1, 'Paul', 32, 'California', 20000.00 )");
#
# cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (2, 'Allen', 25, 'Texas', 15000.00 )");
#
# cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )");
#
# cur.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )");
#
# conn.commit()

# select records
df = pd.read_sql("SELECT id, name, address, salary  from COMPANY", conn)
print(df)

# update
# cur.execute("UPDATE COMPANY set SALARY = 25000.00 where ID=1")
# conn.commit()
#
# # delete
# cur.execute("DELETE from COMPANY where ID=2;")
# conn.commit()

conn.close()
