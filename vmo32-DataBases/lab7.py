from lab4_graphics_fixed import db_config

import psycopg2
import random
from datetime import datetime, timedelta
import time
from faker import Faker

# Инициализация Faker для генерации случайных данных
fake = Faker('ru_RU')  # Русские имена

class CinemaDatabase:
    def __init__(self, dbname="cinema_db", user="postgres", password="password", host="localhost"):
        self.conn_params = db_config
        
    def connect(self):
        return psycopg2.connect(**self.conn_params)
    
    def create_tables(self):
        """Создание обычной таблицы и секционированной таблицы"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                # Удаляем существующие таблицы
                cur.execute("DROP TABLE IF EXISTS orders CASCADE")
                cur.execute("DROP TABLE IF EXISTS orders_partitioned CASCADE")
                
                # Создание обычной таблицы
                cur.execute("""
                    CREATE TABLE orders (
                        id SERIAL PRIMARY KEY,
                        order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        session_date TIMESTAMP NOT NULL,
                        customer VARCHAR(100) NOT NULL,
                        movie VARCHAR(200) NOT NULL,
                        quantity INT NOT NULL CHECK (quantity > 0),
                        price NUMERIC(10, 2) NOT NULL CHECK (price >= 0)
                    );
                """)
                
                # Создание главной секционированной таблицы
                cur.execute("""
                    CREATE TABLE orders_partitioned (
                        id SERIAL,
                        order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        session_date TIMESTAMP NOT NULL,
                        customer VARCHAR(100) NOT NULL,
                        movie VARCHAR(200) NOT NULL,
                        quantity INT NOT NULL CHECK (quantity > 0),
                        price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
                        PRIMARY KEY (id, session_date)
                    ) PARTITION BY RANGE (session_date);
                """)
                
                conn.commit()
                print("Таблицы созданы успешно")
    
    def create_partitions(self, start_year=2023, end_year=2024):
        """Создание секций по месяцам"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                for year in range(start_year, end_year + 1):
                    for month in range(1, 13):
                        partition_name = f"orders_{year}_{month:02d}"
                        start_date = f"{year}-{month:02d}-01"
                        if month == 12:
                            end_date = f"{year+1}-01-01"
                        else:
                            end_date = f"{year}-{month+1:02d}-01"
                        
                        # Удаляем существующую секцию если есть
                        cur.execute(f"DROP TABLE IF EXISTS {partition_name} CASCADE")
                        
                        cur.execute(f"""
                            CREATE TABLE {partition_name}
                            PARTITION OF orders_partitioned
                            FOR VALUES FROM ('{start_date}') TO ('{end_date}');
                        """)
                
                conn.commit()
                print("Секции созданы успешно")
    
    def generate_sample_data(self, num_records=100000):
        """Генерация случайных данных"""
        movies = [
            "Аватар: Путь воды", "Оппенгеймер", "Барби", "Человек-паук: Через вселенные",
            "Дюна", "Топ Ган: Мэверик", "Чёрная Пантера", "Мстители: Финал",
            "Джон Уик 4", "Охотники за привидениями", "Интерстеллар", "Начало"
        ]
        
        data = []
        base_date = datetime(2023, 1, 1)
        
        print(f"Генерация {num_records} записей...")
        for i in range(num_records):
            if i % 10000 == 0:
                print(f"Сгенерировано {i}/{num_records} записей")
                
            # Случайная дата сеанса в пределах 2023-2024 годов
            days_offset = random.randint(0, 730)
            session_date = base_date + timedelta(days=days_offset)
            
            # Дата заказа до даты сеанса (до 30 дней)
            order_offset = random.randint(1, 30)
            order_date = session_date - timedelta(days=order_offset)
            
            customer = fake.name()
            movie = random.choice(movies)
            quantity = random.randint(1, 10)
            price = round(random.uniform(5.0, 25.0) * quantity, 2)
            
            data.append((order_date, session_date, customer, movie, quantity, price))
        
        print("Генерация данных завершена")
        return data
    
    def insert_data(self, table_name, data, batch_size=1000):
        """Вставка данных в указанную таблицу"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                query = f"""
                    INSERT INTO {table_name} 
                    (order_date, session_date, customer, movie, quantity, price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                total_time = 0
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    start_time = time.time()
                    
                    cur.executemany(query, batch)
                    conn.commit()
                    
                    batch_time = time.time() - start_time
                    total_time += batch_time
                    print(f"Вставлено {i + len(batch)}/{len(data)} записей. Время: {batch_time:.2f} сек")
                
                print(f"Общее время вставки в {table_name}: {total_time:.2f} сек")
                return total_time
    
    def create_indexes(self):
        """Создание индексов для секционированной таблицы"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                # Индекс по дате сеанса (ключ секционирования)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_partitioned_session_date 
                    ON orders_partitioned (session_date);
                """)
                
                # Индекс по фильму
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_partitioned_movie 
                    ON orders_partitioned (movie);
                """)
                
                # Индекс по клиенту
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_partitioned_customer 
                    ON orders_partitioned (customer);
                """)
                
                # Составной индекс для часто используемых запросов
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_partitioned_movie_date 
                    ON orders_partitioned (movie, session_date);
                """)
                
                conn.commit()
                print("Индексы для секционированной таблицы созданы успешно")
    
    def create_single_table_indexes(self):
        """Создание индексов для обычной таблицы"""
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_session_date 
                    ON orders (session_date);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_movie 
                    ON orders (movie);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_customer 
                    ON orders (customer);
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_movie_date 
                    ON orders (movie, session_date);
                """)
                
                conn.commit()
                print("Индексы для обычной таблицы созданы успешно")

class PerformanceTester:
    def __init__(self, db):
        self.db = db
    
    def measure_query_time(self, query, description, params=None, is_select=True):
        """Измерение времени выполнения запроса"""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                start_time = time.time()
                cur.execute(query, params or ())
                
                if is_select:
                    results = cur.fetchall()
                    execution_time = time.time() - start_time
                    print(f"{description}: {execution_time:.4f} сек, строк: {len(results)}")
                    return execution_time, results
                else:
                    # Для не-SELECT запросов (DELETE, UPDATE, etc.)
                    conn.commit()
                    execution_time = time.time() - start_time
                    print(f"{description}: {execution_time:.4f} сек")
                    return execution_time, None
    
    def _setup_delete_test_tables(self):
        """Создание временных таблиц для теста удаления с правильным секционированием"""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                # Удаляем существующие временные таблицы
                cur.execute("DROP TABLE IF EXISTS orders_delete_test CASCADE")
                cur.execute("DROP TABLE IF EXISTS orders_partitioned_delete_test CASCADE")
                
                # Создаем обычную таблицу для теста
                cur.execute("CREATE TABLE orders_delete_test AS SELECT * FROM orders")
                
                # Создаем секционированную таблицу для теста с правильной структурой
                cur.execute("""
                    CREATE TABLE orders_partitioned_delete_test (
                        id SERIAL,
                        order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        session_date TIMESTAMP NOT NULL,
                        customer VARCHAR(100) NOT NULL,
                        movie VARCHAR(200) NOT NULL,
                        quantity INT NOT NULL CHECK (quantity > 0),
                        price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
                        PRIMARY KEY (id, session_date)
                    ) PARTITION BY RANGE (session_date);
                """)
                
                # Создаем секции для временной таблицы
                for year in [2023]:
                    for month in range(1, 13):
                        partition_name = f"orders_delete_{year}_{month:02d}"
                        start_date = f"{year}-{month:02d}-01"
                        if month == 12:
                            end_date = f"{year+1}-01-01"
                        else:
                            end_date = f"{year}-{month+1:02d}-01"
                        
                        cur.execute(f"""
                            CREATE TABLE {partition_name}
                            PARTITION OF orders_partitioned_delete_test
                            FOR VALUES FROM ('{start_date}') TO ('{end_date}')
                        """)
                
                # Вставляем данные во временную секционированную таблицу
                print("Заполнение временной секционированной таблицы...")
                cur.execute("""
                    INSERT INTO orders_partitioned_delete_test 
                    (order_date, session_date, customer, movie, quantity, price)
                    SELECT order_date, session_date, customer, movie, quantity, price 
                    FROM orders_partitioned
                """)
                
                conn.commit()
                print("Временные таблицы для теста удаления созданы успешно")
    
    def run_performance_tests(self):
        """Запуск тестов производительности"""
        print("\n" + "="*60)
        print("ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("="*60)
        
        results = []
        
        # Тест 1: Запрос по диапазону дат
        print(f"\n--- Тест 1: Запрос по дате сеанса (один месяц) ---")
        time_ordinary, result_ordinary = self.measure_query_time(
            "SELECT COUNT(*) FROM orders WHERE session_date >= '2023-06-01' AND session_date < '2023-07-01'",
            "Обычная таблица"
        )
        
        time_partitioned, result_partitioned = self.measure_query_time(
            "SELECT COUNT(*) FROM orders_partitioned WHERE session_date >= '2023-06-01' AND session_date < '2023-07-01'",
            "Секционированная таблица"
        )
        
        speedup = time_ordinary / time_partitioned if time_partitioned > 0 else 0
        results.append({
            'test': 'Запрос по дате сеанса',
            'ordinary': time_ordinary,
            'partitioned': time_partitioned,
            'speedup': speedup
        })
        print(f"Ускорение: {speedup:.2f}x")
        
        # Тест 2: Агрегация по месяцам
        print(f"\n--- Тест 2: Агрегация по месяцам ---")
        time_ordinary, result_ordinary = self.measure_query_time(
            """
            SELECT 
                DATE_TRUNC('month', session_date) as month,
                COUNT(*) as total_orders,
                SUM(quantity) as total_tickets,
                SUM(price) as total_revenue
            FROM orders 
            WHERE session_date >= '2023-01-01' AND session_date < '2024-01-01'
            GROUP BY DATE_TRUNC('month', session_date)
            ORDER BY month
            """,
            "Обычная таблица"
        )
        
        time_partitioned, result_partitioned = self.measure_query_time(
            """
            SELECT 
                DATE_TRUNC('month', session_date) as month,
                COUNT(*) as total_orders,
                SUM(quantity) as total_tickets,
                SUM(price) as total_revenue
            FROM orders_partitioned 
            WHERE session_date >= '2023-01-01' AND session_date < '2024-01-01'
            GROUP BY DATE_TRUNC('month', session_date)
            ORDER BY month
            """,
            "Секционированная таблица"
        )
        
        speedup = time_ordinary / time_partitioned if time_partitioned > 0 else 0
        results.append({
            'test': 'Агрегация по месяцам',
            'ordinary': time_ordinary,
            'partitioned': time_partitioned,
            'speedup': speedup
        })
        print(f"Ускорение: {speedup:.2f}x")
        
        # Тест 3: Поиск по фильму с фильтром по дате
        print(f"\n--- Тест 3: Поиск по фильму с фильтром по дате ---")
        time_ordinary, result_ordinary = self.measure_query_time(
            "SELECT COUNT(*) FROM orders WHERE movie = 'Дюна' AND session_date >= '2023-01-01'",
            "Обычная таблица"
        )
        
        time_partitioned, result_partitioned = self.measure_query_time(
            "SELECT COUNT(*) FROM orders_partitioned WHERE movie = 'Дюна' AND session_date >= '2023-01-01'",
            "Секционированная таблица"
        )
        
        speedup = time_ordinary / time_partitioned if time_partitioned > 0 else 0
        results.append({
            'test': 'Поиск по фильму',
            'ordinary': time_ordinary,
            'partitioned': time_partitioned,
            'speedup': speedup
        })
        print(f"Ускорение: {speedup:.2f}x")
        
        # Тест 4: Удаление старых данных
        print(f"\n--- Тест 4: Удаление старых данных ---")
        self._setup_delete_test_tables()
        
        # Тестируем удаление на временных таблицах
        time_ordinary, _ = self.measure_query_time(
            "DELETE FROM orders_delete_test WHERE session_date < '2023-04-01'",
            "Обычная таблица",
            is_select=False
        )
        
        # Для секционированной таблицы используем DETACH PARTITION вместо DELETE
        start_time = time.time()
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                # Отсоединяем секции за первые 3 месяца 2023 года
                for month in range(1, 4):
                    partition_name = f"orders_delete_2023_{month:02d}"
                    cur.execute(f"""
                        ALTER TABLE orders_partitioned_delete_test 
                        DETACH PARTITION {partition_name}
                    """)
                conn.commit()
        
        time_partitioned = time.time() - start_time
        print(f"Секционированная таблица (DETACH): {time_partitioned:.4f} сек")
        
        speedup = time_ordinary / time_partitioned if time_partitioned > 0 else 0
        results.append({
            'test': 'Удаление данных',
            'ordinary': time_ordinary,
            'partitioned': time_partitioned,
            'speedup': speedup
        })
        print(f"Ускорение: {speedup:.2f}x")
        
        # Тест 5: Вставка новых данных
        print(f"\n--- Тест 5: Вставка новых данных ---")
        
        # Генерируем небольшой набор данных для теста вставки
        test_data = []
        base_date = datetime(2023, 6, 1)
        for i in range(1000):
            session_date = base_date + timedelta(days=random.randint(0, 30))
            order_date = session_date - timedelta(days=random.randint(1, 10))
            test_data.append((
                order_date, session_date, fake.name(), 
                "Тестовый фильм", random.randint(1, 5), round(random.uniform(5.0, 15.0), 2)
            ))
        
        # Тест вставки в обычную таблицу
        start_time = time.time()
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO orders_delete_test (order_date, session_date, customer, movie, quantity, price) VALUES (%s, %s, %s, %s, %s, %s)",
                    test_data
                )
                conn.commit()
        time_ordinary = time.time() - start_time
        print(f"Обычная таблица: {time_ordinary:.4f} сек")
        
        # Тест вставки в секционированную таблицу
        start_time = time.time()
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO orders_partitioned_delete_test (order_date, session_date, customer, movie, quantity, price) VALUES (%s, %s, %s, %s, %s, %s)",
                    test_data
                )
                conn.commit()
        time_partitioned = time.time() - start_time
        print(f"Секционированная таблица: {time_partitioned:.4f} сек")
        
        speedup = time_ordinary / time_partitioned if time_partitioned > 0 else 0
        results.append({
            'test': 'Вставка данных',
            'ordinary': time_ordinary,
            'partitioned': time_partitioned,
            'speedup': speedup
        })
        print(f"Ускорение: {speedup:.2f}x")
        
        return results

class DatabaseMaintenance:
    def __init__(self, db):
        self.db = db
    
    def get_partition_list(self):
        """Получение списка всех секций"""
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT inhrelid::regclass::text 
                    FROM pg_inherits 
                    WHERE inhparent = 'orders_partitioned'::regclass
                    ORDER BY inhrelid::regclass::text
                """)
                return [row[0] for row in cur.fetchall()]
    
    def reindex_partitions(self):
        """Переиндексация всех секций"""
        partitions = self.get_partition_list()
        
        print(f"Найдено {len(partitions)} секций для переиндексации")
        
        total_time = 0
        for partition_name in partitions:
            print(f"Переиндексация секции: {partition_name}")
            
            start_time = time.time()
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"REINDEX TABLE {partition_name}")
                    conn.commit()
            
            reindex_time = time.time() - start_time
            total_time += reindex_time
            print(f"Секция {partition_name} переиндексирована за {reindex_time:.2f} сек")
        
        print(f"Общее время переиндексации: {total_time:.2f} сек")
    
    def vacuum_analyze_partitions(self):
        """VACUUM ANALYZE для отдельных секций"""
        partitions = self.get_partition_list()
        
        print(f"Выполнение VACUUM ANALYZE для {len(partitions)} секций...")
        
        total_time = 0
        for partition_name in partitions:
            print(f"VACUUM ANALYZE для секции: {partition_name}")
            
            start_time = time.time()
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"VACUUM ANALYZE {partition_name}")
                    conn.commit()
            
            vacuum_time = time.time() - start_time
            total_time += vacuum_time
            print(f"Секция {partition_name} обработана за {vacuum_time:.2f} сек")
        
        print(f"Общее время VACUUM ANALYZE: {total_time:.2f} сек")
    
    def simulate_partition_loss_and_recovery(self):
        """Симуляция потери секции и восстановления"""
        print("\n" + "="*60)
        print("СИМУЛЯЦИЯ ПОТЕРИ И ВОССТАНОВЛЕНИЯ СЕКЦИИ")
        print("="*60)
        
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                try:
                    # Выбираем секцию для теста (июнь 2023)
                    test_partition = "orders_2023_06"
                    backup_table = "orders_2023_06_backup"
                    
                    print(f"1. Создание резервной копии секции {test_partition}...")
                    cur.execute(f"DROP TABLE IF EXISTS {backup_table}")
                    cur.execute(f"""
                        CREATE TABLE {backup_table} AS 
                        SELECT * FROM {test_partition}
                    """)
                    
                    # Сохраняем количество записей для проверки
                    cur.execute(f"SELECT COUNT(*) FROM {backup_table}")
                    backup_count = cur.fetchone()[0]
                    print(f"   Резервная копия содержит {backup_count} записей")
                    
                    print("2. Отсоединение секции (симуляция потери)...")
                    cur.execute(f"""
                        ALTER TABLE orders_partitioned 
                        DETACH PARTITION {test_partition}
                    """)
                    
                    # Проверяем, что данные недоступны
                    cur.execute("""
                        SELECT COUNT(*) FROM orders_partitioned 
                        WHERE session_date >= '2023-06-01' AND session_date < '2023-07-01'
                    """)
                    count_after_detach = cur.fetchone()[0]
                    print(f"   Данные за июнь 2023 после отсоединения: {count_after_detach} записей")
                    
                    print("3. Восстановление секции из резервной копии...")
                    
                    # Создаем новую секцию
                    new_partition_name = "orders_2023_06_restored"
                    cur.execute(f"DROP TABLE IF EXISTS {new_partition_name} CASCADE")
                    
                    cur.execute(f"""
                        CREATE TABLE {new_partition_name}
                        PARTITION OF orders_partitioned
                        FOR VALUES FROM ('2023-06-01') TO ('2023-07-01')
                    """)
                    
                    # Вставляем данные из резервной копии
                    cur.execute(f"""
                        INSERT INTO {new_partition_name} 
                        SELECT * FROM {backup_table}
                    """)
                    
                    # Проверяем восстановление
                    cur.execute("""
                        SELECT COUNT(*) FROM orders_partitioned 
                        WHERE session_date >= '2023-06-01' AND session_date < '2023-07-01'
                    """)
                    count_after_restore = cur.fetchone()[0]
                    
                    # Создаем индексы для восстановленной секции
                    print("4. Создание индексов для восстановленной секции...")
                    cur.execute(f"""
                        CREATE INDEX ON {new_partition_name} (session_date)
                    """)
                    cur.execute(f"""
                        CREATE INDEX ON {new_partition_name} (movie)
                    """)
                    
                    # Удаляем резервную копию
                    cur.execute(f"DROP TABLE {backup_table}")
                    
                    conn.commit()
                    
                    print(f"   Данные после восстановления: {count_after_restore} записей")
                    print("   ✅ Секция успешно восстановлена!")
                    
                    # Проверяем, что данные корректны
                    if count_after_restore == backup_count:
                        print("   ✅ Проверка целостности данных: УСПЕШНО")
                    else:
                        print(f"   ⚠️  Проверка целостности: расхождение ({backup_count} vs {count_after_restore})")
                    
                except Exception as e:
                    print(f"   ❌ Ошибка при симуляции восстановления: {e}")
                    conn.rollback()
                    raise

def main():
    try:
        # Инициализация базы данных
        db = CinemaDatabase()
        
        # Создание таблиц
        print("Создание таблиц...")
        db.create_tables()
        db.create_partitions()
        
        # Генерация тестовых данных (уменьшим объем для быстрого тестирования)
        print("Генерация тестовых данных...")
        sample_data = db.generate_sample_data(50000)  # 50,000 записей
        
        # Вставка данных
        print("\nВставка данных в обычную таблицу...")
        ordinary_time = db.insert_data("orders", sample_data, batch_size=2000)
        
        print("\nВставка данных в секционированную таблицу...")
        partitioned_time = db.insert_data("orders_partitioned", sample_data, batch_size=2000)
        
        # Создание индексов
        print("\nСоздание индексов...")
        db.create_single_table_indexes()
        db.create_indexes()
        
        # Тестирование производительности
        tester = PerformanceTester(db)
        results = tester.run_performance_tests()
        
        # Вывод результатов
        print("\n" + "="*60)
        print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("="*60)
        for result in results:
            print(f"{result['test']}:")
            print(f"  Обычная таблица: {result['ordinary']:.4f} сек")
            print(f"  Секционированная: {result['partitioned']:.4f} сек")
            print(f"  Ускорение: {result['speedup']:.2f}x")
            print()
        
        # Обслуживание базы данных
        maintenance = DatabaseMaintenance(db)
        
        print("\nОбслуживание базы данных...")
        maintenance.vacuum_analyze_partitions()
        maintenance.reindex_partitions()
        
        # Симуляция восстановления
        maintenance.simulate_partition_loss_and_recovery()
        
        # Анализ преимуществ
        analyze_advantages()
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()

def analyze_advantages():
    """Анализ преимуществ секционирования"""
    advantages = """
    АНАЛИЗ ПРЕИМУЩЕСТВ TABLE PARTITIONING:

    1. 🚀 ПРОИЗВОДИТЕЛЬНОСТЬ ЗАПРОСОВ:
       - Partition Pruning: PostgreSQL автоматически исключает нерелевантные секции
       - Ускорение в 2-10 раз для запросов по диапазону дат
       - Эффективное использование кэша для небольших индексов

    2. 🗂️ УПРАВЛЕНИЕ ДАННЫМИ:
       - Мгновенное удаление через DETACH PARTITION вместо медленного DELETE
       - Архивирование данных по секциям без остановки БД
       - Разные стратегии хранения для "горячих" и "холодных" данных

    3. ⚡ ПАРАЛЛЕЛЬНАЯ ОБРАБОТКА:
       - Запросы выполняются параллельно по разным секциям
       - Улучшенная производительность на многопроцессорных системах
       - Минимальные блокировки при конкурентном доступе

    4. 📊 ОПТИМИЗАЦИЯ ИНДЕКСОВ:
       - Индексы в 10-100 раз меньше = сверхбыстрый поиск
       - Переиндексация отдельных секций вместо всей таблицы
       - Локальные индексы для специфичных запросов

    5. 🛡️ ОТКАЗОУСТОЙЧИВОСТЬ:
       - Восстановление отдельных секций без простоя всей системы
       - Изоляция повреждений данных в одной секции
       - Точечное резервное копирование по секциям

    6. 🔧 ОБСЛУЖИВАНИЕ:
       - VACUUM и ANALYZE выполняются в 10-100 раз быстрее
       - REINDEX для отдельных секций вместо всей таблицы
       - Минимальное влияние на работу приложения

    7. 📈 МАСШТАБИРУЕМОСТЬ:
       - Поддержка терабайтов данных без деградации производительности
       - Простое добавление новых секций для будущих периодов
       - Гибкое распределение по табличным пространствам
    """
    print(advantages)

if __name__ == "__main__":
    main()
