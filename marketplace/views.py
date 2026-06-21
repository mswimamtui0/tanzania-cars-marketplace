from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils import translation
from .models import (
    UserProfile, Car, CarListing, CarImage, Dealer, Yard, YardDealerAssignment, 
    DealerAssignment, Favorite, Review, Report, Message, InspectionRequest, ListingPackage
)
from .forms import (
    RegisterForm, CustomAuthenticationForm, UserProfileForm, CarForm, CarImageForm,
    DealerForm, ReviewForm, ReportForm, MessageForm, YardForm, DealerAssignmentForm,
    InspectionRequestForm, ListingPackageForm
)

# ========== HOME AND GENERAL PAGES ==========

def home(request):
    """Home page view."""
    # Get ALL approved cars
    all_cars = Car.objects.filter(is_approved=True)
    
    # Get featured cars (approved and featured)
    featured_cars = Car.objects.filter(is_approved=True, featured=True)[:6]
    
    # Get latest cars (approved, ordered by created_at)
    latest_cars = Car.objects.filter(is_approved=True).order_by('-created_at')[:8]
    
    # Get dealers
    dealers = Dealer.objects.filter(is_verified=True)[:6]
    
    # Get popular makes
    popular_makes = Car.objects.filter(is_approved=True).values('make').annotate(
        count=Count('make')
    ).order_by('-count')[:8]
    
    context = {
        'featured_cars': featured_cars,
        'latest_cars': latest_cars,
        'dealers': dealers,
        'popular_makes': popular_makes,
        'total_cars': all_cars.count(),
        'total_dealers': Dealer.objects.filter(is_verified=True).count(),
        'total_sold': Car.objects.filter(is_sold=True).count(),
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
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Get the role
            role = form.cleaned_data.get('role', 'buyer')
            
            # Log the user in
            auth_login(request, user)
            
            messages.success(request, _('Registration successful!'))
            
            # Redirect based on role
            if role == 'dealer':
                return redirect('dealer_dashboard')
            elif role == 'yard_manager':
                return redirect('yard_dashboard')
            else:
                return redirect('buyer_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'marketplace/register.html', {'form': form})

def login(request):
    """User login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            
            # Check if user is admin
            if user.is_staff:
                messages.success(request, _('Welcome back, Admin!'))
                return redirect('admin_dashboard')
            
            # Check user role from UserProfile
            try:
                profile = user.userprofile
                role = profile.role
                
                if role == 'dealer':
                    messages.success(request, _('Welcome back to your Dealer Dashboard!'))
                    return redirect('dealer_dashboard')
                elif role == 'yard_manager':
                    messages.success(request, _('Welcome back to your Yard Dashboard!'))
                    return redirect('yard_dashboard')
                else:
                    messages.success(request, _('Welcome back, {}!').format(user.username))
                    return redirect('buyer_dashboard')
            except UserProfile.DoesNotExist:
                # If no profile, create one as buyer
                UserProfile.objects.create(
                    user=user,
                    role='buyer',
                    phone='',
                    company_name='',
                    location='',
                    verification_level=1
                )
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
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = None
    
    user_cars = Car.objects.filter(seller=user).order_by('-created_at')
    favorites = Favorite.objects.filter(user=user).select_related('car')
    
    context = {
        'user': user,
        'profile': profile,
        'user_cars': user_cars,
        'favorites': favorites,
    }
    return render(request, 'marketplace/profile.html', context)


# ========== CAR LISTINGS ==========

def car_list(request):
    """List all available cars with filters."""
    cars = Car.objects.filter(is_approved=True)
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        cars = cars.filter(
            Q(title__icontains=search_query) |
            Q(make__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filters
    make = request.GET.get('make', '')
    if make:
        cars = cars.filter(make__icontains=make)
    
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
    
    body_type = request.GET.get('body_type', '')
    if body_type:
        cars = cars.filter(body_type=body_type)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    cars = cars.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(cars, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all makes for filter dropdown
    all_makes = Car.objects.filter(is_approved=True).values_list('make', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'make': make,
        'min_price': min_price,
        'max_price': max_price,
        'condition': condition,
        'transmission': transmission,
        'fuel_type': fuel_type,
        'body_type': body_type,
        'sort_by': sort_by,
        'all_makes': all_makes,
        'total_cars': cars.count(),
    }
    return render(request, 'marketplace/car_list.html', context)

def car_detail(request, car_id):
    """Car detail view."""
    car = get_object_or_404(Car, id=car_id)
    
    # Increment view count
    car.views = getattr(car, 'views', 0) + 1
    car.save()
    
    related_cars = Car.objects.filter(
        Q(make=car.make) | Q(model=car.model)
    ).exclude(id=car.id).filter(is_approved=True)[:6]
    
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
            car.is_approved = False  # Needs admin approval
            car.save()
            
            # Handle images
            if 'images' in request.FILES:
                CarImage.objects.create(car=car, image=request.FILES['images'], is_primary=True)
            
            messages.success(request, _('Your car has been listed successfully and is pending approval!'))
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm()
    
    return render(request, 'marketplace/sell_car.html', {'form': form})

@login_required
def add_car(request):
    """Add car view - for both dealers and yard managers."""
    # Check user role
    try:
        profile = request.user.userprofile
        role = profile.role
    except UserProfile.DoesNotExist:
        messages.error(request, _('Profile not found. Please contact support.'))
        return redirect('home')
    
    # Check if user has permission to add cars
    if role not in ['dealer', 'yard_manager']:
        messages.error(request, _('You do not have permission to add cars.'))
        return redirect('home')
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.seller = request.user
            car.is_sold = False
            
            # If user is dealer, link to dealer
            if role == 'dealer':
                try:
                    dealer = Dealer.objects.get(user=request.user)
                    car.dealer = dealer
                except Dealer.DoesNotExist:
                    pass
            
            # If user is yard manager, link to yard
            if role == 'yard_manager':
                try:
                    yard = Yard.objects.get(manager=request.user)
                    car.yard = yard
                    car.is_approved = False  # Needs yard manager approval
                except Yard.DoesNotExist:
                    messages.warning(request, _('You are not assigned to any yard.'))
            
            car.save()
            
            # Handle image upload with better error handling
            if 'images' in request.FILES:
                image_file = request.FILES['images']
                # Check if file has content
                if image_file and image_file.size > 0:
                    try:
                        # Validate file type
                        valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                        if image_file.content_type not in valid_types:
                            messages.warning(request, _('Please upload a valid image (JPG, PNG, GIF, or WebP).'))
                        else:
                            CarImage.objects.create(
                                car=car, 
                                image=image_file, 
                                is_primary=True
                            )
                            messages.success(request, _('Image uploaded successfully!'))
                    except Exception as e:
                        messages.warning(request, _('Could not upload image. Please try again.'))
                else:
                    messages.warning(request, _('Image file is empty. Please select a valid image.'))
            
            messages.success(request, _('Car added successfully!'))
            
            # Redirect based on role
            if role == 'dealer':
                return redirect('dealer_my_cars')
            else:
                return redirect('yard_cars')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CarForm()
    
    return render(request, 'marketplace/add_car.html', {'form': form})

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
            car = form.save()
            if 'images' in request.FILES:
                CarImage.objects.create(car=car, image=request.FILES['images'])
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
    
    return render(request, 'marketplace/car_detail.html', {'car': car})

@login_required
def sell_car(request):
    """Sell car view."""
    return render(request, 'marketplace/sell_car.html')

@login_required
def create_listing(request):
    """Create listing view."""
    return redirect('sell_car')


# ========== FAVORITES ==========

@login_required
def favorites_list(request):
    """View user's favorite cars."""
    favorites = Favorite.objects.filter(user=request.user).select_related('car')
    return render(request, 'marketplace/car_list.html', {'favorites': favorites})

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


# ========== DEALER DASHBOARD ==========

@login_required
def dealer_dashboard(request):
    """Dealer dashboard view."""
    try:
        dealer = request.user.dealer_profile
    except Dealer.DoesNotExist:
        messages.warning(request, _('Please complete your dealer profile.'))
        return redirect('profile')
    
    # Get cars for this dealer - using 'seller' instead of 'dealer'
    cars = Car.objects.filter(seller=request.user).order_by('-created_at')
    total_cars = cars.count()
    available_cars = cars.filter(is_approved=True, is_sold=False).count()
    sold_cars = cars.filter(is_sold=True).count()
    pending_cars = cars.filter(is_approved=False).count()
    
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
    
    # Use 'seller' instead of 'dealer'
    cars = Car.objects.filter(seller=request.user).order_by('-created_at')
    
    # Calculate stats
    total_cars = cars.count()
    available_cars = cars.filter(is_approved=True, is_sold=False).count()
    pending_cars = cars.filter(is_approved=False).count()
    sold_cars = cars.filter(is_sold=True).count()
    
    context = {
        'cars': cars,
        'total_cars': total_cars,
        'available_cars': available_cars,
        'pending_cars': pending_cars,
        'sold_cars': sold_cars,
    }
    return render(request, 'marketplace/dealer_my_cars.html', context)

@login_required
def dealer_add_car(request):
    """Dealer add car view."""
    return add_car(request)

@login_required
def dealer_edit_car(request, car_id):
    """Dealer edit car view."""
    return edit_car(request, car_id)

@login_required
def dealer_delete_car(request, car_id):
    """Dealer delete car view."""
    return delete_car(request, car_id)

@login_required
def dealer_messages(request):
    """Dealer messages view."""
    messages_list = Message.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'marketplace/dealer_messages.html', {'messages': messages_list})

@login_required
def dealer_sold_requests(request):
    """Dealer sold requests view."""
    try:
        dealer = request.user.dealer_profile
    except Dealer.DoesNotExist:
        messages.warning(request, _('Please complete your dealer profile.'))
        return redirect('profile')
    
    cars = Car.objects.filter(dealer=dealer, status='pending').order_by('-created_at')
    return render(request, 'marketplace/dealer_sold_requests.html', {'cars': cars})

@login_required
def dealer_commission_dashboard(request):
    """Dealer commission dashboard."""
    try:
        dealer = request.user.dealer_profile
    except Dealer.DoesNotExist:
        messages.warning(request, _('Please complete your dealer profile.'))
        return redirect('profile')
    
    cars = Car.objects.filter(dealer=dealer, is_sold=True)
    total_commission = sum(float(car.price) * (dealer.commission_rate / 100) for car in cars)
    
    context = {
        'dealer': dealer,
        'cars': cars,
        'total_commission': total_commission,
        'total_cars_sold': cars.count(),
    }
    return render(request, 'marketplace/dealer_commission.html', context)

@login_required
def approve_sold(request, car_id):
    """Approve a car as sold."""
    car = get_object_or_404(Car, id=car_id)
    
    if car.seller != request.user and not request.user.is_staff:
        messages.error(request, _('Permission denied.'))
        return redirect('dealer_dashboard')
    
    car.is_sold = True
    car.status = 'sold'
    car.save()
    messages.success(request, _('Car marked as sold!'))
    return redirect('dealer_sold_requests')

@login_required
def reject_sold(request, car_id):
    """Reject a car sale."""
    car = get_object_or_404(Car, id=car_id)
    
    if car.seller != request.user and not request.user.is_staff:
        messages.error(request, _('Permission denied.'))
        return redirect('dealer_dashboard')
    
    car.is_sold = False
    car.status = 'available'
    car.save()
    messages.warning(request, _('Sale rejected.'))
    return redirect('dealer_sold_requests')


# ========== YARD MANAGER DASHBOARD ==========

@login_required
def yard_manager_dashboard(request):
    """Yard manager dashboard."""
    try:
        profile = request.user.userprofile
        if profile.role != 'yard_manager':
            messages.warning(request, _('You are not registered as a yard manager.'))
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.warning(request, _('Please complete your profile.'))
        return redirect('profile')
    
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    cars = Car.objects.filter(yard=yard).order_by('-created_at')
    
    context = {
        'profile': profile,
        'yard': yard,
        'cars': cars[:10],
        'total_cars': cars.count(),
        'available_cars': cars.filter(is_approved=True, is_sold=False).count(),
        'pending_cars': cars.filter(is_approved=False).count(),
        'dealer_count': YardDealerAssignment.objects.filter(yard=yard, is_active=True).count(),
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
    return add_car(request)

@login_required
def yard_edit_car(request, car_id):
    """Yard edit car view."""
    return edit_car(request, car_id)

@login_required
def yard_delete_car(request, car_id):
    """Yard delete car view."""
    return delete_car(request, car_id)

@login_required
def yard_pending_cars(request):
    """Yard pending cars view - cars waiting for approval."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    cars = Car.objects.filter(yard=yard, is_approved=False).order_by('-created_at')
    
    return render(request, 'marketplace/yard_pending_cars.html', {'cars': cars, 'yard': yard})

@login_required
def yard_approve_car(request, car_id):
    """Yard approve car view."""
    car = get_object_or_404(Car, id=car_id)
    yards = Yard.objects.filter(manager=request.user)
    
    if not yards.exists() or car.yard not in yards:
        messages.error(request, _('You do not have permission to approve this car.'))
        return redirect('yard_pending_cars')
    
    car.is_approved = True
    car.is_verified = True
    car.save()
    messages.success(request, _('Car approved and listed on marketplace!'))
    return redirect('yard_pending_cars')

@login_required
def yard_reject_car(request, car_id):
    """Yard reject car view."""
    car = get_object_or_404(Car, id=car_id)
    yards = Yard.objects.filter(manager=request.user)
    
    if not yards.exists() or car.yard not in yards:
        messages.error(request, _('You do not have permission to reject this car.'))
        return redirect('yard_pending_cars')
    
    car.delete()
    messages.warning(request, _('Car rejected and removed.'))
    return redirect('yard_pending_cars')

@login_required
def yard_manage_dealers(request):
    """Yard manage dealers view."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    assignments = YardDealerAssignment.objects.filter(yard=yard, is_active=True).select_related('dealer', 'dealer__user')
    
    context = {
        'yard': yard,
        'assignments': assignments,
    }
    return render(request, 'marketplace/yard_manage_dealers.html', context)

@login_required
def yard_assign_dealer(request):
    """Yard assign dealer view."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    
    if request.method == 'POST':
        dealer_id = request.POST.get('dealer_id')
        dealer = get_object_or_404(Dealer, id=dealer_id)
        
        assignment, created = YardDealerAssignment.objects.get_or_create(
            dealer=dealer,
            yard=yard,
            defaults={
                'assigned_by': request.user,
                'is_active': True,
                'is_verified': False
            }
        )
        
        if created:
            messages.success(request, _('Dealer assigned to yard successfully!'))
        else:
            messages.info(request, _('Dealer already assigned to this yard.'))
        
        return redirect('yard_manage_dealers')
    
    assigned_dealers = YardDealerAssignment.objects.filter(yard=yard).values_list('dealer_id', flat=True)
    dealers = Dealer.objects.filter(is_verified=True).exclude(id__in=assigned_dealers)
    
    return render(request, 'marketplace/yard_assign_dealer.html', {'yard': yard, 'dealers': dealers})

@login_required
def yard_remove_dealer(request, dealer_id):
    """Yard remove dealer view."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    assignment = get_object_or_404(YardDealerAssignment, dealer_id=dealer_id, yard=yard)
    assignment.delete()
    messages.success(request, _('Dealer removed from yard.'))
    return redirect('yard_manage_dealers')

@login_required
def yard_verify_dealer(request, dealer_id):
    """Yard verify dealer view."""
    yards = Yard.objects.filter(manager=request.user)
    if not yards.exists():
        messages.warning(request, _('You are not assigned to any yard.'))
        return redirect('home')
    
    yard = yards.first()
    assignment = get_object_or_404(YardDealerAssignment, dealer_id=dealer_id, yard=yard)
    assignment.is_verified = True
    assignment.save()
    
    dealer = assignment.dealer
    dealer.is_verified = True
    dealer.verification_level = '2'
    dealer.save()
    
    messages.success(request, _('Dealer verified successfully!'))
    return redirect('yard_manage_dealers')


# ========== ADMIN DASHBOARD ==========

@login_required
def admin_dashboard(request):
    """Admin dashboard view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    total_cars = Car.objects.count()
    total_users = User.objects.count()
    total_dealers = Dealer.objects.filter(is_verified=True).count()
    total_reports = Report.objects.filter(status='pending').count()
    pending_cars = Car.objects.filter(is_approved=False).count()
    
    context = {
        'total_cars': total_cars,
        'total_users': total_users,
        'total_dealers': total_dealers,
        'total_reports': total_reports,
        'pending_cars': pending_cars,
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
    
    return render(request, 'marketplace/admin_dashboard.html', {'page_obj': page_obj})

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
    
    return render(request, 'marketplace/admin_dashboard.html', {'page_obj': page_obj})

@login_required
def admin_dealers(request):
    """Admin dealers management view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    dealers = Dealer.objects.all().order_by('business_name')
    paginator = Paginator(dealers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplace/admin_dashboard.html', {'page_obj': page_obj})

@login_required
def admin_yards(request):
    """Admin yards management view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    yards = Yard.objects.all().order_by('name')
    paginator = Paginator(yards, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplace/admin_dashboard.html', {'page_obj': page_obj})

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

@login_required
def resolve_report(request, report_id):
    """Admin resolve report view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        report.status = 'resolved'
        report.resolved_by = request.user
        report.resolution_notes = request.POST.get('notes', '')
        report.save()
        messages.success(request, _('Report resolved!'))
        return redirect('admin_reports')
    
    return render(request, 'marketplace/resolve_report.html', {'report': report})

@login_required
def admin_create_yard(request):
    """Admin create yard view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    if request.method == 'POST':
        form = YardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Yard created successfully!'))
            return redirect('admin_yards')
    else:
        form = YardForm()
    
    return render(request, 'marketplace/admin_dashboard.html', {'form': form})

@login_required
def admin_assign_yard(request):
    """Admin assign yard to manager view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    if request.method == 'POST':
        yard_id = request.POST.get('yard_id')
        manager_id = request.POST.get('manager_id')
        
        yard = get_object_or_404(Yard, id=yard_id)
        manager = get_object_or_404(User, id=manager_id)
        
        yard.manager = manager
        yard.save()
        
        messages.success(request, _('Yard manager assigned successfully!'))
        return redirect('admin_yards')
    
    yards = Yard.objects.filter(manager__isnull=True)
    users = User.objects.filter(is_staff=False)
    
    context = {
        'yards': yards,
        'users': users,
    }
    return render(request, 'marketplace/admin_dashboard.html', context)

@login_required
def admin_verify_yard(request, yard_id):
    """Admin verify yard view."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied. Admin only.'))
        return redirect('home')
    
    yard = get_object_or_404(Yard, id=yard_id)
    yard.is_active = not yard.is_active
    yard.save()
    
    status = 'activated' if yard.is_active else 'deactivated'
    messages.success(request, _('Yard {} successfully!').format(status))
    return redirect('admin_yards')


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

@login_required
def buyer_inspections(request):
    """Buyer inspections view."""
    inspections = InspectionRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    return render(request, 'marketplace/buyer_dashboard.html', {'inspections': inspections})

@login_required
def buyer_messages(request):
    """Buyer messages view."""
    messages_list = Message.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'marketplace/buyer_messages.html', {'messages': messages_list})


# ========== INSPECTIONS ==========

@login_required
def request_inspection(request):
    """Request vehicle inspection."""
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        scheduled_date = request.POST.get('scheduled_date')
        notes = request.POST.get('notes', '')
        
        car = get_object_or_404(Car, id=car_id)
        
        inspection = InspectionRequest.objects.create(
            car=car,
            requested_by=request.user,
            scheduled_date=scheduled_date,
            notes=notes,
            status='pending'
        )
        
        messages.success(request, _('Inspection requested successfully!'))
        return redirect('buyer_inspections')
    
    car_id = request.GET.get('car_id')
    car = get_object_or_404(Car, id=car_id) if car_id else None
    
    return render(request, 'marketplace/request_inspection.html', {'car': car})


# ========== CAR COMPARISON ==========

def compare_cars(request):
    """Car comparison view."""
    car_ids = request.GET.getlist('car_ids')
    cars = Car.objects.filter(id__in=car_ids) if car_ids else []
    
    return render(request, 'marketplace/compare.html', {'cars': cars})

@login_required
def add_to_comparison(request, car_id):
    """Add car to comparison."""
    car = get_object_or_404(Car, id=car_id)
    
    comparison_list = request.session.get('comparison_list', [])
    if car_id not in comparison_list:
        comparison_list.append(car_id)
        if len(comparison_list) > 4:
            comparison_list.pop(0)
        request.session['comparison_list'] = comparison_list
        messages.success(request, _('Car added to comparison!'))
    else:
        messages.info(request, _('Car already in comparison list.'))
    
    return redirect('car_detail', car_id=car.id)

@login_required
def remove_from_comparison(request, car_id):
    """Remove car from comparison."""
    comparison_list = request.session.get('comparison_list', [])
    if car_id in comparison_list:
        comparison_list.remove(car_id)
        request.session['comparison_list'] = comparison_list
        messages.success(request, _('Car removed from comparison.'))
    
    return redirect('compare_cars')


# ========== CAR VALUATION ==========

def car_valuation(request):
    """Car valuation tool view."""
    if request.method == 'POST':
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = int(request.POST.get('year', 0))
        mileage = int(request.POST.get('mileage', 0))
        
        base_price = 10000000
        age = 2026 - year
        depreciation = age * 500000
        mileage_deduction = (mileage // 10000) * 100000
        
        estimated_price = max(1000000, base_price - depreciation - mileage_deduction)
        
        context = {
            'make': make,
            'model': model,
            'year': year,
            'mileage': mileage,
            'estimated_price': estimated_price,
            'valuation_done': True,
        }
        return render(request, 'marketplace/valuation_form.html', context)
    
    return render(request, 'marketplace/valuation_form.html')


# ========== MESSAGES ==========

@login_required
def message_detail(request, message_id):
    """View message detail."""
    message = get_object_or_404(Message, id=message_id)
    
    if request.user != message.recipient and request.user != message.sender:
        messages.error(request, _('Access denied.'))
        return redirect('home')
    
    message.is_read = True
    message.save()
    
    return render(request, 'marketplace/message_detail.html', {'message': message})

@login_required
def send_message(request):
    """Send a message."""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content')
        car_id = request.POST.get('car_id')
        
        recipient = get_object_or_404(User, id=recipient_id)
        car = get_object_or_404(Car, id=car_id) if car_id else None
        
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            car=car,
            content=content
        )
        
        messages.success(request, _('Message sent!'))
        return redirect('message_detail', message_id=message.id)
    
    return render(request, 'marketplace/send_message.html')

@login_required
def reply_message(request, message_id):
    """Reply to a message."""
    parent_message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        message = Message.objects.create(
            sender=request.user,
            recipient=parent_message.sender,
            car=parent_message.car,
            content=content,
            parent_message=parent_message
        )
        
        messages.success(request, _('Reply sent!'))
        return redirect('message_detail', message_id=message.id)
    
    return render(request, 'marketplace/reply_message.html', {'parent_message': parent_message})


# ========== ADDITIONAL FEATURES ==========

@login_required
def report_fake_listing(request):
    """Report a fake listing."""
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            report.save()
            messages.success(request, _('Report submitted! We will review it.'))
            return redirect('home')
    else:
        form = ReportForm()
        car_id = request.GET.get('car_id')
        if car_id:
            car = get_object_or_404(Car, id=car_id)
            form.fields['car'].initial = car
    
    return render(request, 'marketplace/report_fake_listing.html', {'form': form})

def whatsapp_chat(request, car_id):
    """WhatsApp chat integration."""
    car = get_object_or_404(Car, id=car_id)
    seller = car.seller
    
    try:
        profile = seller.userprofile
        phone = profile.phone
    except UserProfile.DoesNotExist:
        phone = ''
    
    if phone:
        phone = phone.replace('+', '').replace('-', '').replace(' ', '')
        message = f"Hello, I'm interested in your {car.make} {car.model} ({car.year}) listed on Tanzania Cars Marketplace."
        whatsapp_url = f"https://wa.me/{phone}?text={message}"
        return redirect(whatsapp_url)
    
    messages.error(request, _('Seller contact not available.'))
    return redirect('car_detail', car_id=car.id)

@login_required
def mark_as_sold(request, car_id):
    """Mark a car as sold."""
    car = get_object_or_404(Car, id=car_id)
    
    if request.user != car.seller and not request.user.is_staff:
        messages.error(request, _('You do not have permission to mark this car as sold.'))
        return redirect('car_detail', car_id=car.id)
    
    if request.method == 'POST':
        car.is_sold = True
        car.status = 'sold'
        car.save()
        messages.success(request, _('Car marked as sold!'))
        return redirect('car_detail', car_id=car.id)
    
    return render(request, 'marketplace/reserve_car.html', {'car': car})

@login_required
def approve_sold_admin(request, car_id):
    """Approve a car as sold (admin)."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied.'))
        return redirect('home')
    
    car = get_object_or_404(Car, id=car_id)
    car.is_sold = True
    car.status = 'sold'
    car.save()
    messages.success(request, _('Sale approved!'))
    return redirect('admin_reports')

@login_required
def reject_sold_admin(request, car_id):
    """Reject a car sale (admin)."""
    if not request.user.is_staff:
        messages.error(request, _('Access denied.'))
        return redirect('home')
    
    car = get_object_or_404(Car, id=car_id)
    car.is_sold = False
    car.status = 'available'
    car.save()
    messages.warning(request, _('Sale rejected.'))
    return redirect('admin_reports')


# ========== SEARCH ==========

def search_cars(request):
    """Search cars view."""
    query = request.GET.get('q', '')
    cars = Car.objects.filter(
        Q(title__icontains=query) |
        Q(make__icontains=query) |
        Q(model__icontains=query)
    ).filter(is_approved=True)
    
    context = {
        'cars': cars,
        'query': query,
    }
    return render(request, 'marketplace/search_results.html', context)


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