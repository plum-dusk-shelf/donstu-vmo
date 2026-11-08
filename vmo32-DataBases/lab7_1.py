import psycopg2
from datetime import datetime, timedelta

def quick_partition_demo():
    """Упрощенная демонстрация партиционирования"""
    conn = psycopg2.connect(dbname="myfirstdb",
                               user="simafrus",
                               password="8bzm61K",
                               port=5432
    )
    
    try:
        with conn.cursor() as cur:
            # Создаем партиционированную таблицу
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL,
                recorded_at TIMESTAMP NOT NULL,
                sensor_id INTEGER,
                value FLOAT
            ) PARTITION BY RANGE (recorded_at);
            """)
            
            # Создаем партиции по дням
            for i in range(7):
                date = datetime.now().date() - timedelta(days=i)
                partition_name = f"sensor_data_{date.strftime('%Y_%m_%d')}"
                
                cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {partition_name} 
                PARTITION OF sensor_data
                FOR VALUES FROM ('{date}') TO ('{date + timedelta(days=1)}');
                """)
            
            # Вставляем тестовые данные
            cur.execute("""
            INSERT INTO sensor_data (recorded_at, sensor_id, value) 
            VALUES 
                (NOW() - INTERVAL '1 day', 1, 23.5),
                (NOW() - INTERVAL '2 days', 2, 24.1),
                (NOW(), 1, 22.8);
            """)
            
            # Показываем, какие партиции используются
            cur.execute("""
            EXPLAIN (ANALYZE) 
            SELECT * FROM sensor_data 
            WHERE recorded_at >= NOW() - INTERVAL '1 day';
            """)
            
            result = cur.fetchall()
            for row in result:
                print(row[0])
            
            conn.commit()
            
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    quick_partition_demo()
