import random
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
import psycopg2


conn = psycopg2.connect("dbname=newdb user=simafrus password=8bzm61K")
cur = conn.cursor()


def generate_data():
    for i in range(10000):
        print(i, end="\t")
        cur.execute(
            """
            INSERT INTO sensors_data(time, sensor_id, value)
            VALUES (%s, %s, %s)
            """,
            (datetime.datetime.now() + datetime.timedelta(seconds=i*-1000), random.randint(1, 10), random.uniform(-10, 10))
        )

def generate_sensors():
    sensors = ['Kitchen', 'Livingroom', 'Bathroom'] + [f'Bedroom{i}' for i in range(1,10)]
    for i in range(1, 11):
        cur.execute(
            """
            INSERT INTO sensors(id, room)
            VALUES (%s, %s)
            """,
            (i, sensors[i])
        )

generate_data()
conn.commit()
cur.close()
conn.close()



