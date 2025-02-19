from django.shortcuts import render




def request_on_sign_in_page(requests):
    return render(requests, 'sign_in_page.html')
