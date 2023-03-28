#
#
#


import sqlite3

def test_db1():
      conn = sqlite3.connect('test1.db')

      c = conn.cursor()
      c.execute('''CREATE TABLE COMPANY
      (ID INT PRIMARY KEY     NOT NULL,
      NAME           TEXT    NOT NULL,
      AGE            INT     NOT NULL,
      ADDRESS        CHAR(50),
      SALARY         REAL);''')


      c.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
            VALUES (1, 'Paul', 32, 'California', 20000.00 )")

      c.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
            VALUES (2, 'Allen', 25, 'Texas', 15000.00 )")

      c.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
            VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )")

      c.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
            VALUES (4, 'Mark', 25, 'Rich-Mond', 65000.00 )")

      conn.commit()

      cc = c.execute('SELECT id,name,address from COMPANY')
      for row in cc:
            print(row)

      conn.close()

def test_db2():
      con = sqlite3.connect("test2.db")
      cur = con.cursor()
      cur.execute("CREATE TABLE movie(title, year, score)")

      con.commit()
      con.close()

def test_db3():
      conn = sqlite3.connect("test3.db")
      cursor = conn.cursor()
      cursor.execute('''
CREATE TABLE CITY (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
X FLOAT,
Y FLOAT
);
''')
      cursor.execute('''
CREATE TABLE HERO (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
BORN_YEAR INT,
CITY_ID INT references CITY(ID),
ACITIVIYY INT
);
''')
      cursor.execute('''
CREATE TABLE TROOP (
ID INT PRIMARY KEY NOT NULL,
NAME TEXT NOT NULL,
CHIEF_HERO_ID INT references HERO(ID),
HERO_LIST INT ARRAY[9],
X FLOAT,
Y FLOAT
);
''')
      conn.commit()
      conn.close()

#test_db1()
test_db3()

