from django.contrib import admin
from .models import (
    Car, CarImage, Dealer, Yard, YardDealerAssignment, DealerAssignment,
    Favorite, Review, Report, Message, InspectionRequest, ListingPackage
)

admin.site.register(Car)
admin.site.register(CarImage)
admin.site.register(Dealer)
admin.site.register(Yard)
admin.site.register(YardDealerAssignment)
admin.site.register(DealerAssignment)
admin.site.register(Favorite)
admin.site.register(Review)
admin.site.register(Report)
admin.site.register(Message)
admin.site.register(InspectionRequest)
admin.site.register(ListingPackage)




@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role']
    search_fields = ['user__username', 'phone']

@admin.register(CarYard)
class CarYardAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'city', 'rating']
    list_filter = ['city']
    search_fields = ['name']

@admin.register(CarListing)
class CarListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'make', 'model', 'year', 'price', 'status', 'views_count']
    list_filter = ['make', 'condition', 'transmission', 'fuel_type', 'status']
    search_fields = ['title', 'make', 'model', 'seller__username']
    list_editable = ['status']
    list_per_page = 20
    
    fieldsets = (
        ('Car Information', {
            'fields': ('title', 'make', 'model', 'year', 'price', 'mileage', 'condition', 'transmission', 'fuel_type')
        }),
        ('Description & Images', {
            'fields': ('description', 'images')
        }),
        ('Seller & Status', {
            'fields': ('seller', 'yard', 'package', 'status', 'is_featured')
        }),
    )

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'added_at']

@admin.register(ComparisonSet)
class ComparisonSetAdmin(admin.ModelAdmin):
    list_display = ['user', 'car_count', 'created_at']
    
    def car_count(self, obj):
        return obj.cars.count()
    car_count.short_description = 'Number of Cars'