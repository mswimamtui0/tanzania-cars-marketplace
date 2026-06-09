from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.parse import quote
from .models import UserProfile, CarListing, CarYard, ChatSession, InspectionRequest

# ========== HOME VIEW ==========
def home(request):
    """Homepage view"""
    featured_cars = CarListing.objects.filter(status='approved')[:6]
    return render(request, 'marketplace/home.html', {'featured_cars': featured_cars})

# ========== CAR LISTINGS ==========
def car_list(request):
    """List all cars"""
    cars = CarListing.objects.filter(status='approved')
    query = request.GET.get('q', '')
    if query:
        cars = cars.filter(make__icontains=query) | cars.filter(model__icontains=query)
    return render(request, 'marketplace/car_list.html', {'cars': cars})

def car_detail(request, car_id):
    """Car detail view"""
    car = get_object_or_404(CarListing, id=car_id, status='approved')
    car.views_count += 1
    car.save()
    return render(request, 'marketplace/car_detail.html', {'car': car})

# ========== AUTHENTICATION ==========
class CustomLoginView(LoginView):
    template_name = 'marketplace/login.html'
    
    def get_success_url(self):
        return reverse('dashboard')

def register(request):
    """User registration"""
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

# ========== DASHBOARD ==========
@login_required
def dashboard(request):
    role = request.user.userprofile.role
    context = {'role': role}
    
    if role == 'admin' or request.user.is_superuser:
        from django.contrib.auth.models import User
        total_users = User.objects.count()
        total_cars = CarListing.objects.count()
        pending_approvals = CarListing.objects.filter(status='pending').count()
        context.update({
            'total_users': total_users,
            'total_cars': total_cars,
            'pending_approvals': pending_approvals,
        })
    elif role == 'dealer':
        listings = CarListing.objects.filter(seller=request.user)
        context['listings'] = listings
        context['total_listings'] = listings.count()
    
    return render(request, 'marketplace/dashboard.html', context)

# ========== DEALER CAR MANAGEMENT ==========
@login_required
def dealer_add_car(request):
    """Dealer adds a new car listing"""
    if request.user.userprofile.role not in ['dealer', 'yard_manager', 'admin']:
        messages.error(request, 'Only dealers and yard managers can add cars.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
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
                description=request.POST.get('description'),
                package=request.POST.get('package', 'normal'),
                seller=request.user,
                status='pending'
            )
            messages.success(request, f'{car.make} {car.model} has been added and is pending approval!')
            return redirect('dealer_my_cars')
        except Exception as e:
            messages.error(request, f'Error adding car: {str(e)}')
    
    return render(request, 'marketplace/dealer_add_car.html')

@login_required
def dealer_my_cars(request):
    """Dealer views all their cars"""
    if request.user.userprofile.role not in ['dealer', 'yard_manager', 'admin']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    cars = CarListing.objects.filter(seller=request.user).order_by('-created_at')
    
    total_cars = cars.count()
    approved_cars = cars.filter(status='approved').count()
    pending_cars = cars.filter(status='pending').count()
    sold_cars = cars.filter(status='sold').count()
    
    context = {
        'cars': cars,
        'total_cars': total_cars,
        'approved_cars': approved_cars,
        'pending_cars': pending_cars,
        'sold_cars': sold_cars,
    }
    return render(request, 'marketplace/dealer_my_cars.html', context)

@login_required
def dealer_edit_car(request, car_id):
    """Dealer edits their car listing"""
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
        messages.success(request, 'Car updated successfully!')
        return redirect('dealer_my_cars')
    
    return render(request, 'marketplace/dealer_edit_car.html', {'car': car})

@login_required
def dealer_delete_car(request, car_id):
    """Dealer deletes their car listing"""
    car = get_object_or_404(CarListing, id=car_id, seller=request.user)
    
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Car deleted successfully!')
        return redirect('dealer_my_cars')
    
    return render(request, 'marketplace/dealer_delete_car.html', {'car': car})

# ========== SELL CAR ==========
def sell_car(request):
    """Sell car page with listing packages"""
    if request.method == 'POST':
        seller = request.user if request.user.is_authenticated else None
        car = CarListing.objects.create(
            title=f"{request.POST.get('year')} {request.POST.get('make')} {request.POST.get('model')}",
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
            seller=seller,
            status='pending'
        )
        messages.success(request, 'Your car has been submitted for review!')
        return redirect('home')
    return render(request, 'marketplace/sell_car.html')

# ========== WHATSAPP CHAT ==========
def whatsapp_chat(request, car_id):
    """Handle WhatsApp chat routing based on seller verification level"""
    car = get_object_or_404(CarListing, id=car_id)
    seller_level = 1
    if car.seller and hasattr(car.seller, 'userprofile'):
        seller_level = car.seller.userprofile.verification_level
    
    if seller_level >= 3:
        phone_number = "+255123456789"
        message = f"Hello, I'm interested in {car.year} {car.make} {car.model} (ID: {car.id}). Price: TZS {car.price:.0f}"
    else:
        phone_number = "+255123456789"
        message = f"Hello, I'm interested in {car.year} {car.make} {car.model} (ID: {car.id}). Price: TZS {car.price:.0f}. Please assist me with this vehicle."
    
    encoded_message = quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
    return HttpResponseRedirect(whatsapp_url)

# ========== INSPECTION REQUEST ==========
def request_inspection(request, car_id):
    """Request vehicle inspection"""
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.method == 'POST':
        messages.success(request, f'Inspection requested! We will contact you within 2 hours to confirm.')
        return redirect('car_detail', car_id=car.id)
    
    return render(request, 'marketplace/request_inspection.html', {'car': car})

# ========== PROFILE ==========
def profile(request):
    return render(request, 'marketplace/profile.html', {'user': request.user})

def create_listing(request):
    return render(request, 'marketplace/create_listing.html')

def edit_listing(request, car_id):
    return render(request, 'marketplace/edit_listing.html')

def car_valuation(request):
    return render(request, 'marketplace/valuation_form.html')
# ========== YARD MANAGER VIEWS ==========
@login_required
def yard_manager_cars(request):
    """Yard manager views cars in their yards"""
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Only yard managers can access this page.')
        return redirect('dashboard')
    
    # Get yards managed by this yard manager
    yards = CarYard.objects.filter(manager=request.user)
    
    # Get all cars in those yards
    cars = CarListing.objects.filter(yard__in=yards).order_by('-created_at')
    
    context = {
        'cars': cars,
        'yards': yards,
        'total_cars': cars.count(),
    }
    return render(request, 'marketplace/yard_manager_cars.html', context)