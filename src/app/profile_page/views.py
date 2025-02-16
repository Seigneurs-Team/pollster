from django.shortcuts import render
from databases.mysql_db import client_mysqldb

def request_on_profile_page(requests):
     polls = client_mysqldb.get_polls() #это временно, пока что беру все опросы, потом тут будут опросы пользователя

     return render(requests, 'profile_page.html', context={'yourPolls': polls, 'completedPolls': polls})

