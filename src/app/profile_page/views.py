from django.shortcuts import render

def request_on_profile_page(requests):
     return render(requests, 'profile_page.html')