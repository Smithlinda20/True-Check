from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from decimal import Decimal
import uuid

from .models import (
    User, UserProfile, Service, ServicePackage,
    BackgroundCheckRequest, Payment, Invoice,
    VerificationResult, Notification
)


# ==================== HOME & PUBLIC VIEWS ====================

def home(request):
    """Home page with service showcase"""
    services = Service.objects.filter(is_active=True)
    packages = ServicePackage.objects.filter(is_active=True)
    
    partner_images = [
        'IMG-20260625-WA0001.jpg',
        'IMG-20260625-WA0002.jpg',
        'IMG-20260625-WA0003.jpg',
        'IMG-20260627-WA0067.jpg',
        'IMG-20260627-WA0075.jpg',
        'IMG-20260630-WA0042.jpg',
    ]

    context = {
        'services': services,
        'packages': packages,
        'total_checks': BackgroundCheckRequest.objects.count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'completed_checks': BackgroundCheckRequest.objects.filter(status='COMPLETED').count(),
        'partner_images': partner_images,
    }
    return render(request, 'core/home.html', context)


def services_page(request):
    """Services detail page"""
    services = Service.objects.filter(is_active=True)
    context = {'services': services}
    return render(request, 'core/services.html', context)


def pricing_page(request):
    """Pricing and packages page"""
    packages = ServicePackage.objects.filter(is_active=True).prefetch_related('services')
    
    context = {
        'packages': packages,
        'discount_packages': packages.filter(discount_percentage__gt=0),
    }
    return render(request, 'core/pricing.html', context)


# ==================== AUTHENTICATION VIEWS ====================

@require_http_methods(["GET", "POST"])
def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        user_type = request.POST.get('user_type', 'EMPLOYEE')
        company_name = request.POST.get('company_name', '').strip() if user_type == 'HR_EMPLOYER' else ''
        phone = request.POST.get('phone', '').strip()
        
        # Validation
        errors = []
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')
        
        if len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        
        if password != password_confirm:
            errors.append('Passwords do not match.')
        
        if user_type == 'HR_EMPLOYER' and not company_name:
            errors.append('Company name is required for HR/Employer account.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'core/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                user_type=user_type,
                company_name=company_name if company_name else None,
                phone=phone if phone else None,
                is_active=True,
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'core/register.html')
    
    return render(request, 'core/register.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please enter email and password.')
            return render(request, 'core/login.html')
        
        # Authenticate using email
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
        
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
        
        return render(request, 'core/login.html')
    
    return render(request, 'core/login.html')


@login_required(login_url='login')
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ==================== USER DASHBOARD & PROFILE ====================

@login_required(login_url='login')
def dashboard(request):
    """User dashboard"""
    user = request.user
    
    # Get user's check requests
    check_requests = BackgroundCheckRequest.objects.filter(user=user).prefetch_related('package', 'payment')
    
    # Statistics
    stats = {
        'total_requests': check_requests.count(),
        'pending': check_requests.filter(status='PENDING').count(),
        'in_progress': check_requests.filter(status__in=['UNDER_REVIEW', 'IN_PROGRESS']).count(),
        'completed': check_requests.filter(status='COMPLETED').count(),
        'total_spent': sum(
            float(req.total_amount) for req in check_requests.filter(payment__status='COMPLETED')
        ) if check_requests.exists() else 0,
    }
    
    # Recent notifications
    notifications = user.notifications.all()[:5]
    unread_count = user.notifications.filter(is_read=False).count()
    
    context = {
        'check_requests': check_requests[:10],
        'notifications': notifications,
        'unread_notifications': unread_count,
        'stats': stats,
    }
    return render(request, 'core/dashboard.html', context)


@login_required(login_url='login')
def profile(request):
    """User profile management"""
    user = request.user
    # Auto-create profile if it doesn't exist
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update basic user info
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        
        if user.user_type == 'HR_EMPLOYER':
            user.company_name = request.POST.get('company_name', '').strip()
        
        # Update profile info
        profile.date_of_birth = request.POST.get('date_of_birth') or None
        profile.gender = request.POST.get('gender') or None
        profile.national_id = request.POST.get('national_id', '').strip() or None
        profile.passport_number = request.POST.get('passport_number', '').strip() or None
        profile.address = request.POST.get('address', '').strip()
        profile.city = request.POST.get('city', '').strip()
        profile.state = request.POST.get('state', '').strip()
        profile.country = request.POST.get('country', '').strip()
        profile.zip_code = request.POST.get('zip_code', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        user.save()
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    # Get stats
    check_requests = BackgroundCheckRequest.objects.filter(user=request.user)
    total_checks = check_requests.count()
    completed_checks = check_requests.filter(status='COMPLETED').count()
    pending_checks = check_requests.filter(status='PENDING').count()
    total_spent = sum([r.total_amount for r in check_requests]) if check_requests else 0
    
    context = {
        'user_type_display': user.get_user_type_display(),
        'profile': profile,
        'total_checks': total_checks,
        'completed_checks': completed_checks,
        'pending_checks': pending_checks,
        'total_spent': total_spent,
    }
    return render(request, 'core/profile.html', context)


# ==================== BACKGROUND CHECK REQUESTS ====================

@login_required(login_url='login')
def request_check(request):
    """Request a background check"""
    packages = ServicePackage.objects.filter(is_active=True).prefetch_related('services')
    
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        service_ids = request.POST.getlist('services')
        
        try:
            package = ServicePackage.objects.get(id=package_id, is_active=True)
        except ServicePackage.DoesNotExist:
            messages.error(request, 'Invalid package selected.')
            return render(request, 'core/request_check.html', {'packages': packages})
        
        # Get selected services or use package services
        if service_ids:
            selected_services = Service.objects.filter(id__in=service_ids, is_active=True)
        else:
            selected_services = package.services.all()
        
        if not selected_services.exists():
            messages.error(request, 'Please select at least one service.')
            return render(request, 'core/request_check.html', {'packages': packages})
        
        # Applicant information
        applicant_name = request.POST.get('applicant_name', '').strip()
        applicant_email = request.POST.get('applicant_email', '').strip()
        applicant_phone = request.POST.get('applicant_phone', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        position_applied = request.POST.get('position_applied', '').strip()
        
        if not all([applicant_name, applicant_email, applicant_phone]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'core/request_check.html', {'packages': packages})
        
        # Calculate total amount
        total_amount = package.get_discounted_price()
        
        # Create background check request
        try:
            check_request = BackgroundCheckRequest.objects.create(
                user=request.user,
                package=package,
                applicant_name=applicant_name,
                applicant_email=applicant_email,
                applicant_phone=applicant_phone,
                company_name=company_name or None,
                position_applied=position_applied or None,
                total_amount=total_amount,
                status='PENDING',
            )
            
            # Add selected services
            check_request.selected_services.set(selected_services)
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                notification_type='REQUEST_CREATED',
                title='Background Check Request Created',
                message=f'Your background check request {check_request.request_id} has been created.',
                check_request=check_request,
            )
            
            messages.success(request, f'Request created: {check_request.request_id}')
            return redirect('check_detail', request_id=check_request.request_id)
        
        except Exception as e:
            messages.error(request, f'Error creating request: {str(e)}')
            return render(request, 'core/request_check.html', {'packages': packages})
    
    context = {'packages': packages}
    return render(request, 'core/request_check.html', context)


@login_required(login_url='login')
def check_detail(request, request_id):
    """View background check request details"""
    check_request = get_object_or_404(
        BackgroundCheckRequest,
        request_id=request_id,
        user=request.user
    )
    
    payment = check_request.payment if hasattr(check_request, 'payment') else None
    invoice = check_request.payment.invoice if payment and hasattr(payment, 'invoice') else None
    result = check_request.result if hasattr(check_request, 'result') else None
    
    context = {
        'check_request': check_request,
        'payment': payment,
        'invoice': invoice,
        'result': result,
    }
    return render(request, 'core/check_detail.html', context)


@login_required(login_url='login')
def my_checks(request):
    """List user's background checks"""
    status_filter = request.GET.get('status', '')
    
    check_requests = BackgroundCheckRequest.objects.filter(user=request.user).prefetch_related('package', 'selected_services')
    
    if status_filter:
        check_requests = check_requests.filter(status=status_filter)
    
    check_requests = check_requests.order_by('-requested_at')
    
    context = {
        'check_requests': check_requests,
        'status_filter': status_filter,
        'status_choices': BackgroundCheckRequest.STATUS_CHOICES,
    }
    return render(request, 'core/my_checks.html', context)


# ==================== PAYMENT & INVOICE ====================

@login_required(login_url='login')
def process_payment(request, request_id):
    """Process payment for a check request"""
    check_request = get_object_or_404(
        BackgroundCheckRequest,
        request_id=request_id,
        user=request.user,
        status='PENDING'
    )
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', '')
        
        if not payment_method:
            messages.error(request, 'Please select a payment method.')
            return redirect('check_detail', request_id=request_id)
        
        try:
            # Create payment record
            payment = Payment.objects.create(
                check_request=check_request,
                user=request.user,
                amount=check_request.total_amount,
                status='PROCESSING',
                payment_method=payment_method,
            )
            
            # In production, integrate with Stripe/PayPal here
            # For now, mark as completed
            payment.status = 'COMPLETED'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update check request status
            check_request.status = 'UNDER_REVIEW'
            check_request.started_at = timezone.now()
            check_request.save()
            
            # Create invoice
            Invoice.objects.create(
                payment=payment,
                user=request.user,
                amount=check_request.total_amount,
                total_amount=check_request.total_amount,
                status='ISSUED',
            )
            
            # Create notification
            Notification.objects.create(
                user=request.user,
                notification_type='PAYMENT_SUCCESS',
                title='Payment Successful',
                message=f'Payment of ₦{check_request.total_amount} for {check_request.request_id} successful.',
                check_request=check_request,
            )
            
            messages.success(request, 'Payment successful! Your request is now under review.')
            return redirect('check_detail', request_id=request_id)
        
        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('check_detail', request_id=request_id)
    
    context = {'check_request': check_request}
    return render(request, 'core/process_payment.html', context)


@login_required(login_url='login')
def my_invoices(request):
    """List user's invoices"""
    invoices = Invoice.objects.filter(user=request.user).order_by('-issue_date')
    
    context = {'invoices': invoices}
    return render(request, 'core/my_invoices.html', context)


# ==================== NOTIFICATIONS ====================

@login_required(login_url='login')
def notifications(request):
    """User notifications page"""
    user_notifications = request.user.notifications.all().order_by('-created_at')
    
    # Mark as read
    user_notifications.filter(is_read=False).update(is_read=True)
    
    context = {'notifications': user_notifications}
    return render(request, 'core/notifications.html', context)


@login_required(login_url='login')
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'status': 'success'})


# ==================== ERROR PAGES ====================

def custom_404(request, exception):
    """Custom 404 page"""
    return render(request, 'core/404.html', status=404)


def custom_500(request):
    """Custom 500 page"""
    return render(request, '500.html', status=500)
