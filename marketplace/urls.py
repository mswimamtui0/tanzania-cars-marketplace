from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='marketplace/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('dealer-panel/', views.dealer_dashboard, name='dealer_dashboard'),
    path('yard-panel/', views.yard_manager_dashboard, name='yard_manager_dashboard'),
    path('buyer-panel/', views.buyer_dashboard, name='buyer_dashboard'),
    
    # Dealer URLs
    path('dealer/add-car/', views.dealer_add_car, name='dealer_add_car'),
    path('dealer/my-cars/', views.dealer_my_cars, name='dealer_my_cars'),
    path('dealer/edit-car/<int:car_id>/', views.dealer_edit_car, name='dealer_edit_car'),
    path('dealer/delete-car/<int:car_id>/', views.dealer_delete_car, name='dealer_delete_car'),
    
    # Yard Manager URLs - MAKE SURE THESE EXIST
    path('yard/add-car/', views.yard_add_car, name='yard_add_car'),
    path('yard/my-cars/', views.yard_my_cars, name='yard_my_cars'),
    path('yard/pending-cars/', views.yard_pending_cars, name='yard_pending_cars'),
    path('yard/approve-car/<int:car_id>/', views.yard_approve_car, name='yard_approve_car'),
    path('yard/reject-car/<int:car_id>/', views.yard_reject_car, name='yard_reject_car'),
    path('yard/pending-dealers/', views.yard_pending_dealers, name='yard_pending_dealers'),
    path('yard/verify-dealer/<int:dealer_id>/', views.yard_verify_dealer, name='yard_verify_dealer'),
    path('yard/assign-dealer/<int:dealer_id>/', views.yard_assign_dealer, name='yard_assign_dealer'),
    path('yard/add-car/', views.yard_add_car, name='yard_add_car'),
path('yard/my-cars/', views.yard_my_cars, name='yard_my_cars'),
path('yard/pending-cars/', views.yard_pending_cars, name='yard_pending_cars'),
path('yard/pending-dealers/', views.yard_pending_dealers, name='yard_pending_dealers'),
    
    # Other URLs
    path('save-car/<int:car_id>/', views.save_car, name='save_car'),
    path('whatsapp/chat/<int:car_id>/', views.whatsapp_chat, name='whatsapp_chat'),
    path('request-inspection/<int:car_id>/', views.request_inspection, name='request_inspection'),
    path('compare/', views.compare_cars, name='compare_cars'),
    path('compare/add/<int:car_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('compare/remove/<int:car_id>/', views.remove_from_comparison, name='remove_from_comparison'),
    path('sell-car/', views.sell_car, name='sell_car'),
    path('profile/', views.profile, name='profile'),
    path('valuation/', views.car_valuation, name='car_valuation'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('mark-as-sold/<int:car_id>/', views.mark_as_sold, name='mark_as_sold'),
    path('dealer/sold-requests/', views.dealer_sold_requests, name='dealer_sold_requests'),
    path('dealer/approve-sold/<int:request_id>/', views.approve_sold, name='approve_sold'),
    path('dealer/reject-sold/<int:request_id>/', views.reject_sold, name='reject_sold'),
    path('yard/add-car/', views.yard_add_car, name='yard_add_car'),
path('yard/my-cars/', views.yard_my_cars, name='yard_my_cars'),
path('yard/assign-dealer/', views.yard_assign_dealer, name='yard_assign_dealer'),
path('yard/assigned-dealers/', views.yard_assigned_dealers, name='yard_assigned_dealers'),
path('yard/remove-dealer/<int:assignment_id>/', views.yard_remove_dealer, name='yard_remove_dealer'),
# Add these URLs
path('dealer/commission/', views.dealer_commission_dashboard, name='dealer_commission'),
path('report-fake/<int:car_id>/', views.report_fake_listing, name='report_fake_listing'),
path('admin/reports/', views.admin_reports_dashboard, name='admin_reports'),
path('admin/report/<int:report_id>/resolve/', views.resolve_report, name='resolve_report'),
path('about-us/', views.about_us, name='about_us'),
path('about-us/', views.about_us, name='about_us'),
]