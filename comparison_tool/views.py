from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ComparisonSet
from marketplace.models import CarListing

@login_required
def compare_cars(request):
    comparison, created = ComparisonSet.objects.get_or_create(user=request.user)
    cars = comparison.cars.all()
    return render(request, 'comparison_tool/compare.html', {'cars': cars})

@login_required
def add_to_comparison(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    comparison, _ = ComparisonSet.objects.get_or_create(user=request.user)
    
    if comparison.cars.count() >= 4:
        messages.warning(request, 'You can compare up to 4 cars at a time.')
    elif car in comparison.cars.all():
        messages.info(request, 'Car already in comparison.')
    else:
        comparison.cars.add(car)
        messages.success(request, f'{car.make} {car.model} added to comparison.')
    
    return redirect(request.META.get('HTTP_REFERER', 'compare_cars'))

@login_required
def remove_from_comparison(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    comparison = ComparisonSet.objects.get(user=request.user)
    comparison.cars.remove(car)
    messages.success(request, 'Car removed from comparison.')
    return redirect('compare_cars')