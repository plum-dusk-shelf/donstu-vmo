# ЗАМЕНИ ИМЯ ФАЙЛА НА СВОЕ
from mandatory_access_3 import MandatoryAccessSystem


def print_step(step_num, text):
    print("\n" + "=" * 72)
    print(f"Шаг {step_num}. {text}")
    print("=" * 72)


def print_user_block(username):
    print("\n" + "#" * 72)
    print(f"Демонстрация пользователя: {username}")
    print("#" * 72)


def simulate_login(system, username):
    print(f"User: {username}")

    if system.login(username):
        print("Идентификация прошла успешно, добро пожаловать в систему")

        accessible_objects = system.get_accessible_objects(username)
        if accessible_objects:
            print("Перечень доступных объектов:", ", ".join(accessible_objects))
        else:
            print("Перечень доступных объектов: нет доступных объектов")

        return True
    else:
        print("Пользователь не найден. Попробуйте снова.\n")
        return False


def simulate_command(system, command, object_value=None):
    print(f"Жду ваших указаний > {command}")

    if command == "quit":
        print(f"Работа пользователя {system.current_user} завершена. До свидания.\n")
        system.current_user = None
        return

    if command == "request":
        print(f"К какому объекту хотите осуществить доступ? {object_value}")
        try:
            object_num = int(object_value)
            system.request_access(object_num)
        except ValueError:
            print("Неверный ввод. Нужно ввести номер объекта.")
        return

    print("Неизвестная команда. Доступные команды: request, quit")


def run_demo():
    system = MandatoryAccessSystem()

    # Фиксируем уровни, чтобы демонстрация всегда была одинаковой
    # Объекты:
    # 1 -> Открытые данные
    # 2 -> Секретно
    # 3 -> Совершенно секретно
    # 4 -> Секретно
    system.object_levels = [0, 1, 2, 1]

    # Пользователи:
    # USER -> Совершенно секретно
    # USER2-> Секретно
    # Gianni090 -> Открытые данные
    # Alice -> Совершенно секретно
    system.user_levels = {
        "USER": 2,
        "USER2": 1,
        "Gianni090": 0,
        "Alice": 2
    }

    print_step(1, "Вывод общей информации о системе")
    system.print_system_info()

    print_step(2, "Проверка входа несуществующего пользователя")
    simulate_login(system, "UnknownUser")

    print_user_block("USER")
    print_step(3, "Вход администратора уровня 'Совершенно секретно'")
    if simulate_login(system, "USER"):
        print_step(4, "Запрос доступа к открытому объекту")
        simulate_command(system, "request", 1)

        print_step(5, "Запрос доступа к секретному объекту")
        simulate_command(system, "request", 2)

        print_step(6, "Запрос доступа к совершенно секретному объекту")
        simulate_command(system, "request", 3)

        print_step(7, "Запрос доступа к объекту с неверным номером")
        simulate_command(system, "request", 9)

        print_step(8, "Ввод неизвестной команды")
        simulate_command(system, "hello")

        print_step(9, "Завершение работы пользователя USER")
        simulate_command(system, "quit")

    print_user_block("USER2")
    print_step(10, "Вход пользователя уровня 'Секретно'")
    if simulate_login(system, "USER2"):
        print_step(11, "Запрос доступа к открытому объекту")
        simulate_command(system, "request", 1)

        print_step(12, "Запрос доступа к секретному объекту")
        simulate_command(system, "request", 2)

        print_step(13, "Запрос доступа к совершенно секретному объекту — должен быть отказ")
        simulate_command(system, "request", 3)

        print_step(14, "Запрос доступа к объекту 4")
        simulate_command(system, "request", 4)

        print_step(15, "Проверка ошибки формата ввода")
        simulate_command(system, "request", "abc")

        print_step(16, "Завершение работы пользователя USER2")
        simulate_command(system, "quit")

    print_user_block("Gianni090")
    print_step(17, "Вход пользователя уровня 'Открытые данные'")
    if simulate_login(system, "Gianni090"):
        print_step(18, "Запрос доступа к открытому объекту")
        simulate_command(system, "request", 1)

        print_step(19, "Запрос доступа к секретному объекту — должен быть отказ")
        simulate_command(system, "request", 2)

        print_step(20, "Запрос доступа к совершенно секретному объекту — должен быть отказ")
        simulate_command(system, "request", 3)

        print_step(21, "Завершение работы пользователя Gianni090")
        simulate_command(system, "quit")

    print_user_block("Alice")
    print_step(22, "Вход пользователя уровня 'Совершенно секретно'")
    if simulate_login(system, "Alice"):
        print_step(23, "Запрос доступа к открытому объекту")
        simulate_command(system, "request", 1)

        print_step(24, "Запрос доступа к секретному объекту")
        simulate_command(system, "request", 2)

        print_step(25, "Запрос доступа к совершенно секретному объекту")
        simulate_command(system, "request", 3)

        print_step(26, "Завершение работы пользователя Alice")
        simulate_command(system, "quit")

    print_step(27, "Итог демонстрации")
    print("Проверены все основные ветви работы программы:")
    print("- вывод информации о системе")
    print("- успешный вход")
    print("- неуспешный вход")
    print("- определение доступных объектов")
    print("- успешный запрос доступа")
    print("- отказ в доступе при недостаточном уровне допуска")
    print("- ошибка при неверном номере объекта")
    print("- ошибка при неверном формате ввода")
    print("- ошибка при неизвестной команде")
    print("- завершение работы пользователя")


if __name__ == "__main__":
    run_demo()