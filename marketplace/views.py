from django.db.models import Sum
from .models import UserProfile, CarListing, CarYard, Wishlist, ComparisonSet, SoldRequest, DealerCommission, FakeListingReport
from .models import UserProfile, CarListing, CarYard, Wishlist, ComparisonSet
from .models import UserProfile, CarListing, CarYard, Wishlist, ComparisonSet, SoldRequest, DealerCommission, FakeListingReport
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.parse import quote
from django.utils import timezone
from .models import UserProfile, CarListing, CarYard, Wishlist, ComparisonSet




@login_required
def dealer_commission_dashboard(request):
    """Dealer views their commission earnings"""
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    commissions = DealerCommission.objects.filter(dealer=request.user).order_by('-created_at')
    
    total_earned = commissions.filter(status='paid').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    total_pending = commissions.filter(status='pending').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    
    context = {
        'commissions': commissions,
        'total_earned': total_earned,
        'total_pending': total_pending,
        'pending_count': commissions.filter(status='pending').count(),
        'paid_count': commissions.filter(status='paid').count(),
    }
    return render(request, 'marketplace/dealer_commission.html', context)

@login_required
def report_fake_listing(request, car_id):
    """Buyer reports a fake or suspicious listing"""
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.method == 'POST':
        report = FakeListingReport.objects.create(
            car=car,
            reported_by=request.user,
            reason=request.POST.get('reason'),
            description=request.POST.get('description')
        )
        messages.success(request, 'Thank you for your report. Our team will investigate within 24 hours.')
        return redirect('car_detail', car_id=car.id)
    
    return render(request, 'marketplace/report_fake_listing.html', {'car': car})

@login_required
def admin_reports_dashboard(request):
    """Admin views all reports"""
    if request.user.userprofile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    reports = FakeListingReport.objects.all().order_by('-created_at')
    pending_reports = reports.filter(status='pending')
    
    context = {
        'reports': reports,
        'pending_reports': pending_reports,
        'pending_count': pending_reports.count(),
        'investigating_count': reports.filter(status='investigating').count(),
        'resolved_count': reports.filter(status='resolved').count(),
    }
    return render(request, 'marketplace/admin_reports.html', context)

def about_us(request):
    """About us page - trust building"""
    from django.contrib.auth.models import User
    from django.db.models import Count
    
    total_cars = CarListing.objects.filter(status='approved').count()
    total_dealers = User.objects.filter(userprofile__role='dealer').count()
    total_buyers = User.objects.filter(userprofile__role='buyer').count()
    total_verified = User.objects.filter(userprofile__verification_level=3).count()
    
    context = {
        'total_cars': total_cars,
        'total_dealers': total_dealers,
        'total_buyers': total_buyers,
        'total_verified': total_verified,
    }
    return render(request, 'marketplace/about_us.html', context)

# ========== HOME VIEW ==========
def home(request):
    # Get latest cars (newest first)
    latest_cars = CarListing.objects.filter(status='approved').order_by('-created_at')[:6]
    
    # Get featured cars (manually marked as featured)
    featured_cars = CarListing.objects.filter(status='approved', is_featured=True)[:6]
    
    # If no featured cars, show some latest cars as featured
    if not featured_cars and latest_cars:
        featured_cars = latest_cars[:3]
    
    context = {
        'latest_cars': latest_cars,
        'featured_cars': featured_cars,
    }
    return render(request, 'marketplace/home.html', context)
# ========== CAR LISTINGS ==========
def car_list(request):
    cars = CarListing.objects.filter(status='approved')
    query = request.GET.get('q', '')
    if query:
        cars = cars.filter(make__icontains=query) | cars.filter(model__icontains=query)
    return render(request, 'marketplace/car_list.html', {'cars': cars})

def car_detail(request, car_id):
    car = get_object_or_404(CarListing, id=car_id, status='approved')
    car.views_count += 1
    car.save()
    return render(request, 'marketplace/car_detail.html', {'car': car})

# ========== AUTHENTICATION ==========
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = request.POST.get('role', 'buyer')
            user.userprofile.role = role
            user.userprofile.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'marketplace/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# ========== YARD MANAGER - CAR MANAGEMENT ==========
@login_required
def yard_add_car(request):
    """Yard manager adds a car to their yard"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Only yard managers can add cars.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    
    if not yards:
        messages.error(request, 'You need to be assigned to a yard first.')
        return redirect('yard_manager_dashboard')
    
    if request.method == 'POST':
        try:
            yard_id = request.POST.get('yard')
            yard = CarYard.objects.get(id=yard_id, manager=request.user)
            
            car = CarListing.objects.create(
                title=request.POST.get('title'),
                make=request.POST.get('make'),
                model=request.POST.get('model'),
                year=request.POST.get('year'),
                price=request.POST.get('price'),
                mileage=request.POST.get('mileage'),
                condition=request.POST.get('condition', 'used'),
                transmission=request.POST.get('transmission', 'manual'),
                fuel_type=request.POST.get('fuel_type', 'petrol'),
                description=request.POST.get('description', ''),
                package=request.POST.get('package', 'normal'),
                seller=request.user,
                yard=yard,
                status='approved'  # Yard manager cars are auto-approved
            )
            
            if request.FILES.get('images'):
                car.images = request.FILES['images']
                car.save()
            
            messages.success(request, f'{car.make} {car.model} added to {yard.name}!')
            return redirect('yard_my_cars')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'marketplace/yard_add_car.html', {'yards': yards})

@login_required
def yard_my_cars(request):
    """Yard manager views all cars in their yards"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    cars = CarListing.objects.filter(yard__in=yards).order_by('-created_at')
    
    context = {
        'cars': cars,
        'yards': yards,
        'total_cars': cars.count(),
        'approved_cars': cars.filter(status='approved').count(),
        'pending_cars': cars.filter(status='pending').count(),
        'sold_cars': cars.filter(status='sold').count(),
    }
    return render(request, 'marketplace/yard_my_cars.html', context)

# ========== YARD MANAGER - DEALER VERIFICATION ==========
@login_required
def yard_pending_dealers(request):
    """Yard manager views pending dealer verification requests"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get dealers who have requested to join this yard
    from django.contrib.auth.models import User
    pending_dealers = User.objects.filter(
        userprofile__role='dealer',
        userprofile__verification_level=1  # Unverified
    ).exclude(userprofile__company_name='')
    
    # Dealers already assigned to this yard
    yards = CarYard.objects.filter(manager=request.user)
    assigned_dealers = User.objects.filter(listings__yard__in=yards).distinct()
    
    context = {
        'pending_dealers': pending_dealers,
        'assigned_dealers': assigned_dealers,
        'yards': yards,
        'pending_count': pending_dealers.count(),
    }
    return render(request, 'marketplace/yard_pending_dealers.html', context)

@login_required
def save_car(request, car_id):
    """Add or remove car from wishlist"""
    car = get_object_or_404(CarListing, id=car_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, car=car)
    
    if created:
        messages.success(request, f'{car.make} {car.model} added to your wishlist!')
    else:
        wishlist_item.delete()
        messages.info(request, f'{car.make} {car.model} removed from wishlist.')
    
    return redirect('car_detail', car_id=car.id)

@login_required
def yard_verify_dealer(request, dealer_id):
    """Yard manager verifies a dealer"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    dealer = get_object_or_404(User, id=dealer_id, userprofile__role='dealer')
    yards = CarYard.objects.filter(manager=request.user)
    
    if request.method == 'POST':
        yard_id = request.POST.get('yard')
        yard = get_object_or_404(CarYard, id=yard_id, manager=request.user)
        verification_level = request.POST.get('verification_level', 2)
        
        # Update dealer verification
        profile = dealer.userprofile
        profile.verification_level = int(verification_level)
        profile.verified_badge = verification_level == '3'
        profile.save()
        
        messages.success(request, f'Dealer {dealer.username} verified at Level {verification_level}!')
        return redirect('yard_pending_dealers')
    
    return render(request, 'marketplace/yard_verify_dealer.html', {'dealer': dealer, 'yards': yards})

@login_required
def yard_assign_dealer(request, dealer_id):
    """Yard manager assigns dealer to their yard"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    dealer = get_object_or_404(User, id=dealer_id, userprofile__role='dealer')
    yards = CarYard.objects.filter(manager=request.user)
    
    if request.method == 'POST':
        yard_id = request.POST.get('yard')
        yard = get_object_or_404(CarYard, id=yard_id, manager=request.user)
        
        # Assign dealer to yard (this would be tracked in a separate model)
        messages.success(request, f'Dealer {dealer.username} assigned to {yard.name}!')
        return redirect('yard_pending_dealers')
    
    return render(request, 'marketplace/yard_assign_dealer.html', {'dealer': dealer, 'yards': yards})

# ========== DASHBOARDS ==========
@login_required
def dashboard(request):
    role = request.user.userprofile.role
    if role == 'admin' or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif role == 'dealer':
        return redirect('dealer_dashboard')
    elif role == 'yard_manager':
        return redirect('yard_manager_dashboard')
    else:
        return redirect('buyer_dashboard')

@login_required
def admin_dashboard(request):
    from django.contrib.auth.models import User
    context = {
        'total_users': User.objects.count(),
        'total_cars': CarListing.objects.count(),
        'pending_approvals': CarListing.objects.filter(status='pending').count(),
        'approved_cars': CarListing.objects.filter(status='approved').count(),
        'pending_cars': CarListing.objects.filter(status='pending'),
        'recent_users': User.objects.order_by('-date_joined')[:10],
        'recent_cars': CarListing.objects.order_by('-created_at')[:10],
    }
    return render(request, 'marketplace/admin_dashboard.html', context)

@login_required
def dealer_dashboard(request):
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    cars = CarListing.objects.filter(seller=request.user)
    context = {
        'total_cars': cars.count(),
        'approved_cars': cars.filter(status='approved').count(),
        'pending_cars': cars.filter(status='pending').count(),
        'sold_cars': cars.filter(status='sold').count(),
        'total_views': sum(c.views_count for c in cars),
        'recent_cars': cars.order_by('-created_at')[:5],
    }
    return render(request, 'marketplace/dealer_dashboard.html', context)

@login_required
def yard_manager_dashboard(request):
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    cars = CarListing.objects.filter(yard__in=yards)
    context = {
        'total_yards': yards.count(),
        'total_cars': cars.count(),
        'approved_cars': cars.filter(status='approved').count(),
        'pending_cars': cars.filter(status='pending'),
        'yards': yards,
    }
    return render(request, 'marketplace/yard_manager_dashboard.html', context)

@login_required
def buyer_dashboard(request):
    from marketplace.models import Wishlist, Reservation
    
    # Get wishlist items
    wishlist = Wishlist.objects.filter(user=request.user)
    
    # Get reservations
    reservations = Reservation.objects.filter(buyer=request.user)
    
    context = {
        'wishlist_count': wishlist.count(),
        'recent_wishlist': wishlist.order_by('-added_at')[:5],
        'reservations_count': reservations.count(),
        'active_reservations': reservations.filter(status='confirmed'),
        'unread_messages': 0,  # You can add messaging system later
        'recent_reservations': reservations.order_by('-created_at')[:5],
    }
    return render(request, 'marketplace/buyer_dashboard.html', context)
# ========== DEALER CAR MANAGEMENT ==========
@login_required
def dealer_add_car(request):
    if request.user.userprofile.role not in ['dealer', 'yard_manager', 'admin']:
        messages.error(request, 'Only dealers can add cars.')
        return redirect('dashboard')
    
    yards = CarYard.objects.all()
    
    if request.method == 'POST':
        try:
            yard_id = request.POST.get('yard')
            yard = None
            if yard_id:
                yard = CarYard.objects.get(id=yard_id)
            
            car = CarListing.objects.create(
                title=request.POST.get('title'),
                make=request.POST.get('make'),
                model=request.POST.get('model'),
                year=request.POST.get('year'),
                price=request.POST.get('price'),
                mileage=request.POST.get('mileage'),
                condition=request.POST.get('condition', 'used'),
                transmission=request.POST.get('transmission', 'manual'),
                fuel_type=request.POST.get('fuel_type', 'petrol'),
                description=request.POST.get('description', ''),
                package=request.POST.get('package', 'normal'),
                seller=request.user,
                yard=yard,
                status='approved'
            )
            
            if request.FILES.get('images'):
                car.images = request.FILES['images']
                car.save()
            
            messages.success(request, f'{car.make} {car.model} has been added!')
            return redirect('dealer_my_cars')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'marketplace/dealer_add_car.html', {'yards': yards})

@login_required
def dealer_my_cars(request):
    cars = CarListing.objects.filter(seller=request.user).order_by('-created_at')
    context = {
        'cars': cars,
        'total_cars': cars.count(),
        'approved_cars': cars.filter(status='approved').count(),
        'pending_cars': cars.filter(status='pending').count(),
        'sold_cars': cars.filter(status='sold').count(),
    }
    return render(request, 'marketplace/dealer_my_cars.html', context)

@login_required
def dealer_edit_car(request, car_id):
    car = get_object_or_404(CarListing, id=car_id, seller=request.user)
    if request.method == 'POST':
        car.title = request.POST.get('title')
        car.make = request.POST.get('make')
        car.model = request.POST.get('model')
        car.year = request.POST.get('year')
        car.price = request.POST.get('price')
        car.mileage = request.POST.get('mileage')
        car.condition = request.POST.get('condition')
        car.transmission = request.POST.get('transmission')
        car.fuel_type = request.POST.get('fuel_type')
        car.description = request.POST.get('description')
        car.package = request.POST.get('package')
        car.save()
        messages.success(request, 'Car updated!')
        return redirect('dealer_my_cars')
    return render(request, 'marketplace/dealer_edit_car.html', {'car': car})

@login_required
def dealer_delete_car(request, car_id):
    car = get_object_or_404(CarListing, id=car_id, seller=request.user)
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Car deleted!')
        return redirect('dealer_my_cars')
    return render(request, 'marketplace/dealer_delete_car.html', {'car': car})

# ========== YARD MANAGER APPROVAL ==========
@login_required
def yard_pending_cars(request):
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    pending_cars = CarListing.objects.filter(yard__in=yards, status='pending')
    total_cars = CarListing.objects.filter(yard__in=yards)
    
    context = {
        'pending_cars': pending_cars,
        'total_pending': pending_cars.count(),
        'total_cars': total_cars.count(),
        'approved_cars': total_cars.filter(status='approved').count(),
        'yards': yards,
    }
    return render(request, 'marketplace/yard_pending_cars.html', context)

@login_required
def yard_approve_car(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    if request.method == 'POST':
        car.status = 'approved'
        car.approved_at = timezone.now()
        car.save()
        messages.success(request, f'{car.make} {car.model} approved!')
        return redirect('yard_pending_cars')
    return render(request, 'marketplace/yard_approve_car.html', {'car': car})

@login_required
def yard_reject_car(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    if request.method == 'POST':
        car.status = 'rejected'
        car.save()
        messages.success(request, f'{car.make} {car.model} rejected.')
        return redirect('yard_pending_cars')
    return render(request, 'marketplace/yard_reject_car.html', {'car': car})

# ========== WHATSAPP ==========
def whatsapp_chat(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    phone_number = "+255757170544"
    message = f"Hello, I'm interested in {car.year} {car.make} {car.model}. Price: TZS {car.price:.0f}"
    whatsapp_url = f"https://wa.me/{phone_number}?text={quote(message)}"
    return HttpResponseRedirect(whatsapp_url)

# ========== INSPECTION ==========
def request_inspection(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    if request.method == 'POST':
        messages.success(request, 'Inspection requested! We will contact you within 2 hours.')
        return redirect('car_detail', car_id=car.id)
    return render(request, 'marketplace/request_inspection.html', {'car': car})

# ========== COMPARE ==========
@login_required
def compare_cars(request):
    comparison, _ = ComparisonSet.objects.get_or_create(user=request.user)
    cars = comparison.cars.all()
    return render(request, 'marketplace/compare.html', {'cars': cars})

@login_required
def add_to_comparison(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    comparison, _ = ComparisonSet.objects.get_or_create(user=request.user)
    
    if comparison.cars.count() >= 4:
        messages.warning(request, 'You can compare up to 4 cars.')
    elif car in comparison.cars.all():
        messages.info(request, 'Car already in comparison.')
    else:
        comparison.cars.add(car)
        messages.success(request, f'{car.make} {car.model} added to comparison.')
    
    return redirect(request.META.get('HTTP_REFERER', 'car_list'))

@login_required
def remove_from_comparison(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    comparison = ComparisonSet.objects.get(user=request.user)
    comparison.cars.remove(car)
    messages.success(request, 'Car removed from comparison.')
    return redirect('compare_cars')

# ========== OTHER VIEWS ==========
def sell_car(request):
    return render(request, 'marketplace/sell_car.html')

def profile(request):
    return render(request, 'marketplace/profile.html', {'user': request.user})

def car_valuation(request):
    return render(request, 'marketplace/valuation_form.html')

def create_listing(request):
    return redirect('dealer_add_car')

@login_required
def mark_as_sold(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.user.userprofile.role != 'buyer':
        messages.error(request, 'Only buyers can mark cars as sold.')
        return redirect('car_detail', car_id=car.id)
    
    from .models import SoldRequest
    sold_request = SoldRequest.objects.create(
        car=car,
        buyer=request.user,
        dealer=car.seller,
        status='pending'
    )
    
    messages.success(request, f'Purchase reported! The dealer will confirm the sale.')
    return redirect('car_detail', car_id=car.id)

@login_required
def dealer_sold_requests(request):
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    from .models import SoldRequest
    pending_requests = SoldRequest.objects.filter(dealer=request.user, status='pending')
    
    context = {
        'pending_requests': pending_requests,
        'pending_count': pending_requests.count(),
    }
    return render(request, 'marketplace/dealer_sold_requests.html', context)

@login_required
def approve_sold(request, request_id):
    from .models import SoldRequest
    sold_request = get_object_or_404(SoldRequest, id=request_id, dealer=request.user)
    
    sold_request.status = 'approved'
    sold_request.responded_at = timezone.now()
    sold_request.save()
    
    car = sold_request.car
    car.status = 'sold'
    car.save()
    
    messages.success(request, f'Confirmed: {car.make} {car.model} is sold!')
    return redirect('dealer_sold_requests')

@login_required
def reject_sold(request, request_id):
    from .models import SoldRequest
    sold_request = get_object_or_404(SoldRequest, id=request_id, dealer=request.user)
    
    sold_request.status = 'rejected'
    sold_request.responded_at = timezone.now()
    sold_request.save()
    
    messages.warning(request, f'Purchase request for {sold_request.car.make} {sold_request.car.model} was rejected.')
    return redirect('dealer_sold_requests')

# ========== SOLD CAR WORKFLOW ==========
from .models import SoldRequest
from django.utils import timezone

@login_required
def mark_as_sold(request, car_id):
    """Buyer marks a car as sold"""
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.user.userprofile.role != 'buyer':
        messages.error(request, 'Only buyers can mark cars as sold.')
        return redirect('car_detail', car_id=car.id)
    
    # Check if already marked as sold
    if car.status == 'sold':
        messages.warning(request, 'This car is already marked as sold.')
        return redirect('car_detail', car_id=car.id)
    
    # Create sold request
    sold_request = SoldRequest.objects.create(
        car=car,
        buyer=request.user,
        dealer=car.seller,
        status='pending'
    )
    
    messages.success(request, f'Purchase reported! The dealer will confirm the sale.')
    return redirect('car_detail', car_id=car.id)

@login_required
def dealer_sold_requests(request):
    """Dealer views pending sold requests"""
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    pending_requests = SoldRequest.objects.filter(dealer=request.user, status='pending')
    approved_requests = SoldRequest.objects.filter(dealer=request.user, status='approved')
    rejected_requests = SoldRequest.objects.filter(dealer=request.user, status='rejected')
    
    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'pending_count': pending_requests.count(),
    }
    return render(request, 'marketplace/dealer_sold_requests.html', context)

@login_required
def approve_sold(request, request_id):
    """Dealer approves sold request"""
    sold_request = get_object_or_404(SoldRequest, id=request_id, dealer=request.user)
    
    sold_request.status = 'approved'
    sold_request.responded_at = timezone.now()
    sold_request.save()
    
    # Update car status
    car = sold_request.car
    car.status = 'sold'
    car.save()
    
    messages.success(request, f'Confirmed: {car.make} {car.model} is sold!')
    return redirect('dealer_sold_requests')

@login_required
def reject_sold(request, request_id):
    """Dealer rejects sold request"""
    sold_request = get_object_or_404(SoldRequest, id=request_id, dealer=request.user)
    
    sold_request.status = 'rejected'
    sold_request.responded_at = timezone.now()
    sold_request.save()
    
    messages.warning(request, f'Purchase request for {sold_request.car.make} {sold_request.car.model} was rejected.')
    return redirect('dealer_sold_requests')

@login_required
def yard_add_car(request):
    """Yard manager adds a car to their yard"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Only yard managers can add cars.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    
    if not yards:
        messages.error(request, 'You need to be assigned to a yard first.')
        return redirect('yard_manager_dashboard')
    
    if request.method == 'POST':
        try:
            yard_id = request.POST.get('yard')
            yard = CarYard.objects.get(id=yard_id, manager=request.user)
            
            car = CarListing.objects.create(
                title=request.POST.get('title'),
                make=request.POST.get('make'),
                model=request.POST.get('model'),
                year=request.POST.get('year'),
                price=request.POST.get('price'),
                mileage=request.POST.get('mileage'),
                condition=request.POST.get('condition', 'used'),
                transmission=request.POST.get('transmission', 'manual'),
                fuel_type=request.POST.get('fuel_type', 'petrol'),
                description=request.POST.get('description', ''),
                package=request.POST.get('package', 'normal'),
                seller=request.user,
                yard=yard,
                status='approved'
            )
            
            if request.FILES.get('images'):
                car.images = request.FILES['images']
                car.save()
            
            messages.success(request, f'{car.make} {car.model} added to {yard.name}!')
            return redirect('yard_my_cars')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'marketplace/yard_add_car.html', {'yards': yards})


from .models import YardDealerAssignment

@login_required
def yard_assign_dealer(request):
    """Yard manager assigns a dealer to their yard"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    
    if not yards:
        messages.error(request, 'You need to be assigned to a yard first.')
        return redirect('yard_manager_dashboard')
    
    # Get dealers not already assigned to these yards
    assigned_dealer_ids = YardDealerAssignment.objects.filter(
        yard__in=yards, 
        is_active=True
    ).values_list('dealer_id', flat=True)
    
    available_dealers = User.objects.filter(
        userprofile__role='dealer'
    ).exclude(id__in=assigned_dealer_ids)
    
    if request.method == 'POST':
        yard_id = request.POST.get('yard')
        dealer_id = request.POST.get('dealer')
        
        yard = CarYard.objects.get(id=yard_id, manager=request.user)
        dealer = User.objects.get(id=dealer_id)
        
        # Check if already assigned
        assignment, created = YardDealerAssignment.objects.get_or_create(
            yard=yard,
            dealer=dealer,
            defaults={'assigned_by': request.user}
        )
        
        if created:
            messages.success(request, f'Dealer {dealer.username} assigned to {yard.name}!')
        else:
            messages.info(request, 'Dealer already assigned to this yard.')
        
        return redirect('yard_assigned_dealers')
    
    context = {
        'yards': yards,
        'available_dealers': available_dealers,
    }
    return render(request, 'marketplace/yard_assign_dealer.html', context)

@login_required
def yard_assigned_dealers(request):
    """View all dealers assigned to yard manager's yards"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    assignments = YardDealerAssignment.objects.filter(
        yard__in=yards, 
        is_active=True
    ).select_related('dealer', 'yard')
    
    context = {
        'assignments': assignments,
        'yards': yards,
        'total_dealers': assignments.count(),
    }
    return render(request, 'marketplace/yard_assigned_dealers.html', context)

@login_required
def yard_remove_dealer(request, assignment_id):
    """Yard manager removes a dealer from their yard"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(YardDealerAssignment, id=assignment_id)
    
    # Verify yard manager owns this yard
    if assignment.yard.manager != request.user:
        messages.error(request, 'You can only remove dealers from your yards.')
        return redirect('yard_assigned_dealers')
    
    if request.method == 'POST':
        assignment.is_active = False
        assignment.save()
        messages.success(request, f'Dealer {assignment.dealer.username} removed from {assignment.yard.name}.')
        return redirect('yard_assigned_dealers')
    
    return render(request, 'marketplace/yard_remove_dealer.html', {'assignment': assignment})


# ========== DEALER COMMISSION DASHBOARD ==========
@login_required
def dealer_commission_dashboard(request):
    """Dealer views their commission earnings"""
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    from django.db.models import Sum
    
    commissions = DealerCommission.objects.filter(dealer=request.user).order_by('-created_at')
    
    # Calculate totals
    total_earned = commissions.filter(status='paid').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    total_pending = commissions.filter(status='pending').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    
    context = {
        'commissions': commissions,
        'total_earned': total_earned,
        'total_pending': total_pending,
        'pending_count': commissions.filter(status='pending').count(),
        'paid_count': commissions.filter(status='paid').count(),
    }
    return render(request, 'marketplace/dealer_commission.html', context)

# ========== FAKE LISTING REPORT ==========
@login_required
def report_fake_listing(request, car_id):
    """Buyer reports a fake or suspicious listing"""
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.method == 'POST':
        report = FakeListingReport.objects.create(
            car=car,
            reported_by=request.user,
            reason=request.POST.get('reason'),
            description=request.POST.get('description')
        )
        messages.success(request, 'Thank you for your report. Our team will investigate within 24 hours.')
        return redirect('car_detail', car_id=car.id)
    
    return render(request, 'marketplace/report_fake_listing.html', {'car': car})

@login_required
def admin_reports_dashboard(request):
    """Admin views all reports"""
    if request.user.userprofile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    reports = FakeListingReport.objects.all().order_by('-created_at')
    pending_reports = reports.filter(status='pending')
    
    context = {
        'reports': reports,
        'pending_reports': pending_reports,
        'pending_count': pending_reports.count(),
        'investigating_count': reports.filter(status='investigating').count(),
        'resolved_count': reports.filter(status='resolved').count(),
    }
    return render(request, 'marketplace/admin_reports.html', context)

@login_required
def resolve_report(request, report_id):
    """Admin resolves a report"""
    if request.user.userprofile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    report = get_object_or_404(FakeListingReport, id=report_id)
    
    if request.method == 'POST':
        report.status = request.POST.get('status')
        report.admin_notes = request.POST.get('admin_notes', '')
        report.resolved_at = timezone.now()
        report.save()
        
        # If report is resolved and car is fake, hide the listing
        if report.status == 'resolved' and request.POST.get('hide_car') == 'on':
            report.car.status = 'rejected'
            report.car.save()
        
        messages.success(request, f'Report #{report.id} has been updated.')
        return redirect('admin_reports_dashboard')
    
    return render(request, 'marketplace/resolve_report.html', {'report': report})

# ========== ABOUT US PAGE ==========
def about_us(request):
    """About us page - trust building"""
    from django.contrib.auth.models import User
    from django.db.models import Count, Sum
    
    # Statistics for trust building
    total_cars = CarListing.objects.filter(status='approved').count()
    total_dealers = User.objects.filter(userprofile__role='dealer').count()
    total_buyers = User.objects.filter(userprofile__role='buyer').count()
    total_verified = User.objects.filter(userprofile__verification_level=3).count()
    
    context = {
        'total_cars': total_cars,
        'total_dealers': total_dealers,
        'total_buyers': total_buyers,
        'total_verified': total_verified,
    }
    return render(request, 'marketplace/about_us.html', context)


def about_us(request):
    """About us page - trust building"""
    from django.contrib.auth.models import User
    from django.db.models import Count
    
    total_cars = CarListing.objects.filter(status='approved').count()
    total_dealers = User.objects.filter(userprofile__role='dealer').count()
    total_yard_managers = User.objects.filter(userprofile__role='yard_manager').count()
    total_buyers = User.objects.filter(userprofile__role='buyer').count()
    total_verified = User.objects.filter(userprofile__verification_level=3).count()
    
    # Get recent reviews (example data)
    recent_reviews = []
    
    context = {
        'total_cars': total_cars,
        'total_dealers': total_dealers,
        'total_yard_managers': total_yard_managers,
        'total_buyers': total_buyers,
        'total_verified': total_verified,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'marketplace/about_us.html', context)