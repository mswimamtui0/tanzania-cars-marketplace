from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Car listings
    path('cars/', views.car_list, name='car_list'),
    path('cars/search/', views.search_cars, name='search_cars'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/add/', views.add_car, name='add_car'),
    path('cars/<int:car_id>/edit/', views.edit_car, name='edit_car'),
    path('cars/<int:car_id>/delete/', views.delete_car, name='delete_car'),
    
    # Favorites
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorites/<int:car_id>/toggle/', views.favorite_car, name='favorite_car'),
    
    # Dealer dashboard
    path('dealer/dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('dealer/cars/', views.dealer_cars, name='dealer_cars'),
    path('dealer/cars/add/', views.dealer_add_car, name='dealer_add_car'),
    path('dealer/cars/<int:car_id>/edit/', views.dealer_edit_car, name='dealer_edit_car'),
    path('dealer/cars/<int:car_id>/delete/', views.dealer_delete_car, name='dealer_delete_car'),
    
    # Yard Manager dashboard
    path('yard/dashboard/', views.yard_dashboard, name='yard_dashboard'),
    path('yard/cars/', views.yard_cars, name='yard_cars'),
    path('yard/cars/add/', views.yard_add_car, name='yard_add_car'),
    path('yard/cars/<int:car_id>/edit/', views.yard_edit_car, name='yard_edit_car'),
    path('yard/cars/<int:car_id>/delete/', views.yard_delete_car, name='yard_delete_car'),
    
    # Admin dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/cars/', views.admin_cars, name='admin_cars'),
    path('admin/dealers/', views.admin_dealers, name='admin_dealers'),
    path('admin/yards/', views.admin_yards, name='admin_yards'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    
    # About and other pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Language switcher
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', views.set_language, name='set_language'),
]

# Language-prefixed URLs (optional - for multi-language support)
urlpatterns += i18n_patterns(
    path('', include('marketplace.urls')),
)

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)