contacts = ''' telegram: @kotobormot
email: kot_obormot@mail.ru
'''

about_me = '''Привет, меня зовут Котофей. Я дикий кот. Я помогаю начинающим программистам,
которые учатся на Яндекс.Практикуме. Мой хозяин Тимофей учится познавать ИИ с использованием Python.  
Я люблю мурлыкать и подглядывать за хозяином, когда он кодит'''

projects = {
    "Частушки": {"name": "Частушки_бот",
                 "description": "С помощью этого бота вы сможете с задором прослушивать сообщения.\n"
                                "Бот переделывает сообщения в частушки.\n",
                "link": "@ChastushkiBot"},
    "Ролики": {'name': "Ролики_из_соцсетей",
                "description": "поможет быстро скачать любые файлы (фото, видео или текстовую информацию)\n"
                                " с Pinterest, Instagram и TikTok.\n"
                                "Боту достаточно сообщить ссылку и назад получите готовый файл.\n",
                "link": "@SaveAsBot"},
    'Файлообменник': {"name": "Фалообменник",
                 "description": "Бот дает возможность быстро и просто сохранить нужные фалы\n"
                                "и переслать их другим пользователям без использования других приложений.\n",
                "link": "@filebot"}
}
def show_projects(projects=projects):
    n = 1
    my_projects = "Прикольные проекты:\n\n"
    for name, project in projects.items():
        my_projects +=f"{n}.{name}:{project['link']}\n"
        n += 1
    my_projects +="\n Для получения деталей проекта, введи в чат его название.\n"
    return my_projects

def describe_project(project_name = None, projects = projects):
    if project_name in projects:
        description = f"{project_name}\n{projects[project_name]['description']}\n"
        description += f"Ссылка на проект: {projects[project_name]['link']}\n"
        return description
    else:
        return ""