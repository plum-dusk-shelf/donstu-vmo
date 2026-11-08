import psycopg2 as pg

try:
    connection = pg.connect(database = "myfirstdb",
                               user = "simafrus",
                               password = "8bzm61K",
                               #host = "localhost",
                               port = 5432)
    cursor = connection.cursor()
    print ( connection.get_dsn_parameters(),"\n")
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")
    print(cursor.execute('SELECT * FROM users;'))
    rows = cursor.fetchall()  
    for row in rows:  
        print(row)

except (Exception, pg.Error) as error :
    print ("Error while connecting to PostgreSQL", error)

finally:
    if(connection): cursor.close()
    connection.close()
    print("\nPostgreSQL connection is closed")
