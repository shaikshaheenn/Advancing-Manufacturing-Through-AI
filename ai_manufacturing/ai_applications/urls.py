from django.urls import path
from . import views

app_name = 'ai_applications'
urlpatterns = [
    path('', views.ai_home, name='home'),
    path('predictive-maintenance/', views.predictive_maintenance, name='predictive'),
    path('quality-control/', views.quality_control, name='quality'),
    path('process-optimization/', views.process_optimization, name='process'),
    path('supply-chain/', views.supply_chain, name='supply_chain'),
]
