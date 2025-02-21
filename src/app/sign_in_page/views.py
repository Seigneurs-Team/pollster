from django.shortcuts import render
import json


def request_on_sign_in_page(requests):
    return render(requests, 'sign_in_page.html')


def request_on_sign_in_account(request):
    json_data = json.loads(request.body)

    login = json_data.get('login')
    password = json_data.get('password')

    pow = json_data.get('pow', '')

    assert pow != ''


