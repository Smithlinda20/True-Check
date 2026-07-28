import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Truecheck.settings')
django.setup()

from core.models import Service, ServicePackage
from decimal import Decimal

# Service descriptions
services_data = [
    {
        'name': 'CRIMINAL',
        'description': 'Comprehensive criminal background check covering federal, state, and local records.',
        'base_price': Decimal('55000'),
        'processing_time_days': 5,
    },
    {
        'name': 'EMPLOYMENT',
        'description': 'Verify employment history and previous employment records.',
        'base_price': Decimal('45000'),
        'processing_time_days': 3,
    },
    {
        'name': 'EDUCATION',
        'description': 'Verify educational credentials and degrees from institutions.',
        'base_price': Decimal('40000'),
        'processing_time_days': 3,
    },
    {
        'name': 'REFERENCE',
        'description': 'Contact and verify professional references.',
        'base_price': Decimal('42000'),
        'processing_time_days': 4,
    },
    {
        'name': 'IDENTITY',
        'description': 'Verify identity and personal identification documents.',
        'base_price': Decimal('48000'),
        'processing_time_days': 2,
    },
    {
        'name': 'HEALTH',
        'description': 'Drug screening and health screening tests.',
        'base_price': Decimal('65000'),
        'processing_time_days': 3,
    },
]

# Create services
print("Creating services...")
for data in services_data:
    service, created = Service.objects.get_or_create(
        name=data['name'],
        defaults={
            'description': data['description'],
            'base_price': data['base_price'],
            'processing_time_days': data['processing_time_days'],
            'is_active': True,
        }
    )
    status = "✅ Created" if created else "ℹ️  Already exists"
    print(f"   {status}: {service.get_name_display()}")

# Create service packages
print("\nCreating service packages...")

# Get services
criminal = Service.objects.get(name='CRIMINAL')
employment = Service.objects.get(name='EMPLOYMENT')
education = Service.objects.get(name='EDUCATION')
reference = Service.objects.get(name='REFERENCE')
identity = Service.objects.get(name='IDENTITY')
health = Service.objects.get(name='HEALTH')

packages_data = [
    {
        'name': 'Quick Verify',
        'package_type': 'BASIC',
        'description': 'Essential verification for initial screening and identity confirmation.',
        'price': Decimal('15000'),
        'discount_percentage': Decimal('0'),
        'processing_time_days': 2,
        'features': ['Identity Verification', 'Email Report', '24h Support'],
        'services': [identity],
    },
    {
        'name': 'Standard Check',
        'package_type': 'STANDARD',
        'description': 'Comprehensive verification with multiple checks for most hiring needs.',
        'price': Decimal('25000'),
        'discount_percentage': Decimal('5'),
        'processing_time_days': 3,
        'features': [
            'Criminal Background Check',
            'Employment History Verification',
            'Identity Verification',
            'Reference Checks',
            'Email & PDF Report',
            'Priority Support'
        ],
        'services': [criminal, employment, identity, reference],
    },
    {
        'name': 'Premium Check',
        'package_type': 'PREMIUM',
        'description': 'Complete verification suite including education and health screening.',
        'price': Decimal('45000'),
        'discount_percentage': Decimal('8'),
        'processing_time_days': 4,
        'features': [
            'Criminal Background Check',
            'Employment History Verification',
            'Educational Credential Verification',
            'Reference Checks',
            'Identity Verification',
            'Drug & Health Screening',
            'Certified Report',
            'Phone Support',
            'Unlimited Revisions'
        ],
        'services': [criminal, employment, education, reference, identity, health],
    },
    {
        'name': 'Enterprise Plan',
        'package_type': 'ENTERPRISE',
        'description': 'Complete solution for organizations with unlimited checks and custom support.',
        'price': Decimal('65000'),
        'discount_percentage': Decimal('12'),
        'processing_time_days': 2,
        'features': [
            'Unlimited Background Checks (Monthly)',
            'All Service Types Included',
            'Dedicated Account Manager',
            'Bulk Processing',
            'API Integration',
            'Custom Reports',
            'Priority Support 24/7',
            'Compliance Consulting',
            'SLA Guaranteed',
            'Quarterly Reviews'
        ],
        'services': [criminal, employment, education, reference, identity, health],
    },
]

for data in packages_data:
    package, created = ServicePackage.objects.get_or_create(
        name=data['name'],
        package_type=data['package_type'],
        defaults={
            'description': data['description'],
            'price': data['price'],
            'discount_percentage': data['discount_percentage'],
            'processing_time_days': data['processing_time_days'],
            'features': data['features'],
            'is_active': True,
        }
    )
    
    # Add services to package
    package.services.set(data['services'])
    
    status = "✅ Created" if created else "ℹ️  Already exists"
    print(f"   {status}: {package.name} ({package.get_package_type_display()})")

print("\n✅ Sample data setup completed successfully!")
