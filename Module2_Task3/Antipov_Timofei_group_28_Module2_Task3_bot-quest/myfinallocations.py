locations_data = {
  "start":
    {
      "description": "Добро пожаловать в игру! Цель игры - дойти до конца квеста живым!",
      "actions": {"Начать игру": "entrance-1"},
      "picture": "pictures/gamebegins.jpg"
    },
  "entrance-1":
    {
      "description": "Ты находишься в школе магии. Что будешь делать?",
      "actions":{
        "Учиться": "entrance-2.1",
        "Практиковаться": "entrance-2.2",
        "Колдовать": "entrance-2.3"
      },
      "picture": "pictures/magicianschool.jpg"
    },
  "entrance-2.1":
    {
      "description": "Ого! Ты - в замке магов. Каков твой выбор?",
      "actions": {
        "устроиться помощником мага": "entrance-3.1",
        "сразиться с нечестью": "entrance-3.2"
      },
      "picture": "pictures/magiciancastle.jpg"
    },
  "entrance-3.1":
    {
      "description": "Вот это да! Ты - в библиотеке колдуна. Скорее приготовь снадобье из книг!",
      "actions": {
        "Готовить снадобье": "entrance-4.1"
      },
      "picture": "pictures/magiclibrary.jpg"
    },
  "entrance-3.2":
    {
      "description": "Тебе предстоит битва в Аду! Отступать поздно",
      "actions": {"Сразиться с дьяволом": "entrance-4.2"},
      "picture": "pictures/hellbattle.jpg"
    },
  "entrance-2.2":
    {
      "description": "Ого! Ты - на складе оружия. Каков твой выбор?",
      "actions": {
        "выбрать пистолет": "entrance-3.3",
        "взять посох": "entrance-3.4"
      },
      "picture": "pictures/weapon.jpg"
    },
  "entrance-3.3":
    {
      "description": "Так так! Ты - посередине поля. Кажется, земля уходит из-под ног!",
      "actions": {
        "Узнай, что принесла битва в поле": "entrance-4.2"
      },
      "picture": "pictures/field.jpg"
    },
  "entrance-3.4":
    {
      "description": "Стихия не на шутку разыгралась! Проверь свои шансы!",
      "actions": {"Сразиться со стихией": "entrance-4.2"},
      "picture": "pictures/storm.jpg"
    },
  "entrance-2.3":
    {
      "description": "Что это??? ААаааа! Это логово дракона, выбор лишь один...",
      "actions": {"попасть на ужин к Дракону": "entrance-4.2"},
      "picture": "pictures/dragon.jpg"
    },
  "entrance-4.1":
    {
      "description": "Это ПОБЕДА!!! Поздравляем! Игра завершена.",
      "actions": {"УРА!!! Попробовать снова": "entrance-1"},
      "picture": "pictures/victory.jpg"
    },
  "entrance-4.2":
    {
      "description": "Победить не удалось, Нам жаль. Игра завершена.",
      "actions": {"Попробовать еще раз": "entrance-1"},
      "picture": "pictures/lost.jpg"
    }
  }
