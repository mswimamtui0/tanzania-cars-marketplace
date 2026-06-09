from .models import CarListing

def site_info(request):
    return {
        'site_name': 'Tanzania Car Marketplace',
        'site_description': 'Buy and sell cars in Tanzania',
        'total_cars': CarListing.objects.filter(is_approved=True).count(),
    }