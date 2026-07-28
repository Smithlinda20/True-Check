from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import (
    User, UserProfile, Service, ServicePackage, 
    BackgroundCheckRequest, Payment, Invoice, 
    VerificationResult, Notification
)

# User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'user_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'username', 'company_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Authentication', {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Account Type', {'fields': ('user_type', 'company_name')}),
        ('Verification', {'fields': ('is_verified', 'verification_date')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    ordering = ('-created_at',)

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'city', 'country')
    list_filter = ('gender', 'country', 'updated_at')
    search_fields = ('user__email', 'national_id', 'passport_number')
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal', {'fields': ('date_of_birth', 'gender')}),
        ('Identification', {'fields': ('national_id', 'passport_number')}),
        ('Address', {'fields': ('address', 'city', 'state', 'country', 'zip_code')}),
        ('Profile', {'fields': ('profile_picture', 'bio')}),
        ('Timestamps', {'fields': ('updated_at',), 'classes': ('collapse',)}),
    )

# Service Admin
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'base_price', 'processing_time_days', 'is_active')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Service Info', {'fields': ('name', 'description')}),
        ('Pricing', {'fields': ('base_price', 'processing_time_days')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

# ServicePackage Admin
@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_type', 'price', 'discount_percentage', 'is_active')
    list_filter = ('package_type', 'is_active', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('services',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Package Info', {'fields': ('name', 'package_type', 'description')}),
        ('Services', {'fields': ('services',)}),
        ('Pricing', {'fields': ('price', 'discount_percentage')}),
        ('Details', {'fields': ('processing_time_days', 'features')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

# BackgroundCheckRequest Admin
@admin.register(BackgroundCheckRequest)
class BackgroundCheckRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'user_email', 'status_badge', 'package', 'total_amount', 'requested_at')
    list_filter = ('status', 'package', 'requested_at')
    search_fields = ('request_id', 'user__email', 'applicant_email', 'applicant_name')
    readonly_fields = ('request_id', 'requested_at', 'started_at', 'completed_at')
    filter_horizontal = ('selected_services',)
    
    fieldsets = (
        ('Request Info', {'fields': ('request_id', 'user', 'package', 'selected_services')}),
        ('Applicant', {'fields': ('applicant_name', 'applicant_email', 'applicant_phone', 'company_name', 'position_applied')}),
        ('Status & Dates', {'fields': ('status', 'requested_at', 'started_at', 'completed_at', 'due_date')}),
        ('Amount', {'fields': ('total_amount',)}),
        ('Review', {'fields': ('admin_notes', 'result_summary', 'documents')}),
    )
    ordering = ('-requested_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFC107',
            'UNDER_REVIEW': '#3498DB',
            'IN_PROGRESS': '#9B59B6',
            'VERIFICATION_REQUIRED': '#E67E22',
            'COMPLETED': '#27AE60',
            'FAILED': '#E74C3C',
            'REJECTED': '#C0392B',
            'CANCELLED': '#95A5A6',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#95A5A6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user_email', 'amount', 'status_badge', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('payment_id', 'user__email', 'transaction_id')
    readonly_fields = ('payment_id', 'created_at', 'completed_at')
    
    fieldsets = (
        ('Payment Info', {'fields': ('payment_id', 'check_request', 'user')}),
        ('Amount & Status', {'fields': ('amount', 'status', 'payment_method')}),
        ('Transaction', {'fields': ('transaction_id', 'receipt_url', 'payment_metadata')}),
        ('Dates', {'fields': ('created_at', 'completed_at')}),
    )
    ordering = ('-created_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFC107',
            'PROCESSING': '#3498DB',
            'COMPLETED': '#27AE60',
            'FAILED': '#E74C3C',
            'REFUNDED': '#95A5A6',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#95A5A6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

# Invoice Admin
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'user_email', 'total_amount', 'status_badge', 'issue_date')
    list_filter = ('status', 'issue_date')
    search_fields = ('invoice_number', 'user__email')
    readonly_fields = ('invoice_number', 'issue_date')
    
    fieldsets = (
        ('Invoice Info', {'fields': ('invoice_number', 'payment', 'user')}),
        ('Amounts', {'fields': ('amount', 'tax_amount', 'total_amount')}),
        ('Dates', {'fields': ('issue_date', 'due_date', 'paid_date')}),
        ('Status', {'fields': ('status',)}),
        ('Details', {'fields': ('pdf_url', 'notes')}),
    )
    ordering = ('-issue_date',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def status_badge(self, obj):
        colors = {
            'DRAFT': '#95A5A6',
            'ISSUED': '#3498DB',
            'PAID': '#27AE60',
            'OVERDUE': '#E74C3C',
            'CANCELLED': '#C0392B',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#95A5A6'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

# VerificationResult Admin
@admin.register(VerificationResult)
class VerificationResultAdmin(admin.ModelAdmin):
    list_display = ('check_request', 'status', 'risk_level_badge', 'verified_by', 'is_certified', 'verified_at')
    list_filter = ('status', 'risk_level', 'is_certified', 'verified_at')
    search_fields = ('check_request__request_id', 'verified_by__username')
    readonly_fields = ('verified_at',)
    
    fieldsets = (
        ('Verification Info', {'fields': ('check_request', 'verified_by')}),
        ('Status & Assessment', {'fields': ('status', 'risk_level', 'report_details', 'internal_notes')}),
        ('Certification', {'fields': ('is_certified', 'certificate_number')}),
        ('Timestamps', {'fields': ('verified_at',)}),
    )
    ordering = ('-verified_at',)

    def risk_level_badge(self, obj):
        colors = {
            'LOW': '#27AE60',
            'MEDIUM': '#E67E22',
            'HIGH': '#E74C3C',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.risk_level, '#95A5A6'),
            obj.get_risk_level_display()
        )
    risk_level_badge.short_description = 'Risk Level'

# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Recipient', {'fields': ('user',)}),
        ('Notification Content', {'fields': ('title', 'message', 'notification_type')}),
        ('Status', {'fields': ('is_read',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    ordering = ('-created_at',)
