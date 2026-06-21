from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, 
    Car, 
    CarListing, 
    Dealer, 
    Yard, 
    YardDealerAssignment, 
    DealerAssignment,
    Favorite, 
    Review, 
    Report, 
    Message, 
    InspectionRequest, 
    ListingPackage,
    CarImage
)

# ========================================
# CUSTOM USER ADMIN
# ========================================

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ========================================
# USER PROFILE ADMIN
# ========================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'verification_level', 'verified_badge', 'created_at')
    list_filter = ('role', 'verification_level', 'verified_badge', 'email_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'company_name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'phone', 'email_verified')
        }),
        ('Verification', {
            'fields': ('verification_level', 'id_uploaded', 'location_verified', 'verified_badge')
        }),
        ('Business Information', {
            'fields': ('company_name', 'whatsapp_number')
        }),
        ('Commission & Sales', {
            'fields': ('commission_rate', 'total_sales', 'total_commission', 'is_active_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ========================================
# CAR ADMIN
# ========================================

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'make', 'model', 'year', 'price', 'seller', 'is_approved', 'is_sold', 'featured', 'created_at')
    list_filter = ('is_approved', 'is_sold', 'featured', 'condition', 'fuel_type', 'transmission', 'year', 'created_at')
    search_fields = ('title', 'make', 'model', 'description', 'seller__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'price', 'year', 'make', 'model')
        }),
        ('Vehicle Details', {
            'fields': ('mileage', 'fuel_type', 'transmission', 'body_type', 'color', 'condition')
        }),
        ('Media', {
            'fields': ('images', 'video_url')
        }),
        ('Listing Status', {
            'fields': ('is_approved', 'is_sold', 'featured', 'is_negotiable')
        }),
        ('Seller', {
            'fields': ('seller',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ========================================
# CAR LISTING ADMIN
# ========================================

@admin.register(CarListing)
class CarListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'make', 'model', 'year', 'price', 'seller', 'is_approved', 'is_sold', 'featured', 'created_at')
    list_filter = ('is_approved', 'is_sold', 'featured', 'condition', 'fuel_type', 'transmission', 'year', 'created_at')
    search_fields = ('title', 'make', 'model', 'description', 'seller__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'price', 'year', 'make', 'model')
        }),
        ('Vehicle Details', {
            'fields': ('mileage', 'fuel_type', 'transmission', 'body_type', 'color', 'condition')
        }),
        ('Media', {
            'fields': ('images', 'video_url')
        }),
        ('Listing Status', {
            'fields': ('is_approved', 'is_sold', 'featured', 'is_negotiable')
        }),
        ('Seller', {
            'fields': ('seller',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ========================================
# CAR IMAGE ADMIN
# ========================================

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'caption', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('car__title', 'caption')


# ========================================
# DEALER ADMIN
# ========================================

@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'phone', 'location', 'verification_level', 'is_verified', 'created_at')
    list_filter = ('verification_level', 'is_verified', 'created_at')
    search_fields = ('business_name', 'user__username', 'phone', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('business_name',)
    
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


# ========================================
# YARD ADMIN
# ========================================

@admin.register(Yard)
class YardAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'is_active', 'manager', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'location', 'manager__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        ('Yard Information', {
            'fields': ('name', 'location', 'capacity')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Manager', {
            'fields': ('manager',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ========================================
# YARD DEALER ASSIGNMENT ADMIN
# ========================================

@admin.register(YardDealerAssignment)
class YardDealerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('dealer', 'yard', 'is_active', 'assigned_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('dealer__business_name', 'yard__name', 'assigned_by__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


# ========================================
# DEALER ASSIGNMENT ADMIN
# ========================================

@admin.register(DealerAssignment)
class DealerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('car', 'dealer', 'commission_rate', 'is_active', 'assigned_at')
    list_filter = ('is_active', 'assigned_at')
    search_fields = ('car__title', 'dealer__business_name')
    readonly_fields = ('assigned_at', 'updated_at')


# ========================================
# FAVORITE ADMIN
# ========================================

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'car__title')
    readonly_fields = ('created_at',)


# ========================================
# REVIEW ADMIN
# ========================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'dealer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'car__title', 'dealer__business_name', 'comment')
    readonly_fields = ('created_at', 'updated_at')


# ========================================
# REPORT ADMIN
# ========================================

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


# ========================================
# MESSAGE ADMIN
# ========================================

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'car', 'content_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'content')
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


# ========================================
# INSPECTION REQUEST ADMIN
# ========================================

@admin.register(InspectionRequest)
class InspectionRequestAdmin(admin.ModelAdmin):
    list_display = ('car', 'requested_by', 'scheduled_date', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('car__title', 'requested_by__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Inspection Information', {
            'fields': ('car', 'requested_by', 'scheduled_date', 'notes')
        }),
        ('Status', {
            'fields': ('status', 'inspection_fee', 'inspection_report', 'completed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ========================================
# LISTING PACKAGE ADMIN
# ========================================

@admin.register(ListingPackage)
class ListingPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_featured', 'is_premium', 'created_at')
    list_filter = ('is_featured', 'is_premium', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('price',)


# ========================================
# SITE SETUP - Custom Admin Header
# ========================================

admin.site.site_header = "Tanzania Car Marketplace Admin"
admin.site.site_title = "Tanzania Car Marketplace"
admin.site.index_title = "Welcome to Tanzania Car Marketplace Admin Panel"