"""server_securitate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('__admin/_3console__/', admin.site.urls),
    path('devices/', views.devices),
    path('public_key/', views.send_public_key),
    path('account/', include('django.contrib.auth.urls')),
    path('login/', views.login_view),
    path('add_device/', views.add_device),
    path('delete_device/', views.delete_device),
    path('settings/', views.settings_page),
    path('logout/', LogoutView.as_view()),
    path('data/', views.data),
    path('edit_name/', views.edit_name),
    path('request_uid/', views.request_uid),
    path('port/', views.port),
    path('start_stream/', views.start_stream),
    path('livefeed/', views.livefeed),
    path('check_credentials/', views.check_credentials),
    path('request_add/', views.request_add),
    path('confirm_email/', views.confirm_email),
    path('signup/', views.signup),
    path('camera/', views.camera),
    path('profile/', views.profile),
    path('forgot_password/', views.forgot_password),
    path('forgot_password_link/', views.forgot_password_link),
    path('change_email/', views.change_email),
    path('delete_account/', views.delete_account),
  	path('image_history/', views.image_history),
    path('', views.index)
]
