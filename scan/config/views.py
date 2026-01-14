"""
Custom views for language switching and other utilities.
"""
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import translation
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect


@csrf_protect
@require_POST
def set_language_custom(request):
    """
    Custom language switching view that properly handles prefix_default_language=False.
    """
    next_url = request.POST.get('next', '/')
    language = request.POST.get('language')
    
    # SECURITY: Validate next_url to prevent open redirect attacks
    # Only allow internal URLs (starting with /)
    if not next_url or not next_url.startswith('/') or next_url.startswith('//'):
        next_url = '/'
    
    if language and language in [lang[0] for lang in settings.LANGUAGES]:
        # Activate the language
        translation.activate(language)
        
        # Translate the next URL to include language prefix if needed
        # For default language (ru), don't add prefix
        if language == settings.LANGUAGE_CODE:
            # Default language - remove prefix if present
            translated_url = next_url
            # Remove any language prefix
            for lang_code, _ in settings.LANGUAGES:
                if next_url.startswith(f'/{lang_code}/'):
                    translated_url = '/' + next_url[len(f'/{lang_code}/'):]
                    break
                elif next_url == f'/{lang_code}/' or next_url == f'/{lang_code}':
                    translated_url = '/'
                    break
        else:
            # Non-default language - add prefix if not present
            # Check if URL already has a language prefix
            has_prefix = False
            for lang_code, _ in settings.LANGUAGES:
                if next_url.startswith(f'/{lang_code}/') or next_url == f'/{lang_code}':
                    has_prefix = True
                    # Replace existing prefix with new one
                    if next_url.startswith(f'/{lang_code}/'):
                        translated_url = f'/{language}/' + next_url[len(f'/{lang_code}/'):]
                    else:
                        translated_url = f'/{language}/'
                    break
            
            if not has_prefix:
                # No prefix - add one
                path = next_url.lstrip('/')
                if path:
                    translated_url = f'/{language}/{path}'
                else:
                    translated_url = f'/{language}/'
        
        # Set language cookie
        response = HttpResponseRedirect(translated_url)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            language,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=getattr(settings, 'LANGUAGE_COOKIE_DOMAIN', None),
            secure=getattr(settings, 'LANGUAGE_COOKIE_SECURE', False),
            httponly=getattr(settings, 'LANGUAGE_COOKIE_HTTPONLY', False),
            samesite=getattr(settings, 'LANGUAGE_COOKIE_SAMESITE', 'Lax'),
        )
        return response
    
    # SECURITY: Validate next_url again before final redirect
    if not next_url.startswith('/') or next_url.startswith('//'):
        next_url = '/'
    # If language is invalid, redirect to next URL without changing language
    return HttpResponseRedirect(next_url)


def robots_txt(request):
    """
    Returns robots.txt file to prevent 404 warnings in logs.
    Allows all crawlers to access all content.
    """
    robots_content = """User-agent: *
Allow: /
"""
    return HttpResponse(robots_content, content_type='text/plain')


def test_liquidations(request):
    """
    Test page for liquidations WebSocket connection.
    """
    from django.shortcuts import render
    return render(request, 'test_liquidations.html')


