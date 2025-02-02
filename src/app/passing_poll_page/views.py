from django.shortcuts import render
from databases.mysql_db import client_mysqldb

from Configs.Exceptions import NotFoundPoll


def request_on_passing_poll_page(requests, poll_id):
    print('poll_id: ', poll_id)
    # получение опроса по id
    try:
        poll = client_mysqldb.get_poll(poll_id)
        return render(requests, 'passing_poll_page.html', context={'poll': poll})
    except NotFoundPoll as _ex:
        return render(requests, 'NotFound.html')