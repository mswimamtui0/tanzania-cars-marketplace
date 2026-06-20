from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import (
    home, car_list, car_detail, add_car, edit_car, delete_car,
    register, user_login, user_logout, profile, favorite_car,
    favorites_list, search_cars, dealer_dashboard, dealer_cars,
    dealer_add_car, dealer_edit_car, dealer_delete_car,
    yard_dashboard, yard_cars, yard_add_car, yard_edit_car, yard_delete_car,
    admin_dashboard, admin_users, admin_cars, admin_dealers,
    admin_yards, admin_reports, about, contact, terms, privacy,
    set_language
)

# Main URL patterns
urlpatterns = [
    # Home and general pages
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('terms/', terms, name='terms'),
    path('privacy/', privacy, name='privacy'),
    
    # Language switcher
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', set_language, name='set_language'),
    
    # Authentication
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    
    # Car listings
    path('cars/', car_list, name='car_list'),
    path('cars/search/', search_cars, name='search_cars'),
    path('cars/<int:car_id>/', car_detail, name='car_detail'),
    path('cars/add/', add_car, name='add_car'),
    path('cars/<int:car_id>/edit/', edit_car, name='edit_car'),
    path('cars/<int:car_id>/delete/', delete_car, name='delete_car'),
    
    # Favorites
    path('favorites/', favorites_list, name='favorites_list'),
    path('favorites/<int:car_id>/toggle/', favorite_car, name='favorite_car'),
    
    # Dealer dashboard
    path('dealer/dashboard/', dealer_dashboard, name='dealer_dashboard'),
    path('dealer/cars/', dealer_cars, name='dealer_cars'),
    path('dealer/cars/add/', dealer_add_car, name='dealer_add_car'),
    path('dealer/cars/<int:car_id>/edit/', dealer_edit_car, name='dealer_edit_car'),
    path('dealer/cars/<int:car_id>/delete/', dealer_delete_car, name='dealer_delete_car'),
    
    # Yard Manager dashboard
    path('yard/dashboard/', yard_dashboard, name='yard_dashboard'),
    path('yard/cars/', yard_cars, name='yard_cars'),
    path('yard/cars/add/', yard_add_car, name='yard_add_car'),
    path('yard/cars/<int:car_id>/edit/', yard_edit_car, name='yard_edit_car'),
    path('yard/cars/<int:car_id>/delete/', yard_delete_car, name='yard_delete_car'),
    
    # Admin dashboard
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_users, name='admin_users'),
    path('admin/cars/', admin_cars, name='admin_cars'),
    path('admin/dealers/', admin_dealers, name='admin_dealers'),
    path('admin/yards/', admin_yards, name='admin_yards'),
    path('admin/reports/', admin_reports, name='admin_reports'),
]

# Language-prefixed URLs (optional - for multi-language support)
urlpatterns += i18n_patterns(
    path('', include('marketplace.urls')),
)

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)