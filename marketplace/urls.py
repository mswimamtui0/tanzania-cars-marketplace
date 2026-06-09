from django.urls import path
from . import views

urlpatterns = [
    # Home and listings
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Dealer car management
    path('dealer/add-car/', views.dealer_add_car, name='dealer_add_car'),
    path('dealer/my-cars/', views.dealer_my_cars, name='dealer_my_cars'),
    path('dealer/edit-car/<int:car_id>/', views.dealer_edit_car, name='dealer_edit_car'),
    path('dealer/delete-car/<int:car_id>/', views.dealer_delete_car, name='dealer_delete_car'),
    
    # Yard manager
    path('yard-manager/cars/', views.yard_manager_cars, name='yard_manager_cars'),
    
    # Sell car
    path('sell-car/', views.sell_car, name='sell_car'),
    
    # WhatsApp and inspection
    path('whatsapp/chat/<int:car_id>/', views.whatsapp_chat, name='whatsapp_chat'),
    path('request-inspection/<int:car_id>/', views.request_inspection, name='request_inspection'),
    
    # Profile and valuation
    path('profile/', views.profile, name='profile'),
    path('valuation/', views.car_valuation, name='car_valuation'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('edit-listing/<int:car_id>/', views.edit_listing, name='edit_listing'),
]