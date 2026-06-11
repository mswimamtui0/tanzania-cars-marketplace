from django.urls import path
from . import views

urlpatterns = [
    path('calculator/', views.lease_calculator, name='lease_calculator'),
    path('calculator/<int:car_id>/', views.lease_calculator, name='lease_calculator_for_car'),
    path('apply/<int:plan_id>/', views.apply_for_lease, name='apply_for_lease'),
]