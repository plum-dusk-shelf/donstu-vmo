from flask import Flask, request, jsonify, Response, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            temperature REAL,
            humidity REAL,
            pressure REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json

    conn = sqlite3.connect('weather.db')
    c = conn.cursor()

    c.execute("INSERT INTO data (time, temperature, humidity, pressure) VALUES (?, ?, ?, ?)",
              (datetime.now(), data['temperature'], data['humidity'], data['pressure']))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route('/')
def index():
    return render_template("index.html")
    #conn = sqlite3.connect('weather.db')
    #c = conn.cursor()
    #rows = c.execute("SELECT * FROM data ORDER BY time DESC").fetchall()
    #conn.close()

    #html = "<table border=1><tr><th>Time</th><th>Temp</th><th>Humidity</th><th>Pressure</th></tr>"

    #for row in rows:
    #    html += f"<tr><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"

    #html += "</table>"
    #html += '<br><a href="/csv">Download CSV</a>'

    #return html

@app.route('/csv')
def download_csv():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    rows = c.execute("SELECT * FROM data").fetchall()
    conn.close()

    csv_data = "time,temperature,humidity,pressure\n"
    for row in rows:
        csv_data += f"{row[1]},{row[2]},{row[3]},{row[4]}\n"

    return Response(csv_data, mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=data.csv"})

@app.route('/api/data')
def api_data():
    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    rows = c.execute("SELECT time, temperature, humidity, pressure FROM data").fetchall()
    conn.close()

    return jsonify([
        {
            "time": r[0],
            "temperature": r[1],
            "humidity": r[2],
            "pressure": r[3]
        } for r in rows
    ])

@app.route('/clear/<key>')
def clear(key):
    if key != "1488":
        return "DENIED"

    conn = sqlite3.connect('weather.db')
    c = conn.cursor()
    c.execute("DELETE FROM data")
    conn.commit()
    conn.close()
    return "CLEARED"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
