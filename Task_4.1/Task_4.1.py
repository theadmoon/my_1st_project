import random
magic_digit = random.randint(1,10000)

# Бесконечный цикл, который продолжает выполняться
# до возникновения исключения
while True:

    try:
        user_input = int(input("Введи число. Если задуманное число меньше магического, ты проиграл:\n"))
    # Если полученный ввод не число, будет вызвано исключение
    except ValueError:
        # Цикл будет повторяться до правильного ввода
        print("Error! Это не число, попробуйте снова.")

    # При успешном преобразовании в целое число,
    # цикл закончится.
    else:
        if magic_digit > int(user_input):
            print(f"Магическое число:{magic_digit} больше задуманного: {user_input}, ты проиграл")
        else:
            print(f"Магическое число:{magic_digit} меньше задуманного: {user_input}, ты выиграл")
        break
