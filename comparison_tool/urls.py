from django.urls import path
from . import views

urlpatterns = [
    path('', views.compare_cars, name='compare_cars'),
    path('add/<int:car_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('remove/<int:car_id>/', views.remove_from_comparison, name='remove_from_comparison'),
]