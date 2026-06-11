from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import LeasePlan, LeaseApplication
from marketplace.models import CarListing

def lease_calculator(request, car_id=None):
    car = get_object_or_404(CarListing, id=car_id) if car_id else None
    result = None
    
    if request.method == 'POST':
        car_price = float(request.POST.get('car_price', 0))
        down_payment = float(request.POST.get('down_payment', 0))
        months = int(request.POST.get('months', 36))
        interest_rate = float(request.POST.get('interest_rate', 5.9))
        
        loan_amount = car_price - down_payment
        monthly_interest = (interest_rate / 100) / 12
        
        if monthly_interest > 0:
            monthly_payment = loan_amount * (monthly_interest * (1 + monthly_interest) ** months) / ((1 + monthly_interest) ** months - 1)
        else:
            monthly_payment = loan_amount / months
        
        result = {
            'monthly_payment': round(monthly_payment, 2),
            'total_payment': round(monthly_payment * months, 2),
            'total_interest': round((monthly_payment * months) - loan_amount, 2),
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(result)
    
    return render(request, 'leasing_module/calculator.html', {'car': car, 'result': result})

@login_required
def apply_for_lease(request, plan_id):
    plan = get_object_or_404(LeasePlan, id=plan_id)
    
    if request.method == 'POST':
        application = LeaseApplication.objects.create(
            user=request.user,
            lease_plan=plan,
            employment_status=request.POST.get('employment_status'),
            annual_income=request.POST.get('annual_income'),
        )
        messages.success(request, 'Lease application submitted! We will contact you within 24 hours.')
        return redirect('dashboard')
    
    return render(request, 'leasing_module/apply.html', {'plan': plan})