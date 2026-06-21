from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from urllib.parse import quote
from .models import CarListing, ChatSession, UserProfile


def contact(request):
    return render(request, 'marketplace/contact.html')


def whatsapp_chat(request, car_id):
    """Handle WhatsApp chat routing based on seller verification level"""
    car = get_object_or_404(CarListing, id=car_id, status='approved')
    seller_level = car.seller.userprofile.verification_level
    
    # Determine chat routing based on seller verification level
    if seller_level >= 3:
        # Fully verified - direct to seller
        route_to = 'seller'
        phone_number = car.seller.userprofile.phone
        message = f"Hello, I'm interested in {car.year} {car.make} {car.model} (ID: {car.id}). Price: TZS {car.price:.0f}"
    else:
        # Level 1 or 2 - route to platform agent
        route_to = 'agent'
        # Get available agent
        agent = UserProfile.objects.filter(role='agent', is_active_agent=True).first()
        if agent:
            phone_number = agent.user.userprofile.phone
        else:
            # Fallback to admin number
            phone_number = "+255123456789"  # Replace with your platform number
        
        message = f"Hello, I'm interested in {car.year} {car.make} {car.model} (ID: {car.id}). Price: TZS {car.price:.0f}. Please assist me with this vehicle."
    
    # Create chat session record
    chat_session = ChatSession.objects.create(
        car=car,
        buyer_name=request.GET.get('name', 'Customer'),
        buyer_phone=request.GET.get('phone', ''),
        route_to=route_to,
        assigned_agent=agent.user if route_to == 'agent' else None
    )
    
    # Create WhatsApp URL
    encoded_message = quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
    
    return HttpResponseRedirect(whatsapp_url)