from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from marketplace.models import CarListing
from .models import Reservation

@login_required
def create_reservation(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.method == 'POST':
        reservation = Reservation.objects.create(
            buyer=request.user,
            car=car,
            has_part_exchange=request.POST.get('has_part_exchange') == 'on',
            wants_finance=request.POST.get('wants_finance') == 'on',
            delivery_required=request.POST.get('delivery_required') == 'on',
            delivery_address=request.POST.get('delivery_address', ''),
            expires_at=timezone.now() + timedelta(days=3)
        )
        
        # Update car status
        car.status = 'reserved'
        car.save()
        
        messages.success(request, f'Car reserved! Please complete payment within 3 days.')
        return redirect('checkout', reservation_id=reservation.id)
    
    return render(request, 'reservations/reserve_form.html', {'car': car})

@login_required
def checkout(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, buyer=request.user)
    return render(request, 'reservations/checkout.html', {'reservation': reservation})