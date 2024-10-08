"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('login', views.login),
    re_path('register', views.register),
    re_path('profile', views.profile),
    re_path('upload-json/', views.upload_json, name='upload_json'),
    re_path('get-json/', views.get_json, name='get_json'),
    re_path('upload-excel/', views.upload_excel, name='upload_excel'),
    re_path('download-excel/', views.download_excel, name='download_excel'),
    re_path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    re_path('download-pdf/', views.download_pdf, name='download_pdf'),
    re_path('users/', views.list_user, name='user_list'),
]
