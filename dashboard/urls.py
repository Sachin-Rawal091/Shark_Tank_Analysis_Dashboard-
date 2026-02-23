"""
URL configuration for dashboard app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/filter/', views.api_filter, name='api_filter'),
    path('shark/<str:shark_name>/', views.shark_analysis, name='shark_analysis'),
]
