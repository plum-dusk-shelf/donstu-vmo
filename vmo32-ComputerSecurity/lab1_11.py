import tkinter as tk
from PIL import ImageGrab
from tkinter import ttk

# -----------------------------
# Data for schemes
# -----------------------------

schemes = {
    "Целостность": {
        "Внутренние": {
            "Преднамеренные": [
                "Подмена транзакций",
                "Фальсификация кредитной",
                "Удаление записей",
                "Фиктивные счета",
                "Манипуляция балансами"
            ],
            "Непреднамеренные": [
                "Ошибки ввода",
                "Сбой обновления ПО",
                "Ошибки миграции",
                "Проблемы интеграции",
                "Повреждение БД"
            ]
        },
        "Внешние": {
            "Преднамеренные": [
                "Взлом транзакций",
                "SQL-инъекции",
                "Подмена реквизитов",
                "Атаки на API",
                "Компрометация партнёров"
            ],
            "Непреднамеренные": [
                "Ошибки платёжных систем",
                "Повреждение при передаче",
                "Сбои облака",
                "Проблемы синхронизации",
                "Ошибки внешних сервисов"
            ]
        }
    },
    "Конфиденциальность": {
        "Внутренние": {
            "Преднамеренные": [
                "Утечка данных",
                "Продажа баз",
                "Просмотр VIP",
                "Кража через USB",
                "Передача конкурентам"
            ],
            "Непреднамеренные": [
                "Отправка не туда",
                "Ошибки доступа",
                "Утечки в логах",
                "Потеря ноутбука",
                "Ошибка шифрования"
            ]
        },
        "Внешние": {
            "Преднамеренные": [
                "Фишинг",
                "Взлом интернет-банка",
                "Перехват данных",
                "Вредоносное ПО",
                "Атаки на БД"
            ],
            "Непреднамеренные": [
                "Утечки подрядчиков",
                "Ошибки облака",
                "Публикация данных",
                "Уязвимости ПО",
                "Сбои защиты"
            ]
        }
    },
    "Доступность": {
        "Внутренние": {
            "Преднамеренные": [
                "Саботаж",
                "Удаление сервисов",
                "Блокировка БД",
                "Нарушение серверов",
                "Злоупотребление админом"
            ],
            "Непреднамеренные": [
                "Ошибка конфигурации",
                "Неудачное обновление",
                "Перегрузка",
                "Случайное отключение",
                "Сбой резервного копирования"
            ]
        },
        "Внешние": {
            "Преднамеренные": [
                "DDoS",
                "Блокировка каналов",
                "Ransomware",
                "Атаки на ДЦ",
                "Эксплуатация уязвимостей"
            ],
            "Непреднамеренные": [
                "Сбой провайдера",
                "Отключение питания",
                "Пожары",
                "Отказ оборудования",
                "Сбои внешних сервисов"
            ]
        }
    }
}

# -----------------------------
# Drawing functions
# -----------------------------

def draw_scheme(canvas, scheme_name):
    canvas.delete("all")

    data = schemes[scheme_name]

    # Center node
    canvas.create_oval(750, 20, 950, 80, fill="lightblue")
    canvas.create_text(850, 50, text=scheme_name, font=("Inter", 14, "bold"))

    x_offsets = {"Внутренние": 550, "Внешние": 1150}

    for side, x in x_offsets.items():
        # Side node
        canvas.create_oval(x-100, 120, x+100, 180, fill="lightgray")
        canvas.create_text(x, 150, text=side, font=("Inter", 14))

        canvas.create_line(850, 80, x, 120, arrow=tk.LAST)

        # Разводим по сторонам
        intents = list(data[side].items())

        left_x = x - 200
        right_x = x + 100

        positions = {
            intents[0][0]: left_x,
            intents[1][0]: right_x
        }

        y = 250

        for intent, items in intents:
            ix = positions[intent]

            # Intent node
            canvas.create_oval(ix-120, y, ix+100, y+60, fill="white")
            canvas.create_text(ix, y+30, text=intent, font=("Inter", 14))

            canvas.create_line(x, 180, ix, y, arrow=tk.LAST)

            # Text box
            text = "\n".join([f"{j+1}) {item}" for j, item in enumerate(items)])
            canvas.create_rectangle(ix-150, y+80, ix+150, y+220)
            canvas.create_text(ix, y+150, text=text, width=380, font=("Inter", 13))

            canvas.create_line(ix, y+60, ix, y+80, arrow=tk.LAST)


# -----------------------------
# UI
# -----------------------------

root = tk.Tk()
root.title("Банковская безопасность — схемы")
root.geometry("1900x750")

frame = ttk.Frame(root)
frame.pack(fill=tk.X, pady=5)
selected_scheme = tk.StringVar(value="Целостность")

combo = ttk.Combobox(frame, textvariable=selected_scheme, values=list(schemes.keys()), state="readonly")
combo.pack(side=tk.LEFT, padx=10)

canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)


def update(event=None):
    draw_scheme(canvas, selected_scheme.get())

combo.bind("<<ComboboxSelected>>", update)

# Initial draw
update()
root.mainloop()

