from django.urls import path
from . import views

app_name = 'technologies'
urlpatterns = [
    path('', views.tech_home, name='home'),
    path('<int:pk>/', views.tech_detail, name='detail'),
]
