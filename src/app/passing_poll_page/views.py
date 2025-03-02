from django.shortcuts import render
from databases.mysql_db import client_mysqldb

from Configs.Exceptions import NotFoundPoll


def request_on_passing_poll_page(requests, poll_id):
    # тут должна быть проверка, выполнен ли вход в аккаунт. если да, то user извлекается из БД (id, username и фото профиля в дальнейшем)
    user = {'id' : 123, 'username' : "DikayaKakEnot"}
    print('poll_id: ', poll_id)
    # получение опроса по id
    try:
        poll = client_mysqldb.get_poll(poll_id)
        print(poll)
        return render(requests, 'passing_poll_page.html', context={'user': user, 'poll': poll})
    except NotFoundPoll as _ex:
        return render(requests, 'NotFound.html')