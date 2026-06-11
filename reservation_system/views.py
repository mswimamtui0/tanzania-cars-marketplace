from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Reservation
from marketplace.models import CarListing

@login_required
def create_reservation(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.method == 'POST':
        reservation = Reservation.objects.create(
            buyer=request.user,
            car=car,
            has_part_exchange=request.POST.get('has_part_exchange') == 'on',
            part_exchange_car=request.POST.get('part_exchange_car', ''),
            wants_finance=request.POST.get('wants_finance') == 'on',
            finance_amount=request.POST.get('finance_amount') if request.POST.get('wants_finance') else None,
            delivery_required=request.POST.get('delivery_required') == 'on',
            delivery_address=request.POST.get('delivery_address', ''),
            expires_at=timezone.now() + timedelta(days=3)
        )
        messages.success(request, f'Car reserved! Complete payment within 3 days.')
        return redirect('reservation_checkout', reservation_id=reservation.id)
    
    return render(request, 'reservation_system/reserve.html', {'car': car})

@login_required
def reservation_checkout(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, buyer=request.user)
    return render(request, 'reservation_system/checkout.html', {'reservation': reservation})