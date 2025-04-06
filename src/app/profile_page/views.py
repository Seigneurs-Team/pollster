import json

from django.shortcuts import render
from databases.mysql_db import client_mysqldb

from authentication.check_user_on_auth import authentication_for_profile_page


@authentication_for_profile_page
def request_on_profile_page(requests, id_of_user):
    """
    Функция возвращает страницу пользователя только в том случае, если клиент авторизован в системе

    :param requests:
    :param id_of_user: идентификатор пользователя
    :return: render(requests, 'profile_page.html', context={'user': user, 'tags': tags})
    """
    user_polls = client_mysqldb.get_polls(id_of_user=id_of_user)
    pass_user_polls = client_mysqldb.get_pass_user_polls(id_of_user)

    user_data = client_mysqldb.get_user_data_from_table(id_of_user)
    tags_of_user = json.loads(user_data[4]) if user_data[4] is not None else None
    tags = ['развлечения', 'наука', 'животные', 'кухня', 'искусство',  'дети', 'музыка', 'кино и сериалы', 'путешествия', 'игры', 'мода и стиль', 'здоровье', 'образование']

    if tags_of_user is not None:
        tags = [tag for tag in tags if tag not in tags_of_user]

    user = {'id': id_of_user, 'username': user_data[0], 'email': user_data[1], 'phone': user_data[2], 'date_of_birth': user_data[3], 'tags_of_user': tags_of_user, 'usersPolls': user_polls,  'completedPolls': pass_user_polls}
    return render(requests, 'profile_page.html', context={'user': user, 'tags': tags})

