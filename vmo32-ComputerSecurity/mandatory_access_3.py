import random


class MandatoryAccessSystem:
    def __init__(self):
        # Пользователи-субъекты
        self.users = ['USER', 'USER2', 'Gianni090', 'Alice']
        self.current_user = None

        # Количество объектов доступа
        self.num_objects = 4

        # Уровни безопасности:
        # 0 - Открытые данные
        # 1 - Секретно
        # 2 - Совершенно секретно
        self.security_levels = {
            0: "Открытые данные",
            1: "Секретно",
            2: "Совершенно секретно"
        }

        # Вектор уровней конфиденциальности объектов O
        self.object_levels = self.create_object_levels()

        # Вектор уровней допуска пользователей S
        self.user_levels = self.create_user_levels()

    def create_object_levels(self):
        return [random.randint(0, 2) for _ in range(self.num_objects)]

    def create_user_levels(self):
        return {user: random.randint(0, 2) for user in self.users}

    def login(self, username):
        if username in self.users:
            self.current_user = username
            return True
        return False

    def print_system_info(self):
        print("=== МАНДАТНАЯ МОДЕЛЬ ПОЛИТИКИ БЕЗОПАСНОСТИ ===\n")

        print("Уровни конфиденциальности объектов (O):")
        for i in range(self.num_objects):
            print(f"Объект_{i + 1}: {self.security_levels[self.object_levels[i]]}")

        print("\nУровни допуска пользователей (S):")
        for user in self.users:
            print(f"{user}: {self.security_levels[self.user_levels[user]]}")
        print()

    def get_accessible_objects(self, username):
        user_level = self.user_levels[username]
        accessible = []

        for i in range(self.num_objects):
            object_level = self.object_levels[i]
            if user_level >= object_level:
                accessible.append(f"Объект_{i + 1}")

        return accessible

    def request_access(self, object_num):
        obj_index = object_num - 1

        if not (0 <= obj_index < self.num_objects):
            print("Неверный номер объекта")
            return

        user_level = self.user_levels[self.current_user]
        object_level = self.object_levels[obj_index]

        if user_level >= object_level:
            print("Операция прошла успешно")
        else:
            print("Отказ в выполнении операции. Недостаточно прав.")

    def run(self):
        self.print_system_info()

        while True:
            username = input("User: ").strip()

            if self.login(username):
                print("Идентификация прошла успешно, добро пожаловать в систему")

                accessible_objects = self.get_accessible_objects(username)

                if accessible_objects:
                    print("Перечень доступных объектов:", ", ".join(accessible_objects))
                else:
                    print("Перечень доступных объектов: нет доступных объектов")
            else:
                print("Пользователь не найден. Попробуйте снова.\n")
                continue

            while True:
                command = input("Жду ваших указаний > ").strip().lower()

                if command == "quit":
                    print(f"Работа пользователя {self.current_user} завершена. До свидания.\n")
                    self.current_user = None
                    break

                elif command == "request":
                    try:
                        object_num = int(input("К какому объекту хотите осуществить доступ? "))
                        self.request_access(object_num)
                    except ValueError:
                        print("Неверный ввод. Нужно ввести номер объекта.")

                else:
                    print("Неизвестная команда. Доступные команды: request, quit")


if __name__ == "__main__":
    system = MandatoryAccessSystem()
    system.run()