from django.shortcuts import render

def request_on_create_new_account_page(requests):
    print('rendering create_new_account_page...')
    return render(requests, 'create_new_account_page.html')
