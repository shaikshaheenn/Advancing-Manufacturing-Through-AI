from django.urls import path
from . import views

app_name = 'adminpanel'
urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.manage_users, name='users'),
    path('content/', views.manage_content, name='content'),
    path('reports/', views.admin_reports, name='reports'),
    path('monitoring/', views.system_monitoring, name='monitoring'),
]
