 ```python
@bot.message_handler(func=continue_filter)
def get_promt(message):
    user_id = message.from_user.id

    if not message.text:
        bot.send_message(message.chat.id, "���������� ��������� ������ ��������� ���������")
        bot.register_next_step_handler(message, get_promt)
        return

    # �������� ������ ������������ �� ���������� �������. ���� ���������� �������� ������ - ��������� �� ������ ������������
    if gpt.count_tokens(user_request) >= gpt.MAX_TOKENS:
        bot.send_message(user_id, "������ ��������� ���������� ��������\n������� ������")
        bot.register_next_step_handler(message, get_promt)
        return

    user_request = message.text

    # ��������: ���� � ������������ ��� ������� ������, ����� �� ����� ������
    if user_id not in users_history or users_history[user_id] == {}:
        if user_request == "���������� �������":
            bot.send_message(message.chat.id, "�������, �� ��� �� ������ ������.")
            bot.register_next_step_handler(message, get_promt)
            return
        # ��������� ����� ������������ � ������ ������ GPT � �������� users_history
        users_history[user_id] = {
            'system_content': (
                "�� ���."
                "����� ����������� ���������� �� 1 �� 10."),
            'user_content': user_request,
            'assistant_content': "����� �����: "
        }
        save_to_json()

    # ���� ��� ������� �� GPT ����� ����� �����, ������ �������� ���)
    # answer = "����� ����� ����� �������� �������, � ���� ��� ��� :)"
    prompt = gpt.make_promt(users_history[user_id])
    resp = gpt.send_request(prompt)
    answer = resp.json()['choices'][0]['message']['content']

    users_history[user_id]["assistant_content"] += answer
    save_to_json()

    keyboard = create_keyboard(["���������� �������", "��������� �������"])
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)
```

� ���� ������ ������� `get_promt`, ����� ���������� ������ ��������� �� ���������� (`user_request = message.text`),
 ��������� �������� �� ������� ����� ������:

```python
if not message.text:
    bot.send_message(message.chat.id, "���������� ��������� ������ ��������� ���������")
    bot.register_next_step_handler(message, get_promt)
```

���� ����� ����, �� ������� `get_promt` ����� ���������� ������������ ��������� � �������� ��������� ��������� ���������
 � ��������� ���� ����� ��� ��������� ���������� �������. ��� ������� �������� ������,
 ����� ������������ �������� ������ ������ "��������� �������" ��� ���������������� ���������� �������.