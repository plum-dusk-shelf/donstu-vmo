import os
import sys
import json
import time
import random
import base64
import statistics

# =========================
# НАСТРОЙКИ ПРОГРАММЫ
# =========================

PHRASES_FILE = "phrases.enc"
USERS_FILE = "users_db.json"
SECRET_KEY = "lab5_keyboard_key"

REGISTRATION_SAMPLES = 4       # сколько раз вводится фраза при регистрации
AUTH_ATTEMPTS = 3              # число попыток входа
LOCK_SECONDS = 15              # блокировка после 3 неудач
IDLE_TIMEOUT = 60              # блокировка сеанса при бездействии, сек

PHRASES = [
    "Qaz7!wsx#12",
    "Go9,Fast!Run",
    "Key3,Lock?Up",
    "Type4.Me!Ok",
    "Net7#Code!Go",
    "Win5,Open!It",
    "Fox8!Jump?Hi",
    "Safe2,Pass!Yo",
    "Data6#Check!",
    "Fast1,Type?Go"
]


# =========================
# РАБОТА С ШИФРОВАНИЕМ ФРАЗ
# =========================

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))


def encrypt_text(text: str, key: str) -> str:
    encrypted = xor_bytes(text.encode("utf-8"), key.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_text(text: str, key: str) -> str:
    raw = base64.b64decode(text.encode("utf-8"))
    decrypted = xor_bytes(raw, key.encode("utf-8"))
    return decrypted.decode("utf-8")


def initialize_files():
    if not os.path.exists(PHRASES_FILE):
        phrases_json = json.dumps(PHRASES, ensure_ascii=False)
        encrypted = encrypt_text(phrases_json, SECRET_KEY)
        with open(PHRASES_FILE, "w", encoding="utf-8") as f:
            f.write(encrypted)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)


def load_phrases():
    with open(PHRASES_FILE, "r", encoding="utf-8") as f:
        encrypted = f.read()
    decrypted = decrypt_text(encrypted, SECRET_KEY)
    return json.loads(decrypted)


def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


# =========================
# СЧИТЫВАНИЕ ПОСИМВОЛЬНОГО ВВОДА
# =========================

if os.name == "nt":
    import msvcrt

    def read_char():
        ch = msvcrt.getwch()
        # специальные клавиши
        if ch in ("\x00", "\xe0"):
            _ = msvcrt.getwch()
            return None, "SPECIAL"
        return ch, None

else:
    import tty
    import termios

    class RawMode:
        def __init__(self, stream):
            self.stream = stream
            self.fd = stream.fileno()
            self.old_settings = None

        def __enter__(self):
            self.old_settings = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)

        def __exit__(self, exc_type, exc_val, exc_tb):
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def read_char():
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            return None, "SPECIAL"
        return ch, None


def forbidden_key(ch):
    if ch is None:
        return True
    if ch in ("\r", "\n", "\t", "\x08", "\x7f"):
        return True
    if ord(ch) < 32:
        return True
    return False


# =========================
# ОСНОВНАЯ ЛОГИКА БИОМЕТРИИ
# =========================

class KeyboardBiometricsSystem:
    def __init__(self):
        initialize_files()
        self.phrases = load_phrases()
        self.users = load_users()
        self.locked_users = {}   # username -> timestamp unlock
        self.current_user = None

    def collect_sample(self, phrase):
        """
        Сбор одного образца клавиатурного почерка:
        - посимвольный ввод
        - измерение времени между нажатиями
        - расчёт среднего и отклонения
        """
        print(f"\nФраза для ввода: {phrase}")
        input("Нажмите Enter и сразу начинайте вводить фразу: ")

        print("Ввод: ", end="", flush=True)

        typed_chars = []
        intervals = []
        prev_time = None

        if os.name == "nt":
            sample = self._collect_sample_windows(phrase, typed_chars, intervals, prev_time)
        else:
            sample = self._collect_sample_unix(phrase, typed_chars, intervals, prev_time)

        return sample

    def _collect_sample_windows(self, phrase, typed_chars, intervals, prev_time):
        for _ in range(len(phrase)):
            ch, error = read_char()

            if error or forbidden_key(ch):
                print("\nСлужебные клавиши и Backspace использовать нельзя. Повторите ввод.")
                return None

            now = time.perf_counter()
            if prev_time is not None:
                intervals.append((now - prev_time) * 1000.0)
            prev_time = now

            typed_chars.append(ch)
            print(ch, end="", flush=True)

        print()

        typed_text = "".join(typed_chars)
        mean_interval, deviation = self.calculate_metrics(intervals)

        return {
            "text": typed_text,
            "mean_interval": mean_interval,
            "deviation": deviation
        }

    def _collect_sample_unix(self, phrase, typed_chars, intervals, prev_time):
        with RawMode(sys.stdin):
            for _ in range(len(phrase)):
                ch, error = read_char()

                if error or forbidden_key(ch):
                    print("\nСлужебные клавиши и Backspace использовать нельзя. Повторите ввод.")
                    return None

                now = time.perf_counter()
                if prev_time is not None:
                    intervals.append((now - prev_time) * 1000.0)
                prev_time = now

                typed_chars.append(ch)
                print(ch, end="", flush=True)

        print()

        typed_text = "".join(typed_chars)
        mean_interval, deviation = self.calculate_metrics(intervals)

        return {
            "text": typed_text,
            "mean_interval": mean_interval,
            "deviation": deviation
        }

    def calculate_metrics(self, intervals):
        if not intervals:
            return 0.0, 0.0

        mean_interval = statistics.fmean(intervals)
        deviation = statistics.fmean(abs(x - mean_interval) for x in intervals)
        return mean_interval, deviation

    def register_user(self):
        username = input("\nВведите имя нового пользователя: ").strip()

        if not username:
            print("Имя пользователя не может быть пустым.")
            return

        if username in self.users:
            print("Такой пользователь уже существует.")
            return

        phrase_id = random.randint(0, len(self.phrases) - 1)
        phrase = self.phrases[phrase_id]

        print("\n=== РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ ===")
        print(f"Пользователю назначена фраза: {phrase}")
        print(f"Нужно ввести её {REGISTRATION_SAMPLES} раза без ошибок.\n")

        means = []
        deviations = []
        success_samples = 0

        while success_samples < REGISTRATION_SAMPLES:
            print(f"Попытка регистрации {success_samples + 1} из {REGISTRATION_SAMPLES}")
            sample = self.collect_sample(phrase)

            if sample is None:
                continue

            if sample["text"] != phrase:
                print("Фраза введена неверно. Эта попытка не засчитана.\n")
                continue

            means.append(sample["mean_interval"])
            deviations.append(sample["deviation"])
            success_samples += 1
            print("Попытка успешно сохранена.\n")

        profile_mean = statistics.fmean(means)
        profile_deviation = statistics.fmean(deviations)

        mean_spread = statistics.fmean(abs(x - profile_mean) for x in means)
        deviation_spread = statistics.fmean(abs(x - profile_deviation) for x in deviations)

        # Допуски (погрешности)
        eps_mean = max(60.0, mean_spread * 3 + 20.0)
        eps_deviation = max(40.0, deviation_spread * 3 + 15.0)

        self.users[username] = {
            "phrase_id": phrase_id,
            "mean_interval": round(profile_mean, 3),
            "deviation": round(profile_deviation, 3),
            "eps_mean": round(eps_mean, 3),
            "eps_deviation": round(eps_deviation, 3)
        }

        save_users(self.users)

        print("Пользователь успешно зарегистрирован.")
        print(f"Среднее значение: {profile_mean:.2f} мс")
        print(f"Среднее отклонение: {profile_deviation:.2f} мс")
        print(f"Допуск по среднему: ±{eps_mean:.2f} мс")
        print(f"Допуск по отклонению: ±{eps_deviation:.2f} мс\n")

    def is_locked(self, username):
        if username not in self.locked_users:
            return False

        unlock_time = self.locked_users[username]
        if time.time() >= unlock_time:
            del self.locked_users[username]
            return False
        return True

    def authenticate_user(self, fixed_username=None):
        if fixed_username is None:
            username = input("\nВведите имя пользователя: ").strip()
        else:
            username = fixed_username

        if username not in self.users:
            print("Пользователь не найден.")
            return False, None

        if self.is_locked(username):
            seconds_left = int(self.locked_users[username] - time.time())
            print(f"Пользователь временно заблокирован. Осталось ждать: {seconds_left} сек.")
            return False, None

        profile = self.users[username]
        phrase = self.phrases[profile["phrase_id"]]

        print("\n=== АВТОРИЗАЦИЯ ===")
        print("Нужно правильно ввести закреплённую фразу.")
        print("Также будет проверяться клавиатурный почерк.\n")

        for attempt in range(1, AUTH_ATTEMPTS + 1):
            print(f"Попытка входа {attempt} из {AUTH_ATTEMPTS}")
            sample = self.collect_sample(phrase)

            if sample is None:
                print("Попытка не пройдена.\n")
                continue

            if sample["text"] != phrase:
                print("Неверная фраза.\n")
                continue

            mean_ok = abs(sample["mean_interval"] - profile["mean_interval"]) <= profile["eps_mean"]
            deviation_ok = abs(sample["deviation"] - profile["deviation"]) <= profile["eps_deviation"]

            if mean_ok and deviation_ok:
                print("Идентификация прошла успешно, доступ разрешён.\n")
                self.current_user = username
                return True, username
            else:
                print("Фраза верна, но клавиатурный почерк не совпал.\n")

        self.locked_users[username] = time.time() + LOCK_SECONDS
        print(f"Превышено число попыток. Пользователь заблокирован на {LOCK_SECONDS} секунд.\n")
        return False, None

    def protected_session(self, username):
        print(f"Добро пожаловать, {username}.")
        print("Доступ к программе разрешён.")

        last_prompt_time = time.time()

        while True:
            print("\n1 - Выполнить защищённое действие")
            print("2 - Выйти из учётной записи")
            command = input("Выберите действие: ").strip()

            now = time.time()

            # Блокировка сеанса при бездействии
            if now - last_prompt_time > IDLE_TIMEOUT:
                print("\nСеанс заблокирован из-за бездействия.")
                ok, _ = self.authenticate_user(fixed_username=username)
                if not ok:
                    print("Повторная авторизация не пройдена. Возврат в главное меню.\n")
                    self.current_user = None
                    return
                last_prompt_time = time.time()
                continue

            last_prompt_time = time.time()

            if command == "1":
                print("Защищённое действие выполнено успешно.")
            elif command == "2":
                print(f"Работа пользователя {username} завершена. До свидания.\n")
                self.current_user = None
                return
            else:
                print("Неизвестная команда.")

    def show_users(self):
        if not self.users:
            print("\nПока нет зарегистрированных пользователей.\n")
            return

        print("\nЗарегистрированные пользователи:")
        for username in self.users:
            print("-", username)
        print()

    def run(self):
        while True:
            print("=== БИОМЕТРИЧЕСКАЯ ЗАЩИТА ПО КЛАВИАТУРНОМУ ПОЧЕРКУ ===")
            print("1 - Регистрация пользователя")
            print("2 - Вход в программу")
            print("3 - Показать зарегистрированных пользователей")
            print("0 - Выход")

            choice = input("Выберите пункт меню: ").strip()

            if choice == "1":
                self.register_user()
            elif choice == "2":
                ok, username = self.authenticate_user()
                if ok:
                    self.protected_session(username)
            elif choice == "3":
                self.show_users()
            elif choice == "0":
                print("Программа завершена.")
                break
            else:
                print("Неверный пункт меню.\n")


if __name__ == "__main__":
    app = KeyboardBiometricsSystem()
    app.run()