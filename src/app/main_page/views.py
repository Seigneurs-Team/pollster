from django.shortcuts import render
from django.http import HttpResponse


async def request_on_main_page(requests):
    return HttpResponse("Main page")