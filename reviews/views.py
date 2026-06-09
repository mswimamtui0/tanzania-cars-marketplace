from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from marketplace.models import CarListing
from .models import Review

@login_required
def add_review(request, car_id):
    car = get_object_or_404(CarListing, id=car_id)
    
    if request.method == 'POST':
        review = Review.objects.create(
            reviewer=request.user,
            car=car,
            rating=int(request.POST.get('rating')),
            title=request.POST.get('title'),
            comment=request.POST.get('comment'),
            pros=request.POST.get('pros', ''),
            cons=request.POST.get('cons', ''),
            verified_purchase=True  # Should check actual purchase
        )
        messages.success(request, 'Thank you for your review!')
        return redirect('car_detail', car_id=car.id)
    
    return render(request, 'reviews/add_review.html', {'car': car})