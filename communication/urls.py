from django.urls import path
from django.http import HttpResponse

def temp_view(request):
    return HttpResponse("Communication page coming soon")

urlpatterns = [
    path('', temp_view, name='conversations'),
]