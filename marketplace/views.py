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
from django.db.models import Sum
from django.contrib.auth.models import User
from datetime import timedelta
from .models import (
    UserProfile, CarListing, CarYard, Wishlist, ComparisonSet, 
    SoldRequest, Reservation, InspectionRequest, DealerCommission, 
    FakeListingReport, YardDealerAssignment, Message
)

# ========== HOME ==========
def home(request):
    latest_cars = CarListing.objects.filter(status='approved').order_by('-created_at')[:30]
    featured_cars = CarListing.objects.filter(status='approved', is_featured=True)[:6]
    total_latest = CarListing.objects.filter(status='approved').count()
    
    return render(request, 'marketplace/home.html', {
        'latest_cars': latest_cars,
        'featured_cars': featured_cars,
        'total_latest': total_latest,
    })

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
            profile = UserProfile.objects.get(user=user)
            profile.role = role
            profile.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'marketplace/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

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
    context = {
        'total_users': User.objects.count(),
        'total_cars': CarListing.objects.count(),
        'pending_approvals': CarListing.objects.filter(status='pending').count(),
        'approved_cars': CarListing.objects.filter(status='approved').count(),
        'pending_cars': CarListing.objects.filter(status='pending'),
        'recent_users': User.objects.order_by('-date_joined')[:10],
        'recent_cars': CarListing.objects.order_by('-created_at')[:10],
        'total_yards': CarYard.objects.count(),
        'assigned_yards': CarYard.objects.filter(manager__isnull=False).count(),
        'pending_yards': CarYard.objects.filter(manager__isnull=True).count(),
        'yard_managers': User.objects.filter(userprofile__role='yard_manager').count(),
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
        'pending_approvals': cars.filter(status='pending').count(),
        'yards': yards,
    }
    return render(request, 'marketplace/yard_manager_dashboard.html', context)

@login_required
def buyer_dashboard(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    reservations = Reservation.objects.filter(buyer=request.user)
    inspections = InspectionRequest.objects.filter(buyer=request.user, status='pending')
    messages_list = Message.objects.filter(receiver=request.user)
    unread_messages = messages_list.filter(is_read=False)
    
    context = {
        'wishlist_count': wishlist.count(),
        'recent_wishlist': wishlist.order_by('-added_at')[:5],
        'reservations_count': reservations.count(),
        'active_reservations': reservations.filter(status='confirmed'),
        'recent_reservations': reservations.order_by('-created_at')[:5],
        'unread_messages': unread_messages.count(),
        'pending_inspections': inspections.count(),
        'recent_inspections': inspections[:3],
        'recent_messages': messages_list.order_by('-created_at')[:3],
    }
    return render(request, 'marketplace/buyer_dashboard.html', context)

# ========== WISHLIST ==========
@login_required
def save_car(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, car=car)
    
    if created:
        messages.success(request, f'{car.make} {car.model} added to your wishlist!')
    else:
        wishlist_item.delete()
        messages.info(request, f'{car.make} {car.model} removed from wishlist.')
    
    return redirect('car_detail', car_id=car.id)

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

# ========== YARD MANAGER ==========
@login_required
def yard_add_car(request):
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    
    if not yards:
        messages.error(request, 'You are not assigned to any yard.')
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

@login_required
def yard_my_cars(request):
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
    car.status = 'approved'
    car.save()
    messages.success(request, f'{car.make} {car.model} approved!')
    return redirect('yard_pending_cars')

@login_required
def yard_reject_car(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    car.status = 'rejected'
    car.save()
    messages.success(request, f'{car.make} {car.model} rejected.')
    return redirect('yard_pending_cars')

@login_required
def yard_manage_dealers(request):
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    assigned_dealers = YardDealerAssignment.objects.filter(yard__in=yards, is_active=True)
    assigned_dealer_ids = assigned_dealers.values_list('dealer_id', flat=True)
    pending_dealers = User.objects.filter(
        userprofile__role='dealer'
    ).exclude(id__in=assigned_dealer_ids)
    
    context = {
        'yards': yards,
        'assigned_dealers': assigned_dealers,
        'pending_dealers': pending_dealers,
        'assigned_count': assigned_dealers.count(),
        'pending_count': pending_dealers.count(),
    }
    return render(request, 'marketplace/yard_manage_dealers.html', context)

@login_required
def yard_assign_dealer(request, dealer_id):
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    dealer = get_object_or_404(User, id=dealer_id, userprofile__role='dealer')
    yards = CarYard.objects.filter(manager=request.user)
    
    if request.method == 'POST':
        yard_id = request.POST.get('yard')
        yard = get_object_or_404(CarYard, id=yard_id, manager=request.user)
        
        assignment, created = YardDealerAssignment.objects.get_or_create(
            yard=yard,
            dealer=dealer,
            defaults={'assigned_by': request.user}
        )
        if not created:
            assignment.is_active = True
            assignment.save()
        
        messages.success(request, f'{dealer.username} assigned to {yard.name}!')
        return redirect('yard_manage_dealers')
    
    return render(request, 'marketplace/yard_assign_dealer.html', {'dealer': dealer, 'yards': yards})

@login_required
def yard_remove_dealer(request, assignment_id):
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(YardDealerAssignment, id=assignment_id, yard__manager=request.user)
    assignment.is_active = False
    assignment.save()
    messages.success(request, f'{assignment.dealer.username} removed from {assignment.yard.name}')
    return redirect('yard_manage_dealers')

@login_required
def yard_pending_dealers(request):
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    yards = CarYard.objects.filter(manager=request.user)
    pending_dealers = User.objects.filter(
        userprofile__role='dealer',
        userprofile__verification_level=1
    )
    
    context = {
        'yards': yards,
        'pending_dealers': pending_dealers,
        'pending_count': pending_dealers.count(),
    }
    return render(request, 'marketplace/yard_pending_dealers.html', context)

@login_required
def yard_verify_dealer(request, dealer_id):
    if request.user.userprofile.role != 'yard_manager':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    dealer = get_object_or_404(User, id=dealer_id, userprofile__role='dealer')
    yards = CarYard.objects.filter(manager=request.user)
    
    if request.method == 'POST':
        yard_id = request.POST.get('yard')
        yard = get_object_or_404(CarYard, id=yard_id, manager=request.user)
        level = int(request.POST.get('verification_level', 2))
        
        profile = dealer.userprofile
        profile.verification_level = level
        profile.verified_badge = level == 3
        profile.save()
        
        messages.success(request, f'{dealer.username} verified!')
        return redirect('yard_pending_dealers')
    
    return render(request, 'marketplace/yard_verify_dealer.html', {'dealer': dealer, 'yards': yards})

# ========== ADMIN YARD MANAGEMENT ==========
@login_required
def admin_verify_yard(request):
    if request.user.userprofile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    context = {
        'yard_managers': User.objects.filter(userprofile__role='yard_manager'),
        'pending_yards': CarYard.objects.filter(manager__isnull=True),
        'assigned_yards': CarYard.objects.filter(manager__isnull=False),
        'pending_count': CarYard.objects.filter(manager__isnull=True).count(),
        'assigned_count': CarYard.objects.filter(manager__isnull=False).count(),
    }
    return render(request, 'marketplace/admin_verify_yard.html', context)

@login_required
def admin_assign_yard(request):
    if request.user.userprofile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        yard_id = request.POST.get('yard_id')
        manager_id = request.POST.get('manager_id')
        
        yard = get_object_or_404(CarYard, id=yard_id)
        manager = get_object_or_404(User, id=manager_id, userprofile__role='yard_manager')
        yard.manager = manager
        yard.save()
        messages.success(request, f'{manager.username} assigned to {yard.name}!')
        return redirect('admin_verify_yard')
    
    context = {
        'yards': CarYard.objects.filter(manager__isnull=True),
        'managers': User.objects.filter(userprofile__role='yard_manager'),
    }
    return render(request, 'marketplace/admin_assign_yard.html', context)

@login_required
def admin_create_yard(request):
    if request.user.userprofile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        yard = CarYard.objects.create(
            name=request.POST.get('name'),
            location=request.POST.get('location'),
            city=request.POST.get('city'),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            description=request.POST.get('description', '')
        )
        messages.success(request, f'Yard "{yard.name}" created!')
        return redirect('admin_verify_yard')
    
    return render(request, 'marketplace/admin_create_yard.html')

# ========== WHATSAPP ==========
def whatsapp_chat(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    phone_number = "+255123456789"
    message = f"Hello, I'm interested in {car.year} {car.make} {car.model}. Price: TZS {car.price:.0f}"
    whatsapp_url = f"https://wa.me/{phone_number}?text={quote(message)}"
    return HttpResponseRedirect(whatsapp_url)

# ========== INSPECTION ==========
@login_required
def request_inspection(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    if request.method == 'POST':
        InspectionRequest.objects.create(
            car=car,
            buyer=request.user,
            inspection_date=request.POST.get('inspection_date'),
            location=request.POST.get('location'),
            status='pending'
        )
        messages.success(request, 'Inspection requested!')
        return redirect('buyer_dashboard')
    return render(request, 'marketplace/request_inspection.html', {'car': car})

@login_required
def buyer_inspections(request):
    inspections = InspectionRequest.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'marketplace/buyer_inspections.html', {'inspections': inspections})

# ========== MESSAGES ==========
@login_required
def send_message(request):
    dealers = User.objects.filter(userprofile__role='dealer')
    cars = CarListing.objects.filter(status='approved')
    
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        car_id = request.POST.get('car_id')
        
        receiver = get_object_or_404(User, id=receiver_id)
        car = get_object_or_404(CarListing, id=car_id) if car_id else None
        
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            car=car,
            subject=request.POST.get('subject'),
            content=request.POST.get('content')
        )
        messages.success(request, 'Message sent!')
        return redirect('buyer_messages')
    
    return render(request, 'marketplace/send_message.html', {'dealers': dealers, 'cars': cars})

@login_required
def buyer_messages(request):
    messages_list = Message.objects.filter(receiver=request.user).order_by('-created_at')
    
    for msg in messages_list.filter(is_read=False):
        msg.is_read = True
        msg.save()
    
    context = {
        'messages': messages_list,
        'total_messages': messages_list.count(),
    }
    return render(request, 'marketplace/buyer_messages.html', context)

@login_required
def message_detail(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        messages.error(request, 'Message not found.')
        return redirect('buyer_messages')
    
    if request.user not in [message.sender, message.receiver]:
        messages.error(request, 'Access denied.')
        return redirect('buyer_messages')
    
    if request.user == message.receiver and not message.is_read:
        message.is_read = True
        message.save()
    
    return render(request, 'marketplace/message_detail.html', {'message': message})

@login_required
def reply_message(request, message_id):
    original_message = get_object_or_404(Message, id=message_id)
    
    if request.user != original_message.receiver:
        messages.error(request, 'You cannot reply to this message.')
        return redirect('buyer_messages')
    
    if request.method == 'POST':
        reply = Message.objects.create(
            sender=request.user,
            receiver=original_message.sender,
            subject=request.POST.get('subject', 'RE: ' + original_message.subject),
            content=request.POST.get('content', '')
        )
        messages.success(request, f'Reply sent!')
        return redirect('buyer_messages')
    
    return render(request, 'marketplace/reply_message.html', {'original_message': original_message})

@login_required
def dealer_send_message(request):
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        receiver = get_object_or_404(User, id=request.POST.get('receiver_id'))
        car = get_object_or_404(CarListing, id=request.POST.get('car_id')) if request.POST.get('car_id') else None
        
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            car=car,
            subject=request.POST.get('subject'),
            content=request.POST.get('content')
        )
        messages.success(request, 'Message sent!')
        return redirect('dealer_messages')
    
    context = {
        'buyers': User.objects.filter(userprofile__role='buyer'),
        'cars': CarListing.objects.filter(seller=request.user),
    }
    return render(request, 'marketplace/dealer_send_message.html', context)

@login_required
def dealer_messages(request):
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    context = {
        'sent_messages': Message.objects.filter(sender=request.user).order_by('-created_at'),
        'received_messages': Message.objects.filter(receiver=request.user).order_by('-created_at'),
        'sent_count': Message.objects.filter(sender=request.user).count(),
        'received_count': Message.objects.filter(receiver=request.user).count(),
    }
    return render(request, 'marketplace/dealer_messages.html', context)

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

# ========== SOLD ==========
@login_required
def mark_as_sold(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    SoldRequest.objects.create(
        car=car,
        buyer=request.user,
        dealer=car.seller,
        status='pending'
    )
    messages.success(request, 'Purchase reported!')
    return redirect('car_detail', car_id=car.id)

@login_required
def dealer_sold_requests(request):
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    context = {
        'pending_requests': SoldRequest.objects.filter(dealer=request.user, status='pending'),
        'pending_count': SoldRequest.objects.filter(dealer=request.user, status='pending').count(),
        'approved_requests': SoldRequest.objects.filter(dealer=request.user, status='approved'),
        'rejected_requests': SoldRequest.objects.filter(dealer=request.user, status='rejected'),
    }
    return render(request, 'marketplace/dealer_sold_requests.html', context)

@login_required
def approve_sold(request, request_id):
    sold_request = get_object_or_404(SoldRequest, id=request_id, dealer=request.user)
    sold_request.status = 'approved'
    sold_request.responded_at = timezone.now()
    sold_request.save()
    sold_request.car.status = 'sold'
    sold_request.car.save()
    messages.success(request, 'Sale confirmed!')
    return redirect('dealer_sold_requests')

@login_required
def reject_sold(request, request_id):
    sold_request = get_object_or_404(SoldRequest, id=request_id, dealer=request.user)
    sold_request.status = 'rejected'
    sold_request.responded_at = timezone.now()
    sold_request.save()
    messages.warning(request, 'Sale rejected.')
    return redirect('dealer_sold_requests')

# ========== COMMISSION ==========
@login_required
def dealer_commission_dashboard(request):
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    commissions = DealerCommission.objects.filter(dealer=request.user)
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

# ========== REPORT ==========
@login_required
def report_fake_listing(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.method == 'POST':
        FakeListingReport.objects.create(
            car=car,
            reported_by=request.user,
            reason=request.POST.get('reason'),
            description=request.POST.get('description')
        )
        messages.success(request, 'Report submitted!')
        return redirect('car_detail', car_id=car.id)
    
    return render(request, 'marketplace/report_fake_listing.html', {'car': car})

@login_required
def admin_reports_dashboard(request):
    if request.user.userprofile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    reports = FakeListingReport.objects.all().order_by('-created_at')
    context = {
        'reports': reports,
        'pending_count': reports.filter(status='pending').count(),
        'investigating_count': reports.filter(status='investigating').count(),
        'resolved_count': reports.filter(status='resolved').count(),
    }
    return render(request, 'marketplace/admin_reports.html', context)

@login_required
def resolve_report(request, report_id):
    if request.user.userprofile.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    report = get_object_or_404(FakeListingReport, id=report_id)
    
    if request.method == 'POST':
        report.status = request.POST.get('status')
        report.admin_notes = request.POST.get('admin_notes', '')
        report.resolved_at = timezone.now()
        report.save()
        
        if report.status == 'resolved' and request.POST.get('hide_car') == 'on':
            report.car.status = 'rejected'
            report.car.save()
        
        messages.success(request, 'Report updated!')
        return redirect('admin_reports')
    
    return render(request, 'marketplace/resolve_report.html', {'report': report})

# ========== RESERVATION ==========
@login_required
def create_reservation(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.method == 'POST':
        Reservation.objects.create(
            buyer=request.user,
            car=car,
            status='pending',
            expires_at=timezone.now() + timedelta(days=3)
        )
        messages.success(request, 'Car reserved!')
        return redirect('buyer_dashboard')
    
    return render(request, 'marketplace/reserve_car.html', {'car': car})

# ========== OTHER ==========
def about_us(request):
    context = {
        'total_cars': CarListing.objects.filter(status='approved').count(),
        'total_dealers': User.objects.filter(userprofile__role='dealer').count(),
        'total_buyers': User.objects.filter(userprofile__role='buyer').count(),
        'total_verified': User.objects.filter(userprofile__verification_level=3).count(),
    }
    return render(request, 'marketplace/about_us.html', context)

def sell_car(request):
    return render(request, 'marketplace/sell_car.html')

def profile(request):
    return render(request, 'marketplace/profile.html', {'user': request.user})

def car_valuation(request):
    return render(request, 'marketplace/valuation_form.html')

def create_listing(request):
    return redirect('dealer_add_car')


@login_required
def dealer_message_detail(request, message_id):
    """Dealer views single message"""
    if request.user.userprofile.role != 'dealer':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    message = get_object_or_404(Message, id=message_id)
    
    if message.sender != request.user and message.receiver != request.user:
        messages.error(request, 'Access denied to this message.')
        return redirect('dealer_messages')
    
    if message.receiver == request.user and not message.is_read:
        message.is_read = True
        message.save()
    
    return render(request, 'marketplace/dealer_message_detail.html', {'message': message})