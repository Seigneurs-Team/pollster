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
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView


from django.contrib import admin
from django.urls import path, include, re_path

from app.main_page.views import request_on_main_page, requests_on_get_polls
from app.create_poll_page.views import request_on_create_poll_page, request_on_create_new_poll
from app.passing_poll_page.views import request_on_passing_poll_page
from app.sign_in_page.views import request_on_sign_in_page
from app.create_new_account_page.views import request_on_create_new_account_page
from app.create_new_account_page.views import request_on_create_new_account
from app.sign_in_page.views import request_on_sign_in_account
from app.profile_page.views import request_on_profile_page
from PoW.captcher_post_challenge import request_on_challenge
from app.passing_poll_page.views import request_on_passing_poll
from app.log_out.views import request_on_log_out
from app.delete_account.views import request_on_delete_account
from app.delete_poll.views import request_on_delete_poll

from app.change_settings_of_user import url_patterns_of_changes_in_user_profile

from app.statistics_of_poll.views import request_on_statistics_page, request_on_get_statistics

from app.get_qr_code_of_poll.views import request_of_get_qr_code


handler403 = 'app.custom_handlers_of_status_codes.views.custom_forbidden'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', request_on_main_page, name='home'),
    path('create_poll_page', request_on_create_poll_page, name='create_poll_page'),
    path('passing_poll/<int:poll_id>/', request_on_passing_poll_page, name='passing_poll_page'),
    path('passing_poll/<str:code_of_poll>', request_on_passing_poll_page, name='passing_private_poll_page'),
    path('get_polls/<int:num_of_polls>', requests_on_get_polls),
    path('create_poll', request_on_create_new_poll, name='create_poll_page'),
    path('sign_in', request_on_sign_in_page, name='sign_in_page'),
    path('create_new_account', request_on_create_new_account_page, name='create_new_account_page'),
    path('register', request_on_create_new_account, name='create_new_account'),
    path('log_in', request_on_sign_in_account, name='sign_in_account'),
    path('profile', request_on_profile_page, name='profile_page'),
    path('profile/<slug:id_of_user>', request_on_profile_page, name='profile_page'),
    path('get_challenge', request_on_challenge, name='get_data_of_challenge'),
    path('post_pass_poll', request_on_passing_poll, name="save_answers_in_db"),
    path('log_out', request_on_log_out, name='log_out'),
    path('delete_account', request_on_delete_account, name='delete_account'),
    path('delete_poll/<int:id_of_poll>/', request_on_delete_poll, name='delete_poll'),
    path('change_user_data/', include(url_patterns_of_changes_in_user_profile), name='change_user_settings'),
    path('statistics/<int:id_of_poll>', request_on_statistics_page, name='statistics_page_of_poll'),
    path('get_statistics/<int:id_of_poll>', request_on_get_statistics, name="get_statistics_of_poll"),
    path('get_qr_code/<int:id_of_poll>', request_of_get_qr_code, name="get_qr_code_of_poll"),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
