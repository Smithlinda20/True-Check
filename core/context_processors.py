from django.conf import settings


def site_settings(request):
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'TrueCheck'),
        'site_owner': getattr(settings, 'SITE_OWNER', 'TRUETRACE SOLUTION'),
        'site_tagline': getattr(settings, 'SITE_TAGLINE', 'Trusted verification powered by TRUETRACE SOLUTION'),
    }
