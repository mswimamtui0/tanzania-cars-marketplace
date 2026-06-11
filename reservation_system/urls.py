from django.urls import path
from . import views

urlpatterns = [
    path('reserve/<int:car_id>/', views.create_reservation, name='create_reservation'),
    path('checkout/<int:reservation_id>/', views.reservation_checkout, name='reservation_checkout'),
]