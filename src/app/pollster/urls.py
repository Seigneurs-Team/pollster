"""
URL configuration for pollster project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.main_page.views import request_on_main_page, requests_on_get_polls, request_on_create_new_poll
from app.create_poll_page.views import request_on_create_poll_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', request_on_main_page, name='home'),
    path('create_poll_page', request_on_create_poll_page, name='create_poll_page'),
    path('get_polls', requests_on_get_polls),
    path('create_poll', request_on_create_new_poll)
]
