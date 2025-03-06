from django.shortcuts import render
from databases.mysql_db import client_mysqldb

def request_on_profile_page(requests, id):
    # TODO из БД по id надо получить login пользователя, его почту, номер телефона, дату рождения, созданные и пройденные им опросы
    polls = client_mysqldb.get_polls() # это временно, пока что беру все опросы, потом тут будут опросы пользователя

    user ={'id' : 123, 'username' : 'DikayaKakEnot', 'email': 'someemail@gmail.com', 'phone': '+7(911)-111-11-11', 'date_of_birth': '2006-08-01', 'usersPolls': polls,  'completedPolls': polls}
    return render(requests, 'profile_page.html', context={'user': user})

