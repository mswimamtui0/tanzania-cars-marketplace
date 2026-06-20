from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Car, CarImage, Dealer, Yard, YardDealerAssignment, DealerAssignment,
    Favorite, Review, Report, Message, InspectionRequest, ListingPackage
)

# Customize User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Car Admin
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'model', 'year', 'price', 'status', 'seller', 'created_at')
    list_filter = ('status', 'condition', 'fuel_type', 'transmission', 'year', 'is_featured')
    search_fields = ('title', 'brand', 'model', 'description', 'seller__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'brand', 'model', 'year', 'price', 'mileage')
        }),
        ('Details', {
            'fields': ('fuel_type', 'transmission', 'color', 'description', 'condition', 'location')
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'is_verified')
        }),
        ('Relationships', {
            'fields': ('seller', 'dealer', 'yard')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# CarImage Admin
@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'caption', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('car__title', 'caption')

# Dealer Admin
@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'phone', 'location', 'verification_level', 'is_verified')
    list_filter = ('verification_level', 'is_verified', 'created_at')
    search_fields = ('business_name', 'user__username', 'phone', 'location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Business Information', {
            'fields': ('business_name', 'description', 'phone', 'location', 'website')
        }),
        ('Verification', {
            'fields': ('verification_level', 'is_verified')
        }),
        ('Commission', {
            'fields': ('commission_rate',)
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Yard Admin
@admin.register(Yard)
class YardAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'is_active', 'manager', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'location', 'manager__username')
    readonly_fields = ('created_at', 'updated_at')

# YardDealerAssignment Admin
@admin.register(YardDealerAssignment)
class YardDealerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('dealer', 'yard', 'is_active', 'assigned_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('dealer__business_name', 'yard__name', 'assigned_by__username')
    readonly_fields = ('created_at', 'updated_at')

# DealerAssignment Admin
@admin.register(DealerAssignment)
class DealerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('car', 'dealer', 'commission_rate', 'is_active', 'assigned_at')
    list_filter = ('is_active', 'assigned_at')
    search_fields = ('car__title', 'dealer__business_name')
    readonly_fields = ('assigned_at', 'updated_at')

# Favorite Admin
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'car__title')
    readonly_fields = ('created_at',)

# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'dealer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'car__title', 'dealer__business_name', 'comment')
    readonly_fields = ('created_at', 'updated_at')

# Report Admin
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('car', 'reported_by', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('car__title', 'reported_by__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Report Information', {
            'fields': ('car', 'reported_by', 'reason', 'description')
        }),
        ('Status', {
            'fields': ('status', 'resolved_by', 'resolution_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'car', 'content_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'content')
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

# InspectionRequest Admin
@admin.register(InspectionRequest)
class InspectionRequestAdmin(admin.ModelAdmin):
    list_display = ('car', 'requested_by', 'scheduled_date', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('car__title', 'requested_by__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')

# ListingPackage Admin
@admin.register(ListingPackage)
class ListingPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_featured', 'is_premium')
    list_filter = ('is_featured', 'is_premium')
    search_fields = ('name', 'description')