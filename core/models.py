from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from decimal import Decimal

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("HR_EMPLOYER", "HR/Employer"),
        ("EMPLOYEE", "Employee"),
    )
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default="EMPLOYEE")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "user_type"]

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """Extended user profile for verification details"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    national_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Profile of {self.user.email}"


class Service(models.Model):
    """Background check and verification services"""
    SERVICE_CHOICES = [
        ('CRIMINAL', 'Criminal Background Check'),
        ('EMPLOYMENT', 'Employment History Verification'),
        ('EDUCATION', 'Educational Credential Verification'),
        ('REFERENCE', 'Reference Checks'),
        ('IDENTITY', 'Identity Verification'),
        ('HEALTH', 'Drug & Health Screening'),
    ]
    
    name = models.CharField(max_length=100, choices=SERVICE_CHOICES, unique=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    processing_time_days = models.IntegerField(validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()


class ServicePackage(models.Model):
    """Pricing packages for services"""
    PACKAGE_TYPE_CHOICES = [
        ('BASIC', 'Basic'),
        ('STANDARD', 'Standard'),
        ('PREMIUM', 'Premium'),
        ('ENTERPRISE', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=100)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES)
    description = models.TextField()
    services = models.ManyToManyField(Service, related_name='packages')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    processing_time_days = models.IntegerField(validators=[MinValueValidator(1)])
    features = models.JSONField(default=list)  # List of features included
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['package_type', 'price']
        unique_together = ['name', 'package_type']

    def __str__(self):
        return f"{self.name} ({self.get_package_type_display()})"

    def get_discounted_price(self):
        """Calculate final price after discount"""
        discount_amount = (self.price * self.discount_percentage) / 100
        return self.price - discount_amount


class BackgroundCheckRequest(models.Model):
    """User background check requests"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('UNDER_REVIEW', 'Under Review'),
        ('IN_PROGRESS', 'In Progress'),
        ('VERIFICATION_REQUIRED', 'Verification Required'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    request_id = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='check_requests')
    package = models.ForeignKey(ServicePackage, on_delete=models.PROTECT, related_name='check_requests')
    selected_services = models.ManyToManyField(Service, related_name='check_requests')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Verification data
    applicant_name = models.CharField(max_length=255)
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=255, blank=True)
    position_applied = models.CharField(max_length=255, blank=True)
    
    # Additional documents
    documents = models.JSONField(default=dict)  # Store file paths/URLs
    
    # Dates
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    
    # Review notes
    admin_notes = models.TextField(blank=True)
    result_summary = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['request_id']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.request_id} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.request_id:
            import uuid
            self.request_id = f"BGC-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment records"""
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Stripe'),
    ]
    
    payment_id = models.CharField(max_length=50, unique=True, db_index=True)
    check_request = models.OneToOneField(BackgroundCheckRequest, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    receipt_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata for payment gateway
    payment_metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.payment_id} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            import uuid
            self.payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """Invoice generation"""
    INVOICE_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ISSUED', 'Issued'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='DRAFT')
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    paid_date = models.DateTimeField(blank=True, null=True)
    
    pdf_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            import uuid
            year = timezone.now().year
            self.invoice_number = f"INV-{year}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class VerificationResult(models.Model):
    """Background check verification results"""
    RESULT_STATUS_CHOICES = [
        ('CLEAR', 'Clear'),
        ('ISSUES_FOUND', 'Issues Found'),
        ('PENDING_CLARIFICATION', 'Pending Clarification'),
        ('UNABLE_TO_VERIFY', 'Unable to Verify'),
    ]
    
    check_request = models.OneToOneField(BackgroundCheckRequest, on_delete=models.CASCADE, related_name='result')
    status = models.CharField(max_length=30, choices=RESULT_STATUS_CHOICES)
    findings = models.TextField(blank=True)
    risk_level = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')], default='LOW')
    
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_checks')
    verified_at = models.DateTimeField(auto_now_add=True)
    
    certificate_url = models.URLField(blank=True)
    is_certified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-verified_at']

    def __str__(self):
        return f"Result for {self.check_request.request_id}"


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPE_CHOICES = [
        ('REQUEST_CREATED', 'Request Created'),
        ('PAYMENT_SUCCESS', 'Payment Successful'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('STATUS_UPDATE', 'Status Update'),
        ('VERIFICATION_COMPLETE', 'Verification Complete'),
        ('DOCUMENT_NEEDED', 'Document Needed'),
        ('SYSTEM_ALERT', 'System Alert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    check_request = models.ForeignKey(BackgroundCheckRequest, on_delete=models.CASCADE, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.notification_type} for {self.user.email}"


# ==================== SIGNALS ====================
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when User is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
