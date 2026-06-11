from django.shortcuts import render
from django.http import JsonResponse
from .models import ValuationRequest

def car_valuation(request):
    result = None
    
    if request.method == 'POST':
        valuation = ValuationRequest.objects.create(
            user=request.user if request.user.is_authenticated else None,
            make=request.POST.get('make'),
            model=request.POST.get('model'),
            year=int(request.POST.get('year')),
            mileage=int(request.POST.get('mileage')),
            condition=request.POST.get('condition')
        )
        estimated_value = valuation.calculate_value()
        valuation.estimated_value = estimated_value
        valuation.save()
        result = {'value': f'{estimated_value:,.0f}', 'make': valuation.make, 'model': valuation.model}
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(result)
    
    return render(request, 'valuation_tool/valuation.html', {'result': result})