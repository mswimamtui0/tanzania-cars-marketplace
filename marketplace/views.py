from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils import translation
from .models import (
    Car, CarImage, Dealer, Yard, YardDealerAssignment, DealerAssignment,
    Favorite, Review, Report, Message, InspectionRequest, ListingPackage
)
from .forms import (
    CarForm, CarImageForm, DealerForm, ReviewForm, ReportForm, MessageForm,
    YardForm, DealerAssignmentForm, CustomUserCreationForm
)

# ========== HOME AND GENERAL PAGES ==========

def home(request):
    """Home page view."""
    featured_cars = Car.objects.filter(is_featured=True, status='available')[:6]
    recent_cars = Car.objects.filter(status='available').order_by('-created_at')[:12]
    dealers = Dealer.objects.filter(is_verified=True)[:6]
    
    context = {
        'featured_cars': featured_cars,
        'recent_cars': recent_cars,
        'dealers': dealers,
    }
    return render(request, 'marketplace/home.html', context)

def about_us(request):
    """About page."""
    return render(request, 'marketplace/about_us.html')

def contact(request):
    """Contact page."""
    return render(request, 'marketplace/contact.html')

def terms(request):
    """Terms and conditions page."""
    return render(request, 'marketplace/terms.html')

def privacy(request):
    """Privacy policy page."""
    return render(request, 'marketplace/privacy.html')

# ========== AUTHENTICATION ==========

def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = request.POST.get('role', 'buyer')
            
            if role == 'dealer':
                Dealer.objects.create(
                    user=user,
                    business_name=request.POST.get('business_name', f"{user.username}'s Dealership"),
                    phone=request.POST.get('phone', ''),
                    location=request.POST.get('location', ''),
                    is_verified=False
                )
                auth_login(request, user)
                messages.success(request, _('Registration successful! Welcome to your Dealer Dashboard.'))
                return redirect('dealer_dashboard')
                
            elif role == 'yard_manager':
                auth_login(request, user)
                messages.success(request, _('Registration successful! Welcome to your Yard Dashboard.'))
                return redirect('yard_dashboard')
                
            else:
                auth_login(request, user)
                messages.success(request, _('Registration successful! Welcome to Tanzania Cars Marketplace.'))
                return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'marketplace/register.html', {'form': form})

def login(request):
    """User login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            
            # Redirect based on role
            if user.is_staff:
                messages.success(request, _('Welcome back, Admin!'))
                return redirect('admin_dashboard')
            elif hasattr(user, 'dealer_profile'):
                messages.success(request, _('Welcome back to your Dealer Dashboard!'))
                return redirect('dealer_dashboard')
            elif user.groups.filter(name='Yard Managers').exists():
                messages.success(request, _('Welcome back to your Yard Dashboard!'))
                return redirect('yard_dashboard')
            else:
                messages.success(request, _('Welcome back, {}!').format(user.username))
                return redirect('home')
        else:
            messages.error(request, _('Invalid username or password.'))
    return render(request, 'marketplace/login.html')

def logout(request):
    """User logout view."""
    auth_logout(request)
    messages.info(request, _('You have been logged out.'))
    return redirect('home')

@login_required
def profile(request):
    """User profile view."""
    user = request.user
    user_cars = Car.objects.filter(seller=user).order_by('-created_at')
    favorites = Favorite.objects.filter(user=user).select_related('car')
    
    context = {
        'user': user,
        'user_cars': user_cars,
        'favorites': favorites,
    }
    return render(request, 'marketplace/profile.html', context)

# ========== ADMIN DASHBOARD ==========

@login_required
def admin_dashboard(request):
    """Admin dashboard view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    total_cars = Car.objects.count()
    total_users = User.objects.count()
    total_dealers = Dealer.objects.count()
    total_reports = Report.objects.filter(status='pending').count()
    
    context = {
        'total_cars': total_cars,
        'total_users': total_users,
        'total_dealers': total_dealers,
        'total_reports': total_reports,
        'recent_cars': Car.objects.order_by('-created_at')[:10],
        'recent_users': User.objects.order_by('-date_joined')[:10],
    }
    return render(request, 'marketplace/admin_dashboard.html', context)

@login_required
def admin_users(request):
    """Admin users management view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    users = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplace/admin_users.html', {'page_obj': page_obj})

@login_required
def admin_cars(request):
    """Admin cars management view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    cars = Car.objects.all().order_by('-created_at')
    paginator = Paginator(cars, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplace/admin_cars.html', {'page_obj': page_obj})

@login_required
def admin_dealers(request):
    """Admin dealers management view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    dealers = Dealer.objects.all().order_by('business_name')
    return render(request, 'marketplace/admin_dealers.html', {'dealers': dealers})

@login_required
def admin_yards(request):
    """Admin yards management view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    yards = Yard.objects.all().order_by('name')
    return render(request, 'marketplace/admin_yards.html', {'yards': yards})

@login_required
def admin_reports_dashboard(request):
    """Admin reports management view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    reports = Report.objects.all().order_by('-created_at')
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplace/admin_reports.html', {'page_obj': page_obj})

# ========== DEALER DASHBOARD ==========

@login_required
def dealer_dashboard(request):
    """Dealer dashboard view."""
    try:
        dealer = request.user.dealer_profile
    except Dealer.DoesNotExist:
        messages.warning(request, _('Please complete your dealer profile.'))
        return redirect('profile')
    
    cars = Car.objects.filter(dealer=dealer).order_by('-created_at')
    total_cars = cars.count()
    available_cars = cars.filter(status='available').count()
    sold_cars = cars.filter(status='sold').count()
    pending_cars = cars.filter(status='pending').count()
    
    context = {
        'dealer': dealer,
        'cars': cars[:10],
        'total_cars': total_cars,
        'available_cars': available_cars,
        'sold_cars': sold_cars,
        'pending_cars': pending_cars,
    }
    return render(request, 'marketplace/dealer_dashboard.html', context)

@login_required
def dealer_my_cars(request):
    """Dealer's cars list."""
    try:
        dealer = request.user.dealer_profile
    except Dealer.DoesNotExist:
        messages.warning(request, _('Please complete your dealer profile.'))
        return redirect('profile')
    
    cars = Car.objects.filter(dealer=dealer).order_by('-created_at')
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplace/dealer_my_cars.html', {'page_obj': page_obj})

@login_required
def dealer_add_car(request):
    """Dealer add car view."""
    try:
        dealer = request.user.dealer_profile
    except Dealer.DoesNotExist:
        messages.warning(request, _('Please complete your dealer profile first.'))
        return redirect('profile')
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            car.dealer = dealer
            car.save()
            
            images = request.FILES.getlist('images')
            for img in images:
                CarImage.objects.create(car=car, image=img)
            
            messages.success(request, _('Car added successfully!'))
            return redirect('dealer_my_cars')
    else:
        form = CarForm()
    
    return render(request, 'marketplace/dealer_add_car.html', {'form': form})

@login_required
def dealer_commission_dashboard(request):
    """Dealer commission dashboard."""
    try:
        dealer = request.user.dealer_profile
    except Dealer.DoesNotExist:
        messages.warning(request, _('Please complete your dealer profile.'))
        return redirect('profile')
    
    cars = Car.objects.filter(dealer=dealer, status='sold')
    total_commission = sum(float(car.price) * (dealer.commission_rate / 100) for car in cars)
    
    context = {
        'dealer': dealer,
        'cars': cars,
        'total_commission': total_commission,
        'total_cars_sold': cars.count(),
    }
    return render(request, 'marketplace/dealer_commission.html', context)

@login_required
def dealer_messages(request):
    """Dealer messages view."""
    try:
        dealer = request.user.dealer_profile
    except Dealer.DoesNotExist:
        messages.warning(request, _('Please complete your dealer profile.'))
        return redirect('profile')
    
    messages_list = Message.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'marketplace/dealer_messages.html', {'messages': messages_list})

# ========== YARD MANAGER DASHBOARD ==========

@login_required
def yard_manager_dashboard(request):
    """Yard manager dashboard."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    cars = Car.objects.filter(yard=yard).order_by('-created_at')
    
    context = {
        'yard': yard,
        'cars': cars[:10],
        'total_cars': cars.count(),
        'available_cars': cars.filter(status='available').count(),
        'pending_cars': cars.filter(status='pending').count(),
    }
    return render(request, 'marketplace/yard_manager_dashboard.html', context)

@login_required
def yard_my_cars(request):
    """Yard cars list."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    cars = Car.objects.filter(yard=yard).order_by('-created_at')
    
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplace/yard_my_cars.html', {'page_obj': page_obj, 'yard': yard})

@login_required
def yard_add_car(request):
    """Yard add car view."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            car.yard = yard
            car.status = 'pending'
            car.save()
            
            images = request.FILES.getlist('images')
            for img in images:
                CarImage.objects.create(car=car, image=img)
            
            messages.success(request, _('Car added and pending approval!'))
            return redirect('yard_my_cars')
    else:
        form = CarForm()
    
    return render(request, 'marketplace/yard_add_car.html', {'form': form, 'yard': yard})

@login_required
def yard_pending_cars(request):
    """Yard pending cars view."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    cars = Car.objects.filter(yard=yard, status='pending').order_by('-created_at')
    
    return render(request, 'marketplace/yard_pending_cars.html', {'cars': cars, 'yard': yard})

# ========== BUYER DASHBOARD ==========

@login_required
def buyer_dashboard(request):
    """Buyer dashboard view."""
    favorites = Favorite.objects.filter(user=request.user).select_related('car')
    inspection_requests = InspectionRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    messages_count = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    context = {
        'favorites': favorites[:5],
        'inspection_requests': inspection_requests[:5],
        'unread_messages': messages_count,
        'favorites_count': favorites.count(),
        'inspections_count': inspection_requests.count(),
    }
    return render(request, 'marketplace/buyer_dashboard.html', context)

# ========== CAR LISTINGS ==========

def car_list(request):
    """List all available cars with filters."""
    cars = Car.objects.filter(status='available')
    
    search_query = request.GET.get('q', '')
    if search_query:
        cars = cars.filter(
            Q(title__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    brand = request.GET.get('brand', '')
    if brand:
        cars = cars.filter(brand__icontains=brand)
    
    min_price = request.GET.get('min_price', '')
    if min_price:
        cars = cars.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price', '')
    if max_price:
        cars = cars.filter(price__lte=max_price)
    
    condition = request.GET.get('condition', '')
    if condition:
        cars = cars.filter(condition=condition)
    
    transmission = request.GET.get('transmission', '')
    if transmission:
        cars = cars.filter(transmission=transmission)
    
    fuel_type = request.GET.get('fuel_type', '')
    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)
    
    sort_by = request.GET.get('sort', '-created_at')
    cars = cars.order_by(sort_by)
    
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'brand': brand,
        'min_price': min_price,
        'max_price': max_price,
        'condition': condition,
        'transmission': transmission,
        'fuel_type': fuel_type,
    }
    return render(request, 'marketplace/car_list.html', context)

def car_detail(request, car_id):
    """Car detail view."""
    car = get_object_or_404(Car, id=car_id)
    related_cars = Car.objects.filter(
        Q(brand=car.brand) | Q(model=car.model)
    ).exclude(id=car.id).filter(status='available')[:6]
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, car=car).exists()
    
    context = {
        'car': car,
        'related_cars': related_cars,
        'is_favorite': is_favorite,
    }
    return render(request, 'marketplace/car_detail.html', context)

@login_required
def save_car(request):
    """Save a new car listing."""
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            car.save()
            
            images = request.FILES.getlist('images')
            for img in images:
                CarImage.objects.create(car=car, image=img)
            
            messages.success(request, _('Your car has been listed successfully!'))
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm()
    
    return render(request, 'marketplace/sell_car.html', {'form': form})

@login_required
def add_car(request):
    """Add car view."""
    return save_car(request)

@login_required
def edit_car(request, car_id):
    """Edit a car listing."""
    car = get_object_or_404(Car, id=car_id)
    
    if request.user != car.seller and not request.user.is_staff:
        messages.error(request, _('You do not have permission to edit this car.'))
        return redirect('car_detail', car_id=car.id)
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, _('Car updated successfully!'))
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm(instance=car)
    
    return render(request, 'marketplace/sell_car.html', {'form': form, 'car': car})

@login_required
def delete_car(request, car_id):
    """Delete a car listing."""
    car = get_object_or_404(Car, id=car_id)
    
    if request.user != car.seller and not request.user.is_staff:
        messages.error(request, _('You do not have permission to delete this car.'))
        return redirect('car_detail', car_id=car.id)
    
    if request.method == 'POST':
        car.delete()
        messages.success(request, _('Car deleted successfully!'))
        return redirect('car_list')
    
    return render(request, 'marketplace/car_confirm_delete.html', {'car': car})

# ========== FAVORITES ==========

@login_required
def favorites_list(request):
    """View user's favorite cars."""
    favorites = Favorite.objects.filter(user=request.user).select_related('car')
    return render(request, 'marketplace/favorites.html', {'favorites': favorites})

@login_required
def favorite_car(request, car_id):
    """Toggle favorite status for a car."""
    car = get_object_or_404(Car, id=car_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, car=car)
    
    if not created:
        favorite.delete()
        messages.success(request, _('Removed from favorites'))
    else:
        messages.success(request, _('Added to favorites'))
    
    return redirect('car_detail', car_id=car.id)

# ========== LANGUAGE SWITCHER ==========

def set_language(request):
    """Set user's preferred language."""
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            translation.activate(language)
            request.session[translation.LANGUAGE_SESSION_KEY] = language
            messages.success(request, _('Language changed successfully!'))
    return redirect(request.META.get('HTTP_REFERER', 'home'))