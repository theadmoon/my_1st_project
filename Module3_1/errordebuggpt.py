 ```python
@bot.message_handler(func=continue_filter)
def get_promt(message):
    user_id = message.from_user.id

    if not message.text:
        bot.send_message(message.chat.id, "Необходимо отправить именно текстовое сообщение")
        bot.register_next_step_handler(message, get_promt)
        return

    # Проверка задачи пользователя на количество токенов. Если количество символов больше - сообщение об ошибке пользователю
    if gpt.count_tokens(user_request) >= gpt.MAX_TOKENS:
        bot.send_message(user_id, "Запрос превышает количество символов\nИсправь запрос")
        bot.register_next_step_handler(message, get_promt)
        return

    user_request = message.text

    # Проверка: если у пользователя нет начатой задачи, тогда ее нужно начать
    if user_id not in users_history or users_history[user_id] == {}:
        if user_request == "Продолжить решение":
            bot.send_message(message.chat.id, "Кажется, вы еще не задали вопрос.")
            bot.register_next_step_handler(message, get_promt)
            return
        # Сохраняем промт пользователя и начало ответа GPT в словарик users_history
        users_history[user_id] = {
            'system_content': (
                "Ты бот."
                "Опиши аллергенную обстановку от 1 до 10."),
            'user_content': user_request,
            'assistant_content': "Пишем отчет: "
        }
        save_to_json()

    # Пока что ответом от GPT будет любой текст, просто придумай его)
    # answer = "Позже здесь будет реальное решение, а пока что так :)"
    prompt = gpt.make_promt(users_history[user_id])
    resp = gpt.send_request(prompt)
    answer = resp.json()['choices'][0]['message']['content']

    users_history[user_id]["assistant_content"] += answer
    save_to_json()

    keyboard = create_keyboard(["Продолжить решение", "Завершить решение"])
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)
```

В этой версии функции `get_promt`, перед получением текста сообщения из аргументов (`user_request = message.text`),
 добавлена проверка на пустоту этого текста:

```python
if not message.text:
    bot.send_message(message.chat.id, "Необходимо отправить именно текстовое сообщение")
    bot.register_next_step_handler(message, get_promt)
```

Если текст пуст, то функция `get_promt` будет отправлять пользователю сообщение с просьбой отправить текстовое сообщение
 и запускать себя вновь как следующий обработчик событий. Это поможет избежать ошибки,
 когда пользователь пытается нажать кнопку "Завершить решение" без предварительного выполнения задания.