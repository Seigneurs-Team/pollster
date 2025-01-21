from django.shortcuts import render


def request_on_passing_poll_page(requests):
    return render(requests, 'passing_poll_page.html')
