from django.shortcuts import render
from databases.mysql_db import client_mysqldb

from authentication.check_user_on_auth import authentication_for_profile_page


@authentication_for_profile_page
def request_on_profile_page(requests, id_of_user):
    user_polls = client_mysqldb.get_polls(id_of_user=id_of_user)
    pass_user_polls = client_mysqldb.get_pass_user_polls(id_of_user)

    print(pass_user_polls)
    user_data = client_mysqldb.get_user_data_from_table(id_of_user)
    tags = {  1: 'развлечения',  2: 'наука',  3: 'животные',  4: 'кухня',  5: 'искусство',  6: 'дети',  7: 'музыка',  8: 'кино и сериалы',  9: 'путешествия',  10: 'игры',  11: 'мода и стиль',  12: 'здоровье',  13: 'образование'}
    user = {'id': id_of_user, 'username': user_data[0], 'email': user_data[1], 'phone': '+7(911)-111-11-11', 'date_of_birth': '2006-08-01', 'usersPolls': user_polls,  'completedPolls': pass_user_polls}
    return render(requests, 'profile_page.html', context={'user': user, 'tags': tags.items()})

