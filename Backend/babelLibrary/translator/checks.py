"""
Django system checks for the translator/scraper module.

These checks run during `python manage.py check` and `python manage.py check --deploy`
to validate security-critical configuration settings.
"""
from django.conf import settings
from django.core.checks import register, Warning, Tags


@register(Tags.security, deploy=True)
def check_scraper_domain_whitelist(app_configs, **kwargs):
    """
    Check if SCRAPER_ALLOWED_DOMAINS is configured in production.
    
    This is a security check that warns if the domain whitelist is not set,
    which could allow SSRF (Server-Side Request Forgery) attacks.
    
    Runs during: python manage.py check --deploy
    """
    errors = []
    
    # Only check in non-DEBUG mode (production)
    if not settings.DEBUG:
        allowed_domains = getattr(settings, 'SCRAPER_ALLOWED_DOMAINS', None)
        
        if allowed_domains is None:
            errors.append(
                Warning(
                    'SCRAPER_ALLOWED_DOMAINS is not configured.',
                    hint=(
                        'Set SCRAPER_ALLOWED_DOMAINS in your settings to a list of trusted domains '
                        'to prevent SSRF attacks. Any public URL can be scraped via FlareSolverr '
                        'when this setting is not configured. '
                        'Example: SCRAPER_ALLOWED_DOMAINS = ["booktoki469.com", "example.com"]'
                    ),
                    obj='settings.SCRAPER_ALLOWED_DOMAINS',
                    id='translator.W001',
                )
            )
    
    return errors
