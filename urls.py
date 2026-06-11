from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('marketplace.urls')),
    path('valuation/', include('valuation_tool.urls')),
    path('leasing/', include('leasing_module.urls')),
    path('reservations/', include('reservation_system.urls')),
    path('blog/', include('blog_module.urls')),
    path('compare/', include('comparison_tool.urls')),
]

# THIS IS IMPORTANT - serves media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)