from django.shortcuts import render


def request_on_passing_poll_page(requests, poll_id):
    # получение опроса по id
    # poll = client_mysqldb.
    # return render(requests, 'passing_poll_page.html', context={'poll': poll})

    return render(requests, 'passing_poll_page.html')
