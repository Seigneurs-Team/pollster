import json

from django.shortcuts import render
from databases.mysql_db import client_mysqldb

from authentication.check_user_on_auth import authentication_for_profile_page


@authentication_for_profile_page
def request_on_profile_page(requests, id_of_user):
    user_polls = client_mysqldb.get_polls(id_of_user=id_of_user)
    pass_user_polls = client_mysqldb.get_pass_user_polls(id_of_user)

    user_data = client_mysqldb.get_user_data_from_table(id_of_user)
    tags_of_user = json.loads(user_data[4]) if user_data[4] is not None else None
    tags = {1: 'развлечения',  2: 'наука',  3: 'животные',  4: 'кухня',  5: 'искусство',  6: 'дети',  7: 'музыка',  8: 'кино и сериалы',  9: 'путешествия',  10: 'игры',  11: 'мода и стиль',  12: 'здоровье',  13: 'образование'}

    user = {'id': id_of_user, 'username': user_data[0], 'email': user_data[1], 'phone': user_data[2], 'date_of_birth': user_data[3], 'tags_of_user': tags_of_user, 'usersPolls': user_polls,  'completedPolls': pass_user_polls}
    return render(requests, 'profile_page.html', context={'user': user, 'tags': tags.items()})

