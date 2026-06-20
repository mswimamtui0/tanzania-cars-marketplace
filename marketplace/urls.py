from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Car listings
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/add/', views.save_car, name='add_car'),
    path('cars/<int:car_id>/edit/', views.edit_car, name='edit_car'),
    path('cars/<int:car_id>/delete/', views.delete_car, name='delete_car'),
    
    # Favorites
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorites/<int:car_id>/toggle/', views.favorite_car, name='favorite_car'),
    
    # Dealer dashboard
    path('dealer/dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('dealer/cars/', views.dealer_my_cars, name='dealer_cars'),
    path('dealer/cars/add/', views.dealer_add_car, name='dealer_add_car'),
    path('dealer/cars/<int:car_id>/edit/', views.dealer_edit_car, name='dealer_edit_car'),
    path('dealer/cars/<int:car_id>/delete/', views.dealer_delete_car, name='dealer_delete_car'),
    path('dealer/messages/', views.dealer_messages, name='dealer_messages'),
    path('dealer/sold-requests/', views.dealer_sold_requests, name='dealer_sold_requests'),
    path('dealer/commission/', views.dealer_commission_dashboard, name='dealer_commission_dashboard'),
    
    # Yard Manager dashboard
    path('yard/dashboard/', views.yard_manager_dashboard, name='yard_dashboard'),
    path('yard/cars/', views.yard_my_cars, name='yard_cars'),
    path('yard/cars/add/', views.yard_add_car, name='yard_add_car'),
    path('yard/cars/<int:car_id>/edit/', views.yard_edit_car, name='yard_edit_car'),
    path('yard/cars/<int:car_id>/delete/', views.yard_delete_car, name='yard_delete_car'),
    path('yard/pending/', views.yard_pending_cars, name='yard_pending_cars'),
    path('yard/approve/<int:car_id>/', views.yard_approve_car, name='yard_approve_car'),
    path('yard/reject/<int:car_id>/', views.yard_reject_car, name='yard_reject_car'),
    path('yard/dealers/', views.yard_manage_dealers, name='yard_manage_dealers'),
    path('yard/dealers/assign/', views.yard_assign_dealer, name='yard_assign_dealer'),
    path('yard/dealers/remove/<int:dealer_id>/', views.yard_remove_dealer, name='yard_remove_dealer'),
    path('yard/dealers/verify/<int:dealer_id>/', views.yard_verify_dealer, name='yard_verify_dealer'),
    
    # Admin dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/cars/', views.admin_cars, name='admin_cars'),
    path('admin/dealers/', views.admin_dealers, name='admin_dealers'),
    path('admin/yards/', views.admin_yards, name='admin_yards'),
    path('admin/reports/', views.admin_reports_dashboard, name='admin_reports'),
    path('admin/resolve-report/<int:report_id>/', views.resolve_report, name='resolve_report'),
    path('admin/create-yard/', views.admin_create_yard, name='admin_create_yard'),
    path('admin/assign-yard/', views.admin_assign_yard, name='admin_assign_yard'),
    path('admin/verify-yard/<int:yard_id>/', views.admin_verify_yard, name='admin_verify_yard'),
    
    # Buyer dashboard
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/inspections/', views.buyer_inspections, name='buyer_inspections'),
    path('buyer/messages/', views.buyer_messages, name='buyer_messages'),
    
    # Car comparison
    path('compare/', views.compare_cars, name='compare_cars'),
    path('compare/add/<int:car_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('compare/remove/<int:car_id>/', views.remove_from_comparison, name='remove_from_comparison'),
    
    # Car valuation
    path('valuation/', views.car_valuation, name='car_valuation'),
    
    # Messages
    path('messages/', views.message_detail, name='message_detail'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/reply/<int:message_id>/', views.reply_message, name='reply_message'),
    
    # About and other pages
    path('about/', views.about_us, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Additional features
    path('sell-car/', views.sell_car, name='sell_car'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('request-inspection/', views.request_inspection, name='request_inspection'),
    path('report-fake/', views.report_fake_listing, name='report_fake_listing'),
    path('whatsapp/<int:car_id>/', views.whatsapp_chat, name='whatsapp_chat'),
    path('mark-sold/<int:car_id>/', views.mark_as_sold, name='mark_as_sold'),
    path('approve-sold/<int:car_id>/', views.approve_sold, name='approve_sold'),
    path('reject-sold/<int:car_id>/', views.reject_sold, name='reject_sold'),
    
    # Language switcher
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', views.set_language, name='set_language'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)