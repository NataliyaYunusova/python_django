"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views

"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('myauth/', include('myauth.urls')),
    path('shop/', include('shopapp.urls')),
    path('req/', include('requestdataapp.urls')),
]
