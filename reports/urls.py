from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path('',                views.reports_home,         name='home'),
    path('challenges/',     views.challenges_view,       name='challenges'),
    path('recommendations/',views.recommendations_view,  name='recommendations'),
]
